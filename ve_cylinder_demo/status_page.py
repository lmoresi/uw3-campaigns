"""Status page for the scheme / Courant comparison (2026-10-06): one HTML file with the
drag and lift of every c20_/c40_ run against the SUPG res-80 reference, a table of the
drag error at t = 2, and the queue log.

  python status_page.py <out.html>

Reads runs/*/forces.csv and runs/*.log only; safe to run while jobs write.
"""
import os, sys, glob, re, io, base64, html, datetime
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, "runs")
REF, REF_T = "re100_grid_Wi05_r80", 2.0
SCHEMES = {  # label key -> (description, colour)
    "grid": ("SUPG + Eulerian stress + DEVSS", "#222222"),
    "grid_norelax": ("SUPG, unrelaxed mesh", "#7f7f7f"),
    "grid_bdf": ("SUPG, BDF integrator", "#8c6d31"),
    "bn": ("SUPG + backward-nodes stress", "#1f77b4"),
    "bip": ("SUPG + backward-IP stress", "#2ca02c"),
    "fip": ("SUPG + forward-IP stress", "#d62728"),
    "fip-rs": ("SUPG + forward-IP stress (restart at step 60, overshoot guard 0.6)", "#d62728"),
    "lag": ("SUPG + Lagrangian stress (BDF)", "#9467bd"),
    "slbn": ("backward-nodes momentum + stress", "#ff7f0e"),
}
DASH = {1: "-", 2: "--", 4: ":"}


def forces(label):
    f = os.path.join(RUNS, label, "forces.csv")
    if not os.path.exists(f):
        return None
    try:
        d = np.genfromtxt(f, delimiter=",", names=True, invalid_raise=False)
    except Exception:
        return None
    return d if d.size > 1 else None


def at(d, t):
    """cd at time t (nearest row within half a step), else None."""
    if d is None or d["t"].max() < t - 1e-6:
        return None
    return float(d["cd"][np.argmin(np.abs(d["t"] - t))])


def status(label):
    log = os.path.join(RUNS, label + ".log")
    txt = open(log, errors="replace").read() if os.path.exists(log) else ""
    q = open(os.path.join(RUNS, "night_queue.log")).read() if os.path.exists(os.path.join(RUNS, "night_queue.log")) else ""
    if re.search(rf" {re.escape(label)} KILLED", q):
        return "killed", re.search(rf" {re.escape(label)} KILLED \(([^)]*)\)", q).group(1)
    if "Traceback" in txt:
        return "failed", txt.strip().splitlines()[-1][:90]
    m = re.findall(r"DONE \S+ steps (\d+) t ([\d.]+) s/step ([\d.]+)", txt)
    if m:
        return "done", f"{m[-1][0]} steps, {m[-1][2]} s/step"
    m = re.findall(r"step (\d+)/(\d+) t ([\d.]+).*s/step ([\d.]+)", txt)
    if m:
        s, n, t, r = m[-1]
        return "running", f"step {s}/{n}, {float(r):.0f} s/step"
    return ("starting", "") if txt else ("queued", "")


def parse(label):
    m = re.match(r"c(\d+)_(.+)_C(\d+)$", label)
    return (int(m.group(1)), m.group(2), int(m.group(3))) if m else None


def png(fig):
    b = io.BytesIO(); fig.savefig(b, format="png", dpi=110, bbox_inches="tight"); plt.close(fig)
    return base64.b64encode(b.getvalue()).decode()


labels = sorted({os.path.basename(p)[:-4] for p in glob.glob(os.path.join(RUNS, "c*_*_C*.log"))})
queued = []
qf = os.path.join(RUNS, "queue_courant.txt")
if os.path.exists(qf):
    queued = [l.split()[0] for l in open(qf) if l.strip()]
ref = forces(REF)
cd_ref = at(ref, REF_T)

# figure 1: the comparison runs to t 2 against the reference
fig, ax = plt.subplots(2, 1, figsize=(14, 7.2), sharex=True)
if ref is not None:
    k = ref["t"] <= 2.05
    ax[0].plot(ref["t"][k], ref["cd"][k], color="#c0392b", lw=2.2, alpha=0.35, label="SUPG res 80 (reference)")
    ax[1].plot(ref["t"][k], ref["cl"][k], color="#c0392b", lw=2.2, alpha=0.35)
cd_seen, cl_seen, dropped = [], [], []
if ref is not None:
    k = ref["t"] <= 2.05
    cd_seen.append(ref["cd"][k & (ref["t"] >= 0.5)]); cl_seen.append(ref["cl"][k])
for l in labels:
    p, d = parse(l), forces(l)
    if p is None or d is None:
        continue
    if status(l)[0] in ("killed", "failed"):
        dropped.append(l)          # off the plot: a blow-up would set the scale
        continue
    cd_seen.append(d["cd"][d["t"] >= 0.5]); cl_seen.append(d["cl"])
    res, key, C = p
    desc, col = SCHEMES.get(key, (key, "#17becf"))
    kw = dict(color=col, ls=DASH.get(C, "-."), lw=1.6 if res == 40 else 1.0)
    if res == 20:
        kw.update(color="#bbbbbb", lw=1.4)
    ax[0].plot(d["t"], d["cd"], label=f"res {res}, C {C}: {desc}", **kw)
    ax[1].plot(d["t"], d["cl"], **kw)
ax[0].set_ylabel("cd"); ax[1].set_ylabel("cl"); ax[1].set_xlabel("t")


def span(arrays, pad=0.06):
    v = np.concatenate([a[np.isfinite(a)] for a in arrays if len(a)]) if arrays else np.array([0.0, 1.0])
    lo, hi = float(v.min()), float(v.max())
    return lo - pad * (hi - lo), hi + pad * (hi - lo)


# every valid run fits: cd from the end of the inflow ramp (t 0.5, shaded), cl everywhere
ax[0].set_ylim(*span(cd_seen)); ax[1].set_ylim(*span(cl_seen)); ax[0].set_xlim(0, 2.05)
for a in ax:
    a.grid(alpha=0.3)
    a.axvspan(0, 0.5, color="0.93", zorder=0)
ax[0].text(0.02, 0.04, "inflow ramp", transform=ax[0].transAxes, fontsize=8, color="0.45")
ax[0].legend(fontsize=7.5, ncol=1, loc="upper left", bbox_to_anchor=(1.01, 1.0), borderaxespad=0,
             title=("not plotted (killed / failed):\n" + "\n".join(dropped)) if dropped else None, title_fontsize=7.5)
ax[0].set_title("Re 100, Wi 0.5 Oldroyd-B: stress schemes and Courant number to t 2 "
                "(solid C 1, dashed C 2, dotted C 4)", fontsize=10, loc="left")
fig1 = png(fig)

# figure 2: the reference to t 8 (and the stopped global-projection run)
fig, ax = plt.subplots(2, 1, figsize=(11, 4.6), sharex=True)
f2_cd, f2_cl = [], []
for lab, col, name in ((REF, "#c0392b", "SUPG res 80"), ("re100_ob_Wi05_r80", "#2471a3", "forward + global projection res 80 (stopped)")):
    d = forces(lab)
    if d is not None:
        ax[0].plot(d["t"], d["cd"], color=col, lw=1, label=name); ax[1].plot(d["t"], d["cl"], color=col, lw=1)
        f2_cd.append(d["cd"][d["t"] >= 0.5]); f2_cl.append(d["cl"])
ax[0].set_xlim(0, 8); ax[0].set_ylabel("cd"); ax[1].set_ylabel("cl"); ax[1].set_xlabel("t")
ax[1].axvspan(6, 8, color="0.92")
if f2_cd:
    ax[0].set_ylim(*span(f2_cd)); ax[1].set_ylim(*span(f2_cl))
for a in ax:
    a.grid(alpha=0.3)
ax[0].legend(fontsize=8, loc="lower right")
fig2 = png(fig)

# table
rows = []
ref_st = status(REF) if os.path.exists(os.path.join(RUNS, REF + ".log")) else ("", "")
cd40 = at(forces("c40_grid_norelax_C1"), REF_T)
for l in labels + [q for q in queued if q not in labels]:
    p = parse(l)
    if p is None:
        continue
    res, key, C = p
    st, note = status(l) if l in labels else ("queued", "")
    d = forces(l)
    cd2 = at(d, REF_T)
    latest = f"{d['cd'][-1]:.3f} at t {d['t'][-1]:.2f}" if d is not None else ""
    err = f"{cd2 - cd_ref:+.3f}" if (cd2 is not None and cd_ref is not None) else ""
    ratio = ""
    if cd2 is not None and cd_ref is not None and cd40 is not None and abs(cd40 - cd_ref) > 1e-9 and res == 40:
        ratio = f"{abs(cd2 - cd_ref) / abs(cd40 - cd_ref):.2f}"
    rows.append((res, C, key, l, st, note, latest, f"{cd2:.3f}" if cd2 is not None else "", err, ratio))
rows.sort(key=lambda r: (r[1], r[0], list(SCHEMES).index(r[2]) if r[2] in SCHEMES else 99))
order = {"c20_grid_norelax_C1": None}
cd20 = at(forces("c20_grid_norelax_C1"), REF_T)
conv = ""
if None not in (cd20, cd40, cd_ref) and abs(cd40 - cd_ref) > 1e-12:
    pord = np.log2(abs(cd20 - cd40) / abs(cd40 - cd_ref))
    ext = cd_ref + (cd_ref - cd40) / (2 ** pord - 1) if pord > 0 else float("nan")
    conv = (f"SUPG convergence (unrelaxed, cd at t 2): res 20 {cd20:.4f}, res 40 {cd40:.4f}, res 80 {cd_ref:.4f}; "
            f"observed order {pord:.2f}; extrapolated {ext:.4f}.")

qlog = open(os.path.join(RUNS, "night_queue.log")).read().strip().splitlines()[-12:] if os.path.exists(os.path.join(RUNS, "night_queue.log")) else []
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
pill = {"done": "ok", "running": "run", "killed": "bad", "failed": "bad", "queued": "q", "starting": "run"}
tr = "\n".join(
    f"<tr><td class=m>{html.escape(l)}</td><td>{html.escape(SCHEMES.get(k, (k,))[0])}</td><td class=n>{r}</td><td class=n>{C}</td>"
    f"<td><span class='p {pill.get(st, 'q')}'>{st}</span> <span class=s>{html.escape(note)}</span></td>"
    f"<td class=n>{lat}</td><td class=n>{c2}</td><td class=n>{e}</td><td class=n>{ra}</td></tr>"
    for (r, C, k, l, st, note, lat, c2, e, ra) in rows)
ref_line = f"Reference {REF}: {html.escape(ref_st[0])} {html.escape(ref_st[1])}; cd at t 2 = {cd_ref:.4f}." if cd_ref else ""

page = f"""<title>Cylinder scheme comparison</title>
<style>
/* layout: one column; summary line, table, then the two figures; the figures are light plots on a white plate in both themes */
:root {{ --bg:#f5f6f7; --fg:#1b2026; --muted:#5d6872; --rule:#d6dce1; --plate:#ffffff;
  --ok:#1e7b46; --run:#1f5fa8; --bad:#b03a2e; --q:#7a838b;
  --sans:"IBM Plex Sans",system-ui,sans-serif; --mono:"IBM Plex Mono",ui-monospace,monospace; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg:#13171b; --fg:#e3e7ea; --muted:#9aa4ad; --rule:#2b3239; --plate:#ffffff;
  --ok:#5cc58a; --run:#6aa8ea; --bad:#ec7a6c; --q:#8d969e; color-scheme:dark }} }}
:root[data-theme="dark"] {{ --bg:#13171b; --fg:#e3e7ea; --muted:#9aa4ad; --rule:#2b3239; --plate:#ffffff;
  --ok:#5cc58a; --run:#6aa8ea; --bad:#ec7a6c; --q:#8d969e; color-scheme:dark }}
body {{ background:var(--bg); color:var(--fg); font-family:var(--sans); padding-inline:16px; padding-block:22px 40px; }}
main {{ max-width:1180px; margin:0 auto; display:grid; gap:16px; }}
h1 {{ font-size:1.4rem; margin:0; font-weight:600; text-wrap:balance; }}
h2 {{ font-size:.8rem; letter-spacing:.06em; text-transform:uppercase; color:var(--muted); margin:8px 0 0; font-weight:500; }}
p {{ margin:0; max-width:80ch; line-height:1.5; }}
.sub {{ color:var(--muted); }}
.tbl {{ overflow-x:auto; }}
table {{ border-collapse:collapse; width:100%; min-width:860px; font-size:.86rem; font-variant-numeric:tabular-nums; }}
th,td {{ text-align:left; padding:5px 8px; border-bottom:1px solid var(--rule); vertical-align:top; }}
th {{ font-size:.72rem; letter-spacing:.05em; text-transform:uppercase; color:var(--muted); font-weight:500; }}
td.m {{ font-family:var(--mono); font-size:.8rem; }} td.n {{ font-family:var(--mono); font-size:.8rem; white-space:nowrap; }}
.s {{ color:var(--muted); font-size:.78rem; }}
.p {{ display:inline-block; padding:0 7px; border-radius:9px; font-size:.72rem; border:1px solid currentColor; }}
.p.ok {{ color:var(--ok); }} .p.run {{ color:var(--run); }} .p.bad {{ color:var(--bad); }} .p.q {{ color:var(--q); }}
figure {{ margin:0; background:var(--plate); border:1px solid var(--rule); padding:6px; }}
figure img {{ width:100%; height:auto; display:block; }}
pre {{ font-family:var(--mono); font-size:.76rem; overflow-x:auto; margin:0; color:var(--muted); }}
</style>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono&display=swap">
<main>
<h1>Stress schemes and Courant number, res 40 to t 2</h1>
<p class="sub">Re 100, Wi 0.5 Oldroyd-B, confined cylinder, on Hyperion. Updated {now}. {ref_line}</p>
<p>Error is cd(t 2) minus the SUPG res-80 value. The ratio column divides it by the unrelaxed SUPG res-40 error: below 1 the scheme beats SUPG at res 40, above 1 it is worse. {html.escape(conv)}</p>
<div class="tbl"><table>
<tr><th>Run</th><th>Scheme</th><th>Res</th><th>C</th><th>Status</th><th>Latest cd</th><th>cd at t 2</th><th>Error</th><th>Ratio</th></tr>
{tr}
</table></div>
<h2>Drag and lift to t 2</h2>
<figure><img alt="cd and cl against t for every comparison run and the res-80 reference" src="data:image/png;base64,{fig1}"></figure>
<h2>Res-80 runs to t 8</h2>
<figure><img alt="cd and cl of the SUPG res-80 reference and the stopped global-projection run" src="data:image/png;base64,{fig2}"></figure>
<h2>Queue log</h2>
<pre>{html.escape(chr(10).join(qlog))}</pre>
</main>"""
open(sys.argv[1], "w").write(page)
print("wrote", sys.argv[1], len(page) // 1024, "KB")
