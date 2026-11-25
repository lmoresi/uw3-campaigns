"""#893 in K1's configuration: the hierarchy of the failing job (kaiju runs/slab_ti_check2b,
TAf checkpoint 40, -uw_fault_realisation ti -uw_ti_check 2, chain 2, build 547c2e54),
rebuilt from the campaign driver annulus_faults.py at f14c1ec (2026-10-29 21:38 AEDT, the
commit that added the TI path; the job ran a local patch on it, see p_893.README.md).

    python p_893_k1.py [-uw_refinement 5] [-uw_chain 2] [-uw_split 0] [PETSc options]

What it reproduces from the driver:
- the ZG95 annulus of unit depth (r_i / r_o = 0.55), cell 0.5, refinement 5, qdegree 3;
- FaultedMesh's hierarchy: for k = chain..1 the fault's ladder ribbon is placed on
  levels[-k] at 2^k times the rung spacing S (band width 2 S 2^k), and the finest is the
  ribbon placed on the base (levels[-1]) at S; set_custom_fmg gets
  [L0 .. L(n-chain-1)] + the placed levels; with chain 2 that is
  [L0, L1, L2, placed(L3, 4S), placed(L4, 2S)] under the finest placed(L4, S);
- split=False (the TI realisation), the trace stopping 0.5 rung inside the wall
  (uw_ti_trace_inset), the driver's placement retries (rings, clearance, widen);
- rotated strong free-slip on both walls with the exact radial normal, the pressure null
  space, a P2/P1 Stokes solve.

What it does not reproduce (values not recoverable without the job's files): the fault's
own polyline (TAf's crust-law parabola fit at checkpoint 40) is replaced by a parabola
with the recorded trench angle and surface dip, to the crust law's depth cap 0.25, with an
assumed tip dip; the rheology is a
plain viscous host with a radial buoyancy (the report: the blow-up survives a plain VP
host, the band off and FAC disabled, and comes before the first iteration).

RES prints the largest per-rank peak RSS and the sum over ranks after the hierarchy build
and after the solve, with the global cell count of each level.
"""
import resource
import sys
import time

import numpy as np
import sympy

import underworld3 as uw
from underworld3.utilities.custom_mg import set_custom_fmg
from underworld3.utilities.place_surface import place_fault_ribbon_2d

params = uw.Params(
    uw_cell=0.5,
    uw_refinement=5,
    uw_chain=2,
    uw_spacing=0.004,           # S at the time of the job (the driver default then)
    uw_theta_deg=-3.14,         # TAf 40's fault trench angle (DECISIONS, recipe v2 acceptance)
    uw_dip=25.4,                # and its dip
    uw_depth=0.25,              # the crust law's tip: uw_fault_depth_max
    uw_tip_dip=45.0,            # NOT RECOVERED: the fitted parabola's dip at its tip
    uw_trace_inset=0.5,         # uw_ti_trace_inset
    uw_split=0,                 # 0: the TI realisation (split=False); 1: the split control
    uw_solve=1,                 # 0: build the hierarchy only
)

RATIO = 0.55
r_o, r_i = 1.0 / (1.0 - RATIO), RATIO / (1.0 - RATIO)
S = float(params.uw_spacing)
W = 2.0 * S
chain = int(params.uw_chain)


def peak_mb():
    # ru_maxrss is in bytes on macOS, kilobytes on Linux
    scale = 1.0e6 if sys.platform == "darwin" else 1.0e3
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / scale


def over_ranks(x):
    xs = uw.mpi.comm.allgather(x)
    return max(xs), sum(xs)


def fault_polyline():
    """The crust law's fault (a parabola from the trench to uw_fault_depth_max), rebuilt:
    depth z = t0 x + k x^2 along the surface arc x from the trench (toward +theta, the
    driver's down-dip side), dip uw_dip at the surface and uw_tip_dip at the tip, started
    0.02 above the wall as the driver's spines are, and resampled at S with a whole number
    of 2^chain blocks (the driver's resample_polyline)."""
    t0, t1 = np.tan(np.radians(float(params.uw_dip))), np.tan(np.radians(float(params.uw_tip_dip)))
    depth = float(params.uw_depth)
    X = 2.0 * depth / (t0 + t1)
    k = (t1 - t0) / (2.0 * X)
    x = np.linspace(-0.02 / t0, X, 4001)
    z = np.where(x < 0, t0 * x, t0 * x + k * x ** 2)
    theta = np.radians(float(params.uw_theta_deg)) + x / r_o
    pts = np.column_stack([(r_o - z) * np.cos(theta), (r_o - z) * np.sin(theta)])
    arc = np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(pts, axis=0).T))])
    block = 2 ** chain
    n = block * max(1, int(round(arc[-1] / (block * S))))
    a = np.linspace(0.0, arc[-1], n + 1)
    return np.column_stack([np.interp(a, arc, pts[:, 0]), np.interp(a, arc, pts[:, 1])])


POLY = fault_polyline()


def fault_trace(coarsening):
    """annulus_faults.fault_trace for a fault with points: the spine at coarsening x S,
    and the trace to place (uw_trace_inset rungs inside the wall)."""
    spine = POLY[::coarsening]
    trace = spine[np.hypot(spine[:, 0], spine[:, 1]) <= r_o - float(params.uw_trace_inset) * S]
    return spine, trace


def placed_ladder(host, coarsening):
    """annulus_faults.placed_ladders for one fault, with the driver's retries."""
    spine, trace = fault_trace(coarsening)
    width = W * coarsening
    attempts = [(1, 0.7, 1.0), (1, 0.7, 1.25), (2, 0.7, 1.0), (1, 0.7, 1.5)]
    for n, (rings, clearance, widen) in enumerate(attempts):
        try:
            mesh, info = place_fault_ribbon_2d(
                host, [("F0", trace)], width * widen, spines=[("F0", spine)],
                margin_rings=rings, clearance=clearance, split=bool(params.uw_split),
                mesher="ladder", seams="gather")
            uw.pprint(f"  placed at {coarsening}S: margin_rings {rings}, clearance {clearance}, "
                      f"width x{widen}")
            return mesh
        except (RuntimeError, ValueError) as err:
            retryable = any(s in str(err) for s in ("crosses itself", "domain wall", "ligament", "seam"))
            if not retryable or n == len(attempts) - 1:
                raise


t0 = time.time()
base = uw.meshing.Annulus(radiusOuter=r_o, radiusInner=r_i, cellSize=float(params.uw_cell),
                          refinement=int(params.uw_refinement), qdegree=3)
levels = base._coarse_level_meshes()[:-1] + [base]
mids = [placed_ladder(levels[len(levels) - k], 2 ** k) for k in range(chain, 0, -1)]
# FaultedMesh: with faults and chain 0 the unplaced base itself is the top coarse level
tail = levels[:len(levels) - chain] + mids if chain else levels
fine = placed_ladder(base, 1)
m_build = peak_mb()
cells = [over_ranks(m.dm.getHeightStratum(0)[1])[1] for m in tail + [fine]]
b_max, b_sum = over_ranks(m_build)
uw.pprint(f"BUILD np {uw.mpi.size} refinement {int(params.uw_refinement)} chain {chain} "
          f"split {int(params.uw_split)} cells {cells} peak per rank {b_max:.0f} MB "
          f"(sum {b_sum:.0f} MB) in {time.time() - t0:.1f}s")

if int(params.uw_solve):
    x, y = fine.X
    r = sympy.sqrt(x ** 2 + y ** 2)
    v = uw.discretisation.MeshVariable("V", fine, 2, degree=2)
    p = uw.discretisation.MeshVariable("P", fine, 1, degree=1, continuous=True)
    s = uw.systems.Stokes(fine, velocityField=v, pressureField=p)
    s.constitutive_model = uw.constitutive_models.ViscousFlowModel
    s.constitutive_model.Parameters.shear_viscosity_0 = 1.0
    s.bodyforce = 1.0e3 * sympy.cos(3 * sympy.atan2(y, x)) * sympy.sin(sympy.pi * (r - r_i)) \
        * fine.CoordinateSystem.unit_e_0
    unit_r = fine.CoordinateSystem.unit_e_0
    s.add_rotated_freeslip_bc(0, "Upper", normal=unit_r)
    s.add_rotated_freeslip_bc(0, "Lower", normal=unit_r)
    s.petsc_use_pressure_nullspace = True
    s.tolerance = 1.0e-4
    set_custom_fmg(s, tail, field_id=0)
    t1 = time.time()
    s.solve(zero_init_guess=True)
    a_max, a_sum = over_ranks(peak_mb())
    info = getattr(s, "_rotated_freeslip_info", None) or {}
    uw.pprint(f"RES np {uw.mpi.size} refinement {int(params.uw_refinement)} chain {chain} "
              f"split {int(params.uw_split)} cells {cells} peak per rank after build {b_max:.0f} MB, "
              f"after solve {a_max:.0f} MB (sum {b_sum:.0f} -> {a_sum:.0f} MB) solve "
              f"{time.time() - t1:.1f}s converged {info.get('converged')} its {info.get('ksp_its')}")
