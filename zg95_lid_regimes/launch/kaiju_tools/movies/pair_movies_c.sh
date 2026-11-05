#!/bin/bash
# kaiju_tools: the same for the step-0 reruns (_c) (2026-11-04)
# Side-by-side movies of the step-0 recipe v2 reruns on the corrected driver (TAf-v2_c, Earth run 2_c, which carries
# on past the base into the overturn) against their old twins, every complete checkpoint so far; the twins' frames are
# reused from pair_movies.sh. Composes with PAIRSET=c into out/*_c*.mp4 (the earlier movies are not touched).
#SBATCH --job-name=pair_movies_c
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=02:00:00
#SBATCH --exclude=n1
#SBATCH --output=/home/louis/+Claude/kaiju/movies/pair_movies_c_%j.out
#SBATCH --error=/home/louis/+Claude/kaiju/movies/pair_movies_c_%j.err
set -uo pipefail
export PATH=/usr/local/bin:/usr/bin:/bin   # submitted with --export=NONE (the session's environment cannot be written)
M=/home/louis/+Claude/kaiju/movies
R=/home/louis/+Claude/kaiju/runs
SIF=/home/louis/uw3/images/uw3-gadi-development-20261021.sif
LIB=/home/louis/uw3/overlay-warmdiag
CAMP=/home/louis/campaigns/zg95-render-vring/zg95_lid_regimes
HEADLESS=/home/louis/campaigns/kaiju-launch/slab_scan/render_headless.py
declare -A NEW=([TAf_v2]=$R/slab_thermal_fault_TAf_v2_c [earth_run2]=$R/slab_earth_run2_c)
ax() { APPTAINERENV_OMPI_MCA_pml=ob1 APPTAINERENV_OMPI_MCA_btl=self,vader APPTAINERENV_OMP_NUM_THREADS=1 \
       apptainer exec --bind "$LIB:/uw3-extra" "$SIF" bash -c "PYTHONPATH=/uw3-extra:\$PYTHONPATH MPLBACKEND=Agg $*"; }
complete() {
    python3 - "$1" "$(dirname "$1")" <<'EOF'
import json, os, sys
s = json.load(open(sys.argv[1]))
sys.exit(0 if all(os.path.exists(os.path.join(sys.argv[2], f)) for f in s.get("checkpoint_files", [])) else 1)
EOF
}
link_ckpt() {   # checkpoint state $1 and its files from its run dir into $2
    local s=$1 W=$2 n; n=$(basename "$s" | sed -E 's/state_([0-9]+)\.json/\1/')
    ln -sf "$(readlink -f "$s")" "$W/"
    for f in "$(dirname "$s")"/annulus.*.$n.* "$(dirname "$s")"/annulus.*$n.*; do [ -e "$f" ] && ln -sf "$(readlink -f "$f")" "$W/"; done
}
t0=$(date +%s)
for name in TAf_v2 earth_run2; do
    W=$M/work/${name}_c; mkdir -p "$W/ckpts" "$W/frames" "$W/zoom"
    find "$W/ckpts" -maxdepth 1 -type l -delete
    for f in "${NEW[$name]}"/annulus.*00000.*; do [ -e "$f" ] && ln -sf "$(readlink -f "$f")" "$W/ckpts/"; done
    cp "${NEW[$name]}/records.json" "$W/ckpts/records.json"
    for s in "${NEW[$name]}"/state_*.json; do complete "$s" && link_ckpt "$s" "$W/ckpts"; done
    ( ax python3 "$HEADLESS" "$CAMP/render/render_annulus.py" -uw_run "$W/ckpts" -uw_panels strain -uw_zoom 0 \
          -uw_trace_width 6 -uw_vring 0.2 -uw_vring_vmax 6000 -uw_renders "$W/frames" > "$W/render.log" 2>&1
      echo "${name}_c: $(ls "$W/frames"/frame_*.png 2>/dev/null | wc -l) whole frames, $(( $(date +%s) - t0 )) s" ) &
    ( ax python3 "$HEADLESS" "$CAMP/render/render_annulus.py" -uw_run "$W/ckpts" -uw_panels strain -uw_zoom 0.5 \
          -uw_renders "$W/zoom" > "$W/render_zoom.log" 2>&1
      echo "${name}_c: $(ls "$W/zoom"/zoom_*.png 2>/dev/null | wc -l) zoom images, $(( $(date +%s) - t0 )) s" ) &
done
wait
export PAIRSET=c
ax PAIRSET=c python3 /home/louis/+Claude/kaiju/launch/movies/pair_frames.py frame
ax PAIRSET=c python3 /home/louis/+Claude/kaiju/launch/movies/pair_frames.py zoom
echo "total $(( $(date +%s) - t0 )) s"
