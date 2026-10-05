#!/usr/bin/env bash
# pool.sh <queue-file> <ranks>: one worker; pops the first line of the queue (under a
# lock) and runs it through run_guarded.sh, until the queue is empty. Start as many
# workers as the cores allow; each line is "<label> <options...>".
cd $(dirname "$0")/..
q=$1; np=$2
while :; do
  job=$(flock "$q.lock" bash -c 'l=$(head -1 "$0"); [ -n "$l" ] && sed -i 1d "$0"; echo "$l"' "$q")
  [ -z "$job" ] && break
  ./run_guarded.sh $np $job
done
