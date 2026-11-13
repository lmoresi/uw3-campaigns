"""Earth units for the slab workbench: the one place where an input given in Earth units becomes
one of the model's numbers.

The model is dimensionless. One length is the mantle's depth, one time is that depth squared
over the diffusivity, one temperature is the drop from the surface to the base. A viscosity is
counted in eta_0, the viscosity the Rayleigh number is written on, and a stress in
eta_0 kappa / D^2. eta_0 follows from the reference viscosity (given at the potential
temperature), the activation energy and the two temperatures: the model's viscosity law is
eta_0 deta^(1 - T_i) exp(E / (T + T0) - E / (T_i + T0)) with deta = exp(E / (T_i + T0)^2), so
eta_0 = eta_ref / deta^(1 - T_i).

``to_model`` takes the Earth-unit options and returns the model's values under the names the
driver uses (age_sub, ra, tau0, ...) with the size of one model unit of each kind.

Plain Python (no numpy, no underworld3): a tool on a login node can import it.
"""
import math

DEPTH_KM = 2900.0           # one model length: the mantle's depth
DIFFUSIVITY = 1.0e-6        # m^2/s
DENSITY = 3300.0            # kg/m^3
EXPANSIVITY = 3.0e-5        # 1/K
GRAVITY = 9.81              # m/s^2
CONDUCTIVITY = 3.138        # W/m/K (Stein & Stein 1992, GDH1)
GAS_CONSTANT = 8.314462618  # J/mol/K
SURFACE_K = 273.0           # the surface temperature: 0 C in the options
YEAR_S = 365.25 * 86400.0

# (the option in Earth units, the model's name for it, the kind of unit)
SCALED = [
    ("uw_T_potential_c", "T_interior", "c"),
    ("uw_heal_T_c", "heal_T", "c"),
    ("uw_age_sub_myr", "age_sub", "myr"),
    ("uw_age_over_myr", "age_over", "myr"),
    ("uw_age_thin_myr", "age_thin", "myr"),
    ("uw_cont_age_myr", "cont_age", "myr"),
    ("uw_slab_wedge_age_myr", "slab_wedge_age", "myr"),
    ("uw_heal_time_myr", "heal_time", "myr"),
    ("uw_dt_max_myr", "dt_max", "myr"),
    ("uw_ridge_sub_km", "ridge_sub", "arc_km"),
    ("uw_ridge_over_km", "ridge_over", "arc_km"),
    ("uw_cont_extent_km", "cont_extent", "arc_km"),
    ("uw_ridge_patch_km", "ridge_patch", "km"),
    ("uw_over_gap_km", "over_gap", "km"),
    ("uw_over_ramp_km", "over_ramp", "km"),
    ("uw_over_comp_thick_km", "over_comp_thick", "km"),
    ("uw_crust_thick_km", "crust_thick", "km"),
    ("uw_crust_depth_km", "crust_depth", "km"),
    ("uw_ridge_crust_stop_km", "ridge_crust_stop", "km"),
    ("uw_ocrust_depth_km", "ocrust_depth", "km"),
    ("uw_crust_line_spacing_km", "crust_line_spacing", "km"),
    ("uw_marker_rheo_depth_km", "marker_rheo_depth", "km"),
    ("uw_marker_rheo_ramp_km", "marker_rheo_ramp", "km"),
    ("uw_slab_length_km", "slab_length", "km"),
    ("uw_slab_contact_km", "slab_contact", "km"),
    ("uw_slab_rate_cm_yr", "slab_rate", "cm_yr"),
    ("uw_asth_top_km", "asth_top", "km"),
    ("uw_asth_bottom_km", "asth_bottom", "km"),
    ("uw_asth_ramp_km", "asth_ramp", "km"),
    ("uw_lm_depth_km", "lm_depth", "km"),
    ("uw_lm_ramp_km", "lm_ramp", "km"),
    ("uw_spline_length_km", "spline_length", "km"),
    ("uw_fault_depth_max_km", "fault_depth_max", "km"),
    ("uw_advect_offset_km", "advect_offset", "km"),
    ("uw_over_drho_kg_m3", "over_dT", "kg_m3"),
    ("uw_heating_nw_m3", "heating", "nw_m3"),
    ("uw_eta_max_pas", "arr_eta_max", "pas"),
    ("uw_eta_reg_pas", "eta_reg", "pas"),
    ("uw_tau0_mpa", "tau0", "mpa"),
    ("uw_tau1_mpa_km", "tau1", "mpa_km"),
]
# the options that set the scales themselves
SCALES = ["uw_T_base_c", "uw_eta_ref_pas", "uw_activation_kj_mol"]
OPTIONS = SCALES + [option for option, _, _ in SCALED]
LABEL = {"c": "C", "myr": "Myr", "arc_km": "km of surface", "km": "km", "cm_yr": "cm/yr", "kg_m3": "kg/m3",
         "nw_m3": "nW/m3", "pas": "Pa s", "mpa": "MPa", "mpa_km": "MPa/km"}
# the model-unit options this replaces, and what to give instead
RETIRED = dict([("uw_" + name, option) for option, name, _ in SCALED],
               uw_ra="uw_eta_ref_pas", uw_deta="uw_eta_ref_pas and uw_activation_kj_mol",
               uw_arr_E="uw_activation_kj_mol", uw_arr_T0="uw_T_base_c (the surface is 273 K)")


def to_model(earth, r_o):
    """The model's values of the Earth-unit options ``earth`` ({option: value}, every one of
    OPTIONS) in an annulus of outer radius ``r_o`` (model lengths). Returns (model, unit):
    ``model`` {name: value} with the names of SCALED and the derived T0 (``arr_T0``), E
    (``arr_E``), ``deta`` and ``ra``; ``unit`` {kind: the size of one model unit in that Earth
    unit}. A negative or zero value keeps its sign, so an option's "0: off" or "< 0: derived"
    reads the same in both. uw_ridge_over_km 0 is the rest of the circumference: one ridge."""
    dT = float(earth["uw_T_base_c"])
    T_i = float(earth["uw_T_potential_c"]) / dT
    eta_ref = float(earth["uw_eta_ref_pas"])
    if not (dT > 0 and 0 < T_i <= 1 and eta_ref > 0):
        raise ValueError("Earth units need uw_T_base_c > 0, uw_T_potential_c in (0, uw_T_base_c] "
                         "and uw_eta_ref_pas > 0")
    T0 = SURFACE_K / dT
    E = float(earth["uw_activation_kj_mol"]) * 1.0e3 / (GAS_CONSTANT * dT)
    deta = math.exp(E / (T_i + T0) ** 2)
    eta_0 = eta_ref / deta ** (1 - T_i)
    depth = DEPTH_KM * 1.0e3
    stress = eta_0 * DIFFUSIVITY / depth ** 2                                   # Pa
    unit = {"c": dT, "myr": depth ** 2 / DIFFUSIVITY / (1.0e6 * YEAR_S), "arc_km": r_o * DEPTH_KM,
            "km": DEPTH_KM, "cm_yr": DIFFUSIVITY / depth * YEAR_S * 100.0,
            "kg_m3": DENSITY * EXPANSIVITY * dT, "nw_m3": CONDUCTIVITY * dT / depth ** 2 * 1.0e9,
            "pas": eta_0, "mpa": stress * 1.0e-6, "mpa_km": stress * 1.0e-6 / DEPTH_KM}
    model = {name: float(earth[option]) / unit[kind] for option, name, kind in SCALED}
    model.update(arr_T0=T0, arr_E=E, deta=deta,
                 ra=DENSITY * GRAVITY * EXPANSIVITY * dT * depth ** 3 / (DIFFUSIVITY * eta_0))
    if model["arr_eta_max"] <= 1:
        raise ValueError("uw_eta_max_pas must be above the viscosity's floor eta_0 (%.4g Pa s)" % eta_0)
    if model["ridge_over"] <= 0:
        model["ridge_over"] = 2 * math.pi - abs(model["ridge_sub"])
    return model, unit


def table(earth, model, unit):
    """The log's lines: the scales, then every option in Earth units beside its model value."""
    lines = ["Earth units -> model units (depth %g km, kappa %g m2/s, rho %g kg/m3, alpha %g /K, g %g m/s2, "
             "k %g W/m/K, surface %g K)" % (DEPTH_KM, DIFFUSIVITY, DENSITY, EXPANSIVITY, GRAVITY, CONDUCTIVITY,
                                            SURFACE_K),
             "  one model unit: " + ", ".join("%.6g %s" % (unit[k], LABEL[k]) for k in
                                              ("km", "myr", "cm_yr", "c", "pas", "mpa", "kg_m3", "nw_m3")),
             "  uw_T_base_c %g C, uw_eta_ref_pas %g Pa s, uw_activation_kj_mol %g kJ/mol -> T0 %.6g, E %.6g, "
             "deta %.6g, Ra %.6g; the viscosity's floor is eta_0, %.4g Pa s"
             % (earth["uw_T_base_c"], earth["uw_eta_ref_pas"], earth["uw_activation_kj_mol"], model["arr_T0"],
                model["arr_E"], model["deta"], model["ra"], unit["pas"])]
    for option, name, kind in SCALED:
        lines.append("  %-26s %12.6g %-13s -> %-18s %.10g" % (option, earth[option], LABEL[kind], name, model[name]))
    return lines
