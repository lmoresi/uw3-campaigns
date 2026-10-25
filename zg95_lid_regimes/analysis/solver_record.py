"""The solver's behaviour through a moving-fault run, step by step, beside the physics.

Reads each run's records.json (the "solver" sub-record of annulus_faults.py; older
records without it fall back to the top-level newton / t_stokes / n_built fields, with
the step kinds inferred from n_built and the fault names). One column per run on a
shared x axis:

1. nonlinear iterations per step, Picard (light) stacked under Newton (dark), cold
   starts outlined, a red x on a cold retry;
2. wall time per step by phase;
3. linear iterations per increment, velocity and pressure blocks (mean line, max dots);
4. |F^0| / F_ref, where each solve starts relative to the rest state (log);
5. line-search cutbacks per step;
6-8. trench position of each fault, slip_max, vrms.
Vertical lines through every panel mark same-set rebuilds (dashed grey), changed-set
rebuilds (solid orange, labelled +F11 / -F10) and the run's first step (dotted black).

Also writes <run>/solver_summary.csv (medians by step kind, and totals) and, with
-uw_table, one markdown table of those summaries for all the runs (for the wiki).

    python solver_record.py -uw_runs <dir>[,<dir>...] -uw_x step|t -uw_out solver.png [-uw_table solver.md]
                            [-uw_first <step> -uw_last <step>]
"""
import csv
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import underworld3 as uw

params = uw.Params(
    uw_runs="",                 # run directories, comma separated
    uw_x="step",                # "step" or "t"
    uw_out="solver_record.png",
    uw_table="",                # a markdown file for the summary table ("" for none)
    uw_first=-1,                # first step shown and summarised (-1: from the start)
    uw_last=-1,                 # last step (-1: to the end)
)

PHASES = ["build", "transfer", "stokes", "to_base", "energy_strain", "swarm", "detection", "checkpoint"]
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
PICARD, NEWTON, TOTAL = "#86b6ef", "#1c5cab", "#3987e5"
INK, MUTED, GRID = "#1a1a19", "#6b6a64", "#e4e3dd"
KINDS = ["ordinary", "rebuild_same_set", "rebuild_changed_set", "restart_first", "init_first"]


def load(run):
    with open(os.path.join(run, "records.json")) as f:
        records = [r for r in json.load(f) if "step" in r]
    # a restart truncates records.json to its own start, so the steps are unique; keep the last
    by_step = {r["step"]: r for r in records}
    return [by_step[s] for s in sorted(by_step)]


def restarts_of(run):
    """The steps a run (re)started from, from run_info.json (one entry per start)."""
    try:
        with open(os.path.join(run, "run_info.json")) as f:
            return {int(r["restart_from"]) for r in json.load(f) if r.get("restart_from") is not None}
    except (OSError, ValueError):
        return set()


def solver_of(records, restarts=()):
    """Each record's solver sub-record, or one inferred from the top-level fields: a
    restart's first step (after a step listed in run_info.json, or where n_built drops,
    as older drivers reset it), a rebuild where n_built grows."""
    out = []
    for n, r in enumerate(records):
        s = r.get("solver")
        if s is not None:
            out.append(s)
            continue
        # a record's faults are those after its detection; a step solves on the set its
        # predecessor decided, so a rebuild at step n goes from record n-2's set to n-1's
        names_of = lambda m: [f["name"] for f in records[m].get("faults", [])] if m >= 0 else None
        prev = records[n - 1] if n else None
        after = names_of(n - 1) if n else names_of(n)
        before = names_of(n - 2) if n >= 2 else after
        names = after
        rebuilt = prev is not None and r.get("n_built", 0) > prev.get("n_built", 0)
        restarted = prev is not None and (prev["step"] in restarts or r.get("n_built", 0) < prev.get("n_built", 0))
        kind = "ordinary"
        if restarted:
            kind = "restart_first"
        elif rebuilt:
            kind = "rebuild_same_set" if names == before else "rebuild_changed_set"
        out.append({"kind": kind, "start": None, "cold_retry": False, "faults_before": before,
                    "faults_after": names, "nonlinear_its": r.get("newton"), "picard_its": None,
                    "newton_its": None, "F0": None, "F_ref": None, "line_search_cutbacks": None,
                    "ksp_summary": {}, "wall": {"stokes": r.get("t_stokes"), "step": r.get("t_step")}})
    return out


def num(x):
    return np.nan if x is None else float(x)


def event_label(s):
    before, after = set(s.get("faults_before") or []), set(s.get("faults_after") or [])
    return " ".join([f"+{n}" for n in sorted(after - before)] + [f"-{n}" for n in sorted(before - after)])


def draw_events(axes, x, solver, label_ax):
    for xi, s in zip(x, solver):
        kind = s.get("kind")
        style = {"rebuild_same_set": dict(color="#9a9990", ls="--", lw=1),
                 "rebuild_changed_set": dict(color=SERIES[1], ls="-", lw=1.5),
                 "restart_first": dict(color=INK, ls=":", lw=1.5),
                 "init_first": dict(color=INK, ls=":", lw=1.5)}.get(kind)
        if style is None:
            continue
        for ax in axes:
            ax.axvline(xi, zorder=0, **style)
        text = event_label(s) if kind == "rebuild_changed_set" else ("restart" if kind == "restart_first"
                                                                    else "init" if kind == "init_first" else "")
        if text:
            label_ax.annotate(text, (xi, 1.0), xycoords=("data", "axes fraction"), xytext=(2, 2),
                              textcoords="offset points", fontsize=7, color=INK, rotation=90, va="bottom")


def plot_run(axes, run, records, solver, xkey):
    recorded = any(r.get("solver") is not None for r in records)
    x = np.array([r["step"] if xkey == "step" else r["t"] for r in records], dtype=float)
    width = 0.8 * (np.median(np.diff(x)) if len(x) > 1 else 1.0)
    ax = axes[0]
    picard = np.array([num(s.get("picard_its")) for s in solver])
    newton = np.array([num(s.get("newton_its")) for s in solver])
    total = np.array([num(s.get("nonlinear_its")) for s in solver])
    split = ~np.isnan(picard) & ~np.isnan(newton)
    edge = [INK if s.get("start") == "cold" else "none" for s in solver]
    if split.any():
        ax.bar(x[split], picard[split], width, color=PICARD, edgecolor=np.array(edge)[split], label="Picard")
        ax.bar(x[split], newton[split], width, bottom=picard[split], color=NEWTON,
               edgecolor=np.array(edge)[split], label="Newton")
    if (~split).any():
        ax.bar(x[~split], total[~split], width, color=TOTAL, label="nonlinear (no split recorded)")
    retry = np.array([bool(s.get("cold_retry")) for s in solver])
    if retry.any():
        ax.plot(x[retry], total[retry] + 1, "x", color=SERIES[7], ms=8, mew=2, label="cold retry")
    if any(e == INK for e in edge):
        ax.bar([np.nan], [0], color="white", edgecolor=INK, label="cold start (outlined)")
    ax.set_ylabel("nonlinear its")
    ax.set_title(os.path.basename(os.path.normpath(run)), fontsize=10, color=INK, loc="left")

    ax = axes[1]
    bottom = np.zeros(len(x))
    for phase, colour in zip(PHASES, SERIES):
        values = np.array([num((s.get("wall") or {}).get(phase)) for s in solver])
        if np.all(np.isnan(values)):
            continue
        values = np.nan_to_num(values)
        ax.bar(x, values, width, bottom=bottom, color=colour, label=phase)
        bottom += values
    if not bottom.any():           # no phase record: the step's wall time
        ax.bar(x, [num((s.get("wall") or {}).get("step")) for s in solver], width, color=TOTAL, label="step")
    ax.set_ylabel("wall per step (s)")

    ax = axes[2]
    for block, colour in (("vel", SERIES[0]), ("pres", SERIES[1])):
        mean = np.array([num((s.get("ksp_summary") or {}).get(f"{block}_mean")) for s in solver])
        top = np.array([num((s.get("ksp_summary") or {}).get(f"{block}_max")) for s in solver])
        if np.all(np.isnan(mean)):
            continue
        ax.plot(x, mean, color=colour, lw=2, label=f"{block} mean")
        ax.plot(x, top, "o", color=colour, ms=4, label=f"{block} max")
    ax.set_ylabel("KSP its / increment")

    ax = axes[3]
    ratio = np.array([num(s.get("F0")) / num(s.get("F_ref")) if s.get("F_ref") else np.nan for s in solver])
    if not np.all(np.isnan(ratio)):
        ax.semilogy(x, ratio, "o-", color=SERIES[0], lw=2, ms=4, label="|F0| / F_ref")
    ax.set_ylabel("|F0| / F_ref")

    ax = axes[4]
    cut = np.array([num(s.get("line_search_cutbacks")) for s in solver])
    if not np.all(np.isnan(cut)):
        ax.bar(x, np.nan_to_num(cut), width, color=SERIES[6], label="cutbacks")
    ax.set_ylabel("line-search\ncutbacks")

    ax = axes[5]
    # each trench's shift from where it was first seen, wrapped (faults sit anywhere,
    # -180 deg included, so absolute angles crush the motion)
    names = sorted({f["name"] for r in records for f in r.get("faults", [])}, key=lambda n: int(n[1:]))
    for n, name in enumerate(names):
        theta = np.array([next((f["theta"] for f in r.get("faults", []) if f["name"] == name), np.nan)
                          for r in records])
        first = theta[np.isfinite(theta)][0]
        shift = np.degrees((theta - first + np.pi) % (2 * np.pi) - np.pi)
        ax.plot(x, shift, lw=2, color=SERIES[n % len(SERIES)], label=f"{name} ({np.degrees(first):.0f} deg)")
    ax.set_ylabel("trench shift (deg)")

    axes[6].plot(x, [num(r.get("slip_max")) for r in records], color=SERIES[0], lw=2, label="slip_max")
    axes[6].set_ylabel("slip_max")
    axes[7].plot(x, [num(r.get("vrms")) for r in records], color=SERIES[0], lw=2, label="vrms")
    axes[7].set_ylabel("vrms")
    axes[7].set_xlabel("step" if xkey == "step" else "t")

    empty = [not ax.lines and not ax.patches for ax in axes]      # before the event lines
    draw_events(axes, x, solver, axes[0])
    for ax, nothing in zip(axes, empty):
        if nothing:
            ax.text(0.5, 0.5, "not recorded" if recorded else "no solver record", transform=ax.transAxes, ha="center", va="center",
                    color=MUTED, fontsize=9)
            ax.set_yticks([])
        ax.grid(axis="y", color=GRID, lw=0.8)
        ax.set_axisbelow(True)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        handles, labels = ax.get_legend_handles_labels()
        if len(handles) >= 2:
            ax.legend(fontsize=7, frameon=False, ncol=min(4, len(handles)), loc="upper left")


def summarise(records, solver):
    """Medians by step kind, and totals, as rows of a table."""
    rows = []
    groups = {kind: [n for n, s in enumerate(solver) if s.get("kind") == kind] for kind in KINDS}
    groups["all"] = list(range(len(solver)))
    for kind, idx in groups.items():
        if not idx:
            continue
        pick = lambda f: np.array([f(solver[n], records[n]) for n in idx], dtype=float)
        its = pick(lambda s, r: num(s.get("nonlinear_its")))
        stokes = pick(lambda s, r: num((s.get("wall") or {}).get("stokes")))
        step = pick(lambda s, r: num((s.get("wall") or {}).get("step")))
        med = lambda a: float(np.nanmedian(a)) if np.isfinite(a).any() else None
        rows.append({
            "kind": kind, "steps": len(idx), "its": med(its),
            "picard": med(pick(lambda s, r: num(s.get("picard_its")))),
            "newton": med(pick(lambda s, r: num(s.get("newton_its")))),
            "F0/F_ref": med(pick(lambda s, r: num(s.get("F0")) / num(s.get("F_ref")) if s.get("F_ref") else np.nan)),
            "s/step": med(step), "s/nonlinear it": med(stokes / np.where(its > 0, its, np.nan)),
            "vel KSP mean": med(pick(lambda s, r: num((s.get("ksp_summary") or {}).get("vel_mean")))),
            "pres KSP mean": med(pick(lambda s, r: num((s.get("ksp_summary") or {}).get("pres_mean")))),
            "cold retries": int(sum(bool(solver[n].get("cold_retry")) for n in idx)),
            "total its": float(np.nansum(its)), "total s": float(np.nansum(step))})
    return rows


def fmt(v):
    if v is None:
        return ""
    if isinstance(v, float):
        return f"{v:.3g}"
    return str(v)


runs = [os.path.expanduser(r) for r in params.uw_runs.split(",") if r]
if not runs:
    raise SystemExit("give -uw_runs <dir>[,<dir>...]")
fig, grid = plt.subplots(8, len(runs), figsize=(6.5 * len(runs), 17), sharex="col", squeeze=False,
                         gridspec_kw={"height_ratios": [3, 2.5, 2, 1.5, 1, 1.5, 1.2, 1.2]})
table = []
for c, run in enumerate(runs):
    records = load(run)
    solver = solver_of(records, restarts_of(run))
    keep = [n for n, r in enumerate(records) if (params.uw_first < 0 or r["step"] >= params.uw_first)
            and (params.uw_last < 0 or r["step"] <= params.uw_last)]
    records, solver = [records[n] for n in keep], [solver[n] for n in keep]
    plot_run(grid[:, c], run, records, solver, params.uw_x)
    rows = summarise(records, solver)
    with open(os.path.join(run, "solver_summary.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    table += [dict(run=os.path.basename(os.path.normpath(run)), **row) for row in rows]
fig.tight_layout()
fig.savefig(os.path.expanduser(params.uw_out), dpi=130)
print(f"wrote {params.uw_out} and solver_summary.csv in {len(runs)} run(s)")
if params.uw_table:
    keys = list(table[0])
    with open(os.path.expanduser(params.uw_table), "w") as f:
        f.write("| " + " | ".join(keys) + " |\n|" + "---|" * len(keys) + "\n")
        for row in table:
            f.write("| " + " | ".join(fmt(row[k]) for k in keys) + " |\n")
    print(f"wrote {params.uw_table}")
