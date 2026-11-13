"""The slab workbench: one split-node fault fitted to the crust of a prescribed slab, in
the strain-weakening annulus.

The driver forked from ``annulus_faults.py`` at 8fff721 for Louis's Earth-scaled plate
model. This commit is the cut only: what the plate model needs is kept as it was, with no
change of behaviour, and the rest of the parent is gone. Kept: the slab initial state
(plate ages, ridge positions, the overriding plate and the continent), the fixed ridge
patch, the crust particles advected with the split velocity and refilled, the fault fitted
to the crust by a smoothing spline and ended at the depth cap, the frictionless split with
its ladder and bridge, strain weakening and healing, the Arrhenius viscosity, the
asthenosphere and lower-mantle factors, the graded mesh, the solver with its retries,
records, checkpoints and restart (``uw_restart`` in ``uw_out``).

    mpirun -np 16 python slab_workbench.py -uw_out <dir> -uw_restart 60
"""
import gc
import json
import os
import sys
import time
import warnings

import numpy as np
import sympy
import underworld3 as uw
from underworld3.utilities.custom_mg import set_custom_fmg
from underworld3.utilities.fault_contact import _fault_pair_nodes_on, fault_slip
from underworld3.utilities.place_surface import place_fault_ribbon_2d

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from annulus_model import (AnnulusDiagnostics, annulus_mesh, annulus_radii, arrhenius_E, clamp_radii,
                           free_slip_walls, set_viscoplastic)

params = uw.Params(
    uw_out="~/+Simulations/zg95/slab_workbench/runs/test",
    # the "slab" state (half-space cooling referenced to an age line): the plate age along
    # the surface ramps from zero at each plate's ridge to uw_age_sub (subducting side) or
    # uw_age_over (overriding side, the side the fault dips under) at the trench; the age
    # continues down the slab's upper surface, the fault plane, as the trench age plus the
    # distance down-dip over uw_slab_rate; T = T_i erf(d / 2 sqrt(age)) with d the distance
    # to the age line (the depth below the surface, or the distance into the subducting side
    # of the slab plane), the colder of the two where both apply. Plate thickness 2 sqrt(age):
    # age 0.0025 is a 0.1 d plate.
    uw_T_interior=0.75,
    uw_age_sub=0.0025,
    uw_age_over=0.001,
    uw_ridge_sub=3.14159,       # angle from the trench to the subducting plate's ridge (radians)
    uw_ridge_over=3.14159,      # angle from the trench to the overriding plate's ridge (radians)
    uw_age_thin=2.0e-5,         # the age of the surface where there is no plate (a 0.009 d boundary layer)
    uw_over_plate=1,            # 0: no overriding plate, the thin boundary layer instead
    uw_top_hot=0,               # 2: a fixed ridge (uw_ridge_patch); 0: none
    uw_ridge_patch=0.05,        # uw_top_hot 2 (a fixed ridge): only a patch of this half-width (arc, layer depths) at the
                                #   subducting plate's ridge (uw_ridge_sub behind the trench: the antipode by default) is
                                #   held at T_interior, tanh ramps of uw_over_ramp; T = 0 elsewhere
    uw_cont_extent=0.0,         # > 0: the compositional overriding plate (the continent) ends this angle (radians) from the
                                #   trench (uw_theta_trench) instead of at the overriding plate's ridge. Measured from the
                                #   trench, not from the continent's start: 1/3 of the annulus from the start at
                                #   uw_over_gap is 2.094 + uw_over_gap / r_o (2.4315 for a 0.75 gap)
    uw_cont_age=0.0,            # > 0: a uniform thermal age (layer depths^2) under the continent in the slab state, in place
                                #   of the ocean's ramp (0.000625: a 0.05 d, ~145 km, conductive lid)
    uw_lm_eta=1.0,              # a viscosity factor below uw_lm_depth (the 670 km step; 1 = none); Ra and the yield
                                #   stresses stay referenced to the upper mantle
    uw_lm_depth=0.231,          # layer depths (670 km of a 2900 km mantle)
    uw_lm_ramp=0.02,
    uw_fault_precedence=0,      # 1: inside a fault's band the fault's own rheology alone: the crust and continent
                                #   factors are off there (Louis: "the fault rheology should always win")
    uw_marker_rheo_depth=0.0,   # > 0: below this depth (layer depths) the crust and continent factors fade out
                                #   (tanh, uw_marker_rheo_ramp); their markers are still advected, recorded and drawn,
                                #   so entrained material is tracked without acting (Louis: "change the material
                                #   index so we track it but it does not have a rheological influence")
    uw_marker_rheo_ramp=0.02,
    uw_over_gap=0.0,            # the overriding plate starts this arc length (layer depths) from the trench
    uw_over_ramp=0.03,          # over which its age ramps up from the thin layer's
    # a weak oceanic crust carried by particles: a layer uw_crust_thick thick (< 0: one cell)
    # on the subducting plate's surface and down the slab's top face, its viscosity and yield
    # stress times uw_crust_weak (1 = no crust), the weakness fading below uw_crust_depth
    uw_crust_weak=1.0,
    uw_crust_thick=-1.0,
    uw_crust_depth=0.5,
    uw_crust_fill=1,            # particles per cell parameter (1: about 3 per cell)
    uw_crust_ppc=0,             # > 0: the crust layer seeded denser than the swarm, about this many
                                #   particles per cell on a lattice in the layer's own frame (0: the swarm's)
    uw_crust_refill_every=0,    # > 0 (with uw_crust_ppc): every this many steps, the crust on the subducting
                                #   plate's surface topped up to the uw_crust_ppc spacing where it has thinned
    uw_ridge_crust=0,           # 1 (with uw_crust_ppc and uw_crust_refill_every): crust on plate made at the
                                #   ridge. At every refill the subducting plate's surface layer is brought to the
                                #   uw_crust_ppc spacing wherever it holds no crust particle, from the edge of its ridge's
                                #   hot patch (uw_top_hot 2, uw_ridge_patch; from the ridge itself without one) to
                                #   uw_ridge_crust_stop short of the trench, and the oceanic-crust line (uw_ocrust_depth)
                                #   is carried on the same way. 0: crust only where the start put it and where the refill
                                #   finds it, so plate made at the ridge carries none, and the fault has
                                #   nothing to follow once that plate nears the trench (earth_young80, ridge 0.6 rad
                                #   behind the trench, 2026-11-12: every fit refused from step 225)
    uw_ridge_crust_stop=0.1,    # uw_ridge_crust: no crust is made within this arc (layer depths) of the trench, where
                                #   the layer bends under and the refill's own rule (crust only where its proxy is) holds
    uw_ocrust_depth=0.0,        # > 0: a passive oceanic-crust line, marker "ocrust": particles every
                                #   line_spacing() this deep under the subducting plate's surface and into the slab's top
                                #   face (below the weak crust layer when deeper than uw_crust_thick), its gaps filled at
                                #   the refill (refill_line); carried and written, never in the rheology or the fault's placement
                                #   (Louis, 2026-11-12: "we treat a slightly deeper layer as the oceanic crust itself for the
                                #   purpose of tracking deep advection of the oceanic crust and locations for dehydration
                                #   reactions", "I'd trace the oceanic crust as a near-line. We don't need to know its
                                #   thickness, just its location"). 0: none
    uw_crust_line_spacing=0.0,  # the particle spacing along the oceanic-crust line; 0: a quarter of the rung spacing S
    uw_buoy_T=1.0,              # scales the thermal buoyancy
    # the compositional overriding plate (stage 3): a layer uw_over_comp_thick thick from
    # uw_over_gap behind the trench to its ridge, viscosity x uw_over_eta, deficit uw_over_dT (negative: buoyant;
    # a 0.05 d continent over a uniform lid of age 0.000625 is neutral at about -0.39)
    uw_over_dT=0.0,
    uw_over_eta=1.0,
    uw_over_comp_thick=0.1,
    uw_slab_length=0.35,
    uw_slab_rate=1000.0,        # the convergence rate the slab went down at (its age continuation); at
                                #   100 (the model's own plate speed at Ra 3e6) a 0.35 d slab has warmed through
    uw_slab_contact=-1.0,       # the slab's top stays cold (against the overriding plate) to this depth and
                                #   is heated by the mantle below it; < 0: the overriding plate's thickness at
                                #   the trench, 2 sqrt(uw_age_over) (zero without an overriding plate)
    uw_slab_wedge_age=6.25e-4,  # the slab's top is cold (T = 0 on the plane): the wedge is cooled beside the slab over
                                #   2 sqrt(this) (0.05 d), continuous across the plane, no mask
    uw_restart=-1,
    uw_cell=0.5,
    uw_refinement=4,
    uw_cell_outer=0.0,          # > 0: a graded mesh, the coarse cell this size at the outer wall (Louis, 2026-11-13: refine
    uw_cell_inner=0.0,          #   near the surface to resolve a slab of half the age with fewer cells overall); > 0: the
                                #   coarse cell at the inner wall; 0 = uw_cell. Then the base cell H_B (the crust lattice,
                                #   the rung spacing by default, the rebuild threshold) is the outer wall's cell, where
                                #   the plates, the crust and the fault are
    uw_ra=9.1125e5,
    uw_deta=3.0e4,
    # the viscosity's temperature law is Arrhenius (Louis, 2026-11-12: "an Arrhenius version of the young slab
    # run"): exp(E / (T + T0)), equal to uw_deta ** (1 - T) at uw_T_interior and capped (annulus_model.eta_of_T)
    uw_arr_T0=0.1092,           # the surface temperature over the temperature drop (273 K / 2500 K)
    uw_arr_E=0.0,               # the activation term E (E* / R dT). 0: the slope of uw_deta ** (1 - T) at uw_T_interior,
                                #   ln(uw_deta) (uw_T_interior + uw_arr_T0)^2 (6.12 for uw_deta 4e3: 127 kJ/mol at dT 2500 K)
    uw_arr_eta_max=0.0,         # the viscosity's cap. 0: uw_deta
    uw_tau0=2.025e4,
    uw_tau1=1.366875e6,
    uw_heating=1.4175,
    uw_yield_softness=0.2,
    # an asthenosphere: the viscosity times uw_asth in a channel between two depths
    uw_asth=1.0,                # 1: no channel; 0.01-0.1 for a weak channel under the lid
    uw_asth_top=0.3,
    uw_asth_bottom=0.7,
    uw_asth_ramp=0.05,
    # the trench and the dip of the slab state
    uw_theta_trench=0.0,
    uw_dip=45.0,
    # the fault band
    uw_spacing=0.0,             # the ladder's rung spacing S. 0 (the default): one base cell, uw_cell / 2**uw_refinement, so S
                                #   follows the refinement (0.0156 at refinement 5). Louis (2026-11-02): S matched to the base
                                #   mesh; 0.004 before (ratio 3.9). Kaiju arms (page 7cbuaxBnoZrfjdPioMHroT, chain 0, np 16):
                                #   the serial FAC patch 3.2x smaller and 2.3-4.5x cheaper, 14 % less per step on the
                                #   rollback state, vrms within 0.3 %; velocity iterations per increment unchanged (7.2-7.5),
                                #   the gain is fewer Newton increments (65 against 79 over 10 steps) and the patch. With
                                #   S = h_b the 1-rung inset is one base cell deep (the cut's top ~0.020 below the surface),
                                #   so the early-slab near-surface slip is 10-18 % lower than the old recipe's
    uw_eta_w=1.0e-3,
    uw_band_widen=1,
    uw_rebuild_cells=1.0,       # rebuild the faulted mesh when a fault moved more than this many BASE CELLS
                                #   (uw_cell / 2**uw_refinement, independent of the rung spacing): the fault polyline's
                                #   gap to the built one. Replaces uw_rebuild_rungs (retired 2026-11-04): counted in rungs
                                #   of S, the spacing default (S = h_b) made rungs 4 a tolerance of 0.0625 where the old
                                #   recipe's was 0.016, and the built cut lagged into hot mantle (Earth run 2: 69 % of it
                                #   at T > 0.7; TAf-v2: all of it)
    uw_placement_refused="stop",  # a fault the placement refuses after all its attempts. "stop" (Louis, 2026-11-13:
                                #   "Stop - and checkpoint the final step. Fine to restart"): the run ends there with
                                #   exit code 3, after writing the last finished step's checkpoint if the cadence had
                                #   not, so it can be restarted. "keep" (every run to 2026-11-13): the previous faults
                                #   stay and the run goes on with the fault where it was
    # the fault's locator (crust_spline_points): a smoothing spline in arc length through the crust's centre line,
    # from the incoming plate through the bend down the slab; no level of the layer chosen, no straight top, no dip
    # floor (Louis, 2026-11-12: "a smooth fit with finite curvature (a spline is a plate bending solution of
    # sorts)", "let the dynamics control the shape and not the other way around"). The fault ends at the depth cap,
    # uw_fault_depth_max: a curve ending within 0.03 of it is carried to it along its own direction, one ending
    # higher is refused
    uw_spline_side="centre",    # "centre" (the layer's median line) or "base" (Louis, 2026-11-12: "a thin, weak upper
                                #   layer that we follow the base": a second pass about the centre line takes the quantile
                                #   with 10 % of the layer beyond it toward the plate interior)
    uw_spline_length=0.02,      # the smoothing length L (layer depths): lam = L^4 / 0.005 (offline on 12 stored
                                #   checkpoints, 2026-11-12: radius of curvature 0.04-0.13; 0.012 kinked at the wedge)
    uw_wall_normal="analytic",  # the free-slip walls' normal: "analytic" (radial unit_r, every run to 2026-11-01) or
                                #   "geometric" (the library default: facet normals summed across ranks)
    uw_wall_check=1,            # 1: every solve records the free-slip constraint as solved (max |v.n| per wall, nodes
                                #   above 1e-8 |v|max) in the step's solver record, and warns when it is broken
    uw_retry_keep="best",       # after a failed warm start and its cold retry, keep the attempt with the smaller final
                                #   residual ("best"; the warm iterate restored), or the cold one always ("last", before
                                #   2026-11-01: TAti_smooth step 61 kept a cold 0.12 over a warm 2.0e-2)
    uw_fault_normal="node",     # the contact's normal: "node" = per-node from the cut facets (the default);
                                #   "trace" = the library's smoothed normal of the fault's own polyline (normal="trace")
    uw_rebuild_newton_switch=1.0e-2,
    # strain weakening, regularisation, healing
    uw_strain_crit=0.5,
    uw_weak_min=0.5,
    uw_yield_boost=1.25,
    uw_eta_reg=10.0,
    uw_heal_time=0.002,
    uw_heal_T=0.7,
    # fitting the fault
    uw_detect_every=5,
    uw_detect_start=0,          # steps before the first detection (a prescribed slab needs a few to
                                #   establish its shear band before the fit is allowed to move the fault)
    uw_fault_seams="gather",    # the placement's seam handling for a band that straddles a partition seam: "gather"
                                #   (the band's region moved onto one rank and carved there; every campaign run to
                                #   2026-11-01) or "conform" (#670, 2-D: meshed through the seam, each rank its own
                                #   side). The mesh record carries the mode and the band's cells per rank
    uw_resample_restored="auto",  # restart: re-sample restored fault polylines at this run's S when it differs from
                                #   the checkpoint's ("auto"); "force" or "never" for tests
    uw_split_inset=1.0,         # how many rungs inside the outer wall the split's cut stops. 1 (Louis, 2026-11-02: "logical
                                #   set back based on the purpose, appears to be safe"): the inset is one element because the
                                #   surface DOFs cannot be rotated, not a physical depth. 3 before (no recorded reason). Kaiju
                                #   test (page T37Y3MMpYyfgQZbCmuk5YQ): 1 rung placed all 80 stored faults on the finest level;
                                #   slip is ~10 % higher than at 3 (the cut reaches 0.005 instead of 0.013 below the surface)
    uw_split_inset_along=0,     # 1: uw_split_inset is measured along the fault from where its spine crosses the outer wall,
                                #   not as depth below the wall. Louis (2026-11-08): the split should run to one element
                                #   from the boundary, as the ladder does; by depth, a 27-degree fault's cut stopped ~2 cells
                                #   along the fault short of that (refinement 6: first split node 1.8 cells deep). 0 keeps
                                #   the depth rule (the recipe until ruled)
    uw_fault_depth_max=0.25,
    uw_advect_offset=0.1,       # a record's plate speeds are sampled this arc (layer depths) on each side of the trench
    # solver and time stepping
    uw_tol=1.0e-3,
    uw_pres_rtol=1.0e-2,        # > 0: the Schur (pressure) KSP rtol, overriding the library's 0.1 x uw_tol (the
                                #   rotated free-slip solve's solver._rotated_pres_rtol, and the native path's option);
                                #   0 = the library's. 1e-2 (Louis, 2026-11-01): kaiju A/B 2026-10-28, -28 to -57 %
                                #   Stokes time, the answer to 7e-6; kaiju budget 2026-11-01 (TAf 40, np 16), 2.3x, vrms
                                #   to 6 figures, slip within 0.05 (12-22 pressure its per increment against 41-47).
                                #   A run's README records the value it used; pinned running drivers keep theirs.
                                #   Warm solves only from 2026-11-04: cold solves take uw_pres_rtol_cold
    uw_pres_rtol_cold=1.0e-4,   # the Schur (pressure) KSP rtol for every COLD solve: the run's first solve and any cold
                                #   retry (keep-best's cold attempt included); warm solves keep uw_pres_rtol. 1e-4 is the
                                #   library's 0.1 x uw_tol. Kaiju 2026-11-04: at refinement 6 the cold first solve at 1e-2
                                #   stalled in the line search (pressure 4 its per solve, alpha to 0, rel 0.77; job 3972)
                                #   and at 1e-4 converged in 6 (alpha 1.0, rel 2.8e-5; job 3977). 0 = uw_pres_rtol
    uw_picard=0,
    uw_newton_switch=1.0e-2,
    uw_warm_newton_switch=1.0e-1,  # Picard -> Newton on warm steps once |F| <= this x max(F0, F_rest) (rotated_bc).
                                #   1e-1 (Louis, 2026-11-05): one or two Picard steps bring a warm iterate into
                                #   Newton's basin; pure Newton (1.0, the old default) took 1.5-2x the iterations
                                #   with line-search cutbacks, 1e-2 (the launch lines from 2026-10-28) 2-6 Picard
                                #   steps; -13 % (TAf-v2) and -22 % (Earth) per step against 1e-2, answers to 4-5
                                #   figures (kaiju jobs 3973, 3983, 3985, 3987; DECISIONS.md, Newton switches)
    uw_verbose=0,
    uw_dt_mult=3.0,
    uw_courant=1.0,
    uw_dt_max=5.0e-3,
    uw_steps=20,
    uw_ckpt_every=10,
)

out = os.path.expanduser(params.uw_out)
os.makedirs(out, exist_ok=True)
r_o, r_i = annulus_radii()
def effective_spacing(p):
    """The rung spacing a parameter set means: uw_spacing, or one base cell (uw_cell / 2**uw_refinement) when 0."""
    sp = float(p.get("uw_spacing", 0.0) or 0.0)
    return sp if sp > 0 else float(p.get("uw_cell", 0.5)) / 2 ** int(p.get("uw_refinement", 4))


CELL_TOP = float(params.uw_cell_outer or params.uw_cell)          # the coarse cell at the surface (graded or not)
S = effective_spacing({"uw_spacing": params.uw_spacing, "uw_cell": CELL_TOP, "uw_refinement": params.uw_refinement})
H_B = CELL_TOP / 2 ** int(params.uw_refinement)    # the base cell at the surface (effective_spacing's derivation)
PRES_RTOL_WARM = float(params.uw_pres_rtol) if float(params.uw_pres_rtol) > 0 else 0.1 * float(params.uw_tol)
PRES_RTOL_COLD = float(params.uw_pres_rtol_cold) if float(params.uw_pres_rtol_cold) > 0 else PRES_RTOL_WARM
FIRST_SOLVE = True             # the run's first solve: an unconverged cold one stops a fresh run
REBUILD = float(params.uw_rebuild_cells) * H_B                  # the rebuild threshold, a distance (needs_rebuild)
if str(params.uw_fault_seams) not in ("gather", "conform"):
    raise ValueError(f"-uw_fault_seams must be gather or conform, not {params.uw_fault_seams!r}")
try:                                   # which mechanism puts a gathered fault on one rank (the record says)
    import underworld3.utilities.addon_partition  # noqa: F401  (development: the add-on is partitioned first)
    _addon_partition = True
except ImportError:
    _addon_partition = False
FAULT_PARTITION = ("serial" if uw.mpi.size == 1 else
                   "conform: meshed across the seams in place" if params.uw_fault_seams != "gather" else
                   "gather via addon_partition.partition_addon (the band's region on one rank first)"
                   if _addon_partition else "gather by the placement (the region moved onto one rank)")
W = 2.0 * S

base = annulus_mesh(params.uw_cell, params.uw_refinement, outer=params.uw_cell_outer, inner=params.uw_cell_inner,
                    filename=f"{out}/annulus_graded.msh")
levels = base._coarse_level_meshes()[:-1] + [base]
T_b = uw.discretisation.MeshVariable("T", base, 1, degree=2)
V_b = uw.discretisation.MeshVariable("V", base, base.dim, degree=2)
log_eta_b = uw.discretisation.MeshVariable("log10_eta", base, 1, degree=1)
yield_ratio_b = uw.discretisation.MeshVariable("yield_ratio", base, 1, degree=1)
gamma_b = uw.discretisation.MeshVariable("plastic_strain", base, 1, degree=2)
edot_p_b = uw.discretisation.MeshVariable("edot_plastic", base, 1, degree=1)

# The crust: particles over the whole base mesh carrying a 0/1 crust marker; its proxy is
# the per-cell linear fit through the cell's particles (sharp at cell edges, no value in a
# cell the crust has left); crust_b (P1) is the checkpointed picture for the renders.
crust_on = params.uw_crust_weak < 1
RIDGE_CRUST = bool(int(params.uw_ridge_crust))
if RIDGE_CRUST and (not crust_on or params.uw_crust_ppc <= 0 or params.uw_crust_refill_every <= 0):
    raise ValueError("-uw_ridge_crust 1 makes crust at the refill: it needs the crust layer (uw_crust_weak < 1) "
                     "with uw_crust_ppc > 0 and uw_crust_refill_every > 0")
if not crust_on:
    raise ValueError("the fault follows the crust layer: it needs one (uw_crust_weak < 1)")
over_on = params.uw_over_dT != 0 or params.uw_over_eta != 1   # a negative uw_over_dT is a buoyant block
swarm_on = crust_on or over_on
crust_thick = (float(params.uw_crust_thick) if params.uw_crust_thick > 0
               else H_B)
ocrust_on = crust_on and params.uw_ocrust_depth > 0
# the markers: name -> (swarm variable, its P1 picture on the base mesh, the geometry
# of the slab state as a function of particle coordinates)
markers = {}
if swarm_on:
    crust_swarm = uw.swarm.Swarm(base)
    # populated by the initial state: fresh particles for the slab state, the saved ones on a restart
for name, on, geometry in (("crust", crust_on, lambda xy: layer_marker(xy, crust_thick)),
                           ("ocrust", ocrust_on, lambda xy: np.zeros(len(xy))),   # 1 on its line's particles only
                           ("over", over_on, lambda xy: over_marker(xy, float(params.uw_over_comp_thick)))):
    if on:
        markers[name] = (uw.swarm.SwarmVariable(name, crust_swarm, 1, proxy_location="cells", proxy_degree=1),
                         uw.discretisation.MeshVariable(name, base, 1, degree=1), geometry)
if crust_on:
    crust_var, crust_b = markers["crust"][:2]


def clamp01(sym):
    return sympy.Max(0, sympy.Min(1, sym))


def marker_rheo_window(mesh):
    """1 above uw_marker_rheo_depth, fading to 0 below it (tanh, uw_marker_rheo_ramp): where a
    marker's rheology acts; 1 everywhere when the gate is off."""
    if params.uw_marker_rheo_depth <= 0:
        return 1
    depth = r_o - sympy.sqrt(mesh.X[0] ** 2 + mesh.X[1] ** 2)
    return (1 - sympy.tanh((depth - params.uw_marker_rheo_depth) / params.uw_marker_rheo_ramp)) / 2


def crust_factor_on(mesh, crust_sym, mask=0):
    """The viscosity (and yield stress) factor of the crust proxy ``crust_sym`` on ``mesh``:
    uw_crust_weak where the marker is 1, fading to 1 below uw_crust_depth (and below
    uw_marker_rheo_depth), and 1 where ``mask`` (the fault band, uw_fault_precedence) is 1."""
    depth = r_o - sympy.sqrt(mesh.X[0] ** 2 + mesh.X[1] ** 2)
    window = (1 - sympy.tanh((depth - params.uw_crust_depth) / 0.05)) / 2 * marker_rheo_window(mesh)
    return 1 - (1 - params.uw_crust_weak) * clamp01(crust_sym) * window * (1 - mask)


def comp_factor_on(marker_sym, eta, mask=0, window=1):
    """The viscosity (and yield stress) factor of a compositional layer: ``eta`` where
    the marker is 1, times ``window`` (the depth gate), and 1 where ``mask`` is 1."""
    return 1 + (eta - 1) * clamp01(marker_sym) * window * (1 - mask)


Ra = uw.expression(r"\mathrm{Ra}", params.uw_ra, "Rayleigh number on the basal viscosity")
deta = uw.expression(r"\Delta\eta", params.uw_deta, "viscosity contrast across the layer")
tau0 = uw.expression(r"\tau_0", params.uw_tau0, "yield stress at the surface")
tau1 = uw.expression(r"\tau_1", params.uw_tau1, "yield stress gradient with depth")
H = uw.expression(r"H", params.uw_heating, "internal heating rate")
heating = params.uw_heating

# (E, T0, T_i, eta_max) of annulus_model.eta_of_T
ARRHENIUS = (float(params.uw_arr_E) or arrhenius_E(params.uw_deta, params.uw_T_interior, params.uw_arr_T0),
             float(params.uw_arr_T0), float(params.uw_T_interior),
             float(params.uw_arr_eta_max) or float(params.uw_deta))

adv = uw.systems.AdvDiffusion(base, T_b, V_b.sym, order=1)
adv.constitutive_model = uw.constitutive_models.DiffusionModel
adv.constitutive_model.Parameters.diffusivity = 1
adv.f = H


def hot_top_window(rel_arc, lib=np):
    """1 where the surface is held hot (uw_top_hot 2, a fixed ridge): a patch of half-width
    uw_ridge_patch about the subducting plate's ridge, uw_ridge_sub behind the trench (the
    antipode by default), with tanh ramps of uw_over_ramp; numpy or sympy."""
    ramp = max(float(params.uw_over_ramp), 1e-6)
    # dist is the arc to the ridge, either way round
    a = rel_arc / r_o + abs(float(params.uw_ridge_sub))
    dist = (lib.Abs(sympy.atan2(sympy.sin(a), sympy.cos(a))) if lib is sympy
            else np.abs(np.arctan2(np.sin(a), np.cos(a)))) * r_o
    return (1 - lib.tanh((dist - float(params.uw_ridge_patch)) / ramp)) / 2


if int(params.uw_top_hot) not in (0, 2):
    raise ValueError(f"-uw_top_hot {params.uw_top_hot}: 0 (the surface cold everywhere) or 2 (a fixed ridge)")
if params.uw_top_hot:
    x_s, y_s = base.X
    th_t = float(params.uw_theta_trench)
    over_sign = 1.0 if params.uw_dip < 90 else -1.0
    rel_sym = over_sign * sympy.atan2(sympy.sin(sympy.atan2(y_s, x_s) - th_t),
                                      sympy.cos(sympy.atan2(y_s, x_s) - th_t)) * r_o
    adv.add_dirichlet_bc([float(params.uw_T_interior) * hot_top_window(rel_sym, sympy)], "Upper")
else:
    adv.add_dirichlet_bc(0.0, "Upper")
adv.add_dirichlet_bc(1.0, "Lower")

# Accumulated plastic strain, carried by the flow, growing at the plastic strain rate
# and healing where the material has warmed into the mantle.
strain_adv = uw.systems.AdvDiffusion(base, gamma_b, V_b.sym, order=1)
strain_adv.constitutive_model = uw.constitutive_models.DiffusionModel
strain_adv.constitutive_model.Parameters.diffusivity = 1.0e-6
heal_rate = 0
if params.uw_heal_time > 0:
    heal_rate = 1 / params.uw_heal_time
    if params.uw_heal_T > 0:
        heal_rate = heal_rate * (1 + sympy.tanh((T_b.sym[0] - params.uw_heal_T) / 0.02)) / 2
strain_adv.f = edot_p_b.sym[0] - gamma_b.sym[0] * heal_rate


def onto(points):
    return clamp_radii(np.asarray(points, dtype=float), r_o, r_i, inset=1.0e-10)


def model_xy(var):
    """A mesh variable's DOF coordinates in model units (layer depths), the coordinates
    the DM, evaluate and this driver's geometry work in."""
    return var.coords


def swarm_xy():
    """The particles' coordinates in model units (layer depths)."""
    return crust_swarm.coords


def wrap(angle):
    return (angle + np.pi) % (2 * np.pi) - np.pi


def fault_trace(fault, coarsening=1):
    """A fault's spine (from just above the outer wall to its tip) and the trace to cut
    (trace_inset() finest rungs inside the wall), at ``coarsening`` times the rung
    spacing: the fault's ``points``, a polyline already at the rung spacing with its
    surface end above the wall."""
    spine = np.asarray(fault["points"], dtype=float)[::coarsening]
    return spine, cut_of(spine)


def cut_of(spine):
    """The part of a spine to cut: the points trace_inset() rungs inside the wall, by depth, or with
    uw_split_inset_along by distance along the spine from its wall crossing, so the
    cut runs as close to the wall along the fault as the ladder does."""
    r = np.hypot(spine[:, 0], spine[:, 1])
    if not params.uw_split_inset_along or r[0] <= r_o:
        return spine[r <= r_o - trace_inset() * S]
    k = int(np.argmax(r < r_o))                     # the first point inside the wall (the spine starts above it)
    f = (r[k - 1] - r_o) / (r[k - 1] - r[k])        # the crossing on segment k-1 -> k
    cross = spine[k - 1] + f * (spine[k] - spine[k - 1])
    along = np.r_[np.zeros(k), np.linalg.norm(spine[k] - cross)
                  + np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(spine[k:], axis=0), axis=1))]]
    return spine[(np.arange(len(spine)) >= k) & (along >= trace_inset() * S - 1e-12)]


def trace_inset():
    """How many rungs inside the wall a trace stops: uw_split_inset (the cut cannot
    reach the wall; the isotropic bridge covers the rest)."""
    return float(params.uw_split_inset)


def placed_ladders(host, faults, coarsening):
    """Every fault's ladder band placed on ``host`` at ``coarsening`` times the rung
    spacing, each split along its own rungs. The fill-ring self-crossing check gives a
    false positive when a ring runs along mesh nodes collinear to round-off (the annulus
    has a line of them at theta = 0); a wider band or margin moves the ring off it."""
    pieces = [(f["name"],) + fault_trace(f, coarsening) for f in faults]
    width = W * coarsening if params.uw_band_widen else W
    # Every set places in serial; in parallel the "gather" seam handling can reach
    # the domain wall when several bands sit close together (measured: four bands
    # within 11 degrees on 7 ranks), so the ligament seams are the last resort.
    # The ligament seams need the network mesher (one CAD call for all the bands, spines
    # embedded), which also does without the gather. Its levels do not nest, so it is
    # the last resort.
    # (the network mesher with ligament seams DEADLOCKED in parallel on a four-band set,
    # 2026-10-18: one rank raised inside the CAD call, the others waited; not retried)
    seams = str(params.uw_fault_seams)      # "gather" (one rank carves a straddling band) or "conform" (2-D: the
                                             # band meshed through the partition seam, each rank its own side)
    # the ladder only takes "gather"; any other seam mode needs the network mesher (place_fault_ribbon_2d)
    mesher = "ladder" if seams == "gather" else "network"
    attempts = [(1, 0.7, 1.0, seams, mesher), (1, 0.7, 1.25, seams, mesher),
                (2, 0.7, 1.0, seams, mesher), (1, 0.7, 1.5, seams, mesher)]
    for n, (rings, clearance, widen, seams, mesher) in enumerate(attempts):
        try:
            mesh, info = place_fault_ribbon_2d(
                host, [(name, trace) for name, _, trace in pieces], width * widen,
                spines=[(name, spine) for name, spine, _ in pieces], margin_rings=rings,
                clearance=clearance, split=True, mesher=mesher, seams=seams)
            if n:
                uw.pprint(f"  placed with margin_rings {rings}, clearance {clearance}, width x{widen}, "
                          f"seams {seams}, mesher {mesher}")
            return mesh, info, {name: (spine, trace) for name, spine, trace in pieces}
        except (RuntimeError, ValueError) as err:
            # "touches the domain boundary" (fault_split) and "meshed to area ... against CAD" (the ribbon assembly)
            # are job 4400's two refusals (earth_recipe_movie's first try, steps 107 and 81): a wider band places both
            retryable = any(s in str(err) for s in ("crosses itself", "domain wall", "ligament", "seam",
                                                    "touches the domain boundary", "meshed to area"))
            if not retryable or n == len(attempts) - 1:
                raise RuntimeError(str(err))


def fault_depth_cap():
    """The deepest a fault may reach: uw_fault_depth_max."""
    return float(params.uw_fault_depth_max)


def segment_distance(points, a, b):
    ab = b - a
    s = np.clip(((points - a) @ ab) / max(ab @ ab, 1e-30), 0.0, 1.0)
    return np.linalg.norm(points - (a + s[:, None] * ab), axis=1)


def _num(x, kind=float):
    return None if x is None else kind(x)


def nonlinear_record(info):
    """One nonlinear solve's numbers from the rotated loop's info dict. fnorm_rest, ref,
    rnorm_history and line_search_alpha come with a library addition and are None before."""
    its = _num(info.get("nonlinear_iterations"), int)
    switch = _num(info.get("continuation_switch_iteration"), int)
    picard = switch if switch is not None else its
    F0, F_rest, F_final = _num(info.get("rnorm0")), _num(info.get("fnorm_rest")), _num(info.get("rnorm"))
    F_ref = _num(info.get("ref"))
    if F_ref is None and F_rest is not None and F0 is not None:
        F_ref = max(F0, F_rest)
    alpha = info.get("line_search_alpha")
    alpha = None if alpha is None else [float(a) for a in alpha]
    history = info.get("rnorm_history")
    return {"F0": F0, "F_rest": F_rest, "F_ref": F_ref, "F_final": F_final,
            "rel_final": F_final / F_ref if F_final is not None and F_ref else None,
            "converged": bool(info.get("converged")), "nonlinear_its": its, "picard_its": picard,
            "switch_iteration": switch,
            "newton_its": its - picard if its is not None and picard is not None else None,
            "F_history": None if history is None else [float(r) for r in history],
            "line_search_alpha": alpha,
            "line_search_cutbacks": None if alpha is None else sum(a < 1.0 for a in alpha)}


def solver_record(info, attempts, start, caught, wall):
    """The step's "solver" sub-record: the nonlinear numbers summed over the attempts (the
    first attempt's F0, the kept attempt's final state: the cold retry's unless the warm one ended
    closer, -uw_retry_keep), the kept attempt's linear solves, the preconditioner fallbacks among
    the warnings caught, and the solve's wall times."""
    kept = next((a for a in attempts if a.get("kept")), attempts[-1])
    rec = dict(kept)
    rec["kept"] = None if len(attempts) == 1 else ("warm" if kept is attempts[0] else "cold")
    rec["F0"] = attempts[0]["F0"]
    for key in ("nonlinear_its", "picard_its", "newton_its", "line_search_cutbacks"):
        values = [a[key] for a in attempts]
        rec[key] = None if any(v is None for v in values) else sum(values)
    if len(attempts) > 1:
        rec["switch_iteration"] = None if attempts[-1]["switch_iteration"] is None else \
            attempts[0]["nonlinear_its"] + attempts[-1]["switch_iteration"]

    def ints(x):
        if x is None:
            return None
        return [int(v) for v in x] if np.ndim(x) else int(x)

    def summary(x):
        x = [] if x is None else list(np.atleast_1d(x))
        return (float(np.mean(x)), int(np.max(x))) if x else (None, None)

    ksp, vel, pres = ints(info.get("ksp_its")), ints(info.get("vel_its_last")), ints(info.get("pres_its_last"))
    (om, ox), (vm, vx), (pm, px) = summary(ksp), summary(vel), summary(pres)
    keep = ("custom_mg", "fell back", "fallback", "default preconditioner")
    rec.update({
        "start": start, "cold_retry": len(attempts) > 1, "attempts": attempts,
        "ksp_its": ksp, "vel_its": vel, "pres_its": pres,
        "ksp_summary": {"outer_mean": om, "outer_max": ox, "vel_mean": vm, "vel_max": vx,
                        "pres_mean": pm, "pres_max": px},
        "velocity_pc": info.get("velocity_pc"), "velocity_pc_type": info.get("velocity_pc_type"),
        "schur_pre": info.get("schur_pre"),
        "operator_reused": bool(info.get("rotation_reused")) and bool(info.get("workspace_reused")),
        "pc_fallbacks": sorted({str(w.message)[:200] for w in caught
                                if any(k in str(w.message) for k in keep)}),
        "wall": {k: round(v, 3) for k, v in wall.items()}})
    return rec


def polyline_distance(points, poly):
    """The distance from each of ``points`` to the polyline ``poly``."""
    poly = np.asarray(poly, dtype=float)
    return np.min([segment_distance(points, poly[i], poly[i + 1]) for i in range(len(poly) - 1)], axis=0)


def polyline_gap(a, b):
    """The largest distance between two polylines, either way (Hausdorff)."""
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    return float(max(polyline_distance(a, b).max(), polyline_distance(b, a).max()))


def resample_polyline(poly, spacing, block):
    """``poly`` resampled by arc length at about ``spacing``, with a multiple of ``block``
    segments (the chain levels subsample by 2^k)."""
    poly = np.asarray(poly, dtype=float)
    s = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(poly, axis=0), axis=1))]
    n = block * max(1, int(round(s[-1] / (block * spacing))))
    t = np.linspace(0.0, s[-1], n + 1)
    return np.c_[np.interp(t, s, poly[:, 0]), np.interp(t, s, poly[:, 1])]


def division_record(spine, width):
    """The division a ladder was built on: its rung count, the rung length (mean, min, max) and the band width."""
    seg = np.linalg.norm(np.diff(np.asarray(spine, dtype=float), axis=0), axis=1)
    return {"rungs": int(len(seg) + 1), "rung_mean": float(seg.mean()), "rung_min": float(seg.min()),
            "rung_max": float(seg.max()), "width": float(width)}


def crust_spline_points(faults):
    """The fault on a smoothing spline through the crust's centre line, in arc length.
    In map coordinates (X = r_o theta about the trench hint, Y = -depth):
    marching from the incoming plate 0.35 outboard of the hint toward the trench in steps of
    0.005, each point re-centred on the median normal offset of the crust within +-0.005 along and
    +-3 thicknesses across, the direction the chord over the last 4 steps, down to the cap + 0.06;
    then the crust within 3 thicknesses of that line binned by arc length (0.005), the bin medians
    fitted with a smoothing spline in X(s) and Y(s) (lam = uw_spline_length^4 / 0.005, weights
    sqrt(count)). The fault is the curve from where it lies one crust thickness deeper than its
    level on the incoming plate (the trench) to the depth cap; above that point it runs to the
    wall along the curve's own tangent there, with a stub to 0.02 above the wall; resampled at the
    rung spacing. The fit sets no dip at the top (Louis, 2026-11-14: "the fit, at least should not
    enforce a steep continuation of the fault"): the run was the curve's mean slope over the next
    0.015 of depth, 1.3 to 1.5 times steeper than the curve where it starts. How shallow a fault the
    mesh can carry is the placement's to refuse; info["spline_top_dip"] records the run's dip.
    The curve may turn past vertical. Collective. Returns (points, theta, dip, depth,
    info) or None; tested offline on 12 stored checkpoints (scratchpad arcfit_centre,
    2026-11-12)."""
    from scipy.interpolate import make_smoothing_spline
    from scipy.spatial import cKDTree
    cap, ct, ds, band = fault_depth_cap(), crust_thick, 0.005, 3.0 * crust_thick
    xy = np.asarray(swarm_xy(), dtype=float)
    marker = np.asarray(crust_var.array[:, 0, 0]).ravel()
    keep = marker > 0.5
    P = np.c_[uw.utilities.gather_data(xy[keep, 0], bcast=True), uw.utilities.gather_data(xy[keep, 1], bcast=True)]
    depth = r_o - np.hypot(P[:, 0], P[:, 1])
    theta = np.arctan2(P[:, 1], P[:, 0])
    if faults:
        hint = float(faults[0]["theta"])
    else:                                            # the subducted cluster that goes deepest
        sub = (depth > 1.25 * ct) & (depth <= cap + 2 * ct)
        if sub.sum() < 12:
            return None
        o = np.argsort(theta[sub])
        pieces = np.split(o, np.flatnonzero(np.diff(theta[sub][o]) > 0.03) + 1)
        piece = max(pieces, key=lambda p: depth[sub][p].max())
        hint = float(theta[sub][piece][np.argmin(depth[sub][piece])])
    X0 = r_o * hint
    M = np.c_[r_o * (hint + wrap(theta - hint)), -depth]
    M = M[(np.abs(M[:, 0] - X0) < r_o * 0.4) & (depth < cap + 0.11)]
    dep = -M[:, 1]
    sh = dep < 0.5 * ct
    deep = (dep > 0.5 * cap) & (dep < cap + 2 * ct) & (np.abs(M[:, 0] - X0) < 0.3)
    if sh.sum() < 4 or deep.sum() < 12:
        uw.pprint("  crust fault (spline): no subducted crust below cap/2, or none at the wall")
        return None
    inc = 1.0 if np.median(M[sh, 0]) > np.median(M[deep, 0]) else -1.0
    left = lambda t: np.c_[-t[:, 1], t[:, 0]] if t.ndim == 2 else np.array([-t[1], t[0]])
    tree = cKDTree(M)
    pts, t, miss = [np.array([X0 + inc * 0.35, -0.5 * ct])], np.array([-inc, 0.0]), 0
    for _ in range(600):                             # the march along the layer's centre
        q = pts[-1] + ds * t
        idx = tree.query_ball_point(q, 0.02)
        if idx:
            rel = M[idx] - q
            a, n = rel @ t, rel @ left(t)
            m = (np.abs(a) < ds) & (np.abs(n) < band)
            if m.sum() >= 3:
                q, miss = q + np.median(n[m]) * left(t), -1
        miss += 1
        if miss > 6:
            break
        pts.append(q)
        if len(pts) >= 5:
            d = pts[-1] - pts[-5]
            t = d / np.linalg.norm(d)
        if -q[1] > cap + 0.06:
            break
    C = np.array(pts)
    reach = cap - 0.03
    if -C[-1, 1] < reach:                            # the slab's stretched crust thins out
        uw.pprint(f"  crust fault (spline): the march along the crust stopped at depth {-C[-1, 1]:.3f}")
        return None
    lam = float(params.uw_spline_length) ** 4 / ds
    side = str(params.uw_spline_side)
    if side not in ("centre", "base"):
        raise ValueError(f"-uw_spline_side must be centre or base, not {side!r}")
    # pass 1: bin medians about the marched line -> the centre line; with side "base", pass 2: about that centre
    # line, the quantile with 10 % of the band toward the plate interior beyond it (the layer's base)
    stats = ("median",) + (("base",) if side == "base" else ())
    for stat in stats:
        sc = np.r_[0, np.cumsum(np.linalg.norm(np.diff(C, axis=0), axis=1))]
        Cd = np.c_[np.interp(np.arange(0, sc[-1], 0.001), sc, C[:, 0]), np.interp(np.arange(0, sc[-1], 0.001), sc, C[:, 1])]
        s_d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(Cd, axis=0), axis=1))]
        tg = np.gradient(Cd, axis=0)
        tg /= np.linalg.norm(tg, axis=1)[:, None]
        _, k = cKDTree(Cd).query(M)
        rel = M - Cd[k]
        s_p, n_p = s_d[k] + (rel * tg[k]).sum(1), (rel * left(tg[k])).sum(1)
        inb = (np.abs(n_p) < band) & (s_p > s_d[0]) & (s_p < s_d[-1])
        b = np.digitize(s_p[inb], np.arange(s_d[0], s_d[-1] + ds, ds))
        ss, off, cnt = [], [], []
        for j in np.unique(b):
            v = n_p[inb][b == j]
            if len(v) >= 1:                          # weighted by sqrt(count): the slab's stretched crust is sparse
                ss.append(s_p[inb][b == j].mean())
                # + inc * left points into the plate interior (the march runs from the incoming plate to the slab)
                off.append(np.median(v) if stat == "median" else inc * np.quantile(inc * v, 0.9))
                cnt.append(len(v))
        ss, off, w = np.array(ss), np.array(off), np.sqrt(np.array(cnt, float))
        if len(ss) < 12:
            uw.pprint("  crust fault (spline): too few crust bins along the layer")
            return None
        Cs = np.c_[np.interp(ss, s_d, Cd[:, 0]), np.interp(ss, s_d, Cd[:, 1])]
        ts = np.c_[np.interp(ss, s_d, tg[:, 0]), np.interp(ss, s_d, tg[:, 1])]
        ts /= np.linalg.norm(ts, axis=1)[:, None]
        Z = Cs + off[:, None] * left(ts)
        w = w / w.mean()
        sx = make_smoothing_spline(ss, Z[:, 0], w=w, lam=lam)
        sy = make_smoothing_spline(ss, Z[:, 1], w=w, lam=lam)
        sf = np.arange(ss[0], ss[-1], 0.0005)
        F = np.c_[sx(sf), sy(sf)]
        C = F                                        # the next pass's reference
    fd = -F[:, 1]
    sF = np.r_[0, np.cumsum(np.linalg.norm(np.diff(F, axis=0), axis=1))]
    flat = (sF > 0.02) & (sF < 0.15)
    z_flat = float(np.median(fd[flat])) if flat.any() else 0.5 * ct
    kd = int(np.argmax(fd > 0.05))
    above = np.flatnonzero(fd[:kd] <= z_flat + ct)
    kt = int(above[-1]) + 1 if len(above) else 0
    if fd.max() < cap - 0.03:
        uw.pprint(f"  crust fault (spline): the curve reaches only {fd.max():.3f}, short of the cap less 0.03")
        return None
    elif not (fd[kt:] >= cap).any():
        # within 0.03 of the cap (the starting slab's crust reaches ~0.142, and the subducted
        # crust's lattice stretches until a 0.01 of depth can hold no particle): the curve carried on to the cap
        # along its own direction over its last 0.01
        kd = int(np.argmax(fd))
        ke = int(np.argmax(sF >= sF[kd] - 0.01))
        e = F[kd] - F[ke]
        e = e / max(np.linalg.norm(e), 1e-12)
        if e[1] >= -1e-3:
            uw.pprint("  crust fault (spline): the curve's deep end does not descend")
            return None
        F = np.vstack([F[:kd + 1], F[kd] + np.outer(np.arange(0.0005, (cap - fd[kd]) / -e[1] + 0.001, 0.0005), e)])
        fd = -F[:, 1]
        uw.pprint(f"  crust fault (spline): the curve carried from {fd[kd]:.3f} to the cap along its own direction")
    kc = kt + int(np.argmax(fd[kt:] >= cap)) if (fd[kt:] >= cap).any() else len(F) - 1
    seg = F[kt:kc + 1]
    d = seg[1] - seg[0]                              # the run to the wall: the curve's own tangent at its top
    d = d / np.linalg.norm(d)
    if d[1] >= 0:
        uw.pprint("  crust fault (spline): the curve does not descend where it leaves the incoming plate")
        return None
    top_dip = float(np.degrees(np.arctan2(-d[1], abs(d[0]))))
    to_wall = -seg[0, 1] / max(-d[1], 1e-6)
    wall = seg[0] - to_wall * d
    pol = np.vstack([wall - (0.02 / max(-d[1], 1e-6)) * d, wall, seg])   # (X, Y = -depth)
    radius = r_o + pol[:, 1]
    poly = resample_polyline(np.c_[radius * np.cos(pol[:, 0] / r_o), radius * np.sin(pol[:, 0] / r_o)],
                             S, 1)
    rp = np.hypot(poly[:, 0], poly[:, 1])
    k = int(np.argmax(rp <= r_o))
    wk = (rp[k - 1] - r_o) / max(rp[k - 1] - rp[k], 1e-12)
    at_wall = poly[k - 1] + wk * (poly[k] - poly[k - 1])
    theta_t = float(np.arctan2(at_wall[1], at_wall[0]))
    below = poly[np.argmin(np.abs(r_o - rp - 0.03))]
    r_hat = at_wall / np.linalg.norm(at_wall)
    t_hat = np.array([-r_hat[1], r_hat[0]])
    down = (below - at_wall) / max(np.linalg.norm(below - at_wall), 1e-12)
    dip = float(np.degrees(np.arctan2(-down @ r_hat, down @ t_hat)))
    info = {"locator": "spline", "spline_trench_depth": float(-seg[0, 1]), "spline_flat_depth": z_flat,
            "spline_run_to_wall": float(to_wall), "spline_top_dip": top_dip, "spline_end": "cap", "spline_end_depth": float(-seg[-1, 1]), "raw": np.c_[pol[:, 0] / r_o, -pol[:, 1]][::4].round(6).tolist()}
    uw.pprint(f"  crust fault (spline): trench {np.degrees(theta_t):.2f} deg, dip {dip:.1f}, "
              f"leaves the incoming plate at depth {-seg[0, 1]:.4f}, run to the wall {to_wall:.4f} dipping {top_dip:.1f}")
    return poly, theta_t, dip, float((r_o - rp).max()), info


class FaultedMesh:
    """All the faults placed into a copy of the base's finest level, with the Stokes
    solver, the bridge zones and the P1 fields the renders read."""

    def __init__(self, faults, tag):
        wall = time.perf_counter()
        self.faults = [dict(f) for f in faults]
        self.names = [f["name"] for f in self.faults]
        if self.faults:
            self.levels = levels
            self.mesh, info, self.pieces = placed_ladders(base, self.faults, 1)
            band = np.asarray(info["band"], dtype=bool)
            self.width = float(info["width"])
        else:                  # no fault: the base mesh is the solver's mesh
            self.levels, self.mesh, self.pieces = levels[:-1], base, {}
            band = None
            self.width = W
        mesh = self.mesh
        self.T = uw.discretisation.MeshVariable(f"T_{tag}", mesh, 1, degree=2)
        self.v = uw.discretisation.MeshVariable(f"V_{tag}", mesh, mesh.dim, degree=2)
        self.p = uw.discretisation.MeshVariable(f"P_{tag}", mesh, 1, degree=1, continuous=True)
        self.zone = uw.discretisation.MeshVariable(f"zone_{tag}", mesh, 1, degree=0, continuous=False)
        self.log_eta = uw.discretisation.MeshVariable(f"log10_eta_{tag}", mesh, 1, degree=1)
        self.yield_ratio = uw.discretisation.MeshVariable(f"yield_ratio_{tag}", mesh, 1, degree=1)
        self.gamma = uw.discretisation.MeshVariable(f"plastic_strain_{tag}", mesh, 1, degree=2)
        self.edot_p = uw.discretisation.MeshVariable(f"edot_plastic_{tag}", mesh, 1, degree=1)
        # the crust marker on this mesh (DG1, filled from the particles' proxy at each solve)
        self.crust = (uw.discretisation.MeshVariable(f"crust_{tag}", mesh, 1, degree=1, continuous=False)
                      if crust_on else None)
        self.over = (uw.discretisation.MeshVariable(f"over_{tag}", mesh, 1, degree=1, continuous=False)
                     if over_on else None)
        # Each fault's bridge: its band cells outside its split's upper tip.
        centroids = np.asarray(model_xy(self.zone))
        radius = np.hypot(centroids[:, 0], centroids[:, 1])
        bridge = np.zeros(len(centroids), dtype=bool)
        if band is None:
            band = bridge
        for name, (spine, trace) in self.pieces.items():
            near = polyline_distance(centroids, spine) < 2.0 * W
            bridge |= band & near & (radius > np.hypot(*trace[0]) - 0.5 * W)
        self.zone.array[:, 0, 0] = bridge.astype(float)
        # the fault's band (uw_fault_precedence): every band cell, the zone included, where the
        # fault's own rheology alone applies
        self.band_mask = None
        if params.uw_fault_precedence:
            self.band_mask = uw.discretisation.MeshVariable(f"band_{tag}", mesh, 1, degree=0, continuous=False)
            self.band_mask.array[:, 0, 0] = (band | bridge).astype(float)

        s = uw.systems.Stokes(mesh, velocityField=self.v, pressureField=self.p)
        weak = 1 - (1 - params.uw_eta_w) * self.zone.sym[0]
        M = self.band_mask.sym[0] if self.band_mask is not None else 0
        if crust_on:
            weak = weak * crust_factor_on(mesh, self.crust.sym[0], mask=M)
        yield_factor = params.uw_yield_boost * (1 - (1 - params.uw_weak_min) * sympy.Min(
            self.gamma.sym[0] / params.uw_strain_crit, 1))
        if over_on:
            weak = weak * comp_factor_on(self.over.sym[0], params.uw_over_eta, mask=M,
                                         window=marker_rheo_window(mesh))
        asth = ((params.uw_asth, params.uw_asth_top, params.uw_asth_bottom, params.uw_asth_ramp)
                if params.uw_asth < 1 else None)
        self.eta_T = set_viscoplastic(s, self.T.sym[0], deta, tau0, tau1, params.uw_yield_softness,
                                      r_o, weak, yield_factor, asthenosphere=asth,
                                      lower_mantle=((params.uw_lm_eta, params.uw_lm_depth, params.uw_lm_ramp)
                                                    if params.uw_lm_eta != 1 else None),
                                      arrhenius=ARRHENIUS)
        if params.uw_eta_reg > 0:
            s.constitutive_model.Parameters.plastic_rate_strengthening = params.uw_eta_reg
        self.host_cm = s.constitutive_model
        buoyancy = params.uw_buoy_T * self.T.sym[0]
        if over_on:
            buoyancy = buoyancy - params.uw_over_dT * clamp01(self.over.sym[0])
        s.bodyforce = Ra * buoyancy * mesh.CoordinateSystem.unit_e_0
        free_slip_walls(s, params.uw_wall_normal)
        for name in self.names:
            # on a curved or kinked trace the per-node normals partly lock a frictionless contact (box
            # probe: one face carries shear, the normal traction jumps); "trace" smooths them
            s.add_fault_bc(0, boundary=name, **({"normal": "trace"} if params.uw_fault_normal == "trace" else {}))
        s.tolerance = params.uw_tol
        if params.uw_pres_rtol > 0:
            s._rotated_pres_rtol = float(params.uw_pres_rtol)
            s.petsc_options["fieldsplit_pressure_ksp_rtol"] = float(params.uw_pres_rtol)
        self.pres_rtol_now = None
        s.consistent_jacobian = "continuation"
        s.newton_switch_rtol = params.uw_newton_switch
        set_custom_fmg(s, self.levels, field_id=0, fac_zone=None)
        self.stokes = s
        self.has_guess = False

        eta_eff = s.constitutive_model.viscosity
        self.eta_projection = uw.systems.Projection(mesh, self.log_eta)
        self.eta_projection.uw_function = sympy.log(eta_eff) / sympy.log(10)
        self.ratio_projection = uw.systems.Projection(mesh, self.yield_ratio)
        self.ratio_projection.uw_function = eta_eff / self.eta_T
        cm = self.host_cm      # the viscoplastic host: its strain-rate invariant
        self.edot_projection = uw.systems.Projection(mesh, self.edot_p)
        self.edot_projection.uw_function = cm._strainrate_inv_II * sympy.Max(
            0, 1 - eta_eff / (self.eta_T * weak))
        self.diagnostics = AnnulusDiagnostics(T_b, self.v, eta_eff, self.eta_T, heating)
        self.t_build = time.perf_counter() - wall
        level_cells = [int(uw.utilities.gather_data(m.dm.getHeightStratum(0)[1], bcast=True).sum())
                       for m in self.levels + [mesh]]
        band_per_rank = [int(c) for c in uw.utilities.gather_data(
            int(band.sum()) if band is not None else 0, bcast=True)]
        band_cells = int(sum(band_per_rank))
        # for the solver record of the step that solves on this mesh
        self.mesh_record = {"levels_cells": level_cells,
                            "band_cells_fraction": band_cells / max(level_cells[-1], 1),
                            "split_pairs": None, "chain_welded": [],
                            "realisation": "split", "width": self.width,
                            # where the fault lives: with seams "gather" every band sits on one rank, so its FAC
                            # patch solve is serial there (kaiju, 2026-11-01)
                            "seams": str(params.uw_fault_seams), "partition": FAULT_PARTITION,
                            "band_cells_per_rank": band_per_rank,
                            "band_ranks": sum(1 for c in band_per_rank if c),
                            # the division each ladder was built on (Louis, 2026-11-04: "the ladder is built from the
                            # fault points and we can see if that is sufficient"): rungs, rung length, band width
                            "division": {name: division_record(spine, self.width)
                                         for name, (spine, _) in self.pieces.items()}}
        described = ", ".join(f"{f['name']} {np.degrees(f['theta']):.2f} deg / dip {f['dip']:.1f} / "
                              f"depth {f['depth']:.3f}" for f in self.faults) or "no fault"
        uw.pprint(f"faulted mesh {tag}: {described}; levels (cells) {level_cells}, "
                  f"built in {self.t_build:.1f} s; band on {self.mesh_record['band_ranks']} rank(s), seams "
                  f"{params.uw_fault_seams} ({FAULT_PARTITION})")
        for name, d in self.mesh_record["division"].items():
            uw.pprint(f"  {name} division: {d['rungs']} rungs, {d['rung_min']:.4f}-{d['rung_max']:.4f} (mean "
                      f"{d['rung_mean']:.4f}); W {d['width']:.4f}")

    def split_nudges(self, var):
        """Offsets that put each split copy of ``var``'s DOFs on its own side of its
        fault (Plus at -n, Minus at +n, 0.1 rungs), so an evaluation on a faulted source
        takes each side's own slip."""
        nudge = np.zeros((var.array.shape[0], 2))
        _, sub = self.mesh.dm.createSubDM(var.field_id)
        sec = sub.getLocalSection()
        width = var.num_components
        for name in self.names:
            pairs = _fault_pair_nodes_on(self.mesh, self.mesh.dm, self.mesh.dm.getLocalSection(),
                                         name, field=self.v.field_id)
            for q_plus, q_minus, n_hat in pairs:
                for q, sign in ((q_plus, -1.0), (q_minus, 1.0)):
                    if sec.getDof(q) > 0:
                        nudge[sec.getOffset(q) // width] = sign * 0.1 * S * np.asarray(n_hat)
        return nudge

    def warm_start(self, V, P=None):
        """Initial guess from velocity (and pressure) on another mesh, the split copies
        evaluated a hair inside their own side."""
        split_source = getattr(V.mesh, "_fault_point_pairs", None)

        def at(var, source, coords):
            points = np.asarray(coords, dtype=float)
            if split_source:
                points = points + self.split_nudges(var)
            return np.asarray(uw.function.global_evaluate(source.sym, onto(points)))

        self.v.array[:, 0, :] = at(self.v, V, model_xy(self.v)).reshape(-1, 2)
        if P is not None:
            self.p.array[:, 0, 0] = at(self.p, P, model_xy(self.p)).ravel()
        self.has_guess = True

    def _live_pres_ksp(self):
        """The live pressure sub-KSP of the rotated solve's cached KSP context, or None (no context yet, or not a
        fieldsplit context)."""
        cache = getattr(self.stokes, "_rotated_linear_cache", None) or {}
        ksp = (cache.get("ctx") or {}).get("ksp")
        if ksp is None:
            return None
        try:
            subs = ksp.getPC().getFieldSplitSubKSP()          # ("vel", "pres"): the pressure block is the second
            return subs[1] if len(subs) > 1 else None
        except Exception:
            return None

    def _set_pres_rtol(self, rtol):
        """The rotated solve's Schur (pressure) sub-KSP rtol for the next solve. The library reads
        solver._rotated_pres_rtol when it builds the KSP context and then reuses that context across solves
        (rotated_bc's cross-solve cache), so a change must also reach the live pressure sub-KSP."""
        if rtol is None or rtol <= 0 or rtol == self.pres_rtol_now:
            return
        self.stokes._rotated_pres_rtol = float(rtol)
        had_ctx = bool((getattr(self.stokes, "_rotated_linear_cache", None) or {}).get("ctx"))
        sub = self._live_pres_ksp()
        if sub is not None:
            sub.setTolerances(rtol=float(rtol))
        elif had_ctx and not getattr(self, "_pres_rtol_warned", False):
            uw.pprint(f"  warning: the live pressure sub-KSP was not reachable; the pressure rtol {rtol} applies "
                      f"only when the library rebuilds its KSP context (the solver record carries the rtol read back)")
            self._pres_rtol_warned = True
        self.pres_rtol_now = float(rtol)

    def _pres_rtol_applied(self):
        """The pressure rtol the last solve actually ran with, read back from the live sub-KSP; None if unreadable."""
        sub = self._live_pres_ksp()
        try:
            return float(sub.getTolerances()[0]) if sub is not None else None
        except Exception:
            return None

    def _stokes_solve(self, from_rest):
        # cold solves (from rest) take uw_pres_rtol_cold, warm ones uw_pres_rtol (2026-11-04)
        self._set_pres_rtol(PRES_RTOL_COLD if from_rest else PRES_RTOL_WARM)
        self.stokes.solve(zero_init_guess=from_rest, picard=params.uw_picard,
                          verbose=bool(params.uw_verbose))
        info = self.stokes._rotated_freeslip_info
        info["pres_rtol_used"] = self._pres_rtol_applied()      # read back, not the requested value (hub review)
        info["pres_rtol_requested"] = self.pres_rtol_now
        return info

    def solve(self):
        wall = time.perf_counter()
        self.T.array[:, 0, 0] = np.asarray(
            uw.function.global_evaluate(T_b.sym[0], onto(model_xy(self.T)))).ravel()
        self.gamma.array[:, 0, 0] = np.asarray(
            uw.function.global_evaluate(gamma_b.sym[0], onto(model_xy(self.gamma)))).ravel()
        for name, (var, _, _) in markers.items():
            mine = getattr(self, name, None)
            if mine is None:               # a passive marker (ocrust) has no picture on the faulted mesh
                continue
            mine.array[:, 0, 0] = np.asarray(
                uw.function.global_evaluate(var.sym[0], onto(model_xy(mine)))).ravel()
        t_transfer = time.perf_counter() - wall
        start = "cold" if not self.has_guess else "warm"
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            info = self._stokes_solve(from_rest=not self.has_guess)
            attempts = [dict(nonlinear_record(info), pres_rtol=info.get("pres_rtol_used"))]
            if not info.get("converged") and self.has_guess:
                uw.pprint("  the warm start did not converge: solving from rest")
                warm = (info, np.array(self.v.array), np.array(self.p.array))
                self.stokes.newton_switch_rtol = params.uw_newton_switch
                info = self._stokes_solve(from_rest=True)
                attempts.append(dict(nonlinear_record(info), pres_rtol=info.get("pres_rtol_used")))
                F_w, F_c = attempts[0]["F_final"], attempts[1]["F_final"]
                if (params.uw_retry_keep == "best" and not info.get("converged")
                        and F_w is not None and F_c is not None and F_w < F_c):
                    # the cold retry ended further from the answer: keep the warm iterate (TAti_smooth step
                    # 61, 2026-11-01: warm |F| 1.25e4 at rel 2.0e-2, cold 5.2e4 at rel 0.12, the cold kept)
                    info = warm[0]
                    self.v.array[...] = warm[1]
                    self.p.array[...] = warm[2]
                    self.stokes._rotated_freeslip_info = info
                    uw.pprint(f"  the cold retry ended worse (|F| {F_c:.3e} > {F_w:.3e}): the warm iterate kept")
                for a, kept in zip(attempts, (info is warm[0], info is not warm[0])):
                    a["kept"] = kept
        for w in caught:           # put the warnings back where they would have gone
            warnings.showwarning(w.message, w.category, w.filename, w.lineno)
        global FIRST_SOLVE
        if FIRST_SOLVE and start == "cold" and params.uw_restart < 0 and not info.get("converged"):
            # an unconverged cold first solve is not carried forward (2026-11-04: refinement 6's cold start stalled at
            # rel 0.77 and its vrms was 512.6 against the converged 430.9; the run went on from it silently)
            alpha = info.get("line_search_alpha") or []
            why = ("a linear-solve failure" if info.get("linear_failure") else
                   "the line-search stall (no step descended)" if alpha and alpha[-1] == 0.0 else
                   "the iteration cap or a step-norm stagnation")
            rel = (info.get("rnorm") or float("nan")) / (info.get("ref") or float("nan"))
            raise RuntimeError(
                f"the first solve of this fresh run did not converge: {why}, rel |F| {rel:.2e} after "
                f"{info.get('nonlinear_iterations')} iterations (line-search alpha {alpha}), pressure rtol "
                f"{info.get('pres_rtol_used')}. The run stops rather than step on from an unsolved initial flow; tighten "
                f"-uw_pres_rtol_cold, or see the solver record")
        FIRST_SOLVE = False
        self.stokes.newton_switch_rtol = params.uw_warm_newton_switch
        self.has_guess = True
        slips = {}
        for name in self.names:
            _, slip, _ = fault_slip(self.stokes, name, info)
            slips[name] = float(uw.utilities.gather_data(
                np.abs(slip).max() if len(slip) else 0.0, bcast=True).max())
        rec = solver_record(info, attempts, start, caught,
                            {"transfer": t_transfer, "stokes": time.perf_counter() - wall - t_transfer})
        if params.uw_wall_check:
            rec["wall_vn"] = self.wall_constraint()
        return {
            "newton": info.get("nonlinear_iterations"),
            "vel_its": info.get("vel_its_last"),
            "pres_its": info.get("pres_its_last"),
            "converged": bool(info.get("converged")),
            "slip": slips,
            "slip_max": max(slips.values()) if slips else 0.0,
            "solver": rec,
        }

    def wall_constraint(self):
        """The free-slip constraint as solved: the largest |v.n| over the velocity nodes on each wall (n radial: exact
        at a vertex, whose nodal normal is the measure-weighted mean of its two facets', and at a chord's midpoint),
        and how many node entries exceed 1e-8 of the largest |v| (a node shared between ranks counts on each). Kaiju, 2026-11-01: at np 32 a few wall nodes shared between
        ranks came out with v.n ~ |v| (the constraint row missing) while every other node held 1e-13; it showed only
        as a smaller dt. Collective."""
        xy = np.asarray(self.v.coords, dtype=float)
        v = np.asarray(self.v.array, dtype=float).reshape(-1, 2)
        r = np.hypot(xy[:, 0], xy[:, 1])
        vn = np.abs((v * xy).sum(1) / np.maximum(r, 1e-30))
        vmax = float(uw.utilities.gather_data(np.hypot(v[:, 0], v[:, 1]).max() if len(v) else 0.0, bcast=True).max())
        out = {"v_max": vmax}
        tol = 1e-4 * (r_o - r_i)                          # the faceted walls' mid-side nodes sit ~2e-5 inside
        for name, rw in (("inner", r_i), ("outer", r_o)):
            on = np.abs(r - rw) < tol
            m = float(uw.utilities.gather_data(vn[on].max() if on.any() else 0.0, bcast=True).max())
            n = int(uw.utilities.gather_data(int((vn[on] > 1e-8 * vmax).sum()), bcast=True).sum())
            out[name] = {"vn_max": m, "n_above": n}
        if out["inner"]["n_above"] or out["outer"]["n_above"]:
            uw.pprint(f"  WALL CONSTRAINT VIOLATED: |v.n| max inner {out['inner']['vn_max']:.3e} "
                      f"({out['inner']['n_above']} nodes), outer {out['outer']['vn_max']:.3e} "
                      f"({out['outer']['n_above']} nodes), |v| max {vmax:.3e}")
        return out

    def to_base(self):
        V_b.array[:, 0, :] = np.asarray(
            uw.function.global_evaluate(self.v.sym, onto(model_xy(V_b)))).reshape(-1, 2)
        self.edot_projection.solve()
        edot = np.asarray(uw.function.global_evaluate(
            self.edot_p.sym[0], onto(model_xy(edot_p_b)))).ravel()
        edot_p_b.array[:, 0, 0] = np.maximum(edot, 0.0)

    def render_fields_to_base(self):
        self.eta_projection.solve()
        self.ratio_projection.solve()
        log_eta_b.array[:, 0, 0] = np.asarray(
            uw.function.global_evaluate(self.log_eta.sym[0], onto(model_xy(log_eta_b)))).ravel()
        yield_ratio_b.array[:, 0, 0] = np.asarray(
            uw.function.global_evaluate(self.yield_ratio.sym[0], onto(model_xy(yield_ratio_b)))).ravel()


def plate_velocities(faults):
    """Tangential surface velocity (positive toward +theta) uw_advect_offset on each side
    of every trench, just inside the outer wall: {name: (v at -theta side, v at +theta
    side)}. Collective."""
    if not faults:
        return {}
    pts = []
    for f in faults:
        for sign in (-1.0, 1.0):
            th = f["theta"] + sign * params.uw_advect_offset / r_o
            pts.append([(r_o - 0.01) * np.cos(th), (r_o - 0.01) * np.sin(th)])
    pts = np.array(pts)
    v = np.asarray(uw.function.global_evaluate(V_b.sym, onto(pts))).reshape(-1, 2)
    th = np.arctan2(pts[:, 1], pts[:, 0])
    v_t = -v[:, 0] * np.sin(th) + v[:, 1] * np.cos(th)
    return {f["name"]: (float(v_t[2 * n]), float(v_t[2 * n + 1])) for n, f in enumerate(faults)}


def write_records(records):
    with uw.selective_ranks(0) as selected:
        if selected:
            with open(os.path.join(out, "records.json"), "w") as f:
                json.dump(records, f, indent=1)


def write_solver_fields(faulted, step):
    """The solver's (faulted, split) mesh and its V, P at checkpoint ``step``: the mesh by
    Mesh.write (it reloads exactly, split copies included: 33650 cells and 17313 vertices
    at np 16 and np 1), V and P as their values at their DOF coordinates nudged onto their
    own side of each fault (split_nudges), gathered to rank 0. A restart matches them to
    the rebuilt mesh's DOFs by position, on any rank count. Returns the file names."""
    import h5py
    files = {"mesh": f"annulus.solver_mesh.{step:05d}.h5"}
    faulted.mesh.write(os.path.join(out, files["mesh"]))
    for name, var in (("V", faulted.v), ("P", faulted.p)):
        values = var.array[:, 0, :]
        xy = uw.utilities.gather_data((np.asarray(model_xy(var)) + faulted.split_nudges(var)).ravel())
        vals = uw.utilities.gather_data(values.ravel())
        files[name] = f"annulus.solver_mesh.{name}.{step:05d}.h5"
        with uw.selective_ranks(0) as selected:
            if selected:
                with h5py.File(os.path.join(out, files[name]), "w") as h:
                    h["coords"] = np.asarray(xy).reshape(-1, 2)
                    h["values"] = np.asarray(vals).reshape(-1, values.shape[1])
    return files


def read_solver_fields(faulted, files):
    """Seed a faulted mesh from checkpointed V, P (write_solver_fields): each DOF takes the
    saved value at the nearest saved nudged coordinate. Returns the largest match distance
    over all ranks: zero when the rebuilt mesh is the checkpointed one."""
    import h5py
    from scipy.spatial import cKDTree
    worst = 0.0
    for name, var in (("V", faulted.v), ("P", faulted.p)):
        with h5py.File(os.path.join(out, files[name]), "r") as h:
            xy, values = h["coords"][...], h["values"][...]
        dist, idx = cKDTree(xy).query(np.asarray(model_xy(var)) + faulted.split_nudges(var))
        var.array[:, 0, :] = values[idx]
        worst = max(worst, float(dist.max()) if len(dist) else 0.0)
    faulted.has_guess = True
    return float(uw.utilities.gather_data(worst, bcast=True).max())


def checkpoint(step, t, records, faulted, faults, next_id, decisions):
    faulted.render_fields_to_base()
    mesh_vars = [V_b, T_b, log_eta_b, yield_ratio_b, gamma_b, edot_p_b]
    for var, picture, _ in markers.values():
        picture.array[:, 0, 0] = np.asarray(
            uw.function.global_evaluate(var.sym[0], onto(model_xy(picture)))).ravel()
        mesh_vars.append(picture)
    if swarm_on:
        crust_swarm.write_timestep("annulus", "crust_swarm", index=step,
                                   swarmVars=[m[0] for m in markers.values()], outputPath=out)
    base.write_timestep("annulus", index=step, outputPath=out, meshVars=mesh_vars)
    solver_files = write_solver_fields(faulted, step)
    # everything a restart from here reads: it refuses to start if any is missing
    needed = [f"annulus.mesh.{v.clean_name}.{step:05d}.h5" for v in (T_b, V_b, gamma_b)] + list(solver_files.values())
    if swarm_on:
        needed += [f"annulus.crust_swarm.{step:05d}.h5"] + [f"annulus.crust_swarm.{name}.{step:05d}.h5"
                                                          for name in markers]
    with uw.selective_ranks(0) as selected:
        if selected:
            with open(os.path.join(out, f"state_{step:05d}.json"), "w") as f:
                json.dump({"step": step, "t": t, "params": params.to_dict(), "faults": faults,
                           "next_id": next_id, "ridge_origin": theta_0, "ridges": ridges,
                           # the first fault, for the single-fault readers (renders)
                           "theta_trench": faults[0]["theta"] if faults else float(params.uw_theta_trench),
                           "dip": faults[0]["dip"] if faults else float(params.uw_dip),
                           "fault_depth": faults[0]["depth"] if faults else 0.0,
                           # the traces of the faults built into THIS checkpoint's mesh: a fault the
                           # step's detection just formed is not placed until the next step's rebuild
                           "traces": [faulted.pieces[f["name"]][1].tolist() for f in faulted.faults],
                           # what steers the next decisions (restored_decisions)
                           "decisions": dict(decisions, built=faulted.faults),
                           "solver_checkpoint": solver_files, "checkpoint_files": needed},
                          f, indent=1, default=str)
    write_records(records)


# ----------------------------------------------------------------------------- initial state
records = []
def slab_temperature(xy):
    """The prescribed state from an age line (see the parameters): interior at T_i, the
    surface plates by half-space cooling of the surface age, and the slab by half-space
    cooling of the age continued down the fault plane, into the subducting side only.
    T is the colder of the plate and the slab values. Any numpy array of points."""
    from scipy.special import erf, erfc
    xy = np.asarray(xy, dtype=float)
    r = np.hypot(xy[:, 0], xy[:, 1])
    theta = np.arctan2(xy[:, 1], xy[:, 0])
    depth = np.maximum(r_o - r, 0.0)
    theta_t, phi = float(params.uw_theta_trench), np.deg2rad(float(params.uw_dip))
    over = 1.0 if params.uw_dip < 90 else -1.0            # the overriding plate's side (+theta for a dip below 90)
    T_i = float(params.uw_T_interior)

    def half_space(dist, age):
        return T_i * erf(dist / (2.0 * np.sqrt(np.maximum(age, 1e-8))))

    # the surface age: a ramp from the ridge to the trench on each side, each plate measured from
    # the trench round to its own ridge (an overriding plate may reach past the antipode, to a
    # subducting plate's ridge near the trench: uw_ridge_over 2 pi - uw_ridge_sub)
    rel = over * wrap(theta - theta_t)                    # positive on the overriding side
    rel_o = np.mod(over * (theta - theta_t), 2 * np.pi)   # the angle into the overriding side, 0 to 2 pi
    rel_s = 2 * np.pi - rel_o                             # the angle into the subducting side
    ridge_o, ridge_s = abs(float(params.uw_ridge_over)), abs(float(params.uw_ridge_sub))
    age_thin = float(params.uw_age_thin)
    age_o = params.uw_age_over * np.clip(1 - rel_o / max(ridge_o, 1e-6), 0, 1)
    age_s = params.uw_age_sub * np.clip(1 - rel_s / max(ridge_s, 1e-6), 0, 1)
    if not params.uw_over_plate:                          # no overriding plate: the thin layer
        age_o = np.full_like(age_o, age_thin)
    elif params.uw_over_gap > 0:                          # the plate set back from the trench
        w = np.clip((rel_o * r_o - params.uw_over_gap) / max(params.uw_over_ramp, 1e-6), 0, 1)
        age_o = age_thin + (age_o - age_thin) * w
    if params.uw_cont_age > 0:                            # the continent: a uniform, old lid
        cont_end = float(params.uw_cont_extent) or ridge_o
        in_cont = (rel_o * r_o >= float(params.uw_over_gap)) & (rel_o < cont_end)
        age_o = np.where(in_cont, float(params.uw_cont_age), age_o)
    age_surface = np.maximum(np.where(rel_s <= ridge_s, age_s, age_o), age_thin)
    T_plate = half_space(depth, age_surface)
    if params.uw_top_hot:                                 # no cooling at all where the surface is held hot
        T_plate = np.maximum(T_plate, T_i * hot_top_window(rel * r_o))
    # the slab: the age line is the fault plane from the trench, down-dip to uw_slab_length
    r_hat = np.array([np.cos(theta_t), np.sin(theta_t)])
    t_hat = np.array([-np.sin(theta_t), np.cos(theta_t)])
    down = np.cos(phi) * t_hat - np.sin(phi) * r_hat
    n_sub = -np.sign(np.cos(phi)) * (np.sin(phi) * t_hat + np.cos(phi) * r_hat)   # into the subducting side
    a = r_hat * r_o
    rel_xy = xy - a
    s_raw = rel_xy @ down
    s_along = np.clip(s_raw, 0.0, params.uw_slab_length)
    n_into = rel_xy @ n_sub
    # one-sided along the plane: on the overriding side the slab does not cool the wedge;
    # beyond the tip the profile wraps round (a rounded end)
    # time since the slab's top left the overriding plate's base (cold against the plate above it)
    contact = float(params.uw_slab_contact)
    if contact < 0:
        contact = 2.0 * np.sqrt(float(params.uw_age_over)) if params.uw_over_plate else 0.0
    s_contact = contact / max(abs(np.sin(phi)), 0.1)
    tau = np.maximum(s_along - s_contact, 0.0) / max(float(params.uw_slab_rate), 1e-6)
    # cold top: T = 0 on the plane, the plate's half-space profile into the subducting
    # side (its age continued down-dip) and a short cooled halo into the wedge, so the
    # field is continuous across the plane; the profile fades beyond either end of the
    # segment over its own diffusion length, so the tip is rounded on both sides
    age_end = float(params.uw_age_sub) + tau
    overshoot = np.maximum(s_raw - params.uw_slab_length, 0.0) + np.maximum(-s_raw, 0.0)
    end_factor = erfc(overshoot / (2.0 * np.sqrt(age_end)))
    scale = np.where(n_into >= 0, 2.0 * np.sqrt(age_end), 2.0 * np.sqrt(float(params.uw_slab_wedge_age)))
    T_slab = T_i - T_i * end_factor * erfc(np.abs(n_into) / scale)
    return np.minimum(T_plate, T_slab)


def layer_marker(xy, thick):
    """1 in a layer ``thick`` thick of the slab state: at the subducting plate's surface
    (from its ridge to the trench) and down the slab's top face (the plane, into the
    subducting side) to the slab's end; the geometry of slab_temperature."""
    crust_thick = thick
    xy = np.asarray(xy, dtype=float)
    r = np.hypot(xy[:, 0], xy[:, 1])
    theta = np.arctan2(xy[:, 1], xy[:, 0])
    depth = np.maximum(r_o - r, 0.0)
    theta_t, phi = float(params.uw_theta_trench), np.deg2rad(float(params.uw_dip))
    over = 1.0 if params.uw_dip < 90 else -1.0
    rel = over * wrap(theta - theta_t)
    ridge_s = abs(float(params.uw_ridge_sub))
    plate = (rel < 0) & (np.abs(rel) < ridge_s) & (depth < crust_thick)
    r_hat = np.array([np.cos(theta_t), np.sin(theta_t)])
    t_hat = np.array([-np.sin(theta_t), np.cos(theta_t)])
    down = np.cos(phi) * t_hat - np.sin(phi) * r_hat
    n_sub = -np.sign(np.cos(phi)) * (np.sin(phi) * t_hat + np.cos(phi) * r_hat)
    rel_xy = xy - r_hat * r_o
    s_raw, n_into = rel_xy @ down, rel_xy @ n_sub
    slab = (s_raw >= 0) & (s_raw <= params.uw_slab_length - crust_thick) & (n_into >= 0) & (n_into < crust_thick)
    return (plate | slab).astype(float)


def over_marker(xy, thick):
    """1 in the compositional overriding plate of the slab state: a layer ``thick`` thick
    at the surface on the overriding side, from uw_over_gap (arc length) behind the trench
    to the overriding plate's ridge."""
    xy = np.asarray(xy, dtype=float)
    r = np.hypot(xy[:, 0], xy[:, 1])
    theta = np.arctan2(xy[:, 1], xy[:, 0])
    depth = np.maximum(r_o - r, 0.0)
    over = 1.0 if params.uw_dip < 90 else -1.0
    rel = over * wrap(theta - float(params.uw_theta_trench))
    ridge_o = float(params.uw_cont_extent) or abs(float(params.uw_ridge_over))
    plate = (rel * r_o >= float(params.uw_over_gap)) & (rel < ridge_o) & (depth < thick)
    return plate.astype(float)


def crust_spacing():
    """The lattice spacing of the dense crust: about uw_crust_ppc particles per (triangular) cell."""
    return H_B / np.sqrt(2.0 * float(params.uw_crust_ppc))


def crust_layer_points(spacing, surface_only=False):
    """A lattice at ``spacing`` through the slab state's crust layer: the subducting plate's
    surface layer (ridge to trench) and, unless ``surface_only``, the slab's top face, in the
    layer's own frame (along it and across it), kept where layer_marker says crust."""
    theta_t, phi = float(params.uw_theta_trench), np.deg2rad(float(params.uw_dip))
    over = 1.0 if params.uw_dip < 90 else -1.0
    ridge_s = abs(float(params.uw_ridge_sub))
    across = np.arange(0.5 * spacing, crust_thick, spacing)
    rel = -np.arange(0.5 * spacing / r_o, ridge_s, spacing / r_o)
    R, D = np.meshgrid(rel, across, indexing="ij")
    th, rad = theta_t + over * R.ravel(), r_o - D.ravel()
    pts = [np.c_[rad * np.cos(th), rad * np.sin(th)]]
    if not surface_only:
        r_hat = np.array([np.cos(theta_t), np.sin(theta_t)])
        t_hat = np.array([-np.sin(theta_t), np.cos(theta_t)])
        down = np.cos(phi) * t_hat - np.sin(phi) * r_hat
        n_sub = -np.sign(np.cos(phi)) * (np.sin(phi) * t_hat + np.cos(phi) * r_hat)
        sa = np.arange(0.5 * spacing, float(params.uw_slab_length) - crust_thick, spacing)
        Sg, Ng = np.meshgrid(sa, across, indexing="ij")
        pts.append(r_hat * r_o + Sg.ravel()[:, None] * down + Ng.ravel()[:, None] * n_sub)
    xy = onto(np.vstack(pts))
    return xy[layer_marker(xy, crust_thick) > 0.5]


def refill_crust():
    """Top up the crust on the subducting plate's surface: lattice points of the dense crust
    (uw_crust_ppc spacing) where the crust is (its proxy >= 0.5) and no crust particle on this
    rank lies within 0.75 spacing become crust particles; other markers from the nearest
    particle. Crust is never made where there was none, and the slab's (stretched) crust is
    left alone. Collective. Returns the particles added on this rank."""
    from scipy.spatial import cKDTree
    spacing = crust_spacing()
    cand = crust_layer_points(spacing, surface_only=True)
    is_crust = np.asarray(uw.function.global_evaluate(crust_var.sym[0], cand)).ravel() >= 0.5
    cand = cand[is_crust]
    xy = np.asarray(swarm_xy(), dtype=float).reshape(-1, 2)
    old = {name: np.array(var.array[:, 0, 0]) for name, (var, _, _) in markers.items()}
    mine = xy[old["crust"] > 0.5]
    if len(mine) and len(cand):
        cand = cand[cKDTree(mine).query(cand)[0] > 0.75 * spacing]
    added = crust_swarm.add_particles_with_coordinates(np.ascontiguousarray(cand)) if len(cand) else 0
    if added:
        new_xy = np.asarray(swarm_xy(), dtype=float).reshape(-1, 2)[-added:]
        nearest = cKDTree(xy).query(new_xy)[1] if len(xy) else None
        for name, (var, _, _) in markers.items():
            if name == "crust":
                var.array[-added:, 0, 0] = 1.0
            elif name == "ocrust":
                var.array[-added:, 0, 0] = 0.0
            elif nearest is not None:
                var.array[-added:, 0, 0] = old[name][nearest]
    for var, _, _ in markers.values():
        var._update()
    return int(added)


def ridge_crust_window(xy, faults):
    """True where uw_ridge_crust makes crust: on the subducting plate, past the edge of its
    ridge's hot patch (uw_top_hot 2: uw_ridge_patch from the ridge, which stays uw_ridge_sub
    behind uw_theta_trench; the ridge itself without a patch) and more than uw_ridge_crust_stop
    (arc) short of the trench as it is now."""
    theta = np.arctan2(xy[:, 1], xy[:, 0])
    over = 1.0 if params.uw_dip < 90 else -1.0
    from_ridge = r_o * (abs(float(params.uw_ridge_sub)) + over * wrap(theta - float(params.uw_theta_trench)))
    theta_t = float(faults[0]["theta"]) if faults else float(params.uw_theta_trench)
    to_trench = -r_o * over * wrap(theta - theta_t)
    patch = float(params.uw_ridge_patch) if int(params.uw_top_hot) == 2 else 0.0
    return (from_ridge > patch) & (to_trench > float(params.uw_ridge_crust_stop))


def ridge_crust(faults):
    """Crust on plate made at the ridge (uw_ridge_crust). refill_crust never makes crust where
    there was none, so plate that has left the ridge since the start carries none. Here lattice
    points of the dense crust (uw_crust_ppc spacing) in the subducting plate's surface layer,
    inside ridge_crust_window, with no crust particle on this rank within 0.75 spacing become
    crust particles, whatever the crust's proxy says there; the oceanic-crust line's surface
    points (uw_ocrust_depth, line_spacing()) the same way. Other markers from the nearest
    particle. Collective. Returns the particles added on this rank."""
    from scipy.spatial import cKDTree
    targets = [("crust", crust_layer_points(crust_spacing(), surface_only=True), crust_spacing())]
    if ocrust_on:
        targets.append(("ocrust", line_points(params.uw_ocrust_depth, surface_only=True), line_spacing()))
    total = 0
    for target, cand, spacing in targets:
        cand = cand[ridge_crust_window(cand, faults)]
        xy = np.asarray(swarm_xy(), dtype=float).reshape(-1, 2)
        old = {name: np.array(var.array[:, 0, 0]) for name, (var, _, _) in markers.items()}
        mine = xy[old[target] > 0.5]
        if len(mine) and len(cand):
            cand = cand[cKDTree(mine).query(cand)[0] > 0.75 * spacing]
        added = crust_swarm.add_particles_with_coordinates(np.ascontiguousarray(cand)) if len(cand) else 0
        if added:
            new_xy = np.asarray(swarm_xy(), dtype=float).reshape(-1, 2)[-added:]
            nearest = cKDTree(xy).query(new_xy)[1] if len(xy) else None
            for name, (var, _, _) in markers.items():
                if name == target:
                    var.array[-added:, 0, 0] = 1.0
                elif name in ("crust", "ocrust"):
                    var.array[-added:, 0, 0] = 0.0
                elif nearest is not None:
                    var.array[-added:, 0, 0] = old[name][nearest]
        for var, _, _ in markers.values():
            var._update()
        total += int(added)
    return total


def line_spacing():
    return float(params.uw_crust_line_spacing) or 0.25 * S


def line_points(depth, surface_only=False):
    """The oceanic-crust line of the slab state: ``depth`` under the subducting plate's surface
    from the trench back to its ridge, and, unless ``surface_only``, ``depth`` into the
    subducting side of the slab's top face from the trench to the slab's end, every
    line_spacing()."""
    theta_t, phi = float(params.uw_theta_trench), np.deg2rad(float(params.uw_dip))
    over = 1.0 if params.uw_dip < 90 else -1.0
    d, sp = float(depth), line_spacing()
    rel = -np.arange(0.5 * sp / r_o, abs(float(params.uw_ridge_sub)), sp / r_o)
    th = theta_t + over * rel
    surface = np.c_[(r_o - d) * np.cos(th), (r_o - d) * np.sin(th)]
    if surface_only:
        return onto(surface)
    r_hat = np.array([np.cos(theta_t), np.sin(theta_t)])
    t_hat = np.array([-np.sin(theta_t), np.cos(theta_t)])
    down = np.cos(phi) * t_hat - np.sin(phi) * r_hat
    n_sub = -np.sign(np.cos(phi)) * (np.sin(phi) * t_hat + np.cos(phi) * r_hat)
    sa = np.arange(0.5 * sp, float(params.uw_slab_length), sp)
    face = r_hat * r_o + sa[:, None] * down + d * n_sub
    face = face[np.hypot(face[:, 0], face[:, 1]) < r_o - d]   # below the surface part, which already covers the trench
    return onto(np.vstack([surface, face]))


def refill_line(faults, target, line_d):
    """Fill the gaps of a particle line: the line of marker ``target`` (the oceanic-crust line,
    "ocrust"), ``line_d`` deep, which stretches over the ridge and down the slab, and bunches
    harmlessly at the trench: bunching along a line does not move it. The
    line's particles are gathered to every rank and chained from the incoming plate's ridge end
    (the surface particle farthest from the trench on the subducting side): each step goes to the
    nearest unvisited particle within 0.05, so the chain stops at a gap wider than that. Where
    two neighbours on the chain are more than 1.5 spacings apart, evenly spaced points are put
    between them, down to the depth cap plus 0.05; every rank passes the same points and keeps
    its own (add_particles_with_coordinates). Other markers from the nearest particle; a
    new particle is that line's, not the crust's. Collective. Returns the particles added on
    this rank."""
    from scipy.spatial import cKDTree
    sp = line_spacing()
    line_d = float(line_d)
    xy = np.asarray(swarm_xy(), dtype=float).reshape(-1, 2)
    old = {name: np.array(var.array[:, 0, 0]) for name, (var, _, _) in markers.items()}
    mine = xy[old[target] > 0.5]
    P = np.c_[uw.utilities.gather_data(mine[:, 0], bcast=True), uw.utilities.gather_data(mine[:, 1], bcast=True)]
    cand = np.zeros((0, 2))
    if len(P) > 2:
        depth = r_o - np.hypot(P[:, 0], P[:, 1])
        theta = np.arctan2(P[:, 1], P[:, 0])
        theta_t = float(faults[0]["theta"]) if faults else float(params.uw_theta_trench)
        over = 1.0 if params.uw_dip < 90 else -1.0
        rel = over * wrap(theta - theta_t)
        shallow = np.flatnonzero(depth < 2.0 * line_d)
        start = int(shallow[np.argmin(rel[shallow])]) if len(shallow) else int(np.argmin(rel))
        tree = cKDTree(P)
        seen = np.zeros(len(P), dtype=bool)
        chain, cur = [start], start
        seen[start] = True
        limit = fault_depth_cap() + 0.05
        while True:
            dist, idx = tree.query(P[cur], k=min(16, len(P)), distance_upper_bound=0.05)
            nxt = [int(j) for dd, j in zip(np.atleast_1d(dist), np.atleast_1d(idx))
                   if np.isfinite(dd) and j < len(P) and not seen[j]]
            if not nxt:
                break
            cur = nxt[0]
            seen[cur] = True
            chain.append(cur)
            if depth[cur] > limit:
                break
        C = P[chain]
        gaps = np.linalg.norm(np.diff(C, axis=0), axis=1)
        fill = []
        for a, b, g in zip(C[:-1], C[1:], gaps):
            if g > 1.5 * sp:
                n = int(np.floor(g / sp))
                fill.append(a + np.outer(np.arange(1, n) / n, b - a))
        if fill:
            cand = onto(np.vstack(fill))
    added = crust_swarm.add_particles_with_coordinates(np.ascontiguousarray(cand)) if len(cand) else 0
    if added:
        new_xy = np.asarray(swarm_xy(), dtype=float).reshape(-1, 2)[-added:]
        nearest = cKDTree(xy).query(new_xy)[1] if len(xy) else None
        for name, (var, _, _) in markers.items():
            if name == target:
                var.array[-added:, 0, 0] = 1.0
            elif name in ("crust", "ocrust"):
                var.array[-added:, 0, 0] = 0.0
            elif nearest is not None:
                var.array[-added:, 0, 0] = old[name][nearest]
    for var, _, _ in markers.values():
        var._update()
    return int(added)


# The particles are moved with the faulted mesh's own velocity (the solver's, with the jump across the split), not the
# base mesh's, which carries the slip as a band a cell wide, so particles at the fault drift across it into the
# hanging wall (Louis, 2026-11-10: "we advect with the proper (split) velocity")
def advect_split(faulted_mesh, dt):
    """Move the particles one step with the faulted mesh's velocity: the RK2 midpoint step of
    Swarm.advection (global evaluations, so a particle anywhere is sampled on the rank owning
    its point of the faulted mesh, which is partitioned unlike the base), with positions kept in
    the annulus. Swarm.advection itself cannot take the faulted mesh's velocity: its time-step
    estimate evaluates the velocity locally on the swarm's (base) partition. A point in a band
    cell takes the velocity of its own side of the split. Collective."""
    x0 = np.array(crust_swarm._particle_coordinates.data, dtype=float).reshape(-1, 2)
    v1 = np.asarray(uw.function.global_evaluate(faulted_mesh.v.sym, onto(x0))).reshape(-1, 2)
    xm = onto(x0 + 0.5 * dt * v1)
    v2 = np.asarray(uw.function.global_evaluate(faulted_mesh.v.sym, xm)).reshape(-1, 2)
    crust_swarm._particle_coordinates.data[...] = onto(x0 + dt * v2)
    crust_swarm.migrate(delete_lost_points=True)


def seed_swarm():
    """Fresh particles over the base mesh with the slab state's markers; with uw_crust_ppc the
    crust layer gets its own denser lattice on top of the swarm's fill."""
    crust_swarm.populate(fill_param=int(params.uw_crust_fill))
    if crust_on and params.uw_crust_ppc > 0:
        crust_swarm.add_particles_with_coordinates(np.ascontiguousarray(crust_layer_points(crust_spacing())))
    n_oc = (crust_swarm.add_particles_with_coordinates(np.ascontiguousarray(line_points(params.uw_ocrust_depth)))
            if ocrust_on else 0)
    for name, (var, _, geometry) in markers.items():
        var.array[:, 0, 0] = geometry(swarm_xy())
        if name == "ocrust" and n_oc:
            var.array[-n_oc:, 0, 0] = 1.0
        var._update()


def restore_swarm(path, index):
    """The particles of checkpoint ``index`` in ``path``; a checkpoint without particles
    (an older run) gets fresh ones, and a marker the checkpoint lacks is seeded from the
    slab state's geometry on the saved particles."""
    if not os.path.exists(os.path.join(path, f"annulus.crust_swarm.{index:05d}.h5")):
        seed_swarm()
        return
    crust_swarm.read_timestep("annulus", "crust_swarm", index, outputPath=path)
    for name, (var, _, geometry) in markers.items():
        if os.path.exists(os.path.join(path, f"annulus.crust_swarm.{name}.{index:05d}.h5")):
            var.read_timestep("annulus", "crust_swarm", name, index, outputPath=path)
        else:
            var.array[:, 0, 0] = geometry(swarm_xy())
        var._update()


if params.uw_restart < 0:      # the slab state; a restart reads its checkpoint
    T_b.array[:, 0, 0] = slab_temperature(model_xy(T_b))
    V_b.array[:, 0, :] = 0.0
    if swarm_on:
        seed_swarm()
    state = {"t": 0.0, "step": -1}
    faults = []
    next_id = 0
else:
    with open(os.path.join(out, f"state_{params.uw_restart:05d}.json")) as f:
        state = json.load(f)
    missing = [name for name in state.get("checkpoint_files", []) if not os.path.exists(os.path.join(out, name))]
    if missing:
        raise FileNotFoundError(f"checkpoint {params.uw_restart} in {out} lists files that are missing: {missing}")
    for var in (T_b, V_b, gamma_b):
        var.read_timestep("annulus", var.name, params.uw_restart, outputPath=out)
    if swarm_on:
        restore_swarm(out, params.uw_restart)
    with open(os.path.join(out, "records.json")) as f:
        records = [r for r in json.load(f) if r["step"] <= params.uw_restart]
    faults, next_id = state["faults"], int(state["next_id"])
t, step = float(state["t"]), int(state["step"]) + 1
# no ridge seam is imposed: the state keeps the two fields its readers know
theta_0, ridges = float(faults[0]["theta"] if faults else params.uw_theta_trench), []


def restored_decisions(state, records, faults):
    """What steers the fault decisions, as the checkpoint at ``state`` left it: the loop
    counter of the next step (the detection cadence, uw_detect_start and the clearing of
    the refused set run on it), the rebuild count, the refused formation trenches, each
    fault's damage at the last detection, and the faults the mesh was built with (not yet
    the current ones when a fault has moved less than a rebuild; needs_rebuild compares
    against them). A checkpoint from before these were saved: the cadence from the last
    detection in the records (a detection step records its damage), the rebuild count
    and the damage from the records, nothing refused, the mesh built at the faults."""
    saved = state.get("decisions")
    if saved is not None:
        return (int(saved["k"]), int(saved["n_built"]), {n: float(v) for n, v in saved["refused"].items()},
                dict(saved["last_damage"]), saved["built"])
    detections = [r for r in records if r.get("damage")]
    k0 = 0
    if detections:
        k0 = int(params.uw_detect_start) + (int(state["step"]) + 1 - int(detections[-1]["step"])) \
            % int(params.uw_detect_every)
    n_built = int(records[-1].get("n_built", 1)) if records else 1
    return k0, n_built, {}, dict(detections[-1]["damage"]) if detections else {}, faults


k0 = 0                         # the loop counter of the first step
n_built = 1
refused = {}                   # with uw_placement_refused keep: the trench of each fault the placement refused
last_damage = {}               # how far each fault's polyline moved at the last detection (the records' "damage")
built = faults
if params.uw_restart >= 0:
    k0, n_built, refused, last_damage, built = restored_decisions(state, records, faults)
    # the restart rule (2026-11-02): a crust-law fault's stored polyline is at the rung spacing of the run that wrote
    # it, and every build places its ladder on those points, so a restart at a different -uw_spacing re-samples them
    # at this run's S before the first build (otherwise the old rungs last until the next re-fit). An unchanged S
    # leaves them alone, so restarts of existing runs stay bit-identical. -uw_resample_restored force|never: tests.
    S_saved = effective_spacing(state.get("params") or {}) if (state.get("params") or {}) else S
    mode = str(params.uw_resample_restored)
    if mode == "force" or (mode == "auto" and abs(S_saved - S) > 1e-9 * S):
        n_resampled = 0
        for f in [*faults, *(built if built is not faults else [])]:
            if "points" in f:
                f["points"] = resample_polyline(np.asarray(f["points"], dtype=float), S,
                                                1).tolist()
                n_resampled += 1
        uw.pprint(f"restart: {n_resampled} crust-law fault polyline(s) re-sampled from the checkpoint's S {S_saved:g} "
                  f"to this run's S {S:g} ({mode})")
faulted = FaultedMesh(built, "f0")
restart_transfer = "none"
if params.uw_restart >= 0 and "solver_checkpoint" in state:
    # the first solve starts from the checkpointed solution on the faulted mesh: on the
    # same mesh (the built set rebuilt) it is the solution an uninterrupted run would
    # start from, so the step is an ordinary warm step (Newton at once)
    worst = read_solver_fields(faulted, state["solver_checkpoint"])
    same = worst < 1.0e-3 * S
    restart_transfer = "checkpoint" if same else "checkpoint_nearest"
    faulted.stokes.newton_switch_rtol = params.uw_warm_newton_switch if same else params.uw_rebuild_newton_switch
    uw.pprint(f"restart: V, P from the faulted-mesh checkpoint ({'same mesh' if same else 'nearest DOF'}, "
              f"largest match distance {worst:.2e})")
elif params.uw_restart >= 0:
    # an older checkpoint: start from the base velocity (continuous across the faults, no
    # pressure), not from rest: measured from 3580 at np 16, 17 iterations against 33
    faulted.warm_start(V_b)
    restart_transfer = "base_V"
_ra, _tau0, _tau1, _H = params.uw_ra, params.uw_tau0, params.uw_tau1, params.uw_heating
uw.pprint(f"annulus r_o {r_o:.4f} r_i {r_i:.4f}, Ra {_ra:.4g}, tau1/Ra "
          f"{_tau1 / _ra:.3g}, tau0 {_tau0:.4g}, H {_H:.4g}, "
          f"asthenosphere {params.uw_asth:g} in {params.uw_asth_top:g}-{params.uw_asth_bottom:g}; "
          + (f"viscosity arrhenius, E {ARRHENIUS[0]:.4g}, T0 {ARRHENIUS[1]:g}, the fk viscosity "
             f"{float(params.uw_deta) ** (1 - ARRHENIUS[2]):.4g} at T {ARRHENIUS[2]:g}, cap {ARRHENIUS[3]:g}; ")
          + f"{len(faults)} fault(s); "
          + (f"crust x{params.uw_crust_weak:g}, {crust_thick:.4f} thick, to depth {params.uw_crust_depth:g}; "
             if crust_on else "")
          + (f"crust made on new plate to {params.uw_ridge_crust_stop:g} short of the trench; " if RIDGE_CRUST else "")
          + (f"compositional overriding plate {params.uw_over_comp_thick:g} thick from {params.uw_over_gap:g} "
             f"behind the trench, dT {params.uw_over_dT:g}, eta x{params.uw_over_eta:g}; " if over_on else "")
          + (f"{int(uw.utilities.gather_data(crust_swarm.local_size, bcast=True).sum())} particles; "
             if swarm_on else "")
          + f"from t {t:.4f}; output {out}")


def git_head(path):
    """The commit checked out at ``path`` (a clone or a worktree), read from the files: the
    image has no git. None if it cannot be read."""
    try:
        d = os.path.abspath(path)
        while not os.path.exists(os.path.join(d, ".git")):
            if os.path.dirname(d) == d:
                return None
            d = os.path.dirname(d)
        gitdir = os.path.join(d, ".git")
        if os.path.isfile(gitdir):                      # a worktree: "gitdir: <path>"
            gitdir = open(gitdir).read().split(":", 1)[1].strip()
        head = open(os.path.join(gitdir, "HEAD")).read().strip()
        if not head.startswith("ref:"):
            return head
        ref = head.split(None, 1)[1]
        common = gitdir
        if os.path.exists(os.path.join(gitdir, "commondir")):
            common = os.path.normpath(os.path.join(gitdir, open(os.path.join(gitdir, "commondir")).read().strip()))
        for g in (gitdir, common):
            if os.path.exists(os.path.join(g, ref)):
                return open(os.path.join(g, ref)).read().strip()
        for line in open(os.path.join(common, "packed-refs")):
            if line.strip().endswith(" " + ref):
                return line.split()[0]
    except (OSError, IndexError):
        pass
    return None


CHOICE_KNOBS = ["uw_tol", "uw_pres_rtol", "uw_pres_rtol_cold", "uw_newton_switch", "uw_warm_newton_switch",
                "uw_rebuild_newton_switch", "uw_picard", "uw_retry_keep", "uw_spline_side", "uw_spline_length",
                "uw_fault_precedence", "uw_fault_seams", "uw_split_inset", "uw_split_inset_along",
                "uw_resample_restored", "uw_wall_normal", "uw_wall_check", "uw_crust_ppc", "uw_ocrust_depth",
                "uw_crust_refill_every", "uw_ridge_crust", "uw_ridge_crust_stop", "uw_crust_line_spacing",
                "uw_rebuild_cells", "uw_spacing", "uw_dt_mult", "uw_courant", "uw_dt_max", "uw_ckpt_every",
                "uw_placement_refused", "uw_yield_softness", "uw_arr_T0", "uw_arr_E", "uw_arr_eta_max"]


def write_choices(explicit, effective, info):
    """Append this start's choices block to <out>/README.md: each knob the results depend on, its value, and
    whether the launch line set it or the default was taken (Louis's rule, 2026-11-01). Rank 0 only."""
    rows = [f"| {k} | {getattr(params, k)} | {'set' if k in explicit else 'default'} |"
            for k in CHOICE_KNOBS if hasattr(params, k)]
    eff = [f"| {k} | {v} | derived / hard-coded |" for k, v in effective.items()]
    block = "\n".join([
        "", f"## Choices ({info['started']}, driver {info['driver_commit']}, underworld3 {info['uw3_commit']}, "
            f"np {info['mpi_ranks']}, restart from {info['restart_from']})",
        "", "Each value's status and evidence: see zg95_lid_regimes/DECISIONS.md (the drivers are not part of "
            "underworld3, so their decisions are recorded there). A run that changes a decision says so here.",
        "", "| knob | value | set on the launch line or default |", "|---|---|---|", *rows, *eff, ""])
    with open(os.path.join(out, "README.md"), "a") as f:
        f.write(block + "\n")


def write_run_info():
    """Where and with what this run (or restart) ran, appended to <out>/run_info.json."""
    import datetime
    import socket
    from mpi4py import MPI
    from petsc4py import PETSc
    ranks_per_node = MPI.COMM_WORLD.Split_type(MPI.COMM_TYPE_SHARED).Get_size()
    if uw.mpi.rank != 0:
        return
    uw3_commit, uw3_branch = os.environ.get("UW3_COMMIT"), os.environ.get("UW3_BRANCH")
    stamp = os.path.join(os.path.dirname(uw.__file__), "_build_commit.txt")
    if uw3_commit is None and os.path.exists(stamp):
        words = open(stamp).read().split()
        uw3_commit = words[0] if words else None
        uw3_branch = uw3_branch or (words[1] if len(words) > 1 else None)
    info = {"started": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
            "host": socket.gethostname(), "nodes": os.environ.get("SLURM_JOB_NODELIST"),
            "mpi_ranks": uw.mpi.size, "ranks_per_node": ranks_per_node,
            "omp_threads": os.environ.get("OMP_NUM_THREADS"),
            "container": os.environ.get("APPTAINER_CONTAINER") or os.environ.get("SINGULARITY_CONTAINER"),
            "uw3_path": uw.__file__, "uw3_commit": uw3_commit, "uw3_branch": uw3_branch,
            "driver_commit": os.environ.get("DRIVER_COMMIT") or git_head(os.path.dirname(os.path.abspath(__file__))),
            "petsc": ".".join(str(v) for v in PETSc.Sys.getVersion()), "argv": sys.argv,
            "params": params.to_dict(), "restart_from": int(params.uw_restart) if params.uw_restart >= 0 else None,
            "slurm_job": os.environ.get("SLURM_JOB_ID")}
    # the choices this run depends on: which knobs the launch line set (the rest are defaults taken), and the
    # effective values the library derives or the driver hard-codes (Louis, 2026-11-01: every such choice is stated)
    explicit = sorted({a.lstrip("-") for a in sys.argv[1:] if a.startswith("-uw_")})
    pres = float(params.uw_pres_rtol) if float(params.uw_pres_rtol) > 0 else 0.1 * float(params.uw_tol)
    effective = {"pressure_rtol": pres, "pressure_rtol_source": "uw_pres_rtol" if float(params.uw_pres_rtol) > 0
                 else "library default 0.1 x uw_tol",
                 "pressure_rtol_warm": PRES_RTOL_WARM, "pressure_rtol_cold": PRES_RTOL_COLD,
                 "pressure_rtol_rule": "cold solves (the first solve and any cold retry) take the cold rtol, warm "
                                       "solves the warm; an unconverged cold first solve stops a fresh run",
                 "velocity_rtol_rotated": 0.033 * float(params.uw_tol), "consistent_jacobian": "continuation",
                 "rung_spacing": S, "rung_spacing_source": "uw_spacing" if float(params.uw_spacing) > 0
                 else "one base cell (uw_cell / 2**uw_refinement)",
                 "rebuild_threshold": REBUILD,
                 "rebuild_threshold_source": f"uw_rebuild_cells {float(params.uw_rebuild_cells):g} x base cell {H_B:g} "
                                             "(a distance, independent of S)",
                 "fault_seams": str(params.uw_fault_seams),
                 "fault_mesher": "ladder" if params.uw_fault_seams == "gather" else "network",
                 "fault_partition": FAULT_PARTITION, "wall_normal": str(params.uw_wall_normal),
                 "placement_attempts": "margin_rings 1/1/2/1, clearance 0.7, width x1/x1.25/x1/x1.5"}
    info.update({"explicit": explicit, "effective": effective})
    write_choices(explicit, effective, info)
    path = os.path.join(out, "run_info.json")
    runs = []
    if os.path.exists(path):
        try:
            runs = json.load(open(path))
        except ValueError:
            pass
    with open(path, "w") as f:
        json.dump(runs + [info], f, indent=1, default=str)


write_run_info()


def needs_rebuild(faults, built):
    if [f["name"] for f in faults] != [f["name"] for f in built]:
        return True
    for f, g in zip(faults, built):
        if polyline_gap(f["points"], g["points"]) > REBUILD:     # its polyline moved by more than the threshold
            return True
    return False


# ----------------------------------------------------------------------------- time loop
if str(params.uw_placement_refused) not in ("stop", "keep"):
    raise ValueError(f"-uw_placement_refused {params.uw_placement_refused}: stop or keep")
stopped = None                              # why the run ended early (uw_placement_refused stop)
last_ckpt = int(params.uw_restart)          # the last step with a checkpoint on disk (-1: none)
for k in range(k0, k0 + params.uw_steps):
    wall = time.perf_counter()
    events = []
    damage = last_damage
    # for the solver record: what kind of solve this step is, and the phases' wall times
    kind = ("restart_first" if params.uw_restart >= 0 else "init_first") if k == k0 else "ordinary"
    faults_before = list(faulted.names)
    mesh_rec = faulted.mesh_record if k == k0 else None
    t_build = t_warm = 0.0
    if needs_rebuild(faults, faulted.faults):
        asked = [dict(f) for f in faults]       # the set as the last step left it: what a stop's checkpoint holds
        previous = faulted
        try:
            faulted = FaultedMesh(faults, f"f{n_built}")
        except RuntimeError as err:
            uw.pprint(f"  placement of {[f['name'] for f in faults]} failed ({err})")
            if str(params.uw_placement_refused) == "stop":
                # the run ends here rather than going on with the fault where it was. The last finished step is
                # checkpointed if the cadence did not (on the mesh it was solved on, with the faults it asked for),
                # so a restart from it makes this build again
                stopped = f"the placement of {[f['name'] for f in faults]} was refused at step {step}"
                if step - 1 > last_ckpt:
                    checkpoint(step - 1, t, records, previous, asked, next_id,
                               {"k": k, "n_built": n_built, "refused": refused, "last_damage": last_damage})
                    last_ckpt = step - 1
                    stopped += f"; step {last_ckpt} checkpointed"
                elif last_ckpt >= 0:
                    stopped += f"; the last checkpoint is step {last_ckpt}"
                break
            else:
                uw.pprint("  keeping the previous faults")
                for f in faults:
                    if f["name"] not in previous.names:
                        refused[f["name"]] = f["theta"]
                faults = [dict(f) for f in previous.faults]
                faulted = previous
        n_built += 1
        if faulted is not previous:
            # start from the old solution, also when the set has changed (a fault formed or
            # removed): measured on kaiju from 3580 (np 16), a spawn takes 11 iterations warm
            # against 34 cold and a retire 16 against 30, converging to the cold solution
            # within 1e-5. This needs the rotated loop's Picard->Newton switch keyed on the
            # rest-state residual (underworld3 371d3bd); without it a changed set's warm start
            # failed to converge (measured on forming a second fault). solve() retries cold
            # if the warm start does not converge.
            t_warm = time.perf_counter()
            faulted.warm_start(previous.v, previous.p)
            t_warm = time.perf_counter() - t_warm
            faulted.stokes.newton_switch_rtol = params.uw_rebuild_newton_switch
            mesh_rec = faulted.mesh_record
            if k != k0:
                kind = "rebuild_same_set" if faulted.names == previous.names else "rebuild_changed_set"
        t_build = time.perf_counter() - wall - t_warm
        del previous
        gc.collect()
    rec = faulted.solve()
    t_stokes = time.perf_counter() - wall
    t_phase = time.perf_counter()
    faulted.to_base()
    t_to_base = time.perf_counter() - t_phase
    t_phase = time.perf_counter()
    dt_accuracy = params.uw_dt_mult * float(adv.estimate_dt())
    adv.estimate_dt(basis="resolution", direction_aware=True)
    dt_crossing = adv.dt_adv
    dt = min(dt_accuracy, params.uw_courant * dt_crossing, params.uw_dt_max)
    adv.solve(timestep=dt)
    strain_adv.solve(timestep=dt)
    gamma_b.array[:, 0, 0] = np.maximum(gamma_b.array[:, 0, 0], 0.0)
    t_energy_strain = time.perf_counter() - t_phase
    t_phase = time.perf_counter()
    if swarm_on:
        advect_split(faulted, dt)
        for var, _, _ in markers.values():
            var._update()
        if (crust_on and params.uw_crust_ppc > 0 and params.uw_crust_refill_every > 0
                and (k + 1) % int(params.uw_crust_refill_every) == 0):
            n_refill = int(uw.utilities.gather_data(refill_crust(), bcast=True).sum())
            if ocrust_on:
                n_refill += int(uw.utilities.gather_data(refill_line(faults, "ocrust", params.uw_ocrust_depth),
                                                         bcast=True).sum())
            if n_refill:
                events.append(f"crust refill: {n_refill} particles")
            if RIDGE_CRUST:
                n_ridge = int(uw.utilities.gather_data(ridge_crust(faults), bcast=True).sum())
                if n_ridge:
                    events.append(f"ridge crust: {n_ridge} particles")
    t_swarm = time.perf_counter() - t_phase
    t_phase = time.perf_counter()
    t += dt

    damage = {}
    detect_now = (k >= params.uw_detect_start
                  and (k - params.uw_detect_start) % params.uw_detect_every == 0)
    if detect_now:
        # one fault following the weak crust on the slab's top, from the trench down to the
        # depth cap; it forms at the first detection and never retires
        found = crust_spline_points(faults)
        if found is None:
            uw.pprint("  crust fault: no slab top reaching the cap from the surface; the fault keeps its place")
        else:
            poly, theta_t, dip, depth, info = found
            if faults:
                f = faults[0]
                moved = polyline_gap(poly, f["points"])
                for key in ("raw", "trench_gap", "top_dip_data", "top_dip_floored", "particle_trench"):
                    f.pop(key, None)                 # the record's keys describe the locator named in it
                f.update({"points": poly.tolist(), "theta": theta_t, "dip": dip, "depth": depth, **info})
                damage[f["name"]] = float(moved)
            else:
                faults.append({"name": f"F{next_id}", "points": poly.tolist(), "theta": theta_t,
                               "dip": dip, "depth": depth, **info})
                next_id += 1
                events.append(f"formed {faults[0]['name']} on the crust at {np.degrees(theta_t):.1f} deg, "
                              f"dip {dip:.1f}, depth {depth:.3f}, {len(poly)} points")
    if damage:
        last_damage = dict(damage)
    for e in events:
        uw.pprint(f"  fault {e}")

    t_detection = time.perf_counter() - t_phase
    record, profile = faulted.diagnostics.record()
    record.update(rec)
    local = gamma_b.array[:, 0, 0]
    record["strain_max"] = float(uw.utilities.gather_data(local.max() if local.size else 0.0, bcast=True).max())
    # the plates beside each trench: tangential surface velocity on the -theta and +theta
    # sides (the overriding plate is the +theta side for a dip below 90 degrees), and the
    # trench's own rate from the fault's theta history
    record["plates"] = plate_velocities(faults)
    if records and "faults" in records[-1] and dt > 0:
        previous = {f["name"]: f["theta"] for f in records[-1]["faults"]}
        record["trench_rate"] = {f["name"]: float(wrap(f["theta"] - previous[f["name"]]) * r_o / dt)
                                 for f in faults if f["name"] in previous}
    record.update({"faults": [dict(f) for f in faults], "n_faults": len(faults), "damage": damage,
                   "events": events, "n_built": n_built, "t_build": round(faulted.t_build, 1),
                   "theta_trench": faults[0]["theta"] if faults else float(params.uw_theta_trench),
                   "dip": faults[0]["dip"] if faults else float(params.uw_dip),
                   "fault_depth": faults[0]["depth"] if faults else 0.0})
    record.update({"step": step, "t": t, "dt": dt, "courant": dt / dt_crossing,
                   "t_stokes": round(t_stokes, 2), "t_step": round(time.perf_counter() - wall, 2)})
    solver = record["solver"] = dict(rec["solver"])
    solver.update({
        "kind": kind, "faults_before": faults_before, "faults_after": list(faulted.names),
        "transfer": (restart_transfer if kind == "restart_first"
                     else "driver" if solver["start"] == "warm" and kind != "ordinary" else "none"),
        "mesh": mesh_rec,
        "wall": {"build": round(t_build, 3), "transfer": round(t_warm + solver["wall"]["transfer"], 3),
                 "stokes": solver["wall"]["stokes"], "to_base": round(t_to_base, 3),
                 "energy_strain": round(t_energy_strain, 3), "swarm": round(t_swarm, 3),
                 "detection": round(t_detection, 3), "checkpoint": 0.0, "step": record["t_step"]}})
    records.append(record)
    described = " ".join(f"{f['name']}@{np.degrees(f['theta']):.1f}/{f['dip']:.0f}/{f['depth']:.2f}"
                         f"(slip {rec['slip'].get(f['name'], float('nan')):.0f})" for f in faults) or "none"
    uw.pprint(f"step {step:5d} t {t:.5f} dt {dt:.2e} | vrms {record['vrms']:8.2f} "
              f"M {record['mobility']:.3f} lid {record['lid_depth']:.3f} T_mid {record['T_mid']:.3f} "
              f"slip {record['slip_max']:.2f} | faults {described} | "
              f"newton {record['newton']} conv {record['converged']} "
              f"{record['t_stokes']:.1f}/{record['t_step']:.1f} s", flush=True)
    if step % params.uw_ckpt_every == 0 or k == k0 + params.uw_steps - 1:
        t_phase = time.perf_counter()
        checkpoint(step, t, records, faulted, faults, next_id,
                   {"k": k + 1, "n_built": n_built, "refused": refused, "last_damage": last_damage})
        last_ckpt = step
        # the next checkpoint writes it; the last one is written here
        solver["wall"]["checkpoint"] = round(time.perf_counter() - t_phase, 3)
        if k == k0 + params.uw_steps - 1:
            write_records(records)
    step += 1

if stopped:
    uw.pprint(f"STOPPED: {stopped}", flush=True)
    sys.exit(3)
uw.pprint("done")
