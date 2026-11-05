#!/bin/bash
# kaiju_tools: writes the np 16 / 52 scaling run dirs (jobs 3855-3861)
# np 52 against np 16 on the current recipe (Louis, 2026-11-04: "52 cores plus that super_lu trick and see if we can get
# it to run"; the throughput question). 10 steps each from TAf-v2's checkpoint 20 (the cancelled run's; its built cut
# lies wholly in the slab there, gap 0.0135), driver 9e69c6b (uw_rebuild_cells 1), development 25d62812, one exclusive
# node each, -log_view staged per solve (scaling/run_driver.py and its coarse-log hook). The patch is today's serial LU
# (the SuperLU_dist decomposed patch is asked of the dev hub). np 52 has the analytic wall-normal node-set defect
# (DECISIONS.md, uw_wall_normal): this is a timing test, and the wall check records how large the defect is.
#   prepare.sh 16 | 52
set -e
NP=${1:?ranks}
K=$HOME/+Claude/kaiju; DRV=$K/clones/zg95-v2-9e69c6b; OLD=$K/runs/slab_thermal_fault_TAf_v2; N=20
[ "$(git -C "$DRV" rev-parse --short HEAD)" = 9e69c6b ] && [ -z "$(git -C "$DRV" status --porcelain)" ] || { echo "driver clone not clean at 9e69c6b" >&2; exit 1; }
D=$K/runs/np_test_TAf_v2_ck20_np$NP
[ -e "$D" ] && { echo "$D exists" >&2; exit 1; }
mkdir -p "$D"
for f in "$OLD"/*.000$N.* "$OLD"/annulus.mesh.00000.* "$OLD"/annulus.solver_mesh.00000.*; do ln -s "$(readlink -f "$f")" "$D/"; done
cp "$OLD/state_000$N.json" "$D/"
python3 -c "
import json; R=json.load(open('$OLD/records.json')); json.dump([r for r in R if r.get('step',0)<=$N], open('$D/records.json','w'))"
ARGS=$(sed -E "s/-uw_init slab/-uw_init checkpoint/; s/-uw_steps [0-9]+/-uw_steps 10/" "$OLD/ARGS.txt")" -uw_restart $N"
echo "$ARGS" > "$D/ARGS.txt"
cat > "$D/README.md" <<TXT
# np_test_TAf_v2_ck20_np$NP: np $NP, 10 steps from TAf-v2 checkpoint 20 (the throughput test, 2026-11-04)
- Why: Louis wants throughput ("52 cores plus that super_lu trick"). np 52 against np 16 on the current recipe; the old
  measurement (339 against 487 s per step, 1.44x) was on the old recipe, whose serial patch was 3.2x larger.
- Driver 9e69c6b in $DRV (uw_rebuild_cells 1); development 25d62812; one exclusive node, n1 excluded; -log_view staged.
- The patch: today's serial LU on the band's rank. np 52 carries the analytic wall-normal node-set defect: a timing
  test; the wall check records it. DECISIONS.md: no decision changed.
- Seeded by symlink from $OLD checkpoint $N (not written).
- Args: -uw_out $D $ARGS -log_view :$D/log_view_np$NP.txt
TXT
echo "D=$D"
echo "ARGS=$ARGS"
