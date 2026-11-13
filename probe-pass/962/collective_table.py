"""Lines of the rotated solve whose collective-call counts differ between ranks (#962).

    python collective_table.py <dir with lines_rank*.log>

For each rank, the reductions and gathers PETSc counted are attributed to the
line that was running. Prints the counts at the first logged line, every line
on which the ranks disagree, and each rank's last entry.
"""
import glob
import os
import re
import sys
from collections import defaultdict

ENTRY = re.compile(r"^(\S+) (\S+) R=(\d+) G=(\d+)$")


def read(path):
    rows = []
    with open(path) as log:
        for line in log:
            m = ENTRY.match(line.strip())
            if m:
                rows.append((m.group(1), int(m.group(3)), int(m.group(4))))
    return rows


def main(directory):
    logs = sorted(glob.glob(os.path.join(directory, "lines_rank*.log")),
                  key=lambda p: int(re.search(r"rank(\d+)", p).group(1)))
    ranks = [int(re.search(r"rank(\d+)", p).group(1)) for p in logs]
    per_line = {}
    first, last = {}, {}
    for rank, path in zip(ranks, logs):
        rows = read(path)
        if not rows:
            print(f"rank {rank}: no entries")
            continue
        first[rank], last[rank] = rows[0], rows[-1]
        totals = defaultdict(lambda: [0, 0])
        for (where, r0, g0), (_, r1, g1) in zip(rows, rows[1:]):
            totals[where][0] += r1 - r0
            totals[where][1] += g1 - g0
        per_line[rank] = totals
    print("counts before the first logged line (rank: line R G)")
    for rank in ranks:
        if rank in first:
            print(f"  {rank}: {first[rank][0]} R={first[rank][1]} G={first[rank][2]}")
    print("lines on which the ranks disagree (R per rank | G per rank)")
    lines = sorted({w for t in per_line.values() for w in t},
                   key=lambda w: int(w.split(":")[1]) if ":" in w else 0)
    for where in lines:
        r = [per_line[k][where][0] if where in per_line[k] else 0 for k in per_line]
        g = [per_line[k][where][1] if where in per_line[k] else 0 for k in per_line]
        if len(set(r)) > 1 or len(set(g)) > 1:
            print(f"  {where}: R {r} | G {g}")
    print("last entry (rank: line R G)")
    for rank in ranks:
        if rank in last:
            print(f"  {rank}: {last[rank][0]} R={last[rank][1]} G={last[rank][2]}")


if __name__ == "__main__":
    main(sys.argv[1])
