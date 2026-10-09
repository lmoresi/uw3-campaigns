"""Run a campaign's jobs under a process cap, each under the MPI hang supervisor.

Every job, serial ones included, runs as ``mpirun -n <np> python -u <driver> <args>``
under underworld3's ``scripts/mpi_supervisor.py``: one code path for serial and
parallel, and a hung collective is diagnosed (every rank's stack, the odd rank named)
and killed instead of holding cores. Jobs start in file order, first fit: whenever a
queued job's ranks fit under the cap with those running, the first such job starts.

The jobs file holds one JSON object per line::

    {"name": "micro_ref4_l1", "np": 1, "silence": 7200,
     "driver": "notch_length_scale/drivers/micromorphic_notch.py",
     "args": "-uw_ref 4 -uw_xi 0 -uw_beta 0.1 -uw_l_km 1 -uw_linear production_tight"}

Jobs appended to the jobs file while the runner is running are picked up on the next
poll. ``-uw_cap_file`` names a file holding the cap, re-read on every poll, so the cap
follows the machine's load (other people's runs) without restarting the runner.

An optional ``"priority"`` (default 0) orders the queue: while a job of a higher
priority is waiting, no lower-priority job starts, so the ranks it needs drain to it.
Jobs already queued take a new priority from the jobs file when the runner restarts
(restart is safe: running jobs are adopted, not relaunched).

``silence`` is the supervisor's budget in seconds of no output (a Newton step at fine
resolution can be quiet for a long time). Each job logs to ``<logs>/<name>.log``, and
every change of state is appended to ``<status>`` as one JSON line
(queued / running / done / failed / killed, with the exit code and the time), which is
the file to watch. ``-uw_report 1`` prints a table of the jobs and stops.

Usage (from the campaign repository root, inside the underworld3 environment)::

    pixi run -e dev python -u tools/campaign_runner.py -uw_jobs notch_length_scale/jobs/ref4.jsonl
"""
import json
import os
import shlex
import subprocess
import sys
import time

import underworld3 as uw

params = uw.Params(
    uw_jobs=uw.Param("", description="jobs file (JSON lines)"),
    uw_cap=uw.Param(4, description="most ranks running at once"),
    uw_cap_file=uw.Param("", description="file holding the cap as one integer, re-read every "
                                         "poll (raise or lower it without restarting); "
                                         "overrides -uw_cap while it exists"),
    uw_status=uw.Param("", description="status file (default: <jobs>.status.jsonl)"),
    uw_logs=uw.Param("", description="log directory (default: <jobs dir>/logs)"),
    uw_supervisor=uw.Param("", description="mpi_supervisor.py (default: the one shipped "
                                           "with the underworld3 checkout of this env)"),
    uw_poll=uw.Param(30.0, description="seconds between checks"),
    uw_report=uw.Param(0, description="1 = print the jobs' states and stop"),
)
jobs_path = os.path.abspath(str(params.uw_jobs))
status_path = str(params.uw_status) or jobs_path.replace(".jsonl", "") + ".status.jsonl"
logs = str(params.uw_logs) or os.path.join(os.path.dirname(jobs_path), "logs")
# the env lives at <checkout>/.pixi/envs/<env>/..., so the checkout is the part before .pixi
supervisor = str(params.uw_supervisor) or os.path.join(
    os.path.abspath(uw.__file__).split(os.sep + ".pixi" + os.sep)[0], "scripts", "mpi_supervisor.py")
if not os.path.exists(supervisor):
    raise FileNotFoundError(f"no mpi_supervisor.py at {supervisor}; pass -uw_supervisor")
# the env's own launcher, beside its python: a runner started outside ``pixi run`` would
# otherwise find the system mpirun, which cannot start the env's MPI
MPIRUN = os.path.join(os.path.dirname(sys.executable), "mpirun")
if not os.path.exists(MPIRUN):
    raise FileNotFoundError(f"no mpirun beside {sys.executable}")
EXIT_KILLED = 124


def read_jobs():
    with open(jobs_path) as fh:
        return [json.loads(line) for line in fh if line.strip()]


def last_states():
    states = {}
    if os.path.exists(status_path):
        with open(status_path) as fh:
            for line in fh:
                event = json.loads(line)
                states[event["name"]] = event
    return states


def record(name, state, **extra):
    event = dict(name=name, state=state, time=time.strftime("%Y-%m-%d %H:%M:%S"), **extra)
    with open(status_path, "a") as fh:
        fh.write(json.dumps(event) + "\n")
    print(f"[runner] {event['time']} {name}: {state} {extra if extra else ''}", flush=True)


def current_cap():
    path = str(params.uw_cap_file)
    if path and os.path.exists(path):
        with open(path) as fh:
            return int(fh.read().strip())
    return int(params.uw_cap)


def last_line(path, marker="SNES Function norm"):
    if not os.path.exists(path):
        return ""
    with open(path, errors="replace") as fh:
        lines = [l.strip() for l in fh if marker in l]
    return lines[-1] if lines else ""


def report():
    states = last_states()
    print(f"{'job':40s} {'np':>3s} {'state':9s} {'since':19s}  last Newton line")
    for job in read_jobs():
        s = states.get(job["name"], {})
        print(f"{job['name']:40s} {job['np']:>3d} {s.get('state', 'queued'):9s} "
              f"{s.get('time', ''):19s}  {last_line(os.path.join(logs, job['name'] + '.log'))}")


class _Adopted:
    """A job a previous runner started that is still alive: polled by pid. Its exit
    code is not recoverable (it is not our child), so it ends as "done"; the job's own
    log and record say how it went."""

    def __init__(self, pid):
        self.pid = pid

    def poll(self):
        try:
            os.kill(self.pid, 0)
            return None
        except ProcessLookupError:
            return 0


def run():
    os.makedirs(logs, exist_ok=True)
    states = last_states()
    finished = {n for n, s in states.items() if s["state"] in ("done", "failed", "killed")}
    running = {}
    jobs = {job["name"]: job for job in read_jobs()}
    for name, state in states.items():
        if state["state"] == "running" and name in jobs:
            adopted = _Adopted(state["pid"])
            if adopted.poll() is None:
                running[name] = (adopted, jobs[name], open(os.devnull, "w"))
                print(f"[runner] adopted {name} (pid {state['pid']})", flush=True)
    queue = [job for job in jobs.values() if job["name"] not in finished and job["name"] not in running]
    for job in queue:
        record(job["name"], "queued", np=job["np"])
    known = {job["name"] for job in queue} | finished | set(running)
    while True:
        # jobs appended to the file while the runner is running join the queue
        for job in read_jobs():
            if job["name"] not in known:
                known.add(job["name"])
                queue.append(job)
                record(job["name"], "queued", np=job["np"])
        if not (queue or running):
            break
        for name, (proc, job, log) in list(running.items()):
            rc = proc.poll()
            if rc is not None:
                log.close()
                state = "done" if rc == 0 else ("killed" if rc == EXIT_KILLED else "failed")
                record(name, state, rc=rc)
                del running[name]
        in_use = sum(job["np"] for _, job, _ in running.values())
        # first fit within the highest waiting priority: the first queued job of that
        # priority that fits starts, so a wide job waiting for ranks does not leave
        # narrow ones of its own priority idle behind it; lower priorities wait, so
        # they cannot keep taking the ranks a higher-priority wide job is waiting for
        while queue:
            top = max(j.get("priority", 0) for j in queue)
            fits = [j for j in queue
                    if j.get("priority", 0) == top and in_use + j["np"] <= current_cap()]
            if not fits:
                break
            job = fits[0]
            queue.remove(job)
            command = [sys.executable, supervisor, "--silence", str(job.get("silence", 3600)),
                       "--", MPIRUN, "-n", str(job["np"]), sys.executable, "-u",
                       job["driver"], *shlex.split(job.get("args", ""))]
            log = open(os.path.join(logs, job["name"] + ".log"), "w")
            proc = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT,
                                    env=dict(os.environ, UW_NO_USAGE_METRICS="1",
                                             # one thread per rank: an unset OpenMP /
                                             # BLAS pool takes every core per rank
                                             OMP_NUM_THREADS=os.environ.get("OMP_NUM_THREADS", "1"),
                                             OPENBLAS_NUM_THREADS=os.environ.get("OPENBLAS_NUM_THREADS", "1")))
            running[job["name"]] = (proc, job, log)
            record(job["name"], "running", np=job["np"], pid=proc.pid)
            in_use += job["np"]
        time.sleep(float(params.uw_poll))


if int(params.uw_report):
    report()
else:
    run()
