"""Tables from the sweep logs: python table.py <dip> <cellsize> [np-log ...]."""
import re
import sys
from pathlib import Path

L = Path(__file__).resolve().parent / "logs"
LINE = re.compile(r"k =\s*([0-9.]+)\s+top depth = ([0-9.]+) \(([0-9.]+) h\)\s+band top depth = "
                  r"([+-][0-9.]+) \(([+-][0-9.]+) h\)\s+\| (.*)")


def outcome(s):
    if s.startswith("placed outcrop"):
        return "outcrop"
    if s.startswith("placed interior"):
        return "interior"
    if "reached the domain wall" in s:
        return "wall refusal"
    if "fault touches the domain boundary" in s:
        return "split refused: tip on wall"
    if "fill ring crosses itself" in s:
        return "fill ring crosses itself"
    if "does not fill its own outlines" in s:
        return "assembly area check"
    return "REFUSED other: " + s[:60]


def numbers(s):
    m = re.search(r"the cavity reaches ([0-9.e+-]+) from the band's skin, and the nearest wall "
                  r"vertex is ([0-9.e+-]+) from the skin", s)
    return (float(m.group(1)), float(m.group(2))) if m else None


def read(p):
    rows, agree = {}, {}
    last = None
    for ln in p.read_text().splitlines():
        m = LINE.search(ln)
        if m:
            last = float(m.group(1))
            rows[last] = m.groups()
        elif "ranks agree:" in ln and last is not None:
            agree[last] = ln.split(":")[1].strip()
    return rows, agree


dip, cs = sys.argv[1], sys.argv[2]
h = float(cs) / 2
dev, _ = read(L / f"sweep-dev-dip{dip}-cs{cs}-np1.log")
u60, _ = read(L / f"sweep-u60-dip{dip}-cs{cs}-np1.log")
mpi = {}
for f in sorted(L.glob(f"mpi-*-dip{dip}-cs{cs}-np*.log")):
    n = f.stem.split("-np")[1]
    v = f.stem.split("-")[1]
    rows, agree = read(f)
    ser = dev if v == "dev" else u60
    for k, g in rows.items():
        same = agree.get(k) == "True" and outcome(g[5]) == outcome(ser[k][5])
        if v == "u60":
            same = same and numbers(g[5]) == numbers(ser[k][5])
        mpi.setdefault(k, []).append(f"{v} np{n} {'yes' if same else 'NO'}")
print(f"| k (cells) | top depth | band top below wall (cells) | development | UNFILED 60 "
      f"(reach / nearest wall, in h) | np 2-3 agree with serial? |")
print("|---|---|---|---|---|---|")
for k in sorted(dev):
    g = dev[k]
    o = outcome(g[5])
    gu = u60.get(k)
    ou = outcome(gu[5]) if gu else "-"
    nu = numbers(gu[5]) if gu else None
    if nu:
        ou += f" ({nu[0]:.3g} / {nu[1]:.3g}; {nu[0] / h:.2f} h / {nu[1] / h:.2f} h)"
    print(f"| {k:.1f} | {float(g[1]):.4g} | {float(g[4]):+.2f} | {o} | {ou} | "
          f"{', '.join(mpi.get(k, [])) or '-'} |")
