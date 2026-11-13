#!/bin/bash
# usage: drive_extra.sh <tag>
tag=$1
cd /Users/lmoresi/+Underworld/underworld3-pixi/.claude/worktrees/kept-transfer || exit 1
export OMP_NUM_THREADS=1
P=~/+Simulations/issue_sweep/review_1139
: > $P/$tag.extra.jsonl
for c in blist_short blist_full dup_001_len2 dup_11_full neg_m1_0_len1 nat_scalar nat_len1_c0 s3_len2_c12_b s3_scalar_c1 c01_len1 npfloat_c1 empty_c1; do
  pixi run -e runtime python $P/extra_cases.py $c > $P/extra.one.out 2>&1
  r=$(grep '^RESULT ' $P/extra.one.out | sed 's/^RESULT //')
  if [ -z "$r" ]; then r="{\"case\": \"$c\", \"process_exit\": \"$(tail -3 $P/extra.one.out | tr '\n"' ' ~' | cut -c1-300)\"}"; fi
  echo "$r" >> $P/$tag.extra.jsonl
done
echo DONE >> $P/$tag.extra.jsonl
