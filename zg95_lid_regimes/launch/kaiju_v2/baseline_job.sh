#!/bin/bash
# Recipe v2 runs on kaiju (from the baselines of 2026-11-04), one exclusive node, one segment.
# The driver runs through kaiju-launch/kaiju_uw3_job.sh; the stop rule and the convergence trigger run beside it in this
# job, because this session's login-node loops cannot reach Slurm or Apptainer (managed sandbox, 2026-11-03):
#  - stop at the base (Louis, 2026-10-28; stop_at_base.sh): when the slab tip (tip_depth.py) reaches 0.95 at checkpoint
#    N, stop the run once checkpoint N + EVERY is complete, so a restart can continue it. STOP_AT_BASE=0 (the overturn
#    runs, 2026-11-04) logs the base and runs on to -uw_steps;
#  - the pause trigger (the TAti supervisor v4's rule): two consecutive unconverged steps, or more than two in any ten,
#    are logged at once and the run stops at the next complete checkpoint (one segment, so the pause is a stop).
#  - the fault-in-slab check (2026-11-04): at every complete checkpoint, analysis/fault_in_slab.py measures the BUILT
#    cut's hot-mantle fraction (T > 0.7) over its top (depth <= TOP_DEPTH, 0.09) and its deep end, and its gap to the
#    detected fault in base cells, logged as a FAULT line. The run pauses at the next complete checkpoint, as the
#    convergence trigger does, when the top's hot fraction exceeds HOT_PAUSE (0.10) or the gap exceeds GAP_PAUSE (2.0)
#    base cells; a hot deep end is a WATCH line only (it runs along the slab top's warm margin near the depth cap, and
#    a five-step lag puts part of the built cut in it: TAf-v2 checkpoint 50, TAf_env on the old recipe likewise).
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
HOT_PAUSE=${HOT_PAUSE:-0.10}               # the top of the built cut: hot fraction that pauses
GAP_PAUSE=${GAP_PAUSE:-2.0}                # the built cut's gap to the detected fault, base cells, that pauses
TOP_DEPTH=${TOP_DEPTH:-0.09}               # the top of the cut: depth <= TOP_DEPTH
STOP_AT_BASE=${STOP_AT_BASE:-1}            # 0: log the base and run on (a full overturn)
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

note "job ${SLURM_JOB_ID} on ${SLURM_NODELIST}: driver started; $( [ "$STOP_AT_BASE" = 1 ] && echo "stop at the base after checkpoint tip+${EVERY}" || echo "no stop at the base (STOP_AT_BASE=0)"); pause trigger on"
# the watcher's choices, beside the driver's choices block
cat >> "$D/README.md" <<TXT

## Watcher choices (launch/kaiju_v2/baseline_job.sh, job ${SLURM_JOB_ID})
| knob | value |
|---|---|
| STOP_AT_BASE | $STOP_AT_BASE (1: stop one checkpoint interval after the tip reaches 0.95; 0: run on) |
| EVERY (checkpoint interval) | $EVERY |
| HOT_PAUSE (hot fraction of the built cut's top that pauses) | $HOT_PAUSE |
| GAP_PAUSE (built cut to detected fault, base cells, that pauses) | $GAP_PAUSE |
| TOP_DEPTH (the top of the cut: depth <= this) | $TOP_DEPTH |
TXT
setsid bash /home/louis/campaigns/kaiju-launch/kaiju_uw3_job.sh "$@" &
RUN=$!
on_base=""; stop_at=""; why=""; checked=-1
fault_check() {   # checkpoint $1 as "top deep gap cells" (built cut's hot fractions, gap; JSON kept in fault_in_slab.jsonl)
    local j; j=$(apptainer exec "$SIF" python3 "$FIS" "$D" --ckpt "$1" --json --top "$TOP_DEPTH" 2>/dev/null | tail -1)
    [ -z "$j" ] && return 1
    echo "$j" >> "$D/fault_in_slab.jsonl"
    python3 -c "import json,sys; c=json.loads(sys.argv[1]); print(c['built_hot_top_max'], c['built_hot_deep_max'], c['gap_max'], c['gap_cells_max'])" "$j"
}
over() { python3 -c "import sys; sys.exit(0 if float(sys.argv[1]) > float(sys.argv[2]) else 1)" "$1" "$2"; }
while kill -0 "$RUN" 2>/dev/null; do
    sleep 120
    n=$(last_complete); n=${n:-0}
    if [ "$n" -gt "$checked" ] && read -r top deep gap cells < <(fault_check "$n"); then
        checked=$n
        note "FAULT checkpoint $n: built cut hot fraction top $top, deep $deep; gap to detected $gap ($cells base cells)"
        if over "$top" 0 || over "$deep" 0; then
            note "WATCH: the built cut reaches hot mantle at checkpoint $n (top $top, deep $deep, gap $cells base cells)"
        fi
        if [ "$why" != pause ] && { over "$top" "$HOT_PAUSE" || over "$cells" "$GAP_PAUSE"; }; then
            echo "built cut at checkpoint $n: top hot fraction $top (pause above $HOT_PAUSE), gap $cells base cells (pause above $GAP_PAUSE)" > "$D/.trigger"
            note "TRIGGER: $(cat "$D/.trigger"); stopping at the next complete checkpoint"
            stop_at=$((n + EVERY)); why=pause
        fi
    fi
    if [ -z "$on_base" ]; then
        on_base=$(apptainer exec "$SIF" python3 "$TIP" "$D" 2>/dev/null | awk '/ON BASE/ {print $1; exit}')
        if [ -n "$on_base" ] && [ "$STOP_AT_BASE" = 1 ]; then
            note "BASE: tip on the base at checkpoint $on_base; stopping after $((on_base + EVERY))"
            if [ -z "$stop_at" ] || [ $((on_base + EVERY)) -lt "$stop_at" ]; then stop_at=$((on_base + EVERY)); why=base; fi
        elif [ -n "$on_base" ]; then
            note "BASE: tip on the base at checkpoint $on_base; running on (STOP_AT_BASE=0)"
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

## $(date '+%Y-%m-%d %H:%M') PAUSED by a trigger (convergence or fault in slab)
$(cat "$D/.trigger"); job ${SLURM_JOB_ID} stopped the driver after checkpoint $stop_at. A restart from it continues the run.
EOF
            note "PAUSED by a trigger after checkpoint $stop_at: $(head -1 "$D/.trigger")"
        fi
        break
    fi
done
wait "$RUN" 2>/dev/null; rc=$?
[ -z "$why" ] && note "ENDED on its own (exit $rc; on the base at: ${on_base:-not reached})"
# the end-of-run acceptance: the fault in the slab (last complete checkpoint), then the KSP caps
n=$(last_complete); n=${n:-0}
if read -r top deep gap cells < <(fault_check "$n"); then
    note "ACCEPTANCE fault in slab at checkpoint $n: built cut hot fraction top $top, deep $deep; gap $gap ($cells base cells)"
else
    note "ACCEPTANCE fault in slab: no measurement at checkpoint $n"
fi
python3 /home/louis/campaigns/kaiju-launch/ksp_cap_check.py "$D" || note "KSP cap check flagged steps (see slurm out)"
exit 0
