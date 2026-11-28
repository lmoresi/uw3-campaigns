"""The first line at which two stage_dump.py runs differ, per rank.

    python stage_compare.py <prefixA> <prefixB> [nranks]
"""
import sys

a, b = sys.argv[1:3]
n = int(sys.argv[3]) if len(sys.argv) > 3 else 2
for r in range(n):
    A = open(f"{a}-rank{r}.log").read().splitlines()
    B = open(f"{b}-rank{r}.log").read().splitlines()
    first = next((i for i, (x, y) in enumerate(zip(A, B)) if x != y), None)
    if first is None:
        print(f"rank {r}: identical ({len(A)} vs {len(B)} lines)")
    else:
        print(f"rank {r}: first difference at line {first + 1}:")
        print(f"   A {A[first]}")
        print(f"   B {B[first]}")
        if first:
            print(f"   previous (same in both): {A[first - 1]}")
