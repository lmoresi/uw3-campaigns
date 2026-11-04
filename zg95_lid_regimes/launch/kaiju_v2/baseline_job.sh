#!/bin/bash
# Recipe v2 runs on kaiju (from the baselines of 2026-11-04), one exclusive node, one segment.
# The driver runs through kaiju-launch/kaiju_uw3_job.sh; the stop rule and the convergence trigger run beside it in this
# job, because this session's login-node loops cannot reach Slurm or Apptainer (managed sandbox, 2026-11-03):
#  - stop at the base (Louis, 2026-10-28; stop_at_base.sh): when the slab tip (tip_depth.py) reaches 0.95 at checkpoint
#    N, stop the run once checkpoint N + EVERY is complete, so a restart can continue it;
#  - the pause trigger (the TAti supervisor v4's rule): two consecutive unconverged steps, or more than two in any ten,
#    are logged at once and the run stops at the next complete checkpoint (one segment, so the pause is a stop).
#  - the fault-in-slab check (2026-11-04): at every complete checkpoint, analysis/fault_in_slab.py measures the BUILT
#    cut's hot-mantle fraction (T > 0.7) and its gap to the detected fault, logged as a FAULT line. Any hot fraction is a
#    WATCH event; above 10 % the run pauses at the next complete checkpoint, as the convergence trigger does.
# Every unconverged step goes into the README with its Newton count and final relative residual. Events go to
# watch.log in the run dir. At the end the acceptance lines: the last checkpoint's fault-in-slab numbers and the
# KSP-cap check.
#   sbatch [...] --export=ALL,RUN_DIR=<run dir>,EVERY=<ckpt interval>,CONTAINER=...,EXTRA_PKGS=...,SCRIPT=<driver> \
#       baseline_job.sh <driver args>
set -u
D=${RUN_DIR:?run dir}; EVERY=${EVERY:?checkpoint interval}
SIF=/home/louis/uw3/images/uw3-gadi-development-20261021.sif
TIP=/home/louis/campaigns/kaiju-launch/slab_thermal_fault/tip_depth.py
FIS=${FIS:-$(dirname "$(dirname "$SCRIPT")")/analysis/fault_in_slab.py}   # beside the driver's repo
HOT_PAUSE=${HOT_PAUSE:-0.10}
LOG=$D/watch.log
note() { echo "$(date '+%F %T') $*" >> "$LOG"; }

complete() {   # checkpoint N complete: its state file and every file it lists
    local s; s=$D/$(printf "state_%05d.json" "$1")
    [ -e "$s" ] && python3 - "$s" "$D" <<'EOF'
import json, os, sys
s = json.load(open(sys.argv[1]))
sys.exit(0 if all(os.path.exists(os.path.join(sys.argv[2], f)) for f in s.get("checkpoint_files", [])) else 1)
EOF
}
last_complete() {
    for s in $(ls "$D"/state_*.json 2>/dev/null | sort -r); do
        n=$(basename "$s" | sed -E 's/state_0*([0-9]+)\.json/\1/'); [ -z "$n" ] && n=0
        complete "$n" && { echo "$n"; return; }
    done
}
trigger() {   # exit 0 = pause; records unconverged steps in the README
    python3 - "$D" <<'PY'
import glob, os, re, sys
D = sys.argv[1]
conv = {}
for f in sorted(glob.glob(os.path.join(D, "slurm_*.out"))):
    rel = None
    for line in open(f, errors="replace"):
        m = re.search(r"nonlinear iter \d+ .*rel=([0-9.eE+-]+)", line)
        if m:
            rel = float(m.group(1))
        m = re.match(r"\[0\] step (\d+) .*newton (\d+) conv (True|False)", line)
        if m:
            conv[int(m.group(1))] = (m.group(3) == "True", int(m.group(2)), rel)
bad = sorted(s for s, (ok, _, _) in conv.items() if not ok)
readme = os.path.join(D, "README.md")
seen = open(readme).read() if os.path.exists(readme) else ""
with open(readme, "a") as h:
    for s in bad:
        tag = f"- unconverged step {s}:"
        if tag not in seen:
            h.write(f"{tag} {conv[s][1]} Newton, final rel {conv[s][2]:.2e}\n" if conv[s][2] is not None
                    else f"{tag} {conv[s][1]} Newton\n")
pause = any(b + 1 in bad for b in bad) or any(sum(1 for x in bad if lo <= x < lo + 10) > 2 for lo in bad)
print("unconverged:", bad, "pause" if pause else "continue")
sys.exit(0 if pause else 1)
PY
}

note "job ${SLURM_JOB_ID} on ${SLURM_NODELIST}: driver started; stop at the base after checkpoint tip+${EVERY}; pause trigger on"
setsid bash /home/louis/campaigns/kaiju-launch/kaiju_uw3_job.sh "$@" &
RUN=$!
on_base=""; stop_at=""; why=""; checked=-1
fault_check() {   # the fault-in-slab numbers of checkpoint $1 as "hot gap" (one line of JSON kept in fault_in_slab.jsonl)
    local j; j=$(apptainer exec "$SIF" python3 "$FIS" "$D" --ckpt "$1" --json 2>/dev/null | tail -1)
    [ -z "$j" ] && return 1
    echo "$j" >> "$D/fault_in_slab.jsonl"
    python3 -c "import json,sys; c=json.loads(sys.argv[1]); print(c['built_hot_max'], c['gap_max'])" "$j"
}
while kill -0 "$RUN" 2>/dev/null; do
    sleep 120
    n=$(last_complete); n=${n:-0}
    if [ "$n" -gt "$checked" ] && read -r hot gap < <(fault_check "$n"); then
        checked=$n
        note "FAULT checkpoint $n: built cut hot fraction $hot, gap to detected $gap"
        if python3 -c "import sys; sys.exit(0 if float(sys.argv[1]) > 0 else 1)" "$hot"; then
            note "WATCH: the built cut reaches hot mantle at checkpoint $n (hot fraction $hot, gap $gap)"
        fi
        if [ "$why" != pause ] && python3 -c "import sys; sys.exit(0 if float(sys.argv[1]) > float(sys.argv[2]) else 1)" "$hot" "$HOT_PAUSE"; then
            echo "built cut hot fraction $hot > $HOT_PAUSE at checkpoint $n (gap $gap)" > "$D/.trigger"
            note "TRIGGER: built cut hot fraction $hot > $HOT_PAUSE at checkpoint $n; stopping at the next complete checkpoint"
            stop_at=$((n + EVERY)); why=pause
        fi
    fi
    if [ -z "$on_base" ]; then
        on_base=$(apptainer exec "$SIF" python3 "$TIP" "$D" 2>/dev/null | awk '/ON BASE/ {print $1; exit}')
        if [ -n "$on_base" ]; then
            note "BASE: tip on the base at checkpoint $on_base; stopping after $((on_base + EVERY))"
            if [ -z "$stop_at" ] || [ $((on_base + EVERY)) -lt "$stop_at" ]; then stop_at=$((on_base + EVERY)); why=base; fi
        fi
    fi
    if [ "$why" != pause ] && trigger > "$D/.trigger" 2>&1; then
        n=$(last_complete); n=${n:-0}
        note "TRIGGER: $(tail -1 "$D/.trigger"); stopping at the next complete checkpoint after $n"
        stop_at=$((n + EVERY)); why=pause
    fi
    if [ -n "$stop_at" ] && complete "$stop_at"; then
        sleep 20                                          # let records.json land
        kill -TERM -- -"$RUN" 2>/dev/null
        wait "$RUN" 2>/dev/null
        if [ "$why" = base ]; then
            cat >> "$D/README.md" <<EOF

## $(date '+%Y-%m-%d %H:%M') stopped at the base (Louis's rule)
The slab tip (tip_depth.py: T < 0.5 below 0.14, within 90 deg of the trench) reached 0.95 at checkpoint $on_base;
job ${SLURM_JOB_ID} stopped the driver after the next complete checkpoint, $stop_at. A restart from it continues the run.
EOF
            note "STOPPED at the base after checkpoint $stop_at"
        else
            cat >> "$D/README.md" <<EOF

## $(date '+%Y-%m-%d %H:%M') PAUSED by the convergence trigger
$(cat "$D/.trigger"); job ${SLURM_JOB_ID} stopped the driver after checkpoint $stop_at. A restart from it continues the run.
EOF
            note "PAUSED by the convergence trigger after checkpoint $stop_at"
        fi
        break
    fi
done
wait "$RUN" 2>/dev/null; rc=$?
[ -z "$why" ] && note "ENDED on its own (exit $rc; on the base at: ${on_base:-not reached})"
# the end-of-run acceptance: the fault in the slab (last complete checkpoint), then the KSP caps
n=$(last_complete); n=${n:-0}
if read -r hot gap < <(fault_check "$n"); then
    note "ACCEPTANCE fault in slab at checkpoint $n: built cut hot fraction $hot, gap $gap"
else
    note "ACCEPTANCE fault in slab: no measurement at checkpoint $n"
fi
python3 /home/louis/campaigns/kaiju-launch/ksp_cap_check.py "$D" || note "KSP cap check flagged steps (see slurm out)"
exit 0
