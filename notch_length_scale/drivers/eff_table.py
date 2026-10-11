"""Solver efficiency on the matched-width pairs: tight FMG (rtol 1e-8, no
Eisenstat-Walker), refs 1-3 cold from the viscous seed at np 4, ref 4 grid-sequenced
from the exact ref-3 run at np 8, for micromorphic (beta 0.1) and the Cosserat
(l, c) of the same W. Newton steps, median / max Krylov per Newton step, wall time
per Newton step, and W by the current estimator (refs 2-4: mesh independence).
Krylov counts from the logs (lines after the last "0 SNES Function norm"); times
and widths from the json records. Writes ../results/eff_table.json and prints the
markdown table."""
import glob
import json
import os
import re

import numpy as np

_here = os.path.dirname(os.path.abspath(__file__))
NLS = os.path.join(_here, "..")
LINE = re.compile(r"Linear \S+ solve (converged|did not converge) due to (\w+) iterations (\d+)")
SNES = re.compile(r"^\s*(\d+) SNES Function norm ([0-9.eE+-]+)")
PAIRS = [("P1", "micromorphic", 0.25, None), ("P1", "cosserat", 0.14, 1),
         ("P2", "micromorphic", 0.5, None), ("P2", "cosserat", 0.236, 1),
         ("P2", "cosserat", 0.25, 0.1),
         ("P3", "micromorphic", 1.0, None), ("P3", "cosserat", 0.37, 1),
         ("P3", "cosserat", 0.5, 0.054)]


def log_path(model, l_km, c, ref):
    if model == "micromorphic":
        if ref == 4:
            return f"jobs/logs/eff_micro_l{l_km:g}_ref4.log"
        if l_km == 1.0:
            return f"jobs/logs/eff_micro_l1_ref{ref}.log"
        return f"jobs/logs/fmgtable_micro_ref{ref}_l{l_km:g}.log"
    return f"jobs/logs/eff_coss_l{l_km:g}_c{c:g}_ref{ref}.log"


def record(model, l_km, c, ref):
    if model == "micromorphic":
        pattern = f"results/micromorphic/micro_ref{ref}_xi0_beta0.1_l{l_km:g}_production_tight_np*.json"
        found = [f for f in glob.glob(os.path.join(NLS, pattern))
                 if ("_eff" in f) == (ref == 4 or l_km == 1.0)]
    else:
        pattern = f"results/cosserat/cosserat_ref{ref}_xi0_c{c:g}_l{l_km:g}_P1_production_tight_np*_eff.json"
        found = glob.glob(os.path.join(NLS, pattern))
    return json.load(open(sorted(found)[0])) if found else None


def parse(path):
    full = os.path.join(NLS, path)
    if not os.path.exists(full):
        return None
    text = open(full, errors="replace").read().splitlines()
    starts = [i for i, s in enumerate(text) if re.match(r"\s*0 SNES Function norm", s)]
    if not starts:
        return None
    tail = text[starts[-1]:]
    solves = [(m.group(2), int(m.group(3))) for m in map(LINE.search, tail) if m]
    norms = [float(m.group(2)) for m in map(SNES.search, tail) if m]
    killed = any("MPI SUPERVISOR: no output" in s for s in text)
    return dict(solves=solves, norms=norms, killed=killed)


# micromorphic tight runs from the FMG table predate the current-estimator fields in
# their records; their W and peak are the exact runs' at the same (ref, l)
CURRENT = {(r["ref"], r["l_km"]): r
           for r in json.load(open(os.path.join(NLS, "results", "current_widths.json")))}
rows = []
for pair, model, l_km, c in PAIRS:
    for ref in (1, 2, 3, 4):
        k = parse(log_path(model, l_km, c, ref))
        r = record(model, l_km, c, ref)
        if k is None and r is None:
            continue
        its = [n for _, n in (k["solves"] if k else [])]
        nl = r["nl_its"] if r else None
        rows.append(dict(
            pair=pair, model=model, l_km=l_km, c=c, ref=ref,
            np=(r or {}).get("nprocs"), converged=(r or {}).get("converged"),
            reason=(r or {}).get("reason", "killed" if k and k["killed"] else "running"),
            nl_its=nl, krylov=k["solves"] if k else [], residuals=k["norms"] if k else [],
            median=float(np.median(its)) if its else None, max=max(its) if its else None,
            capped=any(s == "DIVERGED_ITS" for s, _ in (k["solves"] if k else [])),
            seconds=(r or {}).get("seconds"),
            per_step_s=(r["seconds"] / nl) if r and nl else None,
            W_km=(r or {}).get("W_outside9_km") or (CURRENT.get((ref, l_km), {}).get("W_km")
                                                    if model == "micromorphic" else None),
            peak=(r or {}).get("peak_outside9") or (CURRENT.get((ref, l_km), {}).get("peak")
                                                   if model == "micromorphic" else None)))
json.dump(rows, open(os.path.join(NLS, "results", "eff_table.json"), "w"), indent=1)

print("| pair | model | ref (np) | Newton | Krylov / step median / max | s per Newton step | W (km) | peak | outcome |")
print("|---|---|---|---|---|---|---|---|---|")
for r in rows:
    model = (f"micromorphic l = {r['l_km']:g}" if r["model"] == "micromorphic"
             else f"Cosserat l = {r['l_km']:g}, c = {r['c']:g}")
    kry = f"{r['median']:.0f} / {r['max']}" + (" (cap)" if r["capped"] else "") if r["median"] else "—"
    t = f"{r['per_step_s']:.0f}" if r["per_step_s"] else "—"
    W = f"{r['W_km']:.2f}" if r["W_km"] and r["converged"] else "—"
    pk = f"{r['peak']:.2f}" if r["peak"] and r["converged"] else "—"
    print(f"| {r['pair']} | {model} | {r['ref']} ({r['np']}) | {r['nl_its']} | {kry} | {t} | {W} | {pk} | {r['reason']} |")


# Cold starts (no viscous seed): the automatic Picard warm-up arms. The solve report
# folds it into nl_its and records its steps as config.tangent.picard_warmup_its,
# which the transcript keeps; reported as "warm-up + Newton".
def cold_record(model, l_km, c, ref):
    if model == "micromorphic":
        base = f"results/micromorphic/micro_ref{ref}_xi0_beta0.1_l{l_km:g}_production_tight_np4_cold"
        trans = base.replace("micromorphic/", "micromorphic/transcripts/") + ".jsonl"
    else:
        base = f"results/cosserat/cosserat_ref{ref}_xi0_c{c:g}_l{l_km:g}_P1_production_tight_np4_cold"
        trans = base.replace("cosserat/", "cosserat/transcripts/") + ".jsonl"
    path = os.path.join(NLS, base + ".json")
    if not os.path.exists(path):
        return None
    r = json.load(open(path))
    warm = 0
    tp = os.path.join(NLS, trans)
    if os.path.exists(tp):
        found = re.findall(r'"picard_warmup_its": (\d+)', open(tp).read())
        warm = int(found[-1]) if found else 0
    return r, warm


cold = []
for pair, model, l_km, c in PAIRS:
    for ref in (1, 2, 3):
        got = cold_record(model, l_km, c, ref)
        log = f"jobs/logs/cold_{'micro' if model == 'micromorphic' else 'coss'}_l{l_km:g}" + \
              ("" if model == "micromorphic" else f"_c{c:g}") + f"_ref{ref}.log"
        k = parse(log)
        if got is None:
            if k and k["killed"]:
                cold.append(dict(pair=pair, model=model, l_km=l_km, c=c, ref=ref, killed=True))
            continue
        r, warm = got
        its = [n for _, n in (k["solves"] if k else [])]
        cold.append(dict(pair=pair, model=model, l_km=l_km, c=c, ref=ref, killed=False,
                         warmup=warm, newton=r["nl_its"] - warm, reason=r["reason"],
                         converged=r["converged"], median=float(np.median(its)) if its else None,
                         max=max(its) if its else None, seconds=r["seconds"],
                         W_km=r.get("W_outside9_km")))
json.dump(cold, open(os.path.join(NLS, "results", "eff_table_cold.json"), "w"), indent=1)
print()
print("| pair | model | ref | warm-up + Newton | Krylov / step median / max | s | outcome |")
print("|---|---|---|---|---|---|---|")
for r in cold:
    model = (f"micromorphic l = {r['l_km']:g}" if r["model"] == "micromorphic"
             else f"Cosserat l = {r['l_km']:g}, c = {r['c']:g}")
    if r["killed"]:
        print(f"| {r['pair']} | {model} | {r['ref']} | — | — | — | killed (no output for 1 h) |")
        continue
    kry = f"{r['median']:.0f} / {r['max']}" if r["median"] else "—"
    print(f"| {r['pair']} | {model} | {r['ref']} | {r['warmup']} + {r['newton']} | {kry} | "
          f"{r['seconds']:.0f} | {r['reason']} |")
