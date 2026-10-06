#!/usr/bin/env bash
# run_guarded.sh <np> <label> <args...>: one run of ve_cylinder.py under a guard that
# kills on blow-up, hang, 3 SNES fails; overshoot cap runs/L.overshoot 
W=${UW3_WORKTREE:-/Users/lmoresi/+Underworld/underworld3-pixi/.claude/worktrees/lagrangian-inflow}
# pixi environment: UW3_PIXI_ENV, else the checkout's .pixi-env (./uw setup), else runtime
E=${UW3_PIXI_ENV:-$(cat $W/.pixi-env 2>/dev/null || echo runtime)}
mtime() { stat -c %Y "$1" 2>/dev/null || stat -f %m "$1" 2>/dev/null; }   # GNU, then BSD/macOS
D=$(cd "$(dirname "$0")" && pwd); np=$1; l=$2; shift 2
cd $D; rm -rf runs/$l
# a hold file defers runs of the named kind until a rebuild lands (FENE-P: the
# rank-local variable names of the first build deadlock the step-50 snapshot)
while [ -f $D/.hold_fene ] && echo "$@" | grep -q fene_p; do sleep 30; done
# a skip file drops FENE-P runs at resolution 40: the velocity multigrid solve
# stalls after the ramp on that mesh (three of three), open for the morning
if [ -f $D/.skip_fene_r40 ] && echo "$@" | grep -q fene_p && echo "$@" | grep -q "resolution 40"; then
  echo "$(date '+%H:%M') $l SKIPPED (FENE-P at res 40 stalls in the velocity multigrid solve after the ramp)" >> runs/night_queue.log; exit 2
fi
# a second skip file drops every remaining FENE-P run: Wi 1 and 2 at res 20 hung at step ~50 too
if [ -f $D/.skip_fene ] && echo "$@" | grep -q fene_p; then
  echo "$(date '+%H:%M') $l SKIPPED (FENE-P Wi 1 and 2 at res 20 hung at step ~50; Wi 4 would too)" >> runs/night_queue.log; exit 2
fi
pixi run --manifest-path $W/pixi.toml -e $E mpirun -n $np python -u ve_cylinder.py -uw_label $l -uw_ksp_max_it 300 -uw_snapshot_every 50 -uw_keep_snapshots 2 "$@" > runs/$l.log 2>&1 &
pid=$!; f=runs/$l/forces.csv; sleep 120
while kill -0 $pid 2>/dev/null; do
  if grep -q "DONE\|STOPPED\|Traceback" runs/$l.log 2>/dev/null; then break; fi
  age=$(( $(date +%s) - $(mtime $f || date +%s) ))
  row=$(tail -1 $f 2>/dev/null); nd=$(grep -c diverged runs/$l.log)
  bad=$(echo "$row" | awk -F, -v nd=$nd -v om=${GUARD_OVERSHOOT:-$(cat runs/$l.overshoot 2>/dev/null || echo 0.3)} 'NF>5{o=$6+0; c=$3+0; tm=$5+0; if (o>om || c>20 || c<-20 || $3 ~ /nan|inf/ || tm>500 || nd>=3) print "bad"}')
  if [ "$bad" = "bad" ] || [ $age -gt 900 ]; then
    pkill -f "uw_label $l "; echo "$(date '+%H:%M') $l KILLED ($([ $age -gt 900 ] && echo "hung ${age}s" || echo "blow-up / $nd SNES failures")): $(echo $row | cut -d, -f1-6)" >> runs/night_queue.log; wait $pid 2>/dev/null; exit 1
  fi
  sleep 30
done
wait $pid 2>/dev/null; echo "$(date '+%H:%M') $l $(grep -h 'DONE\|STOPPED' runs/$l.log | tail -1 | cut -c1-70)" >> runs/night_queue.log
