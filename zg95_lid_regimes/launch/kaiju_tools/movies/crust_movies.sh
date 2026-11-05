#!/bin/bash
# kaiju_tools: renders every checkpoint of the six crust-test arms and composes the movies (jobs 4035, 4050)
# The crust-test renders so far (Louis, 2026-11-05: "I still would like to see how the evolution looks"): every complete
# checkpoint of the six arms (TAf and Earth: production crust, half-element crust, passive crust), whole annulus and
# trench window in the approved style (render_v2: particles, no contours), six renders at a time; composed by
# crust_frames.py into out/crust_TAf.mp4 and out/crust_earth.mp4. Runs still going are read, not written.
#SBATCH --job-name=crust_movies
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=12
#SBATCH --mem=120G
#SBATCH --time=03:00:00
#SBATCH --exclude=n1
#SBATCH --output=/home/louis/+Claude/kaiju/movies/crust_movies_%j.out
#SBATCH --error=/home/louis/+Claude/kaiju/movies/crust_movies_%j.err
set -uo pipefail
export PATH=/usr/local/bin:/usr/bin:/bin
M=/home/louis/+Claude/kaiju/movies
R=/home/louis/+Claude/kaiju/runs
SIF=/home/louis/uw3/images/uw3-gadi-development-20261021.sif
LIB=/home/louis/uw3/overlay-warmdiag
RENDER=/home/louis/+Claude/kaiju/launch/render_v2/render/render_annulus.py
HEADLESS=/home/louis/campaigns/kaiju-launch/slab_scan/render_headless.py
ax() { APPTAINERENV_OMPI_MCA_pml=ob1 APPTAINERENV_OMPI_MCA_btl=self,vader APPTAINERENV_OMP_NUM_THREADS=1 \
       apptainer exec --bind "$LIB:/uw3-extra" "$SIF" bash -c "PYTHONPATH=/uw3-extra:\$PYTHONPATH MPLBACKEND=Agg $*"; }
complete() {
    python3 - "$1" "$(dirname "$1")" <<'EOF'
import json, os, sys
s = json.load(open(sys.argv[1]))
sys.exit(0 if all(os.path.exists(os.path.join(sys.argv[2], f)) for f in s.get("checkpoint_files", [])) else 1)
EOF
}
link_ckpt() {
    local s=$1 W=$2 n; n=$(basename "$s" | sed -E 's/state_([0-9]+)\.json/\1/')
    ln -sf "$(readlink -f "$s")" "$W/"
    for f in "$(dirname "$s")"/annulus.*.$n.* "$(dirname "$s")"/annulus.*$n.*; do [ -e "$f" ] && ln -sf "$(readlink -f "$f")" "$W/"; done
}
t0=$(date +%s)
for c in TAf earth; do for a in c1 c05 passive; do
    RUN=$R/crust_${c}_${a}; W=$M/work/crust_${c}_${a}; mkdir -p "$W/ckpts" "$W/frames" "$W/zoom"
    find "$W/ckpts" -maxdepth 1 -type l -delete
    for f in "$RUN"/annulus.*00000.*; do [ -e "$f" ] && ln -sf "$(readlink -f "$f")" "$W/ckpts/"; done
    cp "$RUN/records.json" "$W/ckpts/records.json"
    for s in "$RUN"/state_*.json; do complete "$s" && link_ckpt "$s" "$W/ckpts"; done
    echo "crust_${c}_${a}: $(ls "$W"/ckpts/state_*.json | wc -l) checkpoints"
    ( ax python3 "$HEADLESS" "$RENDER" -uw_run "$W/ckpts" -uw_panels strain -uw_zoom 0 -uw_trace_width 6 -uw_vring 0.2 \
          -uw_vring_vmax 6000 -uw_outlines 0 -uw_particles 1 -uw_pt_crust 1.5 -uw_pt_cont 2.5 -uw_renders "$W/frames" \
          > "$W/render.log" 2>&1
      echo "crust_${c}_${a}: whole $(ls "$W/frames"/frame_*.png 2>/dev/null | wc -l), $(( $(date +%s) - t0 )) s" ) &
    ( ax python3 "$HEADLESS" "$RENDER" -uw_run "$W/ckpts" -uw_panels strain -uw_zoom 0.5 -uw_outlines 0 -uw_particles 1 \
          -uw_pt_crust 2 -uw_pt_cont 4 -uw_renders "$W/zoom" > "$W/render_zoom.log" 2>&1
      echo "crust_${c}_${a}: zoom $(ls "$W/zoom"/zoom_*.png 2>/dev/null | wc -l), $(( $(date +%s) - t0 )) s" ) &
done; done
wait
ax python3 /home/louis/+Claude/kaiju/launch/movies/crust_frames.py
echo "total $(( $(date +%s) - t0 )) s"
