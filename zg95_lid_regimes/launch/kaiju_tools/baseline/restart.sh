#!/bin/bash
# kaiju_tools: restart line for a baseline run from a checkpoint (used once, 2026-11-04)
# USED ONCE, for the 2026-11-04 restarts 3849/3850 on driver 64feaec. Driver 9e69c6b refuses -uw_rebuild_rungs: a
# restart on it takes the default uw_rebuild_cells 1 and needs neither flag nor this script's note.
# Restart a recipe v2 baseline with -uw_rebuild_rungs 1 (Louis, 2026-11-04: "cancel and restart both with
# rebuild_rungs 1"). Recipe v2's rung spacing (one base cell, 0.0156) made the rebuild threshold, counted in rungs,
# four times the old one (4 x 0.0156 = 0.0625 against 4 x 0.004 = 0.016): the BUILT fault lagged the detected one
# into hot mantle (Earth run 2: up to 69 % of the cut with T > 0.7 by step 60; TAf-v2: 85 % at checkpoint 40, all of
# it at 45). One rung at S = h_b is 0.0156, the old threshold. The new run dir is seeded by symlink from the old run's
# last checkpoint whose built fault was wholly in slab; the old run dir is not written (its README gets the note).
#   restart.sh <old run dir> <new run dir> <checkpoint> <total steps>
set -e
OLD=${1:?old run dir}; NEW=${2:?new run dir}; N=${3:?checkpoint}; TOTAL=${4:?total steps}
[ -e "$NEW" ] && { echo "$NEW exists" >&2; exit 1; }
mkdir -p "$NEW"
NN=$(printf %05d "$N")
for f in "$OLD"/*.$NN.* "$OLD"/annulus.mesh.00000.* "$OLD"/annulus.solver_mesh.00000.*; do ln -s "$(readlink -f "$f")" "$NEW/"; done
cp "$OLD/state_$NN.json" "$NEW/"
python3 -c "
import json; R=json.load(open('$OLD/records.json')); json.dump([r for r in R if r.get('step',0)<=$N], open('$NEW/records.json','w'))"
LINE=$(cat "$OLD/ARGS.txt")
LINE=$(echo "$LINE" | sed -E "s/-uw_init slab/-uw_init checkpoint/; s/-uw_steps [0-9]+/-uw_steps $((TOTAL - N))/")
ARGS="$LINE -uw_restart $N -uw_rebuild_rungs 1"
echo "$ARGS" > "$NEW/ARGS.txt"
cat > "$NEW/README.md" <<TXT
# $(basename "$NEW"): $(basename "$OLD") restarted from checkpoint $N with -uw_rebuild_rungs 1 (Louis, 2026-11-04)
- Why: recipe v2's rung spacing (one base cell, 0.0156) made the rebuild threshold, counted in rungs, 4 x 0.0156 = 0.0625
  against the old recipe's 4 x 0.004 = 0.016, so the built fault lagged the detected one into hot mantle
  (fault_in_slab.py). One rung at S = h_b is 0.0156, the old threshold.
- Seeded by symlink from $OLD checkpoint $N, the last whose built fault lies wholly in slab (T < 0.5); the old run dir
  is not written. Steps to $TOTAL at most; the in-job stop at the base and pause trigger as before.
- Everything else as $(basename "$OLD") (recipe v2; development 25d62812; driver 64feaec; np 16, one exclusive node).
- DECISIONS.md: uw_rebuild_rungs changes from 4 to 1 for this run (a correction of recipe v2; the ledger row to follow).
- Args: -uw_out $NEW $ARGS
TXT
cat >> "$OLD/README.md" <<TXT

## $(date '+%Y-%m-%d %H:%M') cancelled (Louis): the built fault lagged into hot mantle
uw_rebuild_rungs 4 at S = h_b allowed the built fault to drift 0.0625 from the detected one; continued from checkpoint
$N with -uw_rebuild_rungs 1 in $NEW.
TXT
echo "NEW=$NEW"
echo "ARGS=$ARGS"
