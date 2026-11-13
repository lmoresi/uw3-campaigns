#!/bin/bash
# usage: drive.sh <tag>   (tag = before | after). Serial, one process at a time.
set -u
tag=$1
P=~/+Simulations/issue_sweep/review_1139
cd /Users/lmoresi/+Underworld/underworld3-pixi/.claude/worktrees/kept-transfer || exit 1
export OMP_NUM_THREADS=1
git rev-parse HEAD > $P/$tag.head
pixi run -e runtime python -c "import underworld3 as uw; print(uw.__file__)" >> $P/$tag.head 2>&1
: > $P/$tag.jsonl
: > $P/$tag.raw.log
for c in $(pixi run -e runtime python $P/truth_table.py --list 2>/dev/null); do
  echo "=== $c" >> $P/$tag.raw.log
  pixi run -e runtime python $P/truth_table.py $c > $P/one.out 2>&1
  rc=$?
  cat $P/one.out >> $P/$tag.raw.log
  if grep -q '^RESULT ' $P/one.out; then
    grep '^RESULT ' $P/one.out | sed 's/^RESULT //' >> $P/$tag.jsonl
  else
    echo "{\"case\": \"$c\", \"process_exit\": $rc, \"tail\": $(tail -3 $P/one.out | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()[-300:]))')}" >> $P/$tag.jsonl
  fi
done
for f in short full; do
  pixi run -e runtime python $P/conv_box.py $f > $P/one.out 2>&1
  cat $P/one.out >> $P/$tag.raw.log
  grep '^RESULT ' $P/one.out | sed 's/^RESULT //' >> $P/$tag.convbox.jsonl
done
echo DONE >> $P/$tag.head
