#!/bin/bash
# kaiju_tools: renders the recipe v2 baselines and their old twins (2026-11-04)
# Side-by-side movies of the recipe v2 baselines against their old twins (Louis, 2026-11-04: "It has to be movies then"):
#   TAf_env | TAf-v2      and      Earth run 1 | Earth run 2
# 1. renders every complete checkpoint of TAf_env, TAf-v2 and Earth run 2 with the velocity-ring renderer
#    (~/campaigns/zg95-render-vring a7d339a, read only), as slab_movies/movie_slab_vring.sh does, with the ring at a
#    fixed 6000 for all four runs, and a window on the trench (-uw_zoom 0.5) for each; all eight at once;
# 2. pair_frames.py: the left two panels (T with streamlines and marker outlines; log10 strain rate) of each run, side
#    by side at the same step (the slab tips match per step within a few per cent), each half labelled with the run,
#    step, model time and slab tip depth -> ~/+Claude/kaiju/movies/out/<pair>.mp4
# Runs still going are rendered to their last complete checkpoint; rerun at the base for the whole history.
#SBATCH --job-name=pair_movies
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=128G
#SBATCH --time=02:00:00
#SBATCH --exclude=n1
#SBATCH --output=/home/louis/+Claude/kaiju/movies/pair_movies_%j.out
#SBATCH --error=/home/louis/+Claude/kaiju/movies/pair_movies_%j.err
set -uo pipefail
export PATH=/usr/local/bin:/usr/bin:/bin   # submitted with --export=NONE (the session's environment cannot be written)
M=/home/louis/+Claude/kaiju/movies
SIF=/home/louis/uw3/images/uw3-gadi-development-20261021.sif
LIB=/home/louis/uw3/overlay-warmdiag
CAMP=/home/louis/campaigns/zg95-render-vring/zg95_lid_regimes
HEADLESS=/home/louis/campaigns/kaiju-launch/slab_scan/render_headless.py
declare -A RUN=([earth_run1]=/home/louis/campaigns/zg95/runs/slab_earth_run1
                [TAf_env]=/home/louis/campaigns/zg95/runs/slab_thermal_fault_TAf_env
                [TAf_v2]=/home/louis/+Claude/kaiju/runs/slab_thermal_fault_TAf_v2
                [earth_run2]=/home/louis/+Claude/kaiju/runs/slab_earth_run2)
ax() { APPTAINERENV_OMPI_MCA_pml=ob1 APPTAINERENV_OMPI_MCA_btl=self,vader APPTAINERENV_OMP_NUM_THREADS=1 \
       apptainer exec --bind "$LIB:/uw3-extra" "$SIF" bash -c "PYTHONPATH=/uw3-extra:\$PYTHONPATH MPLBACKEND=Agg $*"; }
complete() {   # checkpoint state file complete: every file it lists exists
    python3 - "$1" "$(dirname "$1")" <<'EOF'
import json, os, sys
s = json.load(open(sys.argv[1]))
sys.exit(0 if all(os.path.exists(os.path.join(sys.argv[2], f)) for f in s.get("checkpoint_files", [])) else 1)
EOF
}
t0=$(date +%s)
for name in "${!RUN[@]}"; do
    W=$M/work/$name; R=${RUN[$name]}
    mkdir -p "$W/ckpts" "$W/frames"
    find "$W/ckpts" -maxdepth 1 -type l -delete
    for f in "$R"/annulus.*.00000.* "$R"/annulus.*00000.* "$R"/records.json "$R"/run_info.json; do [ -e "$f" ] && ln -sf "$f" "$W/ckpts/"; done
    for s in "$R"/state_*.json; do
        complete "$s" || continue
        n=$(basename "$s" | sed -E 's/state_([0-9]+)\.json/\1/')
        ln -sf "$s" "$W/ckpts/"
        for f in "$R"/annulus.*.$n.* "$R"/annulus.*$n.*; do [ -e "$f" ] && ln -sf "$f" "$W/ckpts/"; done
    done
    mkdir -p "$W/zoom"
    ( ax python3 "$HEADLESS" "$CAMP/render/render_annulus.py" -uw_run "$W/ckpts" -uw_panels strain -uw_zoom 0 \
          -uw_trace_width 6 -uw_vring 0.2 -uw_vring_vmax 6000 -uw_renders "$W/frames" > "$W/render.log" 2>&1
      echo "$name: $(ls "$W/frames"/frame_*.png 2>/dev/null | wc -l) whole frames, $(( $(date +%s) - t0 )) s" ) &
    ( ax python3 "$HEADLESS" "$CAMP/render/render_annulus.py" -uw_run "$W/ckpts" -uw_panels strain -uw_zoom 0.5 \
          -uw_renders "$W/zoom" > "$W/render_zoom.log" 2>&1
      echo "$name: $(ls "$W/zoom"/*.png 2>/dev/null | wc -l) zoom images ($(ls "$W/zoom" | head -2 | tr '\n' ' ')), $(( $(date +%s) - t0 )) s" ) &
done
wait
ax python3 /home/louis/+Claude/kaiju/launch/movies/pair_frames.py frame
ax python3 /home/louis/+Claude/kaiju/launch/movies/pair_frames.py zoom
echo "total $(( $(date +%s) - t0 )) s"
