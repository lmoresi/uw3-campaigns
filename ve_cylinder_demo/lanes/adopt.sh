#!/usr/bin/env bash
# adopt.sh <label>: guard a run that is already going without one (same checks as
# run_guarded.sh: blow-up, 15-minute hang, three SNES failures), and log its end
cd $(dirname "$0")/..
l=$1; f=runs/$l/forces.csv
pid=$(pgrep -f "mpirun -n [0-9]* python -u ve_cylinder.py -uw_label $l " | head -1)
[ -z "$pid" ] && { echo "no run $l"; exit 1; }
om=$(cat runs/$l.overshoot 2>/dev/null || echo 0.3)
while kill -0 $pid 2>/dev/null; do
  if grep -q "DONE\|STOPPED\|Traceback" runs/$l.log 2>/dev/null; then break; fi
  age=$(( $(date +%s) - $(stat -c %Y $f 2>/dev/null || date +%s) ))
  row=$(tail -1 $f 2>/dev/null); nd=$(grep -c diverged runs/$l.log)
  bad=$(echo "$row" | awk -F, -v nd=$nd -v om=$om 'NF>5{o=$6+0; c=$3+0; tm=$5+0; if (o>om || c>20 || c<-20 || $3 ~ /nan|inf/ || tm>500 || nd>=3) print "bad"}')
  if [ "$bad" = "bad" ] || [ $age -gt 900 ]; then
    kill $pid; echo "$(date '+%H:%M') $l KILLED ($([ $age -gt 900 ] && echo "hung ${age}s" || echo "blow-up / $nd SNES failures")): $(echo $row | cut -d, -f1-6)" >> runs/night_queue.log; exit 1
  fi
  sleep 30
done
echo "$(date '+%H:%M') $l $(grep -h 'DONE\|STOPPED' runs/$l.log | tail -1 | cut -c1-70)" >> runs/night_queue.log
