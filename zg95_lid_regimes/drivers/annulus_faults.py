"""Faults that form where the lid fails: the strain-weakening annulus with a set of
split-node faults, each placed on, and moving with, a plastic-strain band of a
downwelling.

The rheology, walls and transport are those of ``annulus_fault.py`` (yield stress
weakened by an accumulated plastic strain gamma that is carried by the flow and heals
in warm mantle; a declared plastic regularisation eta_reg). The faults:

- every ``uw_detect_every`` steps each fault follows its own band: the saturated,
  cold, descending plastic-strain band near it (``strain_band.detect_fault``) gives a
  trench angle and a dip angle phi (measured below the local horizontal from +theta,
  so phi > 90 dips toward -theta), and the local thermal boundary layer gives the
  depth; the fault relaxes toward them by bounded steps;
- every ``uw_global_every`` steps the whole annulus is scanned
  (``strain_band.rank_bands``). A band whose damage (gamma integrated over its area)
  exceeds ``uw_damage_spawn`` with no fault within ``uw_fault_separation`` becomes a
  new fault, up to ``uw_max_faults``; a fault whose own band has healed below
  ``uw_damage_retire`` is removed (the last fault stays);
- all faults are placed into one copy of the base's finest level (and its split
  chain levels), each split along its own ladder and bridged to the surface, each
  with its own frictionless contact. The faulted mesh is rebuilt whenever a fault has
  moved, turned or changed depth enough, or the set has changed.

Start from an annulus run's checkpoint (``uw_source``/``uw_source_index``, a first
fault at ``uw_theta_trench``), or from a checkpoint of ``annulus_fault.py`` or of this
driver (``uw_restart`` in ``uw_out``; a single-fault state becomes the first fault).

    mpirun -np 7 python annulus_faults.py -uw_out <dir> -uw_restart 2450
"""
import gc
import json
import os
import sys
import time
import warnings

import numpy as np
import sympy
from scipy.optimize import brentq
import underworld3 as uw
from underworld3.utilities.custom_mg import set_custom_fmg
from underworld3.utilities.fault_contact import _fault_pair_nodes_on, fault_slip
from underworld3.utilities.place_surface import place_fault_ribbon_2d

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from annulus_model import (AnnulusDiagnostics, annulus_mesh, annulus_radii, clamp_radii,
                           free_slip_walls, ridge_factor, set_viscoplastic)
from strain_band import (boundary_layer_depth, detect_fault, fit_fault_lines, polar_grid, rank_bands,
                         spine_separation)

params = uw.Params(
    uw_out="~/+Simulations/zg95/annulus_faults/runs/test_multi",
    uw_init="checkpoint",       # "checkpoint": T, V from uw_source at uw_source_index; "slab": the
                                #   prescribed lithosphere + slab below (t = 0, at rest, no damage)
    uw_source="~/+Simulations/zg95/annulus_regimes/runs/tau1x1.50_seed5",
    uw_source_index=2050,
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
    uw_top_hot=0,               # 2: a fixed ridge (uw_ridge_patch). 1: the surface on the overriding side is HELD at T_interior (no boundary
                                #   layer grows there: at this Peclet number the thin layer thickens into a
                                #   plate within the run), from uw_top_hot_start past the trench to the same
                                #   distance short of the antipode, tanh ramps of uw_over_ramp
    uw_top_hot_start=0.06,
    uw_ridge_patch=0.05,        # uw_top_hot 2 (a fixed ridge): only a patch of this half-width (arc, layer depths) at the
                                #   antipode of the trench is held at T_interior, tanh ramps of uw_over_ramp; T = 0 elsewhere
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
    uw_fault_precedence=0,      # 1: inside a fault's band (and its zone) the fault's own rheology alone: the crust,
                                #   continent and compositional-slab factors are off there (Louis: "the fault
                                #   rheology should always win")
    uw_marker_rheo_depth=0.0,   # > 0: below this depth (layer depths) the crust and continent factors fade out
                                #   (tanh, uw_marker_rheo_ramp); their markers are still advected, recorded and drawn,
                                #   so entrained material is tracked without acting (Louis: "change the material
                                #   index so we track it but it does not have a rheological influence")
    uw_marker_rheo_ramp=0.02,
    uw_over_gap=0.0,            # the overriding plate starts this arc length (layer depths) from the trench
    uw_over_ramp=0.03,          # over which its age ramps up from the thin layer's
    # an imposed ridge (any state): a weak vertical seam through the lid at each ridge
    # angle (uw_theta_trench + uw_ridge_sub and - uw_ridge_over, fixed in the mantle frame),
    # the viscosity and the yield stress times uw_ridge_weak, Gaussian across the seam
    # with half-width uw_ridge_width (layer depths), down to uw_ridge_depth; 1 = no ridge
    uw_ridge_weak=1.0,
    uw_ridge_width=0.06,
    uw_ridge_depth=0.2,
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
    # a compositional slab on the same particles: the subducting plate and its slab as a
    # layer uw_comp_thick thick whose buoyancy is a fixed temperature deficit uw_comp_dT
    # (0 = none; it does not diffuse) and whose viscosity and yield stress are times
    # uw_comp_eta; uw_buoy_T scales the thermal buoyancy (0 with uw_deta 1: the slab is
    # compositional and the mantle isoviscous, the standard foundering-slab model)
    uw_comp_dT=0.0,
    uw_comp_eta=1.0,
    uw_comp_thick=0.1,
    uw_buoy_T=1.0,
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
    uw_slab_wedge_age=6.25e-4,  # cold top (uw_slab_warm_top 0): the wedge is cooled beside the slab over
                                #   2 sqrt(this) (0.05 d), continuous across the plane, no mask
    uw_slab_warm_top=1,         # 1: since subduction the slab has exchanged heat with the mantle on its
                                #    contact side: the one-sided plate profile diffuses freely for tau (the
                                #    distance down-dip over uw_slab_rate), so the slab warms and the wedge
                                #    beside it cools, continuously across the plane (tabulated, no closed
                                #    form); 0: the contact side is masked and the slab keeps its erf profile
    uw_restart=-1,
    uw_cell=0.5,
    uw_refinement=4,
    uw_ra=9.1125e5,
    uw_deta=3.0e4,
    uw_tau0=2.025e4,
    uw_tau1=1.366875e6,
    uw_heating=1.4175,
    uw_yield_softness=0.2,
    # an asthenosphere: the viscosity times uw_asth in a channel between two depths
    uw_asth=1.0,                # 1: no channel; 0.01-0.1 for a weak channel under the lid
    uw_asth_top=0.3,
    uw_asth_bottom=0.7,
    uw_asth_ramp=0.05,
    # the first fault, when starting from an annulus run
    uw_theta_trench=0.0,
    uw_dip=45.0,
    uw_fault_depth=0.35,
    # the fault band
    uw_spacing=0.004,
    uw_eta_w=1.0e-3,
    uw_chain=2,
    uw_band_widen=1,
    uw_rebuild_rungs=4,
    uw_fault_surface_gap=2.0,   # crust law: the fit's up-dip end may stop this many crust thicknesses below the
                                #   wall (its shallowest point: the crust base on the incoming plate); deeper, no fault
    uw_weld_ok=0,               # 1: a refused chain level is welded and the build goes on (the old behaviour);
                                #   0: the build is refused and the previous faults kept
    uw_fault_fit="parabola",    # crust law locator: "parabola" (crust_fault_points) or "envelope" (the crust base
                                #   marched up from the cap, crust_envelope_points)
    uw_fault_top_dip_min=30.0,  # envelope: the least dip (deg) of the base's straight extension from its shallowest
                                #   point to the wall; the unfloored dip is recorded
    uw_fault_trench_tol=0.15,   # envelope: no fault when that extension meets the wall further than this (arc, layer
                                #   depths) from the particle trench
    uw_fault_realisation="split",  # "split": the fault cut and split, a frictionless contact; "ti": the band painted
                                #   transversely isotropic on the unsplit placed mesh (FaultedMesh, ti_band_viscosity)
    uw_ti_tau_frac=1.0e-2,      # ti: the band's yield stress, this fraction of the host's (tau0 + tau1 depth), on the
                                #   resolved fault-plane shear
    uw_ti_eta_reg=0.1,          # ti: the band's rate strengthening (added to its yield viscosity)
    uw_ti_eta_min=0.1,          # ti: the band's viscosity floor (the host's is 1)
    uw_ti_trace_inset=0.5,      # ti: the trace runs to this many rungs inside the wall: the band outcrops, no bridge
    uw_ti_smooth=0,             # ti: 1 = the band's min and floor in the host's own smooth forms (_combine_yield's
                                #   softmin, _apply_floor's smooth max, the host's delta) for Newton; 0 = hard Min/Max
    uw_bridge_eta_min=1.0,      # split: the bridge zone's own viscosity floor (the host's is 1; the zone's x uw_eta_w
                                #   weakening is otherwise undone by it): 1 = unchanged
    uw_bridge_eta_reg=10.0,     # split: the bridge zone's own rate strengthening (the host's uw_eta_reg, 10): 10 = unchanged
    uw_ti_check=0,              # ti, checks only: 1 the TI model with the band off (eta_1 = eta_0); 2 the host
                                #   viscoplastic model alone on the same unsplit mesh (1 and 2 must agree)
    uw_addon_timing=0,          # measurement runs (addon_timing.py): > 0 times each faulted-mesh build and
                                #   its first solve, counts every level's cells per rank, forces this many
                                #   rebuilds of the same set after the first step, stops after the last
                                #   one's solve, and writes <uw_out>/addon_timing.json; nothing else written
    uw_rebuild_dip=2.0,
    uw_depth_hysteresis=0.016,  # a fitted depth within this of the fault's keeps the fault's (two detection rows)
    uw_rebuild_newton_switch=1.0e-2,
    # strain weakening, regularisation, healing
    uw_strain_crit=0.5,
    uw_weak_min=0.5,
    uw_yield_boost=1.25,
    uw_eta_reg=10.0,
    uw_heal_time=0.002,
    uw_heal_T=0.7,
    # following the bands
    uw_detect_every=5,
    uw_detect_start=0,          # steps before the first detection (a prescribed slab needs a few to
                                #   establish its shear band before the fit is allowed to move the fault)
    uw_detect_window=40.0,      # largest half-width of a fault's own search arc (degrees)
    uw_detect_gamma_sat=0.5,
    uw_detect_T_lith=0.6,
    uw_detect_depth_max=0.45,
    uw_detect_depth_min=0.1,    # shallowest band point in the fit: the near-surface damage fans out (a V-top) above it
    uw_detect_max_dtheta=2.0,
    uw_detect_max_ddip=5.0,
    uw_dip_min=40.0,            # the ladder cap of a shallower fault reaches the outer wall and cannot be carved
    uw_dip_max=140.0,
    uw_bl_T=0.7,
    uw_fault_depth_min=0.06,
    uw_fault_depth_max=0.25,
    uw_fault_cut_lid=0,         # 1: the depth cap is the larger of uw_fault_depth_max and the
                                #    lid depth of the last record plus uw_fault_lid_margin, so a
                                #    fault can cut the whole lithosphere
    uw_fault_lid_margin=0.05,
    uw_detect_max_ddepth=0.05,
    # forming and removing faults
    uw_fault_law="lines",       # "none": no detection; "lines": N faults fitted to the damage each detection; "bands": per-fault band tracking; "crust": one fault on the base of the crust layer (or, without a crust marker, the compositional slab's top), a parabola from the trench to uw_fault_depth_max
    uw_line_gamma=2.0,          # "lines": damage counted (plastic strain at or above this)
    uw_line_min_damage=0.01,    # "lines": smallest damage (strain x area) that is a fault
    uw_line_width=0.035,        # "lines": half-width of a line's inlier band
    uw_line_surface=0.05,       # "lines": a fault's damage must start within this of the surface
    uw_line_match=6.0,          # "lines": a line within this arc of a fault's trench is that fault (degrees)
    uw_line_patience=3,         # "lines": detections a fault survives without a line before retiring
    # "rate": faults fitted to the strain rate of the lithosphere (the total invariant on the
    # base mesh, which carries a slipping fault's jump as a one-cell band), normalised by its
    # robust maximum; the trench advects with the overriding plate between detections; a
    # fault retires when its slip stays below a fraction of the largest
    uw_rate_frac=0.3,           # "rate": points at or above this fraction of the lid's 99.5th-percentile rate
    uw_rate_min_activity=0.002, # "rate": smallest rate-area (normalised rate x area) that is a fault
    uw_retire_slip_frac=0.1,    # "rate": slip below this fraction of the largest slip counts as idle
    uw_retire_patience=3,       # "rate": detections idle before retiring (the last fault stays)
    uw_trench_advect=0,         # 1: every step, move each trench with the surface velocity of its
                                #    overriding plate (sampled uw_advect_offset beyond the trench on
                                #    the side the fault dips under); "rate" turns it on
    uw_advect_offset=0.1,
    uw_heal_time_lid=0.0,       # > 0: damage also decays on this time scale everywhere (the lid's scars fade)
    uw_fault_damage=0.0,        # > 0: a fault damages its surroundings at this rate x slip, within a band width,
                                #      from its trench to one band width past its tip (so it can grow)
    uw_global_every=10,
    uw_damage_spawn=0.05,       # band damage (strain x area, layer depths squared) that forms a fault
    uw_damage_retire=0.01,      # a fault whose band has healed below this is removed
    uw_max_faults=3,            # 0: no fault at all (the plain annulus, the slab founders on its own)
    uw_fault_separation=20.0,   # no new fault within this arc of an existing one (degrees)
    uw_fault_clearance=0.08,    # smallest distance between two faults' spines (layer depths): a
                                #   converging pair (the conjugate V) is kept apart by shortening the
                                #   weaker one; two ribbons through one cell hang the mesher
    # solver and time stepping
    uw_tol=1.0e-3,
    uw_pres_rtol=0.0,           # > 0: the Schur (pressure) KSP rtol, overriding the library's 0.1 x uw_tol (the
                                #   rotated free-slip solve's solver._rotated_pres_rtol, and the native path's option)
    uw_vel_rtol=0.0,            # > 0: the native path's inner velocity KSP rtol (0.033 x uw_tol); the rotated solve,
                                #   which these drivers use, has no knob for its velocity rtol (0.033 x uw_tol)
    uw_picard=0,
    uw_newton_switch=1.0e-2,
    uw_warm_newton_switch=1.0,
    uw_verbose=0,
    uw_dt_mult=3.0,
    uw_courant=1.0,
    uw_dt_max=5.0e-3,
    uw_steps=20,
    uw_ckpt_every=10,
)

# The scaled mode (-uw_scaled 1; off by default, and then nothing below changes): the
# physical parameters are given as quantities and the solvers non-dimensionalise
# themselves through the units system (docs/developer/design/UNITS_SIMPLIFIED_DESIGN_2025-11.md,
# ND_UNITS_BOUNDARY_CONTRACT.md): the model's reference quantities are the layer depth,
# the thermal diffusivity, the basal viscosity and the temperature drop, so one length is
# d, one time d^2/kappa, one stress eta_ref kappa/d^2 and one temperature dT; Ra, tau0,
# tau1 and H follow from the quantities and are printed, and -uw_ra, -uw_tau0, -uw_tau1 and
# -uw_heating are not used. The fields (T in units of dT above the surface, V, the
# geometry parameters in layer depths, the times uw_age_*, uw_heal_time ...) stay in
# model units, which the boundary contract allows; the records gain physical columns.
# The defaults reproduce TA's Ra 2.386e7, tau0 1.789e6, tau1 2.386e8 and H 1.4175 with
# d 2900 km, kappa 1e-6 m^2/s, rho 3300 kg/m^3, alpha 3e-5 /K, g 9.81 m/s^2, dT 2500 K.
SCALED = bool(uw.Params(uw_scaled=0).uw_scaled)
units = None
if SCALED:
    units = uw.Params(
        uw_depth=uw.Param(2900.0, units="km", description="layer depth d (the length scale)"),
        uw_kappa=uw.Param(1.0e-6, units="m**2/s", description="thermal diffusivity"),
        uw_eta_ref=uw.Param(2.481805627619447e21, units="Pa*s",
                            description="viscosity at the basal temperature (the viscosity scale)"),
        uw_dT=uw.Param(2500.0, units="K", description="temperature drop across the layer"),
        uw_rho=uw.Param(3300.0, units="kg/m**3", description="reference density"),
        uw_alpha=uw.Param(3.0e-5, units="1/K", description="thermal expansivity"),
        uw_gravity=uw.Param(9.81, units="m/s**2", description="gravity"),
        uw_yield_0=uw.Param(527.9370116303437, units="MPa", description="yield stress at the surface"),
        uw_yield_grad=uw.Param(24.27975, units="MPa/km", description="yield stress gradient with depth"),
        uw_heat_rate=uw.Param(13.297532104637336, units="K/Gyr",
                              description="internal heating as a rate of temperature rise"),
        uw_units_dt_local=0,    # 1: the step-size estimates computed here from model-unit coordinates
                                #   (CHECK ONLY: the library's direction-aware crossing time and first
                                #   accuracy estimate read dimensional mesh coordinates in a units model)
    )
    orchestration_model = uw.get_default_model()
    orchestration_model.set_reference_quantities(
        length=units.uw_depth, diffusivity=units.uw_kappa, viscosity=units.uw_eta_ref,
        temperature=units.uw_dT)

out = os.path.expanduser(params.uw_out)
os.makedirs(out, exist_ok=True)
r_o, r_i = annulus_radii()
S = float(params.uw_spacing)
W = 2.0 * S

base = annulus_mesh(params.uw_cell, params.uw_refinement)
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
TI = params.uw_fault_realisation == "ti"
if TI and SCALED:
    raise ValueError("-uw_fault_realisation ti is not set up for a units run (-uw_scaled 1)")
comp_on = params.uw_comp_dT > 0 or params.uw_comp_eta != 1
if params.uw_fault_law == "crust" and not (crust_on or comp_on):
    raise ValueError("the crust fault law follows the base of the crust layer (uw_crust_weak < 1) "
                     "or, without one, the compositional slab's top (uw_comp_dT or uw_comp_eta)")
over_on = params.uw_over_dT != 0 or params.uw_over_eta != 1   # a negative uw_over_dT is a buoyant block
swarm_on = crust_on or comp_on or over_on
crust_thick = (float(params.uw_crust_thick) if params.uw_crust_thick > 0
               else float(params.uw_cell) / 2 ** int(params.uw_refinement))
# the markers: name -> (swarm variable, its P1 picture on the base mesh, the geometry
# of the slab state as a function of particle coordinates)
markers = {}
if swarm_on:
    crust_swarm = uw.swarm.Swarm(base)
    # populated by the initial state: fresh particles for the slab state, the saved ones on a restart
for name, on, geometry in (("crust", crust_on, lambda xy: layer_marker(xy, crust_thick)),
                           ("slab", comp_on, lambda xy: layer_marker(xy, float(params.uw_comp_thick))),
                           ("over", over_on, lambda xy: over_marker(xy, float(params.uw_over_comp_thick)))):
    if on:
        markers[name] = (uw.swarm.SwarmVariable(name, crust_swarm, 1, proxy_location="cells", proxy_degree=1),
                         uw.discretisation.MeshVariable(name, base, 1, degree=1), geometry)
if crust_on:
    crust_var, crust_b = markers["crust"][:2]
if comp_on:
    slab_var, slab_b = markers["slab"][:2]


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


eta_ref = None
if not SCALED:
    Ra = uw.expression(r"\mathrm{Ra}", params.uw_ra, "Rayleigh number on the basal viscosity")
    deta = uw.expression(r"\Delta\eta", params.uw_deta, "viscosity contrast across the layer")
    tau0 = uw.expression(r"\tau_0", params.uw_tau0, "yield stress at the surface")
    tau1 = uw.expression(r"\tau_1", params.uw_tau1, "yield stress gradient with depth")
    H = uw.expression(r"H", params.uw_heating, "internal heating rate")
    heating = params.uw_heating
else:
    # the physical parameters; the buoyancy of one unit of T (rho alpha g dT) takes Ra's
    # place in the body force, and the solver's unwrap non-dimensionalises every one
    deta = uw.expression(r"\Delta\eta", params.uw_deta, "viscosity contrast across the layer")
    eta_ref = uw.expression(r"\eta_r", units.uw_eta_ref, "viscosity at the basal temperature")
    kappa = uw.expression(r"\kappa", units.uw_kappa, "thermal diffusivity")
    rho0 = uw.expression(r"\rho_0", units.uw_rho, "reference density")
    alpha = uw.expression(r"\alpha", units.uw_alpha, "thermal expansivity")
    gravity = uw.expression(r"g", units.uw_gravity, "gravity")
    delta_T = uw.expression(r"\Delta T", units.uw_dT, "temperature drop across the layer")
    Ra = rho0 * alpha * gravity * delta_T
    tau0 = uw.expression(r"\tau_0", units.uw_yield_0, "yield stress at the surface")
    tau1 = uw.expression(r"\tau_1", units.uw_yield_grad, "yield stress gradient with depth")
    H = uw.expression(r"H", units.uw_heat_rate, "internal heating as a rate of temperature rise")

    def _nd(value):
        """A plain float in model units, through the library's crossing."""
        return float(uw.non_dimensionalise(value))

    def _solver_sees(expr):
        """The number the solver's kernels see for ``expr`` (the unwrap the JIT uses)."""
        return float(uw.function.expressions.unwrap_expression(expr, mode="nondimensional"))

    def _phys(value, dims, unit):
        """``value`` in model units as a float in ``unit`` (dims: Pint dimensionality)."""
        return float(uw.dimensionalise(float(value), dims).to(unit).magnitude)

    VEL, TIME, LEN, STRESS = ({"[length]": 1, "[time]": -1}, {"[time]": 1}, {"[length]": 1},
                              {"[mass]": 1, "[length]": -1, "[time]": -2})
    heating = _solver_sees(H)
    # Ra from the quantities: their product is dimensionless but carries km^3 / m^3, which
    # uw.non_dimensionalise does not reduce (it returns 0.02386 for TA's 2.386e7), so Pint's .to
    _ra_q = (units.uw_rho * units.uw_alpha * units.uw_gravity * units.uw_dT
             * units.uw_depth ** 3 / (units.uw_kappa * units.uw_eta_ref))
    derived = {
        "Ra": float(_ra_q.to("dimensionless").magnitude), "Ra_non_dimensionalise": _nd(_ra_q),
        "Ra_solver": _solver_sees(Ra), "tau0": _solver_sees(tau0), "tau1": _solver_sees(tau1),
        "H": heating, "deta": float(params.uw_deta), "eta_ref_solver": _solver_sees(eta_ref),
        "kappa_solver": _solver_sees(kappa)}
    scales = {"cm_per_yr": _phys(1.0, VEL, "cm/year"), "Myr": _phys(1.0, TIME, "Myr"),
              "km": _phys(1.0, LEN, "km"), "MPa": _phys(1.0, STRESS, "MPa")}
    uw.pprint("scaled run: reference quantities "
              + ", ".join(f"{k} {getattr(units, k)}" for k in ("uw_depth", "uw_kappa", "uw_eta_ref", "uw_dT")))
    uw.pprint("  derived (what the solver sees): " + ", ".join(f"{k} {v:.17g}" for k, v in derived.items()))
    uw.pprint("  one model unit is: " + ", ".join(f"{v:.6g} {k}" for k, v in scales.items()))
    uw.pprint(f"  plate age {params.uw_age_sub:g} = {_phys(params.uw_age_sub, TIME, 'Myr'):.4g} Myr, "
              f"plate thickness 2 sqrt(age) = {_phys(2 * np.sqrt(params.uw_age_sub), LEN, 'km'):.4g} km; "
              f"interior viscosity (T {params.uw_T_interior:g}) deta^{1 - params.uw_T_interior:g} eta_ref = "
              f"{float(params.uw_deta) ** (1 - params.uw_T_interior):.4g} x eta_ref")

adv = uw.systems.AdvDiffusion(base, T_b, V_b.sym, order=1)
adv.constitutive_model = uw.constitutive_models.DiffusionModel
adv.constitutive_model.Parameters.diffusivity = kappa if SCALED else 1
adv.f = H


def hot_top_window(rel_arc, lib=np):
    """1 where the surface is held hot (uw_top_hot): on the overriding side between
    uw_top_hot_start past the trench and the same distance short of the antipode, with
    tanh ramps; numpy or sympy."""
    start, ramp = float(params.uw_top_hot_start), max(float(params.uw_over_ramp), 1e-6)
    if int(params.uw_top_hot) == 2:
        # a fixed ridge: a patch of half-width uw_ridge_patch about the antipode of the trench
        dist = np.pi * r_o - (lib.Abs(rel_arc) if lib is sympy else np.abs(rel_arc))
        return (1 - lib.tanh((dist - float(params.uw_ridge_patch)) / ramp)) / 2
    far = np.pi * r_o - start
    return (1 + lib.tanh((rel_arc - start) / ramp)) * (1 + lib.tanh((far - rel_arc) / ramp)) / 4


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
if params.uw_heal_time_lid > 0:
    heal_rate = heal_rate + 1 / params.uw_heal_time_lid
fault_damage_b = uw.discretisation.MeshVariable("fault_damage", base, 1, degree=1)
strain_adv.f = edot_p_b.sym[0] + fault_damage_b.sym[0] - gamma_b.sym[0] * heal_rate
# the strain-rate invariant of the base velocity, for the "rate" law and the trench advection
_E_b = (V_b.sym.jacobian(base.X) + V_b.sym.jacobian(base.X).T) / 2
edot_total_b = sympy.sqrt((_E_b[0, 0] ** 2 + _E_b[1, 1] ** 2 + 2 * _E_b[0, 1] ** 2) / 2)
trench_advect = bool(params.uw_trench_advect) or params.uw_fault_law == "rate"


def onto(points):
    return clamp_radii(np.asarray(points, dtype=float), r_o, r_i, inset=1.0e-10)


def model_xy(var):
    """A mesh variable's DOF coordinates in model units (layer depths), the coordinates
    the DM, evaluate and this driver's geometry work in: ``.coords``, which a units run
    makes dimensional, so there ``.coords_nd``."""
    return var.coords_nd if SCALED else var.coords


def swarm_xy():
    """The particles' coordinates in model units: ``crust_swarm.coords``, which a units run
    makes dimensional (a Pint array in metres), so there the model-unit store its docstring
    names, ``_particle_coordinates.data``: the swarm has no ``coords_nd``, and
    uw.non_dimensionalise(crust_swarm.coords) raises TypeError ("only 0-dimensional arrays
    can be converted to Python scalars", units.py:888)."""
    if SCALED:
        return np.asarray(crust_swarm._particle_coordinates.data, dtype=float)
    return crust_swarm.coords


def wrap(angle):
    return (angle + np.pi) % (2 * np.pi) - np.pi


def fault_trace(fault, coarsening=1):
    """A fault's spine (from just above the outer wall to its tip) and the trace to cut
    (trace_inset() finest rungs inside the wall), at ``coarsening`` times the rung
    spacing; the dip angle phi is measured below the local horizontal from +theta. A
    fault with ``points`` (the crust-following law) is that polyline, already at the
    rung spacing with its surface end above the wall."""
    if "points" in fault:
        spine = np.asarray(fault["points"], dtype=float)[::coarsening]
        return spine, spine[np.hypot(spine[:, 0], spine[:, 1]) <= r_o - trace_inset() * S]
    theta_t, phi = fault["theta"], np.deg2rad(fault["dip"])
    r_hat = np.array([np.cos(theta_t), np.sin(theta_t)])
    t_hat = np.array([-np.sin(theta_t), np.cos(theta_t)])
    down_dip = np.cos(phi) * t_hat - np.sin(phi) * r_hat
    top = r_hat * (r_o + 0.02)
    b = top @ down_dip
    c = top @ top - (r_o - fault["depth"]) ** 2
    length = -b - np.sqrt(b * b - c)
    block = 2 ** int(params.uw_chain)
    n = block * max(1, int(round(length / (block * S))))
    spine = np.array([top + down_dip * (length * i / n) for i in range(n + 1)])[::coarsening]
    return spine, spine[np.hypot(spine[:, 0], spine[:, 1]) <= r_o - trace_inset() * S]


def trace_inset():
    """How many rungs inside the wall a trace stops: three for the split (the cut cannot
    reach the wall; the isotropic bridge covers the rest), uw_ti_trace_inset for a TI band,
    which outcrops and is its own bridge."""
    return float(params.uw_ti_trace_inset) if TI else 3.0


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
    # the last resort, on the finest level only (a chain level that refuses is welded).
    # (the network mesher with ligament seams DEADLOCKED in parallel on a four-band set,
    # 2026-10-18: one rank raised inside the CAD call, the others waited; not retried)
    attempts = [(1, 0.7, 1.0, "gather", "ladder"), (1, 0.7, 1.25, "gather", "ladder"),
                (2, 0.7, 1.0, "gather", "ladder"), (1, 0.7, 1.5, "gather", "ladder")]
    for n, (rings, clearance, widen, seams, mesher) in enumerate(attempts):
        try:
            mesh, info = place_fault_ribbon_2d(
                host, [(name, trace) for name, _, trace in pieces], width * widen,
                spines=[(name, spine) for name, spine, _ in pieces], margin_rings=rings,
                clearance=clearance, split=not TI, mesher=mesher, seams=seams)
            if n:
                uw.pprint(f"  placed with margin_rings {rings}, clearance {clearance}, width x{widen}, "
                          f"seams {seams}, mesher {mesher}")
            return mesh, info, {name: (spine, trace) for name, spine, trace in pieces}
        except (RuntimeError, ValueError) as err:
            retryable = any(s in str(err) for s in ("crosses itself", "domain wall", "ligament", "seam"))
            if not retryable or n == len(attempts) - 1:
                raise RuntimeError(str(err))


def fault_depth_cap():
    """The deepest a fault may reach: uw_fault_depth_max, or with uw_fault_cut_lid the
    lid depth of the last record plus a margin if that is deeper."""
    cap = float(params.uw_fault_depth_max)
    if params.uw_fault_cut_lid and records:
        cap = max(cap, float(records[-1]["lid_depth"]) + float(params.uw_fault_lid_margin))
    return cap


def depth_target(line, fault):
    """The depth a fitted line asks of its fault, with hysteresis: the fit's bottom is the
    deepest inlier ROW of the detection grid (rows 0.008 apart, the same as the rebuild
    threshold 2S), so a one-row flip on round-off noise decided rebuilds (kaiju, step
    3591 of the Ra x3 run: 0.116 in three runs, 0.108 in a fourth agreeing to 1e-6 in
    vrms). A change smaller than uw_depth_hysteresis keeps the fault's depth."""
    target = float(np.clip(line["depth_bottom"], params.uw_fault_depth_min, fault_depth_cap()))
    if abs(target - fault["depth"]) <= float(params.uw_depth_hysteresis):
        return float(fault["depth"])
    return target


def keep_apart(faults, slips, damage, events):
    """Shorten the weaker of any two faults whose spines come within uw_fault_clearance
    of each other, so the mesher never has to carve two ribbons through one cell (a
    conjugate pair closing into a V hung gmsh on the surgery rank, 2026-10-21, at a
    separation of 0.2 fine cells). The weaker fault is the one with less slip (then
    less line damage, then the younger); it loses depth in rung steps until it clears,
    and retires if it cannot clear at the shallowest depth allowed."""
    clearance = float(params.uw_fault_clearance)
    if clearance <= 0 or len(faults) < 2:
        return

    def strength(f):
        return (slips.get(f["name"], 0.0) or 0.0, damage.get(f["name"], 0.0) or 0.0, -int(f["name"][1:]))

    changed = True
    while changed:
        changed = False
        spines = {f["name"]: fault_trace(f)[0] for f in faults}
        for i in range(len(faults)):
            for j in range(i + 1, len(faults)):
                a, b = faults[i], faults[j]
                if spine_separation(spines[a["name"]], spines[b["name"]]) >= clearance:
                    continue
                weak, strong = (a, b) if strength(a) < strength(b) else (b, a)
                depth = weak["depth"]
                while depth - S >= params.uw_fault_depth_min:
                    depth -= S
                    trial = dict(weak, depth=depth)
                    if spine_separation(fault_trace(trial)[0], spines[strong["name"]]) >= clearance:
                        break
                else:
                    depth = None
                if depth is None:
                    faults.remove(weak)
                    events.append(f"retired {weak['name']} at {np.degrees(weak['theta']):.1f} deg "
                                  f"(converges on {strong['name']} at every depth)")
                else:
                    events.append(f"shortened {weak['name']} to depth {depth:.3f} (clear of {strong['name']} "
                                  f"by {clearance:.2f})")
                    weak["depth"] = float(depth)
                changed = True
                break
            if changed:
                break


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
    first attempt's F0, the last one's final state), the last attempt's linear solves,
    the preconditioner fallbacks among the warnings caught, and the solve's wall times."""
    rec = dict(attempts[-1])
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


def parabola_fit(pts):
    """A parabola through a polyline's points, least squares in the frame of its chord
    (distance along the chord, offset from it). A marker contour wiggles at the cell
    scale, and the ladder places every vertex verbatim (the wiggles become kinks in the
    band and in the slip direction); the parabola keeps the trace's position and
    curvature only. Returns the curve as a function of distance along the chord (s = 0
    at the first point, negative before it) and the chord length."""
    pts = np.asarray(pts, dtype=float)
    chord = pts[-1] - pts[0]
    L = max(np.linalg.norm(chord), 1e-12)
    e = chord / L
    nrm = np.array([-e[1], e[0]])
    s = (pts - pts[0]) @ e
    d = (pts - pts[0]) @ nrm
    c = np.polyfit(s, d, 2)

    def curve(ss):
        ss = np.asarray(ss, dtype=float)
        return pts[0] + ss[..., None] * e + np.polyval(c, ss)[..., None] * nrm

    return curve, L


def crust_base_curve(faults, cap):
    """The base of the crust layer from the crust particles (the marker's proxy is one
    cell thick and too smeared to contour: values 0.2-0.6 with gaps on B1 at step 60;
    the particles themselves draw the layer cleanly). The subducted crust, particles with
    the marker set deeper than 1.25 layer thicknesses and no deeper than the cap plus two,
    is gathered to every rank; the cluster nearest the fault's trench (or holding the
    shallowest subducted particle) and connected in theta is fitted by a least-squares
    parabola in its own principal frame and offset to its lower envelope (nine particles
    in ten sit above the curve), which is the base. Needs the cloud to reach the cap.
    Collective. Returns the curve as a function of distance along its axis (increasing
    with depth) and the start of the fitted range, or None."""
    xy = np.asarray(swarm_xy(), dtype=float)
    marker = np.asarray(crust_var.array[:, 0, 0]).ravel()
    depth = r_o - np.hypot(xy[:, 0], xy[:, 1])
    sel = (marker > 0.5) & (depth > 1.25 * crust_thick) & (depth <= cap + 2.0 * crust_thick)
    P = np.c_[uw.utilities.gather_data(xy[sel, 0], bcast=True), uw.utilities.gather_data(xy[sel, 1], bcast=True)]
    if len(P) < 12:
        return None
    depth = r_o - np.hypot(P[:, 0], P[:, 1])
    theta = np.arctan2(P[:, 1], P[:, 0])
    # the clusters: particles connected in theta (gaps under 0.03 rad); stray crust
    # elsewhere (the ridge, stripped blobs) makes small or shallow ones
    order = np.argsort(theta)
    pieces = [p for p in np.split(order, np.flatnonzero(np.diff(theta[order]) > 0.03) + 1) if len(p) >= 12]
    if faults:
        hint = faults[0]["theta"]
        pieces = [p for p in pieces if np.abs(wrap(theta[p] - hint)).min() < 0.4]
        pieces.sort(key=lambda p: np.abs(wrap(theta[p] - hint)).min())
    else:
        pieces.sort(key=lambda p: -depth[p].max())  # the slab's crust is the one that goes deepest
    if not pieces or depth[pieces[0]].max() < cap:
        return None
    piece = pieces[0]
    Q = P[piece]
    mu = Q.mean(axis=0)
    e = np.linalg.svd(Q - mu, full_matrices=False)[2][0]
    nrm = np.array([-e[1], e[0]])
    if nrm @ mu > 0:
        nrm = -nrm                                   # the normal points down, away from the surface
    s, d = (Q - mu) @ e, (Q - mu) @ nrm
    if depth[piece][np.argmin(s)] > depth[piece][np.argmax(s)]:
        e, s = -e, -s                                # s increases with depth
    coef = np.polyfit(s, d, 2)
    off = float(np.quantile(d - np.polyval(coef, s), 0.9))

    def curve(ss):
        ss = np.asarray(ss, dtype=float)
        return mu + ss[..., None] * e + (np.polyval(coef, ss) + off)[..., None] * nrm

    return curve, float(s.min())


def slab_top_curve(faults, cap):
    """The slab top where there is no crust marker: the slab marker's 0.5 contour on the
    polar grid from the surface down to the cap (the compositional slab's proxy is crisp).
    The piece taken is the one whose surface end is nearest the fault's trench when there
    is a fault, else the one reaching the cap by the shortest path; its least-squares
    parabola is fitted below the top rows, where the contour hooks along the wall.
    Collective. Returns the curve and the start of the fitted range, or None."""
    import contourpy
    th, dep, xy = polar_grid(r_o, n_theta=1440, depth_max=0.5, n_depth=64)
    m = np.asarray(uw.function.global_evaluate(markers["slab"][0].sym[0], onto(xy))).reshape(len(dep), len(th))
    best, best_score = None, np.inf
    for line in contourpy.contour_generator(th, dep, m).lines(0.5):
        line = np.asarray(line, dtype=float)
        if line[-1, 1] < line[0, 1]:
            line = line[::-1]                        # the surface end first
        if line[0, 1] > dep[1] or line[:, 1].max() < cap:
            continue
        k = int(np.argmax(line[:, 1] >= cap))        # the first point at or below the cap
        w = (cap - line[k - 1, 1]) / max(line[k, 1] - line[k - 1, 1], 1e-12)
        path = np.vstack([line[:k], line[k - 1] + w * (line[k] - line[k - 1])])
        r = r_o - path[:, 1]
        pts = np.c_[r * np.cos(path[:, 0]), r * np.sin(path[:, 0])]
        if faults:
            score = abs(wrap(path[0, 0] - faults[0]["theta"]))
            if score > np.deg2rad(params.uw_line_match):
                continue
        else:
            score = np.linalg.norm(np.diff(pts, axis=0), axis=1).sum()
        if score < best_score:
            best, best_score = pts, score
    if best is None:
        return None
    buried = (r_o - np.hypot(best[:, 0], best[:, 1])) >= 0.012
    curve, _ = parabola_fit(best[buried] if buried.sum() >= 4 else best)
    return curve, 0.0


def crust_fault_points(faults):
    """The fault that follows the weak crust: the base of the crust layer when the run
    carries the crust marker (crust_base_curve; Sandiford & Moresi 2019, the fault is the
    base of the weak crust), else the compositional slab's top (slab_top_curve). The
    fault is the fitted parabola down to the depth cap from its up-dip end: walking up
    from the fitted points, where it crosses the wall or, if first, its shallowest point
    (within uw_fault_surface_gap crust thicknesses of the wall, else no fault: the base
    of the crust on the incoming plate is a thickness deep). Above that end it is a
    straight stub along the chord to 0.03 deep, out to 0.02 above the wall; resampled at
    the rung spacing. Round a broad hinge the parabola can run just under the surface for
    tens of degrees before it crosses (demo step 39: 0.005-0.022 deep from -5 to -30
    deg), and a band round that arm leaves the domain. The surface is the placement's
    business: the cut stops three rungs inside the wall (fault_trace) and the ribbon's TI
    zone covers the rest. Collective. Returns the points and (theta, dip, depth) in the
    fault's usual terms, theta and dip where the stub crosses the wall, or None."""
    cap = fault_depth_cap()
    got = crust_base_curve(faults, cap) if crust_on else slab_top_curve(faults, cap)
    if got is None:
        return None
    curve, s_lo = got

    def depth(s):
        return r_o - np.hypot(*curve(s))

    s_top, step = s_lo, 0.005
    while depth(s_top) > 0 and depth(s_top - step) < depth(s_top) and s_top > s_lo - 0.5:
        s_top -= step
    if depth(s_top) <= 0:
        s_top = brentq(depth, s_top, s_top + step)
    elif depth(s_top) > params.uw_fault_surface_gap * crust_thick:
        top = curve(s_top)
        uw.pprint(f"  crust fault: the fit's shallowest point is {depth(s_top):.4f} deep at "
                  f"{np.degrees(np.arctan2(top[1], top[0])):.1f} deg (gap "
                  f"{params.uw_fault_surface_gap * crust_thick:.4f})")
        return None                                  # the parabola turns away below the wall
    s_cap = s_lo
    while depth(s_cap) < cap and s_cap < s_lo + 1.0:
        s_cap += step
    if depth(s_cap) < cap:
        return None                                  # the parabola turns up before the cap
    s_cap = brentq(lambda s: depth(s) - cap, s_cap - step, s_cap)
    inner = curve(np.linspace(s_top, s_cap, 400))
    top = inner[0]
    below = inner[np.argmin(np.abs(r_o - np.hypot(inner[:, 0], inner[:, 1]) - 0.03))]
    down = below - top
    down /= max(np.linalg.norm(down), 1e-12)

    def up_to(radius):                                # distance up the chord from top to radius
        b = top @ -down
        return -b + np.sqrt(b * b - (top @ top - radius ** 2))

    at_wall = top - up_to(r_o) * down
    theta_t = float(np.arctan2(at_wall[1], at_wall[0]))
    r_hat = at_wall / np.linalg.norm(at_wall)
    t_hat = np.array([-r_hat[1], r_hat[0]])
    dip = float(np.degrees(np.arctan2(-down @ r_hat, down @ t_hat)))
    stub = top - np.outer(np.linspace(up_to(r_o + 0.02), 0.0, 20)[:-1], down)
    poly = resample_polyline(np.vstack([stub, inner]), S, 2 ** int(params.uw_chain))
    radius = np.hypot(poly[:, 0], poly[:, 1])
    return poly, theta_t, dip, float((r_o - radius).max())


def wquantile(x, w, q):
    """The q-quantile of x with weights w."""
    o = np.argsort(x)
    c = np.cumsum(w[o])
    return float(np.interp(q * c[-1], c, x[o]))


def crust_envelope_points(faults):
    """The fault on the base of the crust layer, located without an assumed shape (the
    parabola of crust_fault_points cannot follow a broad hinge). In x = arc length at the
    wall: the subducted crust is the particles deeper than 1.25 crust thicknesses; the
    incoming plate lies on the side where the crust at the wall is, relative to the crust
    below cap/2, and the base faces it. Marching up from the cap in steps of 0.0025, the
    base at each depth is the 10th percentile toward the incoming side of the subducted
    crust in the run (gaps over 2 thicknesses split runs) nearest the base one step deeper,
    the particles weighted by a Gaussian in depth (half a thickness); a depth with no crust
    near the previous base is skipped, a gap over 0.03 or a march short of the cap gives no
    fault. Smoothed by a local quadratic in depth (Gaussian, 0.015). Above its shallowest
    point the base goes straight to the wall at its own slope over the top 0.03, dipping at
    least uw_fault_top_dip_min; no fault if it meets the wall over uw_fault_trench_tol from
    the particle trench (the overriding-side end of the crust at the wall). A stub to 0.02
    above the wall; resampled at the rung spacing. Theta and dip are measured on that
    placed polyline. Collective. Returns (points, theta, dip, depth, info) or None; info
    carries the locator, its raw trace (x, depth before resampling), the trench gap and the
    unfloored top dip. Tested offline on 40 stored checkpoints (kaiju-launch/crust_fit)."""
    cap = fault_depth_cap()
    ct = crust_thick
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
    th = hint + wrap(theta - hint)
    near = np.abs(th - hint) < 0.4
    x, depth = r_o * th[near], depth[near]
    sub = depth > 1.25 * ct
    deep = sub & (depth > 0.5 * cap) & (depth <= cap + 2 * ct)
    sh = depth < 0.5 * ct
    if deep.sum() < 12 or sh.sum() < 4:
        uw.pprint("  crust fault (envelope): no subducted crust below cap/2, or none at the wall")
        return None
    xd = np.sort(x[deep])
    runs = np.split(xd, np.flatnonzero(np.diff(xd) > r_o * 0.03) + 1)
    xdeep = float(np.median(min(runs, key=lambda r: np.abs(r - r_o * hint).min())))
    inc = 1.0 if np.median(x[sh]) > xdeep else -1.0
    h_z, h_s, dz, q = 0.5 * ct, 0.015, 0.0025, 0.1
    zs = np.arange(cap, 1.25 * ct, -dz)
    base = np.full(len(zs), np.nan)
    prev = xdeep
    for j, z in enumerate(zs):
        sel = sub & (np.abs(depth - z) < 2.5 * h_z)
        if sel.sum() < 3:
            continue
        xs, ws = x[sel], np.exp(-0.5 * ((depth[sel] - z) / h_z) ** 2)
        o = np.argsort(xs)
        xs, ws = xs[o], ws[o]
        cut = np.flatnonzero(np.diff(xs) > 2 * ct) + 1
        a, b = min(zip(np.r_[0, cut], np.r_[cut, len(xs)]), key=lambda ab: np.abs(xs[ab[0]:ab[1]] - prev).min())
        if np.abs(xs[a:b] - prev).min() > 2 * ct:
            continue
        base[j] = wquantile(xs[a:b], ws[a:b], q if inc < 0 else 1 - q)
        prev = base[j]
    ok = np.isfinite(base)
    zk, bk = zs[ok][::-1], base[ok][::-1]            # shallow to deep
    if len(zk) < 6 or zk[-1] < cap - 0.03 or np.abs(np.diff(zk)).max() > 0.03 or zk[0] > 4 * ct:
        uw.pprint(f"  crust fault (envelope): the crust base has a gap or misses the cap "
                  f"({len(zk)} depths{f', {zk[0]:.3f}-{zk[-1]:.3f}' if len(zk) else ''})")
        return None
    zg = np.arange(zk[0], cap + 1e-9, dz)
    sm = np.empty(len(zg))
    for j, z in enumerate(zg):
        w = np.exp(-0.5 * ((zk - z) / h_s) ** 2)
        A = np.c_[np.ones_like(zk), zk - z, (zk - z) ** 2] * np.sqrt(w)[:, None]
        sm[j] = np.linalg.lstsq(A, bk * np.sqrt(w), rcond=None)[0][0]
    xsh = np.sort(x[sh])
    runs = np.split(xsh, np.flatnonzero(np.diff(xsh) > 2 * ct) + 1)
    run = min(runs, key=lambda r: np.abs(r - sm[0]).min())
    xt = float(np.quantile(run, 0.01 if inc > 0 else 0.99))
    top = zg <= zg[0] + 0.03
    slope = np.polyfit(zg[top], sm[top], 1)[0]       # dx/dz; going up the base moves toward inc
    top_dip = float(np.degrees(np.arctan2(1.0, max(-slope * inc, 1e-12))))
    run_len = float(np.clip(-slope * inc, 0.0, 1.0 / np.tan(np.radians(params.uw_fault_top_dip_min))))
    xa = sm[0] + inc * run_len * zg[0]
    gap = abs(xa - xt)
    if gap > params.uw_fault_trench_tol:
        uw.pprint(f"  crust fault (envelope): the base meets the wall {gap:.3f} from the particle trench")
        return None
    raw = np.c_[np.r_[xa, sm], np.r_[0.0, zg]]       # (x, depth)
    d = raw[1] - raw[0]
    pol = np.vstack([raw[0] - d * (0.02 / d[1]), raw])
    radius = r_o - pol[:, 1]
    poly = resample_polyline(np.c_[radius * np.cos(pol[:, 0] / r_o), radius * np.sin(pol[:, 0] / r_o)],
                             S, 2 ** int(params.uw_chain))
    rp = np.hypot(poly[:, 0], poly[:, 1])
    k = int(np.argmax(rp <= r_o))
    w = (rp[k - 1] - r_o) / max(rp[k - 1] - rp[k], 1e-12)
    at_wall = poly[k - 1] + w * (poly[k] - poly[k - 1])
    theta_t = float(np.arctan2(at_wall[1], at_wall[0]))
    below = poly[np.argmin(np.abs(r_o - rp - 0.03))]
    r_hat = at_wall / np.linalg.norm(at_wall)
    t_hat = np.array([-r_hat[1], r_hat[0]])
    down = (below - at_wall) / max(np.linalg.norm(below - at_wall), 1e-12)
    dip = float(np.degrees(np.arctan2(-down @ r_hat, down @ t_hat)))
    info = {"locator": "envelope", "trench_gap": float(gap), "top_dip_data": top_dip,
            "top_dip_floored": bool(top_dip < params.uw_fault_top_dip_min),
            "particle_trench": float(xt / r_o), "raw": np.c_[raw[:, 0] / r_o, raw[:, 1]].round(6).tolist()}
    uw.pprint(f"  crust fault (envelope): trench {np.degrees(theta_t):.2f} deg, dip {dip:.1f}, top dip from the "
              f"data {top_dip:.1f}{' (floored)' if info['top_dip_floored'] else ''}, trench gap {gap:.3f}")
    return poly, theta_t, dip, float((r_o - rp).max()), info


def ti_band_viscosity(s, faulted, footprint, tag):
    """Swap the solver's viscoplastic host for a transversely isotropic model whose eta_0
    is that host's viscosity and whose eta_1, on the footprint, yields on the resolved
    fault-plane shear gdot = sqrt(|E n|^2 - (n.E n)^2):

        eta_b = max(eta_min_b, min(eta_0, f_b (tau0 + tau1 depth) / (2 gdot) + eta_reg_b))
        eta_1 = eta_0 + fband (eta_b - eta_0)

    with f_b, eta_reg_b, eta_min_b = uw_ti_tau_frac, uw_ti_eta_reg, uw_ti_eta_min (the band's
    own bounds, not the host's floor 1 and rate strengthening). The director is each cell's
    nearest trace segment's normal. f_b -> 0 with small eta_reg_b, eta_min_b is the limit
    of the frictionless split. -uw_ti_check 1 turns the band off (fband = 0). Returns the
    expressions the residual-stress record integrates."""
    mesh = faulted.mesh
    host = s.constitutive_model
    eta_0 = host.viscosity
    fband = uw.discretisation.MeshVariable(f"fband_{tag}", mesh, 1, degree=0, continuous=False)
    director = uw.discretisation.MeshVariable(f"director_{tag}", mesh, mesh.dim, degree=0, continuous=False)
    cells = np.asarray(model_xy(fband))
    on = np.asarray(footprint, dtype=bool) if params.uw_ti_check != 1 else np.zeros(len(cells), dtype=bool)
    fband.array[:, 0, 0] = on.astype(float)
    normals = np.tile([0.0, 1.0], (len(cells), 1))
    for name, (spine, _) in faulted.pieces.items():
        seg = np.diff(spine, axis=0)
        a = spine[:-1]
        L2 = np.maximum((seg ** 2).sum(axis=1), 1e-300)
        idx = np.flatnonzero(on)
        if not len(idx):
            continue
        w = np.clip(((cells[idx, None, :] - a[None]) * seg[None]).sum(axis=2) / L2[None], 0, 1)
        d = np.linalg.norm(cells[idx, None, :] - (a[None] + w[..., None] * seg[None]), axis=2)
        k = np.argmin(d, axis=1)
        t_hat = seg[k] / np.sqrt(L2[k])[:, None]
        normals[idx] = np.c_[-t_hat[:, 1], t_hat[:, 0]]
    director.array[:, 0, :] = normals
    n = sympy.Matrix([director.sym[0], director.sym[1]])
    E = mesh.vector.strain_tensor(faulted.v.sym)
    En = E * n
    gdot = sympy.sqrt(sympy.Max((En.T * En)[0] - ((n.T * En)[0]) ** 2, 0) + 1.0e-12)
    depth = r_o - sympy.sqrt(mesh.X[0] ** 2 + mesh.X[1] ** 2)
    tau_y = tau0 + tau1 * depth
    eta_y = params.uw_ti_tau_frac * tau_y / (2 * gdot) + params.uw_ti_eta_reg
    if params.uw_ti_smooth:    # yield and floor exactly as the host does (Newton through smooth kinks)
        eta_b = host._apply_floor(host._combine_yield(eta_0, eta_y), sympy.Float(params.uw_ti_eta_min))
    else:
        eta_b = sympy.Max(params.uw_ti_eta_min, sympy.Min(eta_0, eta_y))
    eta_1 = eta_0 + fband.sym[0] * (eta_b - eta_0)
    s.constitutive_model = uw.constitutive_models.TransverseIsotropicFlowModel
    s.constitutive_model.Parameters.shear_viscosity_0 = eta_0
    s.constitutive_model.Parameters.shear_viscosity_1 = eta_1
    s.constitutive_model.Parameters.director = n
    at_floor = sympy.Piecewise((1, eta_y < params.uw_ti_eta_min), (0, True))
    at_host = sympy.Piecewise((1, eta_y > eta_0), (0, True))
    return {"fband": fband.sym[0], "director": director, "fband_var": fband, "eta_1": eta_1, "gdot": gdot,
            "tau_y": tau_y, "on_yield": 1 - at_floor - at_host, "at_floor": at_floor, "at_host": at_host}


class FaultedMesh:
    """All the faults placed into a copy of the base's finest level, with the Stokes
    solver, the bridge zones and the P1 fields the renders read."""

    def __init__(self, faults, tag):
        wall = time.perf_counter()
        self.faults = [dict(f) for f in faults]
        self.names = [f["name"] for f in self.faults]
        chain = int(params.uw_chain) if self.faults else 0
        mids = []
        welded = []
        for k in range(chain, 0, -1):
            host = levels[len(levels) - k]
            try:
                mids.append(placed_ladders(host, self.faults, 2 ** k)[0])
            except (RuntimeError, ValueError) as err:
                # not seen in ~300 faulted builds before demo step 39, where the welded mesh
                # (a band along the surface) went out of memory in the next solve
                if not params.uw_weld_ok:
                    raise RuntimeError(f"chain level {2 ** k}S refused, build refused "
                                       f"(-uw_weld_ok 1 welds it): {err}") from err
                uw.pprint(f"  chain level {2 ** k}S refused ({str(err)[:80]}): welded")
                mids.append(host)
                welded.append(f"{2 ** k}S")
        if self.faults:
            self.levels = levels[:len(levels) - chain] + mids if chain else levels
            self.mesh, info, self.pieces = placed_ladders(base, self.faults, 1)
            band = np.asarray(info["band"], dtype=bool)
            # ti: the band's rheology is painted on the footprints (band cells within 0.6 w
            # of the trace), the paint the library's own TI realisation uses
            footprint = np.zeros_like(band)
            for mask in info["footprints"].values():
                footprint |= np.asarray(mask, dtype=bool)
            self.width = float(info["width"])
        else:                  # no fault: the base mesh is the solver's mesh
            self.levels, self.mesh, self.pieces = levels[:-1], base, {}
            band = None
            footprint = None
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
        self.slab = (uw.discretisation.MeshVariable(f"slab_{tag}", mesh, 1, degree=1, continuous=False)
                     if comp_on else None)
        self.over = (uw.discretisation.MeshVariable(f"over_{tag}", mesh, 1, degree=1, continuous=False)
                     if over_on else None)
        # Each fault's bridge: its band cells outside its split's upper tip.
        centroids = np.asarray(model_xy(self.zone))
        radius = np.hypot(centroids[:, 0], centroids[:, 1])
        bridge = np.zeros(len(centroids), dtype=bool)
        if band is None:
            band = bridge
        for name, (spine, trace) in self.pieces.items():
            if TI:             # a TI band outcrops: it is its own bridge
                break
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
        weak = (1 - (1 - params.uw_eta_w) * self.zone.sym[0]) * ridge_factor(
            mesh, r_o, ridges, params.uw_ridge_width, params.uw_ridge_depth, params.uw_ridge_weak)
        M = self.band_mask.sym[0] if self.band_mask is not None else 0
        if crust_on:
            weak = weak * crust_factor_on(mesh, self.crust.sym[0], mask=M)
        if comp_on:
            weak = weak * comp_factor_on(self.slab.sym[0], params.uw_comp_eta, mask=M)
        if over_on:
            weak = weak * comp_factor_on(self.over.sym[0], params.uw_over_eta, mask=M,
                                         window=marker_rheo_window(mesh))
        yield_factor = params.uw_yield_boost * (1 - (1 - params.uw_weak_min) * sympy.Min(
            self.gamma.sym[0] / params.uw_strain_crit, 1))
        asth = ((params.uw_asth, params.uw_asth_top, params.uw_asth_bottom, params.uw_asth_ramp)
                if params.uw_asth < 1 else None)
        self.eta_T = set_viscoplastic(s, self.T.sym[0], deta, tau0, tau1, params.uw_yield_softness,
                                      r_o, weak, yield_factor, asthenosphere=asth,
                                      lower_mantle=((params.uw_lm_eta, params.uw_lm_depth, params.uw_lm_ramp)
                                                    if params.uw_lm_eta != 1 else None),
                                      eta_ref=eta_ref)
        if params.uw_eta_reg > 0:
            # in a units run a viscosity: uw_eta_reg times the basal viscosity
            s.constitutive_model.Parameters.plastic_rate_strengthening = (
                params.uw_eta_reg * eta_ref if SCALED else params.uw_eta_reg)
        bridge_own = params.uw_bridge_eta_min != 1.0 or params.uw_bridge_eta_reg != params.uw_eta_reg
        if bridge_own and not SCALED:
            # the split's bridge zone with its own floor and rate strengthening (the TI band has
            # its own): the zone's x uw_eta_w weakening is otherwise held up by the host's 1 and 10
            Z = self.zone.sym[0]
            s.constitutive_model.Parameters.shear_viscosity_min = 1 + Z * (params.uw_bridge_eta_min - 1)
            s.constitutive_model.Parameters.plastic_rate_strengthening = (
                params.uw_eta_reg + Z * (params.uw_bridge_eta_reg - params.uw_eta_reg))
        self.host_cm = s.constitutive_model
        self.ti = None
        if TI and self.faults and params.uw_ti_check != 2:
            self.ti = ti_band_viscosity(s, self, footprint, tag)
            # for the checkpoint's band record: eta_1/eta_0, and how much of the shear lies in the
            # weak plane (gdot / edot_II: 1 where the director is the shear's own normal)
            # cell means (DG0): a P1 projection averages a two-cell band with its neighbours
            self.ti_ratio = uw.discretisation.MeshVariable(f"ti_ratio_{tag}", mesh, 1, degree=0, continuous=False)
            self.ti_align = uw.discretisation.MeshVariable(f"ti_align_{tag}", mesh, 1, degree=0, continuous=False)
            self.ti_projections = []
            for var, fn in ((self.ti_ratio, self.ti["eta_1"] / self.host_cm.viscosity),
                            (self.ti_align, self.ti["gdot"] / (self.host_cm._strainrate_inv_II + 1.0e-12))):
                proj = uw.systems.Projection(mesh, var)
                proj.uw_function = fn
                self.ti_projections.append(proj)
        buoyancy = params.uw_buoy_T * self.T.sym[0]
        if comp_on:                # the slab's fixed temperature deficit, carried by the particles
            buoyancy = buoyancy - params.uw_comp_dT * clamp01(self.slab.sym[0])
        if over_on:
            buoyancy = buoyancy - params.uw_over_dT * clamp01(self.over.sym[0])
        s.bodyforce = Ra * buoyancy * mesh.CoordinateSystem.unit_e_0
        free_slip_walls(s)
        for name in self.names if not TI else []:
            s.add_fault_bc(0, boundary=name)
        s.tolerance = params.uw_tol
        if params.uw_pres_rtol > 0:
            s._rotated_pres_rtol = float(params.uw_pres_rtol)
            s.petsc_options["fieldsplit_pressure_ksp_rtol"] = float(params.uw_pres_rtol)
        if params.uw_vel_rtol > 0:
            s.petsc_options["fieldsplit_velocity_ksp_rtol"] = float(params.uw_vel_rtol)
        s.consistent_jacobian = "continuation"
        s.newton_switch_rtol = params.uw_newton_switch
        # a painted (TI) band has no split topology for the finest level's strong patch to
        # detect: key the patch on the band explicitly, as the library asks (custom_mg, #629)
        set_custom_fmg(s, self.levels, field_id=0, fac_zone=(band if TI and self.faults else None))
        self.stokes = s
        self.has_guess = False

        eta_eff = s.constitutive_model.viscosity
        self.eta_projection = uw.systems.Projection(mesh, self.log_eta)
        self.eta_projection.uw_function = sympy.log(eta_eff) / sympy.log(10)
        self.ratio_projection = uw.systems.Projection(mesh, self.yield_ratio)
        self.ratio_projection.uw_function = eta_eff / self.eta_T
        cm = self.host_cm      # the viscoplastic host (under a TI model too): its strain-rate invariant
        self.edot_projection = uw.systems.Projection(mesh, self.edot_p)
        self.edot_projection.uw_function = cm._strainrate_inv_II * sympy.Max(
            0, 1 - eta_eff / (self.eta_T * weak))
        self.diagnostics = AnnulusDiagnostics(T_b, self.v, eta_eff, self.eta_T, heating)
        self.t_build = time.perf_counter() - wall
        level_cells = [int(uw.utilities.gather_data(m.dm.getHeightStratum(0)[1], bcast=True).sum())
                       for m in self.levels + [mesh]]
        band_cells = int(uw.utilities.gather_data(int(band.sum()) if band is not None else 0, bcast=True).sum())
        # for the solver record of the step that solves on this mesh
        self.mesh_record = {"levels_cells": level_cells,
                            "band_cells_fraction": band_cells / max(level_cells[-1], 1),
                            "split_pairs": None, "chain_welded": welded,
                            "realisation": params.uw_fault_realisation, "width": self.width}
        described = ", ".join(f"{f['name']} {np.degrees(f['theta']):.2f} deg / dip {f['dip']:.1f} / "
                              f"depth {f['depth']:.3f}" for f in self.faults) or "no fault"
        uw.pprint(f"faulted mesh {tag}: {described}; levels (cells) {level_cells}, "
                  f"built in {self.t_build:.1f} s")

    def split_nudges(self, var):
        """Offsets that put each split copy of ``var``'s DOFs on its own side of its
        fault (Plus at -n, Minus at +n, 0.1 rungs), so an evaluation on a faulted source
        takes each side's own slip."""
        nudge = np.zeros((var.array.shape[0], 2))
        if TI:                 # an unsplit mesh: one copy of every DOF
            return nudge
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

    def _stokes_solve(self, from_rest):
        self.stokes.solve(zero_init_guess=from_rest, picard=params.uw_picard,
                          verbose=bool(params.uw_verbose))
        return self.stokes._rotated_freeslip_info

    def solve(self):
        wall = time.perf_counter()
        self.T.array[:, 0, 0] = np.asarray(
            uw.function.global_evaluate(T_b.sym[0], onto(model_xy(self.T)))).ravel()
        self.gamma.array[:, 0, 0] = np.asarray(
            uw.function.global_evaluate(gamma_b.sym[0], onto(model_xy(self.gamma)))).ravel()
        for name, (var, _, _) in markers.items():
            mine = getattr(self, name)
            mine.array[:, 0, 0] = np.asarray(
                uw.function.global_evaluate(var.sym[0], onto(model_xy(mine)))).ravel()
        t_transfer = time.perf_counter() - wall
        start = "cold" if not self.has_guess else "warm"
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            info = self._stokes_solve(from_rest=not self.has_guess)
            attempts = [nonlinear_record(info)]
            if not info.get("converged") and self.has_guess:
                uw.pprint("  the warm start did not converge: solving from rest")
                self.stokes.newton_switch_rtol = params.uw_newton_switch
                info = self._stokes_solve(from_rest=True)
                attempts.append(nonlinear_record(info))
        for w in caught:           # put the warnings back where they would have gone
            warnings.showwarning(w.message, w.category, w.filename, w.lineno)
        self.stokes.newton_switch_rtol = params.uw_warm_newton_switch
        self.has_guess = True
        slips = {}
        for name in self.names:
            if TI:
                slips[name] = self.ti_slip(name)
                continue
            _, slip, _ = fault_slip(self.stokes, name, info)
            slips[name] = float(uw.utilities.gather_data(
                np.abs(slip).max() if len(slip) else 0.0, bcast=True).max())
        extra = {"ti": self.ti_stress()} if self.ti is not None else {}
        return {
            **extra,
            "newton": info.get("nonlinear_iterations"),
            "vel_its": info.get("vel_its_last"),
            "pres_its": info.get("pres_its_last"),
            "converged": bool(info.get("converged")),
            "slip": slips,
            "slip_max": max(slips.values()) if slips else 0.0,
            "solver": solver_record(info, attempts, start, caught,
                                    {"transfer": t_transfer, "stokes": time.perf_counter() - wall - t_transfer}),
        }

    def ti_slip(self, name):
        """A TI band's slip-equivalent: the tangential velocity jump across the band,
        probed at +-(w/2 + h) along the trace's normals between 0.01 deep and 0.01 above its
        tip (the library prefers a probe to band strain rate x w once w nears h). The largest
        jump, as the split's slip_max is. Collective."""
        _, trace = self.pieces[name]
        trace = np.asarray(trace, dtype=float)
        depth = r_o - np.hypot(trace[:, 0], trace[:, 1])
        seg = np.diff(trace, axis=0)
        t_hat = seg / np.linalg.norm(seg, axis=1)[:, None]
        mid = 0.5 * (trace[1:] + trace[:-1])
        keep = (0.5 * (depth[1:] + depth[:-1]) > 0.01) & (0.5 * (depth[1:] + depth[:-1]) < depth.max() - 0.01)
        if not keep.any():
            return 0.0
        mid, t_hat = mid[keep], t_hat[keep]
        n_hat = np.c_[-t_hat[:, 1], t_hat[:, 0]]
        d = 0.5 * self.width + float(params.uw_cell) / 2 ** int(params.uw_refinement)
        pts = np.vstack([mid + d * n_hat, mid - d * n_hat])
        vel = np.asarray(uw.function.global_evaluate(self.v.sym, onto(pts))).reshape(-1, 2)
        jump = ((vel[:len(mid)] - vel[len(mid):]) * t_hat).sum(axis=1)
        return float(np.abs(jump).max())

    def ti_stress(self):
        """The TI band's residual shear stress against zero (the frictionless split),
        averaged over the footprint and given as fractions of the host's mean yield stress
        there: the whole stress 2 eta_1 gdot, and the two terms of the yielding branch,
        f_b tau_y and 2 eta_reg_b gdot, with the footprint fractions at the floor and at the
        host's own viscosity. Collective."""
        t = self.ti
        mesh = self.mesh
        vals = {k: float(uw.maths.Integral(mesh, t["fband"] * e).evaluate())
                for k, e in (("area", 1), ("stress", 2 * t["eta_1"] * t["gdot"]), ("tau_y", t["tau_y"]),
                             ("term_fb", t["on_yield"] * params.uw_ti_tau_frac * t["tau_y"]),
                             ("term_reg", t["on_yield"] * 2 * params.uw_ti_eta_reg * t["gdot"]),
                             ("at_floor", t["at_floor"]), ("at_host", t["at_host"]))}
        ty = max(vals["tau_y"], 1e-300)
        area = max(vals["area"], 1e-300)
        return {"stress_frac": vals["stress"] / ty, "term_fb_frac": vals["term_fb"] / ty,
                "term_reg_frac": vals["term_reg"] / ty, "floor_frac": vals["at_floor"] / area,
                "host_frac": vals["at_host"] / area, "footprint_area": vals["area"],
                "f_b": params.uw_ti_tau_frac, "eta_reg_b": params.uw_ti_eta_reg, "eta_min_b": params.uw_ti_eta_min}

    def to_base(self, slips=None):
        slips = slips or {}
        V_b.array[:, 0, :] = np.asarray(
            uw.function.global_evaluate(self.v.sym, onto(model_xy(V_b)))).reshape(-1, 2)
        self.edot_projection.solve()
        edot = np.asarray(uw.function.global_evaluate(
            self.edot_p.sym[0], onto(model_xy(edot_p_b)))).ravel()
        edot_p_b.array[:, 0, 0] = np.maximum(edot, 0.0)
        if params.uw_fault_damage > 0:
            self.fault_damage(slips)

    def fault_damage(self, slips):
        """The damage a fault does to its surroundings: at rate uw_fault_damage x its slip,
        within one band width of its line, from the trench to one band width past the
        tip, so the band ahead of the tip saturates and the next fit lengthens the fault."""
        pts = np.asarray(model_xy(fault_damage_b))
        rate = np.zeros(len(pts))
        for f in self.faults:
            spine, _ = self.pieces[f["name"]]
            a, b = spine[0], spine[-1]
            u = (b - a) / np.linalg.norm(b - a)
            b = b + u * 2.0 * W
            d = segment_distance(pts, a, b)
            rate = np.maximum(rate, params.uw_fault_damage * slips.get(f["name"], 0.0) * (d < 2.0 * W))
        fault_damage_b.array[:, 0, 0] = rate

    def render_fields_to_base(self):
        self.eta_projection.solve()
        self.ratio_projection.solve()
        log_eta_b.array[:, 0, 0] = np.asarray(
            uw.function.global_evaluate(self.log_eta.sym[0], onto(model_xy(log_eta_b)))).ravel()
        yield_ratio_b.array[:, 0, 0] = np.asarray(
            uw.function.global_evaluate(self.yield_ratio.sym[0], onto(model_xy(yield_ratio_b)))).ravel()


def sample(th, dep, xy):
    """T, v_r, gamma and edot_plastic at grid points (collective: every rank evaluates
    the same points and so takes the same decisions)."""
    pts = onto(xy)
    shape = (len(dep), len(th))
    T = np.asarray(uw.function.global_evaluate(T_b.sym[0], pts)).reshape(shape)
    v = np.asarray(uw.function.global_evaluate(V_b.sym, pts)).reshape(-1, 2)
    v_r = ((v[:, 0] * pts[:, 0] + v[:, 1] * pts[:, 1]) / np.hypot(pts[:, 0], pts[:, 1])).reshape(shape)
    gamma = np.asarray(uw.function.global_evaluate(gamma_b.sym[0], pts)).reshape(shape)
    edot = np.asarray(uw.function.global_evaluate(edot_p_b.sym[0], pts)).reshape(shape)
    return T, v_r, gamma, edot


def sample_rate(th, dep, xy):
    """T and the total strain-rate invariant at grid points (collective)."""
    pts = onto(xy)
    shape = (len(dep), len(th))
    T = np.asarray(uw.function.global_evaluate(T_b.sym[0], pts)).reshape(shape)
    rate = np.asarray(uw.function.global_evaluate(edot_total_b, pts)).reshape(shape)
    return T, rate


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


def advect_trenches(faults, dt):
    """Each trench moves with the surface velocity of its overriding plate: the plate on
    the side the fault dips under (+theta for a dip below 90 degrees), sampled
    uw_advect_offset beyond the trench, just inside the outer wall. Collective."""
    pts = []
    for f in faults:
        sign = 1.0 if f["dip"] < 90 else -1.0
        th = f["theta"] + sign * params.uw_advect_offset / r_o
        pts.append([(r_o - 0.01) * np.cos(th), (r_o - 0.01) * np.sin(th)])
    v = np.asarray(uw.function.global_evaluate(V_b.sym, onto(np.array(pts)))).reshape(-1, 2)
    for n, f in enumerate(faults):
        th = np.arctan2(pts[n][1], pts[n][0])
        v_theta = -v[n, 0] * np.sin(th) + v[n, 1] * np.cos(th)
        f["theta"] = float(wrap(f["theta"] + v_theta / r_o * dt))


def detect_band(theta_c, half_width, fit_depth=None, prefer=True):
    """The band nearest ``theta_c`` within ``half_width``: trench, dip angle phi, the
    local boundary-layer depth and the band's damage, or None. The line is fitted over
    the band down to ``fit_depth`` only (the depth the fault occupies: a band that kinks
    below it would tilt the fit), and clusters nearer ``theta_c`` are preferred."""
    th, dep, xy = polar_grid(r_o, n_theta=max(41, int(4 * np.degrees(2 * half_width))), depth_max=0.5,
                             n_depth=64, centre=theta_c, half_width=half_width)
    T, v_r, gamma, edot = sample(th, dep, xy)
    found = detect_fault(th, dep, gamma, edot, T, v_r, r_o, params.uw_detect_gamma_sat,
                         params.uw_detect_T_lith,
                         params.uw_detect_depth_max if fit_depth is None else fit_depth,
                         depth_min=params.uw_detect_depth_min,
                         periodic=False, prefer=theta_c if prefer else None)
    if found is None:
        return None
    if abs(wrap(found["theta_t"] - theta_c)) > half_width:
        # a fitted line that reaches the surface outside the searched arc is not this
        # band (measured: a V-topped band fitted from 0.05 d gave a 23 degree line whose
        # trench lay 21 degrees away); the fault keeps its place
        return None
    found["phi"] = found["dip"] if found["direction"] > 0 else 180.0 - found["dip"]
    found["bl_depth"] = boundary_layer_depth(th, dep, T, found["theta_t"], params.uw_bl_T)
    bands = rank_bands(th, dep, gamma, edot, T, v_r, params.uw_detect_gamma_sat,
                       params.uw_detect_T_lith, params.uw_detect_depth_max, min_points=10,
                       periodic=False, r_o=r_o)
    found["damage"] = bands[0][4] if bands else 0.0
    return found


def global_bands():
    th, dep, xy = polar_grid(r_o, n_theta=720, depth_max=0.5, n_depth=48)
    T, v_r, gamma, edot = sample(th, dep, xy)
    return rank_bands(th, dep, gamma, edot, T, v_r, params.uw_detect_gamma_sat, params.uw_detect_T_lith,
                      params.uw_detect_depth_max, min_points=10, r_o=r_o)


def own_window(fault, faults):
    """A fault's search arc: the detection window, shrunk so it stops short of its
    neighbours' bands."""
    others = [abs(wrap(g["theta"] - fault["theta"])) for g in faults if g is not fault]
    half = np.deg2rad(params.uw_detect_window)
    return min([half] + [0.45 * d for d in others])


def as_fault(name, band, depth=None):
    return {"name": name, "theta": float(band["theta_t"]),
            "dip": float(np.clip(band["phi"], params.uw_dip_min, params.uw_dip_max)),
            "depth": float(np.clip(band["bl_depth"] if band.get("bl_depth") is not None
                                   else (depth or params.uw_fault_depth),
                                   params.uw_fault_depth_min, fault_depth_cap()))}


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


def write_ti_band(faulted, step):
    """A TI band's record at a checkpoint: for every footprint cell (on rank 0), its centroid,
    its director, eta_1/eta_0 and gdot/edot_II (the shear's share in the weak plane), as cell
    means (DG0 projections) on the solver mesh. Returns the file name, or None without a TI band."""
    if getattr(faulted, "ti", None) is None:
        return None
    import h5py
    for proj in faulted.ti_projections:
        proj.solve()
    var = faulted.ti["fband_var"]
    on = np.asarray(var.array[:, 0, 0]) > 0.5
    xy = np.asarray(model_xy(var))
    pts = onto(xy) if len(xy) else xy
    ratio = np.asarray(uw.function.global_evaluate(faulted.ti_ratio.sym[0], pts)).ravel()
    align = np.asarray(uw.function.global_evaluate(faulted.ti_align.sym[0], pts)).ravel()
    n = np.asarray(faulted.ti["director"].array[:, 0, :])
    rows = np.c_[xy, n, ratio, align][on]
    allrows = uw.utilities.gather_data(rows.ravel())
    name = f"annulus.ti_band.{step:05d}.h5"
    with uw.selective_ranks(0) as selected:
        if selected:
            with h5py.File(os.path.join(out, name), "w") as h:
                h["cells"] = np.asarray(allrows).reshape(-1, 6)
                h["cells"].attrs["columns"] = "x y n_x n_y eta1_over_eta0 gdot_over_edotII"
    return name


def checkpoint(step, t, records, faulted, faults, next_id, decisions):
    faulted.render_fields_to_base()
    write_ti_band(faulted, step)
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
                           "solver_checkpoint": solver_files, "checkpoint_files": needed,
                           **({"units": units.to_dict(), "derived": derived, "scales": scales} if SCALED else {})},
                          f, indent=1, default=str)
    write_records(records)


# ----------------------------------------------------------------------------- add-on timing
# Measurement runs only (-uw_addon_timing N): the phases of every faulted-mesh build and of
# its first solve, and each level's cells per rank, into <uw_out>/addon_timing.json.
if params.uw_addon_timing:
    import addon_timing
    _clk = addon_timing.install()
    _clk.placements = []
    _addon_placed, _addon_init, _addon_solve = placed_ladders, FaultedMesh.__init__, FaultedMesh.solve
    _addon_warm, _addon_read = FaultedMesh.warm_start, read_solver_fields

    def placed_ladders(host, faults, coarsening):
        snap = _clk.snapshot()
        with _clk.section("conform_split", "placed_ladders"):
            result = _addon_placed(host, faults, coarsening)
        phases, labels, calls, events = _clk.since(snap)
        _clk.placements.append({"coarsening": coarsening, "phases": phases, "labels": labels,
                                "calls": calls, "events": events})
        return result

    def _level_names(fm):
        n, chain = len(levels), (int(params.uw_chain) if fm.faults else 0)
        if not fm.faults:
            return [f"base_L{i}" for i in range(n - 1)] + [f"finest_base_L{n - 1}"]
        return ([f"base_L{i}" for i in range(n - chain)]
                + [f"addon_{2 ** k}S_on_L{n - k}" for k in range(chain, 0, -1)] + ["finest_1S_on_L%d" % (n - 1)])

    def _timed_init(self, faults, tag):
        _clk.placements = []
        snap = _clk.snapshot()
        with _clk.section("solver_setup", "FaultedMesh.__init__"):
            _addon_init(self, faults, tag)
        phases, labels, calls, events = _clk.since(snap)
        with _clk.section("instr", "instr"):
            self._addon_tag = tag
            cells = []
            for name, m in zip(_level_names(self), self.levels + [self.mesh]):
                owned, local = addon_timing.per_rank_cells(m.dm)
                cells.append({"level": name, "owned_per_rank": owned, "local_per_rank": local,
                              "global": int(sum(owned))})
            placements = [{"coarsening": p["coarsening"],
                           "phases": addon_timing.reduce_over_ranks(p["phases"]),
                           "labels": addon_timing.reduce_over_ranks(p["labels"]),
                           "calls": p["calls"], "events": p["events"]} for p in _clk.placements]
            addon_timing.RECORDS.append({
                "record": "build", "tag": tag, "faults": [f["name"] for f in self.faults],
                "t_build_driver": round(self.t_build, 3), "chain_welded": self.mesh_record["chain_welded"],
                "phases": addon_timing.reduce_over_ranks(phases),
                "labels": addon_timing.reduce_over_ranks(labels), "calls": calls, "events": events,
                "placements": placements, "levels": cells})
            addon_timing.dump(out)

    def _timed_solve(self):
        first = not getattr(self, "_addon_solved", False)
        snap = _clk.snapshot()
        with _clk.section("solve", "FaultedMesh.solve"):
            rec = _addon_solve(self)
        if first:
            self._addon_solved = True
            phases, labels, calls, events = _clk.since(snap)
            with _clk.section("instr", "instr"):
                h = (getattr(self.stokes, "_custom_mg", None) or {}).get("hierarchy")
                addon_timing.RECORDS.append({
                    "record": "first_solve", "tag": getattr(self, "_addon_tag", None),
                    "phases": addon_timing.reduce_over_ranks(phases),
                    "labels": addon_timing.reduce_over_ranks(labels), "calls": calls, "events": events,
                    "driver_wall": rec["solver"]["wall"], "newton": rec["newton"], "converged": rec["converged"],
                    "level_transfer_stats": getattr(h, "level_transfer_stats", None),
                    "pc_fallbacks": getattr(self.stokes, "pc_fallbacks", None), "solver_record": rec["solver"]})
                addon_timing.dump(out)
        return rec

    def _timed_warm(self, V, P=None):
        with _clk.section("transfer_warm", "warm_start"):
            return _addon_warm(self, V, P)

    def read_solver_fields(faulted, files):
        with _clk.section("transfer_warm", "read_solver_fields"):
            return _addon_read(faulted, files)

    FaultedMesh.__init__, FaultedMesh.solve, FaultedMesh.warm_start = _timed_init, _timed_solve, _timed_warm


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

    # the surface age: a ramp from the ridge to the trench on each side
    rel = over * wrap(theta - theta_t)                    # positive on the overriding side
    ridge_o, ridge_s = abs(float(params.uw_ridge_over)), abs(float(params.uw_ridge_sub))
    age_thin = float(params.uw_age_thin)
    age_o = params.uw_age_over * np.clip(1 - np.abs(rel) / max(ridge_o, 1e-6), 0, 1)
    age_s = params.uw_age_sub * np.clip(1 - np.abs(rel) / max(ridge_s, 1e-6), 0, 1)
    if not params.uw_over_plate:                          # no overriding plate: the thin layer
        age_o = np.full_like(age_o, age_thin)
    elif params.uw_over_gap > 0:                          # the plate set back from the trench
        w = np.clip((np.abs(rel) * r_o - params.uw_over_gap) / max(params.uw_over_ramp, 1e-6), 0, 1)
        age_o = age_thin + (age_o - age_thin) * w
    if params.uw_cont_age > 0:                            # the continent: a uniform, old lid
        cont_end = float(params.uw_cont_extent) or ridge_o
        in_cont = (rel * r_o >= float(params.uw_over_gap)) & (rel < cont_end)
        age_o = np.where(in_cont, float(params.uw_cont_age), age_o)
    age_surface = np.maximum(np.where(rel >= 0, age_o, age_s), age_thin)
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
    if params.uw_slab_warm_top:
        # signed distance to the plane (positive into the subducting side; beyond the tip the
        # distance to the tip), and the freely diffused one-sided profile
        # the perpendicular distance to the plane everywhere; the profile fades beyond
        # either end of the segment over its own diffusion length, so the tip is rounded
        # on both sides without the cold profile wrapping round into the wedge
        age_end = float(params.uw_age_sub) + tau
        overshoot = np.maximum(s_raw - params.uw_slab_length, 0.0) + np.maximum(-s_raw, 0.0)
        end_factor = erfc(overshoot / (2.0 * np.sqrt(age_end)))
        T_slab = T_i - T_i * end_factor * slab_diffused(n_into, tau, float(params.uw_age_sub))
    else:
        # cold top: T = 0 on the plane, the plate's half-space profile into the subducting
        # side (its age continued down-dip) and a short cooled halo into the wedge, so the
        # field is continuous across the plane; the ends fade as above
        age_end = float(params.uw_age_sub) + tau
        overshoot = np.maximum(s_raw - params.uw_slab_length, 0.0) + np.maximum(-s_raw, 0.0)
        end_factor = erfc(overshoot / (2.0 * np.sqrt(age_end)))
        scale = np.where(n_into >= 0, 2.0 * np.sqrt(age_end), 2.0 * np.sqrt(float(params.uw_slab_wedge_age)))
        T_slab = T_i - T_i * end_factor * erfc(np.abs(n_into) / scale)
    return np.minimum(T_plate, T_slab)


_slab_table = {}


def slab_diffused(signed, tau, age):
    """u / T_i for the one-sided plate profile u0 = erfc(x / 2 sqrt(age)) on x > 0, zero on
    x < 0, diffused freely for time tau: u(x, tau) = int_0^inf G(x - xi, tau) u0(xi) dxi.
    Tabulated once per age on x in [-0.6, 0.6] and tau in [0, tau_max] and interpolated
    bilinearly; the half-space value erfc(x / 2 sqrt(age)) at tau = 0."""
    from scipy.special import erfc
    from scipy.interpolate import RegularGridInterpolator
    tau = np.asarray(tau, dtype=float)
    key = (round(age, 9), float(np.ceil(tau.max() * 1.05 * 1e6) / 1e6) if tau.size else 0.0)
    if key not in _slab_table:
        x = np.linspace(-0.6, 0.6, 1201)
        tau_max = max(key[1], 1e-6)
        taus = np.concatenate([[0.0], np.geomspace(1e-7, tau_max, 120)])
        xi = np.linspace(0.0, 1.2, 2401)
        u0 = erfc(xi / (2.0 * np.sqrt(age)))
        table = np.empty((len(taus), len(x)))
        table[0] = np.where(x > 0, erfc(np.maximum(x, 0) / (2.0 * np.sqrt(age))), 0.0)
        dxi = xi[1] - xi[0]
        for n, t in enumerate(taus[1:], 1):
            G = np.exp(-(x[:, None] - xi[None, :]) ** 2 / (4.0 * t)) / np.sqrt(4.0 * np.pi * t)
            table[n] = (G * u0[None, :]).sum(axis=1) * dxi
        _slab_table[key] = RegularGridInterpolator((taus, x), table, bounds_error=False, fill_value=None)
    f = _slab_table[key]
    xs = np.clip(np.asarray(signed, dtype=float), -0.6, 0.6)
    out = f(np.stack([np.clip(tau, 0.0, key[1]), xs], axis=-1))
    out = np.where(np.abs(np.asarray(signed)) > 0.6, 0.0, out)
    return np.clip(out, 0.0, 1.0)


def layer_marker(xy, thick):
    """1 in a layer ``thick`` thick of the slab state: at the subducting plate's surface
    (from its ridge to the trench) and down the slab's top face (the plane, into the
    subducting side) to the slab's end; the geometry of slab_temperature. The crust is
    the one-cell layer, the compositional slab the plate-thick one."""
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
    h = float(params.uw_cell) / 2 ** int(params.uw_refinement)
    return h / np.sqrt(2.0 * float(params.uw_crust_ppc))


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
            elif nearest is not None:
                var.array[-added:, 0, 0] = old[name][nearest]
    for var, _, _ in markers.values():
        var._update()
    return int(added)


def seed_swarm():
    """Fresh particles over the base mesh with the slab state's markers; with uw_crust_ppc the
    crust layer gets its own denser lattice on top of the swarm's fill."""
    crust_swarm.populate(fill_param=int(params.uw_crust_fill))
    if crust_on and params.uw_crust_ppc > 0:
        crust_swarm.add_particles_with_coordinates(np.ascontiguousarray(crust_layer_points(crust_spacing())))
    for var, _, geometry in markers.values():
        var.array[:, 0, 0] = geometry(swarm_xy())
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


if params.uw_init == "slab" and params.uw_restart < 0:     # a restart of a slab run reads its checkpoint
    T_b.array[:, 0, 0] = slab_temperature(model_xy(T_b))
    V_b.array[:, 0, :] = 0.0
    if swarm_on:
        seed_swarm()
    state = {"t": 0.0, "step": -1}
    faults = ([{"name": "F0", "theta": float(params.uw_theta_trench), "dip": float(params.uw_dip),
                "depth": float(params.uw_fault_depth)}]
              if params.uw_max_faults > 0 and params.uw_fault_law != "crust" else [])
    next_id = 1 if faults else 0
elif params.uw_restart < 0:
    source = os.path.expanduser(params.uw_source)
    for var in (T_b, V_b):
        var.read_timestep("annulus", var.name, params.uw_source_index, outputPath=source)
    if swarm_on:
        restore_swarm(source, params.uw_source_index)
    with open(os.path.join(source, f"state_{params.uw_source_index:05d}.json")) as f:
        state = json.load(f)
    if os.path.exists(os.path.join(source, "records.json")):
        with open(os.path.join(source, "records.json")) as f:
            records = [r for r in json.load(f) if r["step"] <= params.uw_source_index]
    faults = ([{"name": "F0", "theta": float(params.uw_theta_trench), "dip": float(params.uw_dip),
                "depth": float(params.uw_fault_depth)}]
              if params.uw_max_faults > 0 and params.uw_fault_law != "crust" else [])
    next_id = 1 if faults else 0
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
    if "faults" in state:
        faults, next_id = state["faults"], int(state["next_id"])
    else:                      # a single-fault state of annulus_fault.py
        faults = [{"name": "F0", "theta": float(state["theta_trench"]),
                   "dip": float(state.get("dip", params.uw_dip)),
                   "depth": float(state.get("fault_depth", params.uw_fault_depth))}]
        next_id = 1
t, step = float(state["t"]), int(state["step"]) + 1
# the imposed ridges stay where the plates' ridges were at the start (the mantle frame),
# carried through restarts in the state
if params.uw_ridge_weak < 1:
    theta_0 = float(state.get("ridge_origin", faults[0]["theta"] if faults else params.uw_theta_trench))
    ridges = [float(wrap(theta_0 + params.uw_ridge_sub))]
    other = float(wrap(theta_0 - params.uw_ridge_over))
    if abs(wrap(other - ridges[0])) > 0.01:      # one ridge when both plates share it (the antipode)
        ridges.append(other)
else:
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
refused = {}                   # formation trenches the surgery refused: no new fault within 3 deg for a while
last_damage = {}               # each fault's line damage at the last detection
built = faults
if params.uw_restart >= 0:
    k0, n_built, refused, last_damage, built = restored_decisions(state, records, faults)
keep_apart(faults, (records[-1].get("slip") or {}) if records else {}, {}, [])
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
_ra, _tau0, _tau1, _H = ((derived["Ra_solver"], derived["tau0"], derived["tau1"], heating) if SCALED
                         else (params.uw_ra, params.uw_tau0, params.uw_tau1, params.uw_heating))
uw.pprint(f"annulus r_o {r_o:.4f} r_i {r_i:.4f}, Ra {_ra:.4g}, tau1/Ra "
          f"{_tau1 / _ra:.3g}, tau0 {_tau0:.4g}, H {_H:.4g}, "
          f"asthenosphere {params.uw_asth:g} in {params.uw_asth_top:g}-{params.uw_asth_bottom:g}; "
          f"{len(faults)} fault(s); "
          + (f"ridge x{params.uw_ridge_weak:g} at {', '.join(f'{np.degrees(a):.1f}' for a in ridges)} deg "
             f"(width {params.uw_ridge_width:g}, to {params.uw_ridge_depth:g}); " if ridges else "")
          + (f"crust x{params.uw_crust_weak:g}, {crust_thick:.4f} thick, to depth {params.uw_crust_depth:g}; "
             if crust_on else "")
          + (f"compositional slab {params.uw_comp_thick:g} thick, dT {params.uw_comp_dT:g}, eta x{params.uw_comp_eta:g}, "
             f"thermal buoyancy x{params.uw_buoy_T:g}; " if comp_on else "")
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
    if SCALED:
        info.update({"units": units.to_dict(), "derived": derived, "scales": scales})
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
        if ("points" in f) != ("points" in g):
            return True
        if "points" in f:          # a crust-following fault: its polyline moved by more than the rungs
            if polyline_gap(f["points"], g["points"]) > params.uw_rebuild_rungs * S:
                return True
            continue
        if (abs(wrap(f["theta"] - g["theta"])) * r_o > params.uw_rebuild_rungs * S
                or abs(f["dip"] - g["dip"]) > params.uw_rebuild_dip
                or abs(f["depth"] - g["depth"]) > 2 * S):
            return True
    return False


def local_dt_estimates():
    """CHECK ONLY (-uw_units_dt_local 1 in a units run): the two step-size estimates of the
    time loop, the library's own (AdvDiffusion.estimate_dt: the accuracy step and the
    direction-aware cell-crossing time), computed the library's way but from model-unit
    coordinates. In a units run the library takes np.asarray(mesh.X.coords), which is
    dimensional there (metres), as model units: the crossing time comes out 2.9e6 times
    too long, and the first accuracy estimate evaluates the velocity at points outside
    the mesh. Non-dimensional throughout; returns (dt_accuracy before uw_dt_mult, dt_adv)."""
    from mpi4py import MPI
    from underworld3.function.gradient_evaluation import compute_clement_gradient_at_nodes
    from underworld3.meshing.smoothing import _tri_cells
    from underworld3.systems.solvers import _centroid_velocities_nd
    comm = uw.mpi.comm
    coords = np.asarray(uw.non_dimensionalise(base.X.coords), dtype=float)
    if coords.size and abs(np.hypot(coords[:, 0], coords[:, 1]).max() - r_o) > 1e-6 * r_o:
        raise RuntimeError("non-dimensionalised mesh coordinates are not in layer depths")
    # the accuracy step: the field's range over its largest rate of change
    if adv._last_change_rate is not None:
        dt_acc = _nd(adv.estimate_dt())
    else:
        values = np.asarray(adv.u.array).reshape(-1)
        lo = comm.allreduce(float(values.min()) if values.size else np.inf, op=MPI.MIN)
        hi = comm.allreduce(float(values.max()) if values.size else -np.inf, op=MPI.MAX)
        n = coords.shape[0]
        local = 0.0
        if n:
            grad = np.asarray(compute_clement_gradient_at_nodes(adv.u), dtype=float).reshape(n, -1)
            vel = np.asarray(uw.function.evaluate(adv.V_fn, coords), dtype=float).reshape(n, -1)
            local = float(np.abs((vel[:, :grad.shape[1]] * grad).sum(axis=1)).max())
        rate = comm.allreduce(local, op=MPI.MAX)
        dt_acc = 0.02 * (hi - lo) / rate if rate > 0.0 and hi > lo else np.inf
    # the direction-aware crossing time
    vel = _centroid_velocities_nd(adv.V_fn, base)
    speed = np.linalg.norm(vel, axis=1)
    tris = _tri_cells(base.dm)
    centroids = coords[tris].mean(axis=1)
    vhat = np.where(speed[:, None] > 0, vel / np.maximum(speed[:, None], 1.0e-30), 0.0)
    proj = np.einsum("cvd,cd->cv", coords[tris] - centroids[:, None, :], vhat)
    h = np.maximum(proj.max(axis=1) - proj.min(axis=1), 0.0)
    with np.errstate(divide="ignore", invalid="ignore"):
        per = np.where(speed > 0, h / speed, np.inf)
    fin = per[np.isfinite(per)]
    dt_adv = comm.allreduce(float(np.min(fin)) if len(fin) else np.inf, op=MPI.MIN)
    return dt_acc, (dt_adv if np.isfinite(dt_adv) else 0.0)


# ----------------------------------------------------------------------------- time loop
for k in range(k0, k0 + params.uw_steps):
    wall = time.perf_counter()
    events = []
    damage = last_damage
    # for the solver record: what kind of solve this step is, and the phases' wall times
    kind = ("restart_first" if params.uw_restart >= 0 else "init_first") if k == k0 else "ordinary"
    faults_before = list(faulted.names)
    mesh_rec = faulted.mesh_record if k == k0 else None
    t_build = t_warm = 0.0
    if needs_rebuild(faults, faulted.faults) or (params.uw_addon_timing and k0 < k <= k0 + params.uw_addon_timing):
        previous = faulted
        try:
            faulted = FaultedMesh(faults, f"f{n_built}")
        except RuntimeError as err:
            uw.pprint(f"  placement of {[f['name'] for f in faults]} failed ({str(err)[:120]})")
            # A set the surgery refuses: usually a new fault whose band collides with a
            # fading neighbour's. Try again without the weakest-damage old fault (the new
            # one keeps its place); if that fails too, keep the previous set.
            new_names = [f["name"] for f in faults if f["name"] not in previous.names]
            old = [f for f in faults if f["name"] in previous.names]
            retry = None
            if new_names and len(old) > 1:
                weakest = min(old, key=lambda f: damage.get(f["name"], 1.0))
                trial = [f for f in faults if f["name"] != weakest["name"]]
                try:
                    retry = FaultedMesh(trial, f"f{n_built}")
                    faults = trial
                    events.append(f"retired {weakest['name']} at {np.degrees(weakest['theta']):.1f} deg "
                                  f"(its band collided with {new_names})")
                except RuntimeError as err2:
                    uw.pprint(f"  retry without {weakest['name']} failed ({str(err2)[:80]})")
            if retry is not None:
                faulted = retry
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
    if params.uw_addon_timing:
        # the step's wall phases as the run's solver record has them (build, transfer, stokes)
        addon_timing.RECORDS.append({
            "record": "step", "step": step, "k": k, "kind": kind, "tag": getattr(faulted, "_addon_tag", None),
            "driver_wall": {"build": round(t_build, 3), "transfer": round(t_warm + rec["solver"]["wall"]["transfer"], 3),
                            "stokes": round(rec["solver"]["wall"]["stokes"], 3)},
            "newton": rec["newton"], "converged": rec["converged"],
            "cumulative_labels": {k_: round(v_, 4) for k_, v_ in _clk.snapshot()[1].items()}})
        addon_timing.dump(out)
        if k == k0 + params.uw_addon_timing:
            uw.pprint(f"addon timing: done after {params.uw_addon_timing} forced rebuild(s)")
            break
    t_phase = time.perf_counter()
    faulted.to_base(rec["slip"])
    t_to_base = time.perf_counter() - t_phase
    t_phase = time.perf_counter()
    if not SCALED:
        dt_accuracy = params.uw_dt_mult * float(adv.estimate_dt())
        adv.estimate_dt(basis="resolution", direction_aware=True)
        dt_crossing = adv.dt_adv
    elif units.uw_units_dt_local:
        dt_accuracy, dt_crossing = local_dt_estimates()
        dt_accuracy *= params.uw_dt_mult
    else:
        # estimate_dt returns a time with units in a units run (float() of it would be its
        # magnitude in seconds); dt_adv is non-dimensional
        dt_accuracy = params.uw_dt_mult * _nd(adv.estimate_dt())
        adv.estimate_dt(basis="resolution", direction_aware=True)
        dt_crossing = adv.dt_adv
    dt = min(dt_accuracy, params.uw_courant * dt_crossing, params.uw_dt_max)
    adv.solve(timestep=dt)
    strain_adv.solve(timestep=dt)
    gamma_b.array[:, 0, 0] = np.maximum(gamma_b.array[:, 0, 0], 0.0)
    t_energy_strain = time.perf_counter() - t_phase
    t_phase = time.perf_counter()
    if swarm_on:
        crust_swarm.advection(V_b.sym, dt, order=2)
        for var, _, _ in markers.values():
            var._update()
        if (crust_on and params.uw_crust_ppc > 0 and params.uw_crust_refill_every > 0
                and (k + 1) % int(params.uw_crust_refill_every) == 0):
            n_refill = int(uw.utilities.gather_data(refill_crust(), bcast=True).sum())
            if n_refill:
                events.append(f"crust refill: {n_refill} particles")
    t_swarm = time.perf_counter() - t_phase
    t_phase = time.perf_counter()
    t += dt
    if trench_advect:
        advect_trenches(faults, dt)

    damage = {}
    detect_now = (params.uw_fault_law != "none" and k >= params.uw_detect_start
                  and (k - params.uw_detect_start) % params.uw_detect_every == 0)
    if params.uw_fault_law == "lines" and detect_now:
        # N faults fitted to the damage: each existing fault takes the line nearest its
        # trench (by bounded steps), an unmatched line forms a fault, a fault with no
        # line for uw_line_patience detections retires
        th, dep, xy = polar_grid(r_o, n_theta=1440, depth_max=0.5, n_depth=64)
        T, v_r, gamma, edot = sample(th, dep, xy)
        lines = fit_fault_lines(th, dep, gamma, T, r_o, params.uw_line_gamma, params.uw_detect_T_lith,
                                0.02, params.uw_detect_depth_max, params.uw_max_faults + 2,
                                params.uw_line_min_damage, params.uw_line_width,
                                surface_reach=params.uw_line_surface)
        taken = set()
        for f in faults:
            best, best_d = None, np.deg2rad(params.uw_line_match)
            for n, ln in enumerate(lines):
                d = abs(wrap(ln["theta_t"] - f["theta"]))
                if n not in taken and d < best_d:
                    best, best_d = n, d
            if best is None:
                f["misses"] = f.get("misses", 0) + 1
                damage[f["name"]] = 0.0
                continue
            taken.add(best)
            ln = lines[best]
            f["misses"] = 0
            damage[f["name"]] = ln["damage"]
            cap = np.deg2rad(params.uw_detect_max_dtheta)
            f["theta"] = float(f["theta"] + np.clip(wrap(ln["theta_t"] - f["theta"]), -cap, cap))
            phi = float(np.clip(ln["phi"], params.uw_dip_min, params.uw_dip_max))
            f["dip"] = float(f["dip"] + np.clip(phi - f["dip"], -params.uw_detect_max_ddip,
                                                params.uw_detect_max_ddip))
            target = depth_target(ln, f)
            f["depth"] = float(f["depth"] + np.clip(target - f["depth"], -params.uw_detect_max_ddepth,
                                                    params.uw_detect_max_ddepth))
        if k % (10 * params.uw_detect_every) == 0:
            refused.clear()        # the band may have changed enough to place
        for f in list(faults):
            if len(faults) > 1 and f.get("misses", 0) >= params.uw_line_patience:
                faults.remove(f)
                events.append(f"retired {f['name']} at {np.degrees(f['theta']):.1f} deg (no line)")
        sep = np.deg2rad(params.uw_fault_separation)
        for n, ln in enumerate(lines):
            if n in taken or len(faults) >= params.uw_max_faults:
                continue
            if any(abs(wrap(ln["theta_t"] - f["theta"])) < sep for f in faults):
                continue
            if any(abs(wrap(ln["theta_t"] - th)) < np.deg2rad(3.0) for th in refused.values()):
                continue
            new = {"name": f"F{next_id}", "theta": float(ln["theta_t"]),
                   "dip": float(np.clip(ln["phi"], params.uw_dip_min, params.uw_dip_max)),
                   "depth": float(np.clip(ln["depth_bottom"], params.uw_fault_depth_min, fault_depth_cap())),
                   "misses": 0}
            next_id += 1
            faults.append(new)
            events.append(f"formed {new['name']} at {np.degrees(new['theta']):.1f} deg (line damage "
                          f"{ln['damage']:.3f}), dip {new['dip']:.1f}, depth {new['depth']:.3f}")
    elif params.uw_fault_law == "crust" and detect_now and params.uw_max_faults > 0:
        # one fault following the weak crust on the compositional slab's top, from the
        # trench down to the depth cap; it forms at the first detection and never retires
        if params.uw_fault_fit == "envelope":
            found = crust_envelope_points(faults)
        else:
            found = crust_fault_points(faults)
            found = found + ({"locator": "parabola"},) if found is not None else None
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
    elif params.uw_fault_law == "rate" and detect_now:
        # N faults fitted to the strain rate of the lithosphere: each fault takes the line
        # nearest its trench (by bounded steps), an unmatched line forms a fault, a fault
        # whose slip stays below a fraction of the largest for uw_retire_patience
        # detections retires. The damage decides nothing here: it weakens the material.
        th, dep, xy = polar_grid(r_o, n_theta=1440, depth_max=0.5, n_depth=64)
        T, rate = sample_rate(th, dep, xy)
        lith = (T <= params.uw_detect_T_lith) & (dep[:, None] <= params.uw_detect_depth_max)
        rate_ref = float(np.percentile(rate[lith], 99.5)) if lith.any() else 1.0
        rate_n = rate / max(rate_ref, 1e-30)
        lines = fit_fault_lines(th, dep, rate_n, T, r_o, params.uw_rate_frac, params.uw_detect_T_lith,
                                0.02, params.uw_detect_depth_max, params.uw_max_faults + 2,
                                params.uw_rate_min_activity, params.uw_line_width,
                                surface_reach=params.uw_line_surface)
        taken = set()
        for f in faults:
            best, best_d = None, np.deg2rad(params.uw_line_match)
            for n, ln in enumerate(lines):
                d = abs(wrap(ln["theta_t"] - f["theta"]))
                if n not in taken and d < best_d:
                    best, best_d = n, d
            if best is not None:
                taken.add(best)
                ln = lines[best]
                damage[f["name"]] = ln["damage"]
                cap = np.deg2rad(params.uw_detect_max_dtheta)
                f["theta"] = float(f["theta"] + np.clip(wrap(ln["theta_t"] - f["theta"]), -cap, cap))
                phi = float(np.clip(ln["phi"], params.uw_dip_min, params.uw_dip_max))
                f["dip"] = float(f["dip"] + np.clip(phi - f["dip"], -params.uw_detect_max_ddip,
                                                    params.uw_detect_max_ddip))
                target = depth_target(ln, f)
                f["depth"] = float(f["depth"] + np.clip(target - f["depth"], -params.uw_detect_max_ddepth,
                                                        params.uw_detect_max_ddepth))
            else:
                damage[f["name"]] = 0.0
        slip_max = max(rec["slip"].values()) if rec["slip"] else 0.0
        for f in faults:
            idle = rec["slip"].get(f["name"], 0.0) < params.uw_retire_slip_frac * slip_max
            f["idle"] = f.get("idle", 0) + 1 if idle else 0
        if k % (10 * params.uw_detect_every) == 0:
            refused.clear()
        for f in list(faults):
            if len(faults) > 1 and f.get("idle", 0) >= params.uw_retire_patience:
                faults.remove(f)
                events.append(f"retired {f['name']} at {np.degrees(f['theta']):.1f} deg "
                              f"(slip {rec['slip'].get(f['name'], 0.0):.1f} of {slip_max:.1f})")
        sep = np.deg2rad(params.uw_fault_separation)
        for n, ln in enumerate(lines):
            if n in taken or len(faults) >= params.uw_max_faults:
                continue
            if any(abs(wrap(ln["theta_t"] - f["theta"])) < sep for f in faults):
                continue
            if any(abs(wrap(ln["theta_t"] - th_r)) < np.deg2rad(3.0) for th_r in refused.values()):
                continue
            new = {"name": f"F{next_id}", "theta": float(ln["theta_t"]),
                   "dip": float(np.clip(ln["phi"], params.uw_dip_min, params.uw_dip_max)),
                   "depth": float(np.clip(ln["depth_bottom"], params.uw_fault_depth_min, fault_depth_cap())),
                   "idle": 0}
            next_id += 1
            faults.append(new)
            events.append(f"formed {new['name']} at {np.degrees(new['theta']):.1f} deg (rate-area "
                          f"{ln['damage']:.4f} of ref {rate_ref:.3g}), dip {new['dip']:.1f}, depth {new['depth']:.3f}")
    elif detect_now:
        # each fault follows its own band, by bounded steps
        for f in faults:
            band = detect_band(f["theta"], own_window(f, faults), fit_depth=max(f["depth"] + 0.05, 0.15))
            if band is None:
                damage[f["name"]] = 0.0
                continue
            damage[f["name"]] = band["damage"]
            cap = np.deg2rad(params.uw_detect_max_dtheta)
            f["theta"] = float(f["theta"] + np.clip(wrap(band["theta_t"] - f["theta"]), -cap, cap))
            phi = float(np.clip(band["phi"], params.uw_dip_min, params.uw_dip_max))
            f["dip"] = float(f["dip"] + np.clip(phi - f["dip"], -params.uw_detect_max_ddip,
                                                params.uw_detect_max_ddip))
            if band.get("bl_depth") is not None:
                target = float(np.clip(band["bl_depth"], params.uw_fault_depth_min, fault_depth_cap()))
                f["depth"] = float(f["depth"] + np.clip(target - f["depth"], -params.uw_detect_max_ddepth,
                                                        params.uw_detect_max_ddepth))
    if params.uw_fault_law == "bands" and params.uw_global_every and k % params.uw_global_every == 0:
        bands = global_bands()
        sep = np.deg2rad(params.uw_fault_separation)
        # a fault whose band has healed is removed (the last one stays)
        for f in list(faults):
            if len(faults) > 1 and damage.get(f["name"], 1.0) < params.uw_damage_retire:
                faults.remove(f)
                events.append(f"retired {f['name']} at {np.degrees(f['theta']):.1f} deg")
        # a damaged band away from every fault becomes a fault
        for b in bands:
            if len(faults) >= params.uw_max_faults or not b[4] >= params.uw_damage_spawn:
                continue
            if any(abs(wrap(b[0] - f["theta"])) < sep for f in faults):
                continue
            band = detect_band(b[0], np.deg2rad(min(params.uw_detect_window, 0.45 * params.uw_fault_separation * 2)),
                               fit_depth=0.3)
            if band is None:
                continue
            new = as_fault(f"F{next_id}", band)
            next_id += 1
            faults.append(new)
            events.append(f"formed {new['name']} at {np.degrees(new['theta']):.1f} deg (damage {b[4]:.3f}), "
                          f"dip {new['dip']:.1f}, depth {new['depth']:.3f}")
    if detect_now:
        keep_apart(faults, rec["slip"], damage, events)
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
    if SCALED:                 # the physical columns beside the dimensionless ones
        def cm_yr(v):
            return _phys(v, VEL, "cm/year")
        record.update({
            "t_Myr": _phys(t, TIME, "Myr"), "dt_Myr": _phys(dt, TIME, "Myr"),
            "vrms_cm_yr": cm_yr(record["vrms"]), "vsurf_rms_cm_yr": cm_yr(record["vsurf_rms"]),
            "slip_max_cm_yr": cm_yr(record["slip_max"]),
            "slip_cm_yr": {k: cm_yr(v) for k, v in record["slip"].items()},
            "plates_cm_yr": {k: [cm_yr(a), cm_yr(b)] for k, (a, b) in record["plates"].items()},
            "trench_rate_cm_yr": {k: cm_yr(v) for k, v in record.get("trench_rate", {}).items()},
            "lid_depth_km": _phys(record["lid_depth"], LEN, "km"),
            "fault_depth_km": _phys(record["fault_depth"], LEN, "km")})
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
    if SCALED:
        uw.pprint(f"      t {record['t_Myr']:.3f} Myr, vrms {record['vrms_cm_yr']:.4f} cm/yr, "
                  f"vsurf_rms {record['vsurf_rms_cm_yr']:.4f} cm/yr, lid {record['lid_depth_km']:.0f} km")
    uw.pprint(f"step {step:5d} t {t:.5f} dt {dt:.2e} | vrms {record['vrms']:8.2f} "
              f"M {record['mobility']:.3f} lid {record['lid_depth']:.3f} T_mid {record['T_mid']:.3f} "
              f"slip {record['slip_max']:.2f} | faults {described} | "
              f"newton {record['newton']} conv {record['converged']} "
              f"{record['t_stokes']:.1f}/{record['t_step']:.1f} s", flush=True)
    if step % params.uw_ckpt_every == 0 or k == k0 + params.uw_steps - 1:
        t_phase = time.perf_counter()
        checkpoint(step, t, records, faulted, faults, next_id,
                   {"k": k + 1, "n_built": n_built, "refused": refused, "last_damage": last_damage})
        # the next checkpoint writes it; the last one is written here
        solver["wall"]["checkpoint"] = round(time.perf_counter() - t_phase, 3)
        if k == k0 + params.uw_steps - 1:
            write_records(records)
    step += 1

uw.pprint("done")
