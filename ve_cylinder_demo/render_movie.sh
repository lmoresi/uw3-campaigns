#!/bin/zsh
# render_movie.sh <run> <title...>: chunked frames (a fresh process per 60), then the mp4
W=${UW3_WORKTREE:-/Users/lmoresi/+Underworld/underworld3-pixi/.claude/worktrees/lagrangian-inflow}
D=$(cd "$(dirname "$0")" && pwd)
run=$1; shift; title="$*"
cd $D
for chunk in $(seq 1 40); do
  n=$(pixi run --manifest-path $W/pixi.toml -e amr-dev python -u render_demo.py -uw_run $run -uw_title "$title" ${=RENDER_ARGS} 2>&1 | grep -c "^wrote")
  echo "$run chunk $chunk: $n frames"
  [ "$n" -eq 0 ] && break
done
ffmpeg -y -loglevel error -framerate ${FPS:-12} -pattern_type glob -i "runs/$run/frames/frame_*.png" \
  -c:v libx264 -pix_fmt yuv420p -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" "$D/ve_cylinder_$run.mp4" \
  && echo "wrote $D/ve_cylinder_$run.mp4"
