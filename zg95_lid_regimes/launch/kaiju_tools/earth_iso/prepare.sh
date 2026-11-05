#!/bin/bash
# kaiju_tools: writes the Earth isolation test run dirs (2026-11-03)
# Earth run 2's departure from Earth run 1 (the hub, 2026-11-04): three 10-step arms from Earth run 1's checkpoint 20 on
# the v2 build (development 25d62812, driver 64feaec), np 16, Earth run 2's line with one knob changed:
#   a  v2 as is
#   b  -uw_spacing 0.004 (W back to 0.008: the band, and with precedence 1 the bridge zone's x1e-3, four times narrower)
#   c  -uw_split_inset 3 (the cut's top back to three rungs inside the wall)
# Each run dir is seeded from run 1's checkpoint 20 by symlink (run 1's dir is not written) and reports step 30.
# This writes the run dirs and prints each arm's args; the sbatch line is typed from them (array 0-2, isolate_job.sh).
set -e
K=$HOME/+Claude/kaiju; S=$HOME/campaigns/zg95/runs/slab_earth_run1; CKPT=20
DRV=$K/clones/zg95-v2-64feaec
[ "$(git -C "$DRV" rev-parse --short HEAD)" = 64feaec ] && [ -z "$(git -C "$DRV" status --porcelain)" ] || { echo "driver clone not clean at 64feaec" >&2; exit 1; }
LINE=$(cat $K/runs/slab_earth_run2/ARGS.txt)
LINE=${LINE/-uw_init slab/-uw_init checkpoint}; LINE=${LINE/-uw_steps 130/-uw_steps 10}
declare -A KNOB=([a]="" [b]="-uw_spacing 0.004" [c]="-uw_split_inset 3")
declare -A WHAT=([a]="recipe v2 as is" [b]="-uw_spacing 0.004 (W 0.008, the band four times narrower)" [c]="-uw_split_inset 3")
for arm in a b c; do
    D=$K/runs/earth_iso_${arm}_ck20
    [ -e "$D" ] && { echo "$D exists" >&2; exit 1; }
    mkdir -p "$D"
    for f in "$S"/*.$(printf %05d $CKPT).* "$S"/annulus.mesh.00000.* "$S"/annulus.solver_mesh.00000.*; do ln -s "$(readlink -f "$f")" "$D/"; done
    cp "$S/state_$(printf %05d $CKPT).json" "$D/"
    python3 -c "
import json; R=json.load(open('$S/records.json')); json.dump([r for r in R if r.get('step',0)<=$CKPT], open('$D/records.json','w'))"
    ARGS="$LINE -uw_restart $CKPT ${KNOB[$arm]}"
    echo "$ARGS" > "$D/ARGS.txt"
    cat > "$D/README.md" <<TXT
# earth_iso_${arm}_ck20: why Earth run 2 departs from Earth run 1 (the hub, 2026-11-04), arm ${arm}
- Arm ${arm}: ${WHAT[$arm]}; everything else recipe v2 (Earth run 2's line), 10 steps from Earth run 1's checkpoint 20
  (seeded by symlink; run 1's dir is not written), reported at step 30 against run 1 and run 2.
- Build: underworld3 development 25d62812, image uw3-gadi-development-20261021.sif; driver 64feaec in $DRV;
  np 16, one node, exclusive (n1 excluded).
- The restart rule re-samples the restored polyline (S 0.004) at this run's S where they differ (arms a and c).
- DECISIONS.md: no decision changed by this run (a test of one knob each).
- Args: -uw_out $D $ARGS
TXT
    echo "$arm: $D"
    echo "  $ARGS"
done
