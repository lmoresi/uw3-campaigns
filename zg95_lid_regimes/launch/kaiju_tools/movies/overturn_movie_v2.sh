#!/bin/bash
# kaiju_tools: the restyled overturn movie: particles, no contours, render_v2 (job 3992)
# The Earth overturn movie, restyled (Louis, 2026-11-05: no marker contours; continent and oceanic crust as particles, orange and dark green): steps 0-480, render_v2 renderer; otherwise overturn_movie.sh.
#SBATCH --job-name=overturn_v2
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=02:00:00
#SBATCH --exclude=n1
#SBATCH --output=/home/louis/+Claude/kaiju/movies/overturn_v2_%j.out
#SBATCH --error=/home/louis/+Claude/kaiju/movies/overturn_v2_%j.err
set -uo pipefail
export PATH=/usr/local/bin:/usr/bin:/bin
M=/home/louis/+Claude/kaiju/movies
RUN=/home/louis/+Claude/kaiju/runs/slab_earth_run2_c
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
W=$M/work/earth_overturn_v2; mkdir -p "$W/ckpts" "$W/frames" "$W/zoom"
find "$W/ckpts" -maxdepth 1 -type l -delete
for f in "$RUN"/annulus.*00000.*; do [ -e "$f" ] && ln -sf "$(readlink -f "$f")" "$W/ckpts/"; done
cp "$RUN/records.json" "$W/ckpts/records.json"
for s in "$RUN"/state_*.json; do complete "$s" && link_ckpt "$s" "$W/ckpts"; done
echo "checkpoints: $(ls "$W"/ckpts/state_*.json | wc -l)"
( ax python3 "$HEADLESS" "$RENDER" -uw_run "$W/ckpts" -uw_panels strain -uw_zoom 0 \
      -uw_trace_width 6 -uw_vring 0.2 -uw_vring_vmax 6000 -uw_outlines 0 -uw_particles 1 -uw_pt_crust 1.5 -uw_pt_cont 2.5 -uw_renders "$W/frames" > "$W/render.log" 2>&1
  echo "whole: $(ls "$W/frames"/frame_*.png 2>/dev/null | wc -l) frames, $(( $(date +%s) - t0 )) s" ) &
( ax python3 "$HEADLESS" "$RENDER" -uw_run "$W/ckpts" -uw_panels strain -uw_zoom 0.5 -uw_outlines 0 -uw_particles 1 -uw_pt_crust 2 -uw_pt_cont 4 \
      -uw_renders "$W/zoom" > "$W/render_zoom.log" 2>&1
  echo "zoom: $(ls "$W/zoom"/*.png 2>/dev/null | wc -l) images, $(( $(date +%s) - t0 )) s" ) &
wait
ax python3 /home/louis/+Claude/kaiju/launch/movies/overturn_frames.py v2
echo "total $(( $(date +%s) - t0 )) s"
