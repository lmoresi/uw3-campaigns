import json, subprocess, time
N, O, REPO = "10", "underworldcode", "underworldcode/underworld3"
D = open("ve_discussion_url.txt").read().strip()
PID = json.load(open("project.json"))["id"]
F = {f["name"]: f for f in json.loads(subprocess.run(["gh","project","field-list",N,"--owner",O,"--format","json"],capture_output=True,text=True).stdout)["fields"]}
def opt(field, name): return next(o["id"] for o in F[field]["options"] if o["name"].lower()==name.lower())
def run(*a):
    r = subprocess.run(a, capture_output=True, text=True)
    if r.returncode: print("ERR", a[:3], r.stderr[:200]); return "{}"
    return r.stdout
def setf(iid, status, kind, area, added=None):
    for field, val in (("Status",status),("Kind",kind),("Area",area)):
        run("gh","project","item-edit","--project-id",PID,"--id",iid,"--field-id",F[field]["id"],"--single-select-option-id",opt(field,val))
    if added: run("gh","project","item-edit","--project-id",PID,"--id",iid,"--field-id",F["Added"]["id"],"--date",added)
tail = f"\n\nThread: {D}"
items = [
 ("VE: a library of methods for viscoelastic flow (element × relaxation × objective rate; four stress histories × two reconstructions)", "Design","Active","solvers","2026-10-05",
  "Louis (2026-10-05): we build a library of methods for VE flow, as a code carries several turbulence models; there is no single scheme for everything. Axes: element (maxwell, jeffreys), relaxation (linear, fene_p), objective_rate; stress carried by backward/forward × nodes/integration-points semi-Lagrangian histories or the Eulerian SUPG/DEVSS path; forward arrivals read back by a per-cell fit or a global projection (the stable one). Regularisations are named, visible terms. Domain-neutral names: relaxation law, element, extensibility (not polymer). Landed in PRs #789, #795, #800; docs in stress-transport.md. Open: second order for the forward methods; the global projection as a swarm proxy option; retire SNES_NavierStokes / SNES_AdvectionDiffusion when the composed solvers settle; shared trace in the composed Navier–Stokes."+tail),
 ("VE: benchmarks we chase and their status", "Task","Active","solvers","2026-10-05",
  "Done: steady shear closed forms (Oldroyd-B exact, FENE-P first order), Waters–King start-up (nodal converges, IP degrades with dt, Eulerian diverges), DFG 2D-2 Newtonian at Re 100 (lift and St within the reference band at res 40, drag 2% low). Found but off: cross-slot pitchfork at De 0.71 vs Poole's 0.35 (parked). Open: the VE cylinder at Re 100 has no reference for the DFG geometry (Richter et al. 2010 is FENE-P, 3-D, β 0.9). Next quantitative target: creeping flow past a confined cylinder, Oldroyd-B, β 0.59, 2:1 blockage (Alves, Fan, Hulsen: drag 132.36 at Wi 0 to ~117.8 at Wi 0.7)."+tail),
 ("VE: creeping-flow confined cylinder benchmark (Oldroyd-B, β 0.59, 2:1 blockage, Re 0) — build the driver and rank the histories against the published drag", "Task","Active","solvers","2026-10-05",
  "The one classic quantitative VE cylinder benchmark we have not run. Needs a 2:1 channel instead of the DFG geometry and the Stokes limit of the existing cylinder driver; nothing new in the library. Run the four stress histories and both reconstructions against the Alves/Fan/Hulsen drag table (four figures, Wi 0 to 0.7, log-conformation papers beyond Wi 1). The wall stress boundary layer that dominates the drag is exactly what the projection question is about."+tail),
 ("VE: Re 100 Wi 0.5 regime shift — the stress reconstruction decides; run the res-80 pair (Eulerian stress vs forward global) to separate damping from the cell fit's overshoot", "Task","Active","solvers","2026-10-05",
  "At res 40 with forward momentum: global-projection stress goes steady (cd 3.68, cl 0.001), cell-fit stress keeps shedding and grows (cd 4.22, cl 0.24, St 0.26), Eulerian SUPG+DEVSS stress sheds (cd 4.33, cl 0.52); Newtonian cl 1.01 (DFG-validated). FENE-P global at Wi 0.5: cd 3.25, cl 0.07. Two readings: the global projection damps the shear-layer perturbation, or the cell fit's overshoot at the rear stagnation point (#811) is a perturbation source and carries the extra drag. Decisive experiment: res 80, Re 100, Wi 0.5, Eulerian stress vs forward global, within the 8-core budget on the laptop or on the workstation."+tail),
 ("VE: FENE-P record is log(f c), decoded through its trace — the cylinder stall is solved", "Decision","Done","solvers","2026-10-05",
  "The log-c record overshot L² under the nodal projection at the wall (tr c 105 of 100 from a stress whose own conformation had 70), the spring factor hit its floor and the velocity multigrid ground to the guard's hang limit. The record is now log(σ/G + I) for both relaxation laws, with f* = 1 + (tr e^ψ − d)/L² and c* = e^ψ/f*; every SPD record is admissible. Commits 31709294 and 020b02f1 on PR #800; shear-box constants unchanged; Re 100 Wi 1 res 20 and Wi 0.5 res 40 run to t 8 where they hung before. Lesson for the library: a bounded variable is not the one to project."+tail),
 ("VE: Wi 2 cases (Oldroyd-B and FENE-P) are unresolved at res 20 — rerun at res 40", "Task","Active","solvers","2026-10-05",
  "FENE-P Wi 2 res 20 ran to t 7.1 on the new record then stopped on its third line-search divergence as the nodal stress maximum jumped 1.4 to 6.9 in a step; lift swung ±4 over t 4–7. Oldroyd-B Wi 2 failed at res 20 and 40 (unbounded spring at Re 100 and 200). Resolution, not scheme: rerun FENE-P Wi 2 at res 40; the Oldroyd-B case is the model's own limit."+tail),
 ("VE: runs biased by the first deficit fill — rerun or discount", "Task","Active","solvers","2026-10-05",
  "The deficit fill as first written pulled about half the cells toward the previous field every step (rotating Gaussian lost 18% of its peak); fixed to act only below 50% coverage (FILL_BELOW). Runs that carried the lagging fill: nodal_forward_global3 (the fully-global Re 200 res-20 result 4.19 / 1.26 / 0.258 is biased), r40_fwd_Wi1, r40_fwd_Wi2, r20_fwd_Wi2. Clean: glob600_s0, nodal_forward_global, supg_fwn_global, r40_nodal_forward_global, everything from 2026-10-05 23:08 on."+tail),
 ("VE: cylinder campaign scripts (driver, guard, renderer, summaries) need a repository the workstation can clone", "Task","Active","general","2026-10-05",
  "~/+Simulations/ve_cylinder_demo holds ve_cylinder.py (uw.Params options for Re, Wi, β, L², transports, reconstructions, smoothing, bubble penalty, restart, tracers), run_guarded.sh (hang / blow-up / SNES-failure guard), lane scripts, render_demo.py, render_movie.sh, forces_summary.py, ring_profiles.py, wake_roughness.py, night_report.py. None of it is in git. Proposal: a repo of its own under the org (uw3-campaigns) so the multicore workstation runs the same campaigns."+tail),
 ("VE: global projection as a swarm proxy option (proxy_sampling=\"project\")", "Idea","Someday","swarm","2026-10-05",
  "ParticleL2Projector (weighted least-squares L2 projection of scattered values onto continuous P1/P2 with the particles as quadrature, deficit fill, bubble penalty for P2) is the stable read-back for the forward histories. The same operator could replace the RBF swarm proxy where the proxy feeds a residual."+tail),
 ("VE: second order in time for the forward methods", "Idea","Someday","ddt","2026-10-05",
  "The forward histories are first order (one launch, one arrival set). The exponential step and the log store are first order on the positive-definite path too. Decide whether a two-level forward scheme is worth its cost before Richter-type comparisons."+tail),
 ("VE: cross-slot pitchfork threshold — De 0.71 found vs Poole's 0.35", "Task","Parked","solvers","2026-09-25",
  "The bifurcation appears only with the log store, exp read and SPD update; the old DQ order parameter was blind. Threshold is off by a factor two; seed with a swirl body force; use projections, not evaluate, for diagnostics. Parked behind the cylinder work."+tail),
 ("VE: FENE-P at Re 100 against Richter et al. 2010 (β 0.9, L² 100, 3-D)", "Idea","Someday","solvers","2026-10-05",
  "The only inertial VE cylinder reference with numbers (St and drag against Wi). β differs from our 0.5 and their runs are three-dimensional, so it is a trend comparison, not a match. After the creeping benchmark."+tail),
]
made = {}
for title, kind, status, area, added, body in items:
    out = run("gh","project","item-create",N,"--owner",O,"--title",title,"--body",body,"--format","json")
    iid = json.loads(out).get("id")
    if iid: setf(iid, status, kind, area, added); made[title] = iid; print("draft", title[:70])
    time.sleep(0.3)
for n, status in (("809","Active"),("810","Active"),("811","Active")):
    out = run("gh","project","item-add",N,"--owner",O,"--url",f"https://github.com/{REPO}/issues/{n}","--format","json")
    iid = json.loads(out).get("id")
    if iid: setf(iid, status, "Bug", "ddt" if n != "809" else "checkpoint", "2026-10-04"); print("linked #"+n)
json.dump(made, open("ve_items_made.json","w"), indent=1)
