"""Add-on matrix row 5 (fault networks), 2-D: does H0's FAC patch (the welded base, then
the split S level with the structural LU patch) handle a junction, two faults close
together, and a TI zone band beside a split fault, against H1 (the lean chain)?

The UWTN 2026-022 problem A box (unit box, unit viscosity, simple shear v = (y - 1/2, 0)
on every wall, base UnstructuredSimplexBox(cellSize=1/8, refinement=2), h_b = 1/32),
with the main fault from (0.30, 0.45) to (0.70, 0.55) at S = L / n_rungs, and:

    junction  a branch from (0.45, 0.20) towards the main fault's midpoint, stopping
              short 8 S from the main trace (the stop-short junction ruling: the
              intact gap is the linkage); both split and frictionless
    pair      a second fault parallel to the main one, 0.08 below it; both split
    ti        a TI band parallel to the main fault, 0.08 below it, placed as a ribbon
              but not cut (eta_1 = 0.01 on planes along the band, director its
              normal); the main fault split

Every strand is sampled at S, its interval count a multiple of 4 so the 4S and 2S
ladders of H1 take every 4th and 2nd point. uw_zone keys the FAC patch: "none" (the
structural patch alone), "ti" (fac_zone = the TI band) or "both" (fac_zone = the TI
band and the main fault's band). UW_FAC_STRUCTURAL in the environment unions the
structural rows into a fac_zone patch.

    mpirun -np 4 python row5_networks.py -uw_case pair -uw_hier H0 -uw_out records/x.json
"""
import json
import os
import sys
import resource
import time

import numpy as np
import sympy
import underworld3 as uw
from petsc4py import PETSc
from underworld3.utilities.custom_mg import set_custom_fmg
from underworld3.utilities.fault_contact import fault_slip
from underworld3.utilities.place_surface import place_fault_ribbon_2d

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import row7_common as rc  # noqa: E402  (the collective-safe patch reader)

params = uw.Params(
    uw_case="junction",       # junction, pair or ti
    uw_hier="H0",             # H0 or H1
    uw_n_rungs=320,           # main-fault intervals at S (h_b / S = 24 at 320)
    uw_zone="none",           # ti case: none, ti or both
    uw_gap=8,                 # junction case: the stop-short gap in S
    uw_tol=1.0e-6,
    uw_out="records/row5.json",
)
case, hier, zone_key = params.uw_case, params.uw_hier, params.uw_zone
A, B = np.array([0.30, 0.45]), np.array([0.70, 0.55])
L = float(np.linalg.norm(B - A))
n = int(params.uw_n_rungs)
assert n % 8 == 0
S = L / n
t_hat = (B - A) / L
n_hat = np.array([t_hat[1], -t_hat[0]])          # the main fault's normal, pointing down


def sampled(P, Q):
    """P to Q at about S, the interval count a multiple of 4."""
    m = max(4, 4 * int(round(np.linalg.norm(Q - P) / (4 * S))))
    return P + np.linspace(0.0, 1.0, m + 1)[:, None] * (Q - P)


main = A + (np.arange(n + 1) * S)[:, None] * t_hat
if case == "junction":
    P0, M = np.array([0.45, 0.20]), 0.5 * (A + B)
    d = M - P0
    # stop where the branch is uw_gap S from the main trace (distance along n_hat)
    s_stop = 1.0 - float(params.uw_gap) * S / abs(d @ n_hat)
    second = ("Branch", sampled(P0, P0 + s_stop * d))
elif case in ("pair", "ti"):
    second = ("Second" if case == "pair" else "TI", sampled(A + 0.08 * n_hat, B + 0.08 * n_hat))
else:
    raise ValueError(case)
spines = [("Fault", main), second]
cut = spines if case != "ti" else spines[:1]     # the TI band is placed, not cut

wall = time.perf_counter()
base = uw.meshing.UnstructuredSimplexBox(minCoords=(0, 0), maxCoords=(1, 1), cellSize=1 / 8,
                                         regular=False, qdegree=2, refinement=2)
base_levels = base._coarse_level_meshes()[:-1] + [base]
t_base = time.perf_counter() - wall


def ladder(host, k):
    """Every strand's ladder at 2^k S (every 2^k-th point), 2^(k+1) S wide, in host."""
    c = 2 ** k
    sp = [(lab, P[::c]) for lab, P in spines]
    tr = [(lab, P[::c]) for lab, P in cut]
    last = None
    for clearance in (0.7, 0.5):
        try:
            return place_fault_ribbon_2d(host, tr, 2 * S * c, spines=sp, margin_rings=1,
                                         clearance=clearance, split=True, mesher="ladder")[0]
        except RuntimeError as err:
            last = err
    raise last


wall = time.perf_counter()
if hier == "H0":
    levels = list(base_levels)
elif hier == "H1":
    levels = base_levels[:-2] + [ladder(base_levels[-2], 2), ladder(base_levels[-1], 1)]
else:
    raise ValueError(hier)
mesh = ladder(base, 0)
t_place = time.perf_counter() - wall

x, y = mesh.X
v = uw.discretisation.MeshVariable("v", mesh, 2, degree=2)
p = uw.discretisation.MeshVariable("p", mesh, 1, degree=1, continuous=True)
stokes = uw.systems.Stokes(mesh, velocityField=v, pressureField=p)
band_main = np.asarray(mesh.cells_labelled("Band", 71), dtype=bool)
band_second = np.asarray(mesh.cells_labelled("Band", 72), dtype=bool)
if case == "ti":
    zone = uw.discretisation.MeshVariable("zone", mesh, 1, degree=0, continuous=False)
    c = np.asarray(zone.coords)
    P, Q = second[1][0], second[1][-1]
    s = np.clip(((c - P) @ (Q - P)) / ((Q - P) @ (Q - P)), 0.0, 1.0)
    zone.array[:, 0, 0] = (np.linalg.norm(c - (P + s[:, None] * (Q - P)), axis=1) < S).astype(float)
    stokes.constitutive_model = uw.constitutive_models.TransverseIsotropicFlowModel
    stokes.constitutive_model.Parameters.shear_viscosity_0 = 1.0
    stokes.constitutive_model.Parameters.shear_viscosity_1 = 1.0 - 0.99 * zone.sym[0]
    stokes.constitutive_model.Parameters.director = sympy.Matrix([[n_hat[0], n_hat[1]]])
else:
    stokes.constitutive_model = uw.constitutive_models.ViscousFlowModel
    stokes.constitutive_model.Parameters.shear_viscosity_0 = 1.0
stokes.bodyforce = [0.0, 0.0]
for wall_name in ("Bottom", "Top", "Left", "Right"):
    stokes.add_dirichlet_bc((y - 0.5, 0.0), wall_name)
for lab, _P in cut:
    stokes.add_fault_bc(0, boundary=lab)
stokes.petsc_use_pressure_nullspace = True
stokes.tolerance = float(params.uw_tol)

fac_zone = None
if case == "ti" and zone_key == "ti":
    fac_zone = band_second
elif case == "ti" and zone_key == "both":
    fac_zone = [band_second, band_main]
wall = time.perf_counter()
set_custom_fmg(stokes, levels, field_id=0, fac_zone=fac_zone)
t_fmg = time.perf_counter() - wall

wall = time.perf_counter()
stokes.solve()
t_solve_first = time.perf_counter() - wall
info = stokes._rotated_freeslip_info
peaks = {}
for lab, _P in cut:
    _, slip, _ = fault_slip(stokes, lab, info)
    peaks[lab] = uw.mpi.comm.allreduce(float(np.abs(slip).max()) if len(slip) else 0.0, op=max)


def level_smoothers(velpc):
    """Each velocity MG level's smoother as installed; for a FAC patch level (PC
    composite = whole-level SOR, then ASM over the patch blocks) the ASM blocks, their
    rows summed over the ranks, the largest block and the block solver."""
    out = []
    for lev in range(velpc.getMGLevels()):
        ksp = velpc.getMGSmoother(lev)
        pc = ksp.getPC()
        entry = {"level": lev, "ksp": ksp.getType(), "pc": pc.getType()}
        asm = None
        if pc.getType() == "composite":
            subs = [pc.getCompositePC(i) for i in range(2)]
            entry["composite"] = [s.getType() for s in subs]
            asm = next((s for s in subs if s.getType() == "asm"), None)
        elif pc.getType() == "asm":
            asm = pc
        if asm is not None:
            sub_ksps = asm.getASMSubKSP()
            entry["asm_blocks"] = int(uw.mpi.comm.allreduce(len(sub_ksps)))
            entry["asm_rows"] = int(uw.mpi.comm.allreduce(
                sum(k.getOperators()[0].getSize()[0] for k in sub_ksps)))
            entry["asm_block_rows_max"] = max(uw.mpi.comm.allgather(
                max((k.getOperators()[0].getSize()[0] for k in sub_ksps), default=0)))
            entry["asm_sub_pc"] = sorted(set().union(*uw.mpi.comm.allgather(
                {k.getPC().getType() for k in sub_ksps})))
        out.append(entry)
    return out


ctx = (getattr(stokes, "_rotated_linear_cache", None) or {}).get("ctx")
level_ops, smoothers = [], []
if ctx is not None:
    velpc = ctx["ksp"].getPC().getFieldSplitSubKSP()[0].getPC()
    if velpc.getType() == "mg":
        smoothers = level_smoothers(velpc)
        for lev in range(velpc.getMGLevels()):
            Amat = velpc.getMGSmoother(lev).getOperators()[0]
            level_ops.append({"rows": int(Amat.getSize()[0])})

work = {"applications": 0, "iterations": 0}


def count_velocity_work(_ksp, its, _rnorm):
    if its == 0:
        work["applications"] += 1
    else:
        work["iterations"] += 1


if ctx is not None:
    ctx["pc"].getFieldSplitSubKSP()[0].setMonitor(count_velocity_work)
wall = time.perf_counter()
stokes.solve(zero_init_guess=True)
t_solve_again = time.perf_counter() - wall
info2 = stokes._rotated_freeslip_info

h = (getattr(stokes, "_custom_mg", None) or {}).get("hierarchy")
pr = getattr(h, "level_patch_rows", None)
last = pr[-1] if pr else None


owned = mesh.dm.getCellNumbering().getIndices() >= 0
record = {
    "row": 5, "case": case, "hierarchy": hier, "zone_key": zone_key,
    "UW_FAC_STRUCTURAL": os.environ.get("UW_FAC_STRUCTURAL"),
    "UW_FAC_COVER": os.environ.get("UW_FAC_COVER"), "gap_S": float(params.uw_gap),
    "n_rungs": n, "S": S, "h_b_over_S": (1 / 32) / S,
    "strands": {lab: len(P) - 1 for lab, P in spines}, "cut": [lab for lab, _ in cut],
    "band_cells_per_rank": {"main": uw.mpi.comm.allgather(int((band_main & owned).sum())),
                            "second": uw.mpi.comm.allgather(int((band_second & owned).sum()))},
    "level_ops_velocity": level_ops, "level_smoothers": smoothers,
    # rank-local in the hierarchy, so read with one collective on every rank
    # (one allreduce per local block hung at np 4 on kaiju: the counts differ)
    "patch": rc.finest_patch(h),
    "converged": info.get("converged"), "ksp_its": info.get("ksp_its"),
    "vel_its_last": info.get("vel_its_last"),
    "vel_its_last_again": info2.get("vel_its_last"),
    "vel_applications_again": work["applications"],
    "vel_its_all_applications_again": work["iterations"],
    "peak_slip": peaks,
    "t_base_s": round(t_base, 2), "t_place_s": round(t_place, 2), "t_fmg_s": round(t_fmg, 2),
    "t_solve_first_s": round(t_solve_first, 2), "t_solve_again_s": round(t_solve_again, 2),
    # ru_maxrss is bytes on macOS, kilobytes on Linux
    "peak_rss_mb_per_rank": [round(m / (2 ** 20 if sys.platform == "darwin" else 2 ** 10), 1)
        for m in uw.mpi.comm.allgather(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)],
    "np": uw.mpi.size,
}
uw.pprint("RECORD " + json.dumps(record))
with uw.selective_ranks(0) as selected:
    if selected:
        out = os.path.expanduser(params.uw_out)
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
        with open(out, "w") as f:
            json.dump(record, f, indent=1)
