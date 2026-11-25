# Every custom-MG and placed-ribbon test: iteration counts before (e2aa7be6) and after (aa3d092c)

Serial, macOS (12-core Apple M4). Rotated solves: outer/velocity/pressure; other solves: snes:linear [fieldsplit sub-KSP its]. One entry per solve, in order.

| test | before | after | same |
|---|---|---|---|
| test_0020_restore_continuation.py::test_a_disk_snapshot_carries_the_solver_step_state | 2:2 [3, 83]; 1:1 [4, 64]; 1:1 [7, 36] | 2:2 [3, 83]; 1:1 [4, 64]; 1:1 [7, 36] | yes |
| test_0020_restore_continuation.py::test_a_regretted_step_leaves_no_trace | 0:0; 2:3; 1:2; 0:0; 1:1 [4, 117]; 1:2; 1:2; 1:7; 1:1 [4, 95]; 1:2; 1:2; 1:7; 1:1 [4, 95]; 1:2; 1:2; 1:7; 1:1 [4, 66]; 1:2; 1:2; 1:9; 2:2 [4, 36]; 1:2; 1:2; 1:7; 1:1 [4, 95]; 1:2; 1:2; 1:7; 1:1 [4, 66]; 1:2; 1:2 | 0:0; 2:3; 1:2; 0:0; 1:1 [4, 117]; 1:2; 1:2; 1:7; 1:1 [4, 95]; 1:2; 1:2; 1:7; 1:1 [4, 95]; 1:2; 1:2; 1:7; 1:1 [4, 66]; 1:2; 1:2; 1:9; 2:2 [4, 36]; 1:2; 1:2; 1:7; 1:1 [4, 95]; 1:2; 1:2; 1:7; 1:1 [4, 66]; 1:2; 1:2 | yes |
| test_0020_restore_continuation.py::test_a_restore_brings_back_what_the_solver_carries_between_steps | 2:2 [3, 83]; 1:1 [4, 64]; 1:1 [7, 36] | 2:2 [3, 83]; 1:1 [4, 64]; 1:1 [7, 36] | yes |
| test_0020_restore_continuation.py::test_a_restore_discards_the_rotated_free_slip_workspace | [1]/[22]/[8]; [1]/[22]/[8]; [1]/[22]/[8] | [1]/[22]/[8]; [1]/[22]/[8]; [1]/[22]/[8] | yes |
| test_0020_restore_continuation.py::test_a_restore_keeps_multigrid_transfers_set_in_code | 1:1 [4, 8]; 1:1 [4, 8]; 1:1 [4, 8]; 1:1 [4, 8] | 1:1 [4, 8]; 1:1 [4, 8]; 1:1 [4, 8]; 1:1 [4, 8] | yes |
| test_0020_restore_continuation.py::test_a_restore_of_an_undeformed_mesh_leaves_the_solver_built | 2:2 [3, 83]; 1:1 [4, 64] | 2:2 [3, 83]; 1:1 [4, 64] | yes |
| test_0020_restore_continuation.py::test_an_advection_diffusion_solver_gets_its_step_state_back | 1:3; 1:6 | 1:3; 1:6 | yes |
| test_0753_nested_mg_prolongation.py::test_mg_actually_uses_the_recorded_transfer_for_degree_one | 1:2 | 1:2 | yes |
| test_0835_sbr_adapt_on_top.py::test_child_solver_auto_picks_up_custom_mg | 1:3; 1:16 | 1:3; 1:16 | yes |
| test_0835_sbr_adapt_on_top.py::test_each_sbr_level_is_its_own_mg_level | 1:3 | 1:3 | yes |
| test_0835_sbr_adapt_on_top.py::test_stokes_velocity_block_auto_picks_up_fmg | 1:1 [46, 13]; 1:1 [2, 13] | 1:1 [46, 13]; 1:1 [2, 13] | yes |
| test_0836_nvb_graded_adapt.py::test_poisson_fmg_on_nvb_child_matches_gamg | 1:2; 1:16 | 1:2; 1:16 | yes |
| test_0836_nvb_graded_adapt.py::test_solcx_stokes_velocity_fmg_on_nvb_child | 1:1 [56, 14]; 1:1 [2, 14] | 1:1 [56, 14]; 1:1 [2, 14] | yes |
| test_0840_nvb_3d_serial_adapt.py::test_poisson_fmg_on_3d_nvb_child_matches_gamg | 1:4; 1:25 | 1:4; 1:25 | yes |
| test_0844_line_cut.py::test_a_cut_mesh_carries_a_step_viscosity_without_leaking_stress | 1:1 [24, 8]; 1:3; 1:1 [1, 27]; 1:1 | 1:1 [24, 8]; 1:3; 1:1 [1, 27]; 1:1 | yes |
| test_0844_line_cut.py::test_a_dirichlet_condition_applies_on_the_surface | 1:2 | 1:2 | yes |
| test_0844_line_cut.py::test_serial_reference_for_parallel_confluence | 1:4 | 1:4 | yes |
| test_0848_fault_split_3d.py::test_dof_independence_p2 | 1:6 | 1:6 | yes |
| test_0848_fault_split_3d.py::test_viscous_family_3d | [1]/[19]/[79]; [1]/[19]/[76]; [1]/[18]/[71] | [1]/[19]/[79]; [1]/[19]/[76]; [1]/[18]/[71] | yes |
| test_0855_place_thin_volume.py::test_an_outcropping_ribbon_leaves_a_band_on_the_surface | 1:18 | 1:18 | yes |
| test_0855_place_thin_volume.py::test_an_outcropping_ribbon_on_the_annulus_leaves_a_trace | 1:18 | 1:18 | yes |
| test_0855_place_thin_volume.py::test_an_outcropping_zone_leaves_a_band_on_the_surface | 1:22 | 1:22 | yes |
| test_0855_place_thin_volume.py::test_finite_elements_are_exact_on_the_embedded_mesh | 1:24 | 1:24 | yes |
| test_0857_network_mesher.py::test_a_placed_mesh_owns_the_base_hierarchy_and_the_cut_inherits_it | 1:1 [1, 11]; 1:1 [3, 16] | 1:1 [1, 11]; 1:1 [3, 16] | yes |
| test_0862_conforming_sheet_3d.py::test_a_solver_consumes_the_cut_mesh | 1:2 | 1:2 | yes |
| test_0894_serial_custom_fmg_drops_orphans.py::test_no_orphans_no_change | [1]/[3]/[9] | [1]/[3]/[9] | yes |
| test_0894_serial_custom_fmg_drops_orphans.py::test_orphans_on_a_graded_finest_level_are_dropped_not_repaired | [1]/[13]/[9] | [1]/[3]/[9] | NO |
| test_1014_stokes_multigrid.py::test_auto_falls_back_to_gamg_without_hierarchy | 1:1 [8, 4] | 1:1 [8, 4] | yes |
| test_1014_stokes_multigrid.py::test_auto_selects_geometric_fmg_on_refinement_mesh | 1:1 [2, 5] | 1:1 [2, 5] | yes |
| test_1014_stokes_multigrid.py::test_default_fmg_bundle_is_parallel_safe | 1:1 [2, 5] | 1:1 [2, 5] | yes |
| test_1014_stokes_multigrid.py::test_explicit_gamg_override | 1:1 [18, 5] | 1:1 [18, 5] | yes |
| test_1014_stokes_multigrid.py::test_fmg_without_hierarchy_falls_back | 1:1 [8, 4] | 1:1 [8, 4] | yes |
| test_1014_stokes_multigrid.py::test_geometric_mg_without_galerkin_is_repaired | 1:1 [4, 5] | 1:1 [4, 5] | yes |
| test_1014_stokes_multigrid.py::test_scalar_poisson_auto_falls_back_to_gamg | 1:8 | 1:8 | yes |
| test_1014_stokes_multigrid.py::test_toggle_back_to_fmg | 1:1 [18, 5]; 1:1 [2, 5] | 1:1 [18, 5]; 1:1 [2, 5] | yes |
| test_1015_custom_mg_prolongation.py::test_custom_mg_barycentric_matches_fmg | 1:8; 1:1 | 1:8; 1:1 | yes |
| test_1015_custom_mg_prolongation.py::test_custom_mg_rbf_drives_solver | 1:8; 1:1 | 1:8; 1:1 | yes |
| test_1015_custom_mg_prolongation.py::test_custom_mg_without_refine_hierarchy | 1:1 | 1:1 | yes |
| test_1016_custom_mg_hierarchy.py::test_advdiff_on_nvb_adapt_child_gets_custom_mg | 1:4; 1:1 | 1:4; 1:1 | yes |
| test_1016_custom_mg_hierarchy.py::test_custom_fmg_hierarchy_converges | 1:3; 1:9 | 1:3; 1:9 | yes |
| test_1016_custom_mg_hierarchy.py::test_rbf_builder_also_works | 1:3 | 1:3 | yes |
| test_1016_mesh_multigrid_levels.py::test_an_adapt_child_reports_the_tail_its_solvers_use | 1:2 | 1:2 | yes |
| test_1016_mesh_multigrid_levels.py::test_the_levels_drive_a_custom_fmg_solve | 1:1 | 1:1 | yes |
| test_1017_custom_mg_stokes.py::test_custom_fmg_stokes_constrained | 1:12 [3, 200] | 1:12 [3, 200] | yes |
| test_1017_custom_mg_stokes.py::test_custom_fmg_stokes_on_sbr_child | 1:1 [1, 5] | 1:1 [1, 5] | yes |
| test_1017_custom_mg_stokes.py::test_custom_fmg_vector_solver | 1:1 | 1:1 | yes |
| test_1017_custom_mg_stokes.py::test_custom_fmg_velocity_block_barycentric | 1:1 [38, 14]; 1:1 [4, 14] | 1:1 [38, 14]; 1:1 [4, 14] | yes |
| test_1017_custom_mg_stokes.py::test_custom_fmg_velocity_block_rbf | 1:1 [7, 14] | 1:1 [7, 14] | yes |
| test_1017_nested_native_and_fac.py::test_fac_smoother_is_the_composite_band_patch_and_converges | 1:2; 1:11 | 1:2; 1:11 | yes |
| test_1017_nested_native_and_fac.py::test_fac_split_classifies_band_and_declines_uniform | 1:2 | 1:2 | yes |
| test_1018_rotated_freeslip.py::test_rotated_continuation_warm_start_switches_to_newton_at_once | [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]/[18, 21, 22, 22, 23, 24, 24, 24, 25, 25, 24, 24, 24, 24, 23, 30, 24]/[8, 12, 13, 14, 15, 15, 15, 15, 16, 15, 16, 15, 15, 15, 15, 15, 12]; [1, 1]/[28, 23]/[13, 12] | [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]/[18, 21, 22, 22, 23, 24, 24, 24, 25, 25, 24, 24, 24, 24, 23, 30, 24]/[8, 12, 13, 14, 15, 15, 15, 15, 16, 15, 16, 15, 15, 15, 15, 15, 12]; [1, 1]/[28, 23]/[13, 12] | yes |
| test_1018_rotated_freeslip.py::test_rotated_freeslip_annulus_zero_leakage | [1]/[19]/[5] | [1]/[19]/[5] | yes |
| test_1018_rotated_freeslip.py::test_rotated_freeslip_boundary_normal_traction_solcx | [1]/[40]/[33] | [1]/[40]/[33] | yes |
| test_1018_rotated_freeslip.py::test_rotated_freeslip_box_reproduces_essential | 1:1 [41, 22]; [1]/[38]/[22] | 1:1 [41, 22]; [1]/[38]/[22] | yes |
| test_1018_rotated_freeslip.py::test_rotated_freeslip_continuation_tangent | [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]/[18, 21, 22, 22, 23, 24, 24, 24, 25, 25, 24, 24, 24, 24, 23, 30, 24]/[8, 12, 13, 14, 15, 15, 15, 15, 16, 15, 16, 15, 15, 15, 15, 15, 12]; [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]/[18, 21, 22, 22, 23, 24, 24, 24, 25, 25, 24, 24, 24, 24, 23, 23, 23, 23, 22, 22, 22, 21, 21, 21, 20, 26]/[8, 12, 13, 14, 15, 15, 15, 15, 16, 15, 16, 15, 15, 15, 15, 14, 14, 13, 14, 13, 13, 13, 12, 12, 12, 12] | [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]/[18, 21, 22, 22, 23, 24, 24, 24, 25, 25, 24, 24, 24, 24, 23, 30, 24]/[8, 12, 13, 14, 15, 15, 15, 15, 16, 15, 16, 15, 15, 15, 15, 15, 12]; [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]/[18, 21, 22, 22, 23, 24, 24, 24, 25, 25, 24, 24, 24, 24, 23, 23, 23, 23, 22, 22, 22, 21, 21, 21, 20, 26]/[8, 12, 13, 14, 15, 15, 15, 15, 16, 15, 16, 15, 15, 15, 15, 14, 14, 13, 14, 13, 13, 13, 12, 12, 12, 12] | yes |
| test_1018_rotated_freeslip.py::test_rotated_freeslip_datum_zero_matches_freeslip | [1]/[30]/[15]; [1]/[30]/[15] | [1]/[30]/[15]; [1]/[30]/[15] | yes |
| test_1018_rotated_freeslip.py::test_rotated_freeslip_dynamic_topography_field | [1]/[40]/[33] | [1]/[40]/[33] | yes |
| test_1018_rotated_freeslip.py::test_rotated_freeslip_geometric_fmg_velocity_block | 1:1 [28, 200]; [1]/[5]/[200] | 1:1 [28, 200]; [1]/[5]/[200] | yes |
| test_1018_rotated_freeslip.py::test_rotated_freeslip_newton_tangent | [1, 1, 1, 1, 1, 1, 1, 1]/[18, 24, 28, 30, 33, 30, 26, 14]/[8, 15, 15, 16, 17, 15, 12, 4] | [1, 1, 1, 1, 1, 1, 1, 1]/[18, 24, 28, 30, 33, 30, 26, 14]/[8, 15, 15, 16, 17, 15, 12, 4] | yes |
| test_1018_rotated_freeslip.py::test_rotated_freeslip_nonlinear_annulus_zero_leakage | [1, 1, 1, 1, 1, 1, 1]/[18, 24, 27, 29, 27, 23, 13]/[8, 11, 12, 12, 11, 9, 4] | [1, 1, 1, 1, 1, 1, 1]/[18, 24, 27, 29, 27, 23, 13]/[8, 11, 12, 12, 11, 9, 4] | yes |
| test_1018_rotated_freeslip.py::test_rotated_freeslip_nonlinear_geometric_fmg | 7:7 [24, 59]; [1, 1, 1, 1, 1, 1, 1, 1]/[3, 5, 6, 6, 6, 5, 4, 2]/[48, 56, 53, 59, 58, 51, 41, 23] | 7:7 [24, 59]; [1, 1, 1, 1, 1, 1, 1, 1]/[3, 5, 6, 6, 6, 5, 4, 2]/[48, 56, 53, 59, 58, 51, 41, 23] | yes |
| test_1018_rotated_freeslip.py::test_rotated_freeslip_nonlinear_matches_essential | 7:7 [27, 18]; [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]/[18, 21, 22, 22, 23, 24, 24, 24, 25, 25, 24, 24, 24, 24, 23, 23, 23, 23, 22, 22, 22, 21, 21, 21, 20, 20, 20, 20, 19, 19, 18, 18, 18, 17, 17, 16, 16, 15, 15, 14, 14, 13, 12]/[8, 12, 13, 14, 15, 15, 15, 15, 16, 15, 16, 15, 15, 15, 15, 14, 14, 13, 14, 13, 13, 13, 12, 12, 12, 11, 11, 11, 11, 10, 10, 9, 9, 9, 8, 8, 7, 7, 6, 5, 5, 4, 5] | 7:7 [27, 18]; [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]/[18, 21, 22, 22, 23, 24, 24, 24, 25, 25, 24, 24, 24, 24, 23, 23, 23, 23, 22, 22, 22, 21, 21, 21, 20, 20, 20, 20, 19, 19, 18, 18, 18, 17, 17, 16, 16, 15, 15, 14, 14, 13, 12]/[8, 12, 13, 14, 15, 15, 15, 15, 16, 15, 16, 15, 15, 15, 15, 14, 14, 13, 14, 13, 13, 13, 12, 12, 12, 11, 11, 11, 11, 10, 10, 9, 9, 9, 8, 8, 7, 7, 6, 5, 5, 4, 5] | yes |
| test_1018_rotated_freeslip.py::test_rotated_freeslip_nonlinear_prescribed_normal_datum | [1, 1, 1, 1, 1, 1, 1, 1]/[20, 53, 28, 26, 26, 19, 16, 14]/[11, 14, 9, 9, 9, 8, 7, 6] | [1, 1, 1, 1, 1, 1, 1, 1]/[20, 53, 28, 26, 26, 19, 16, 14]/[11, 14, 9, 9, 9, 8, 7, 6] | yes |
| test_1018_rotated_freeslip.py::test_rotated_freeslip_nonlinear_warm_start | [1, 1, 1, 1, 1, 1, 1, 1]/[18, 24, 28, 30, 33, 30, 26, 14]/[8, 15, 15, 16, 17, 15, 12, 4]; []/[]/[] | [1, 1, 1, 1, 1, 1, 1, 1]/[18, 24, 28, 30, 33, 30, 26, 14]/[8, 15, 15, 16, 17, 15, 12, 4]; []/[]/[] | yes |
| test_1018_rotated_freeslip.py::test_rotated_freeslip_picard_under_newton_stages_picard_then_newton | [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]/[18, 21, 22, 22, 23, 24, 24, 24, 25, 25, 24, 24, 24, 24, 23, 30, 24]/[8, 12, 13, 14, 15, 15, 15, 15, 16, 15, 16, 15, 15, 15, 15, 15, 12] | [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]/[18, 21, 22, 22, 23, 24, 24, 24, 25, 25, 24, 24, 24, 24, 23, 30, 24]/[8, 12, 13, 14, 15, 15, 15, 15, 16, 15, 16, 15, 15, 15, 15, 15, 12] | yes |
| test_1018_rotated_freeslip.py::test_rotated_freeslip_prescribed_normal_datum | [1]/[28]/[14] | [1]/[28]/[14] | yes |
| test_1018_rotated_freeslip.py::test_rotated_freeslip_sigma_nn_lumped_no_overshoot | [1]/[40]/[33] | [1]/[40]/[33] | yes |
| test_1018_rotated_freeslip.py::test_rotated_freeslip_spherical3d_reaction_topography | [1]/[34]/[15] | [1]/[34]/[15] | yes |
| test_1018_rotated_freeslip.py::test_rotated_freeslip_spherical_shell_3d | [1]/[40]/[17] | [1]/[40]/[17] | yes |
| test_1018_rotated_freeslip.py::test_rotated_linear_workspace_reuses_unchanged_operator | [1]/[19]/[8]; [1]/[19]/[9]; [1]/[19]/[0]; []/[]/[] | [1]/[19]/[8]; [1]/[19]/[9]; [1]/[19]/[0]; []/[]/[] | yes |
| test_1018_rotated_freeslip.py::test_rotated_solve_fields_carry_inhomogeneous_dirichlet_walls | [1]/[16]/[18] | [1]/[16]/[18] | yes |
| test_1018_rotated_freeslip.py::test_rotated_solve_records_its_diagnostics | [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]/[18, 21, 22, 22, 23, 24, 24, 24, 25, 25, 24, 24, 24, 24, 23, 30, 24]/[8, 12, 13, 14, 15, 15, 15, 15, 16, 15, 16, 15, 15, 15, 15, 15, 12]; [1, 1]/[28, 23]/[13, 12] | [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]/[18, 21, 22, 22, 23, 24, 24, 24, 25, 25, 24, 24, 24, 24, 23, 30, 24]/[8, 12, 13, 14, 15, 15, 15, 15, 16, 15, 16, 15, 15, 15, 15, 15, 12]; [1, 1]/[28, 23]/[13, 12] | yes |
| test_1018_rotated_freeslip.py::test_rotated_workspace_constant_ramp_invalidates | [1]/[22]/[12]; [1]/[22]/[12]; [1]/[22]/[0]; [1]/[22]/[12] | [1]/[22]/[12]; [1]/[22]/[12]; [1]/[22]/[0]; [1]/[22]/[12] | yes |
| test_1018_rotated_freeslip.py::test_rotated_workspace_deform_invalidates | [1]/[23]/[11]; [1]/[23]/[15]; [1]/[23]/[15] | [1]/[23]/[11]; [1]/[23]/[15]; [1]/[23]/[15] | yes |
| test_1018_rotated_freeslip.py::test_the_rotated_solve_reports_its_own_convergence[False] | [1]/[29]/[18] | [1]/[29]/[18] | yes |
| test_1018_rotated_freeslip.py::test_the_rotated_solve_reports_its_own_convergence[True] | [1]/[None]/[None] | [1]/[None]/[None] | yes |
| test_1020_fmg_single_field_lockout.py::test_cartesian_box_scalar_fmg_also_unlocked | 1:2 | 1:2 | yes |
| test_1020_fmg_single_field_lockout.py::test_options_db_and_record_stay_honest_between_build_and_solve | 1:2 | 1:2 | yes |
| test_1020_fmg_single_field_lockout.py::test_scalar_auto_still_uses_gamg_and_records_the_decline | 1:13 | 1:13 | yes |
| test_1020_fmg_single_field_lockout.py::test_scalar_fmg_degrades_readably_when_the_build_fails | 1:13 | 1:13 | yes |
| test_1020_fmg_single_field_lockout.py::test_scalar_fmg_routes_to_custom_geometric_mg | 1:2 | 1:2 | yes |
| test_1020_fmg_single_field_lockout.py::test_switch_to_gamg_after_fmg_is_honoured | 1:2; 1:13 | 1:2; 1:13 | yes |
| test_1021_mg_option_bundle.py::test_a_rotated_set_up_that_raises_leaves_no_options_behind | 0:0 | 0:0 | yes |
| test_1021_mg_option_bundle.py::test_a_user_key_still_beats_the_strategy | 1:1 [6, 10]; 0:0 [6, 10] | 1:1 [6, 10]; 0:0 [6, 10] | yes |
| test_1021_mg_option_bundle.py::test_a_user_set_svd_coarse_solve_still_reaches_the_standard_route | 1:1 [4, 11] | 1:1 [4, 11] | yes |
| test_1021_mg_option_bundle.py::test_all_three_routes_share_one_bundle | 1:1 [3, 11]; 1:1 [4, 11]; [1]/[4]/[14] | 1:1 [3, 11]; 1:1 [4, 11]; [1]/[4]/[14] | yes |
| test_1021_mg_option_bundle.py::test_an_adapt_child_scalar_solve_converges_truly | 1:1 | 1:1 | yes |
| test_1021_mg_option_bundle.py::test_default_strategy_does_not_change_behaviour | 1:1 [3, 10]; 0:0 [3, 10]; 1:1 [3, 11]; 0:0 [3, 11] | 1:1 [3, 10]; 0:0 [3, 10]; 1:1 [3, 11]; 0:0 [3, 11] | yes |
| test_1021_mg_option_bundle.py::test_rotated_coarse_is_redundant_lu_with_a_rotation_mode | [1]/[4]/[9] | [1]/[4]/[9] | yes |
| test_1021_mg_option_bundle.py::test_rotated_fmg_survives_repeated_newton_increments | [1, 1, 1, 1, 1, 1, 1, 1]/[4, 5, 5, 5, 5, 5, 4, 3]/[12, 15, 15, 15, 16, 14, 11, 6] | [1, 1, 1, 1, 1, 1, 1, 1]/[4, 5, 5, 5, 5, 5, 4, 3]/[12, 15, 15, 15, 16, 14, 11, 6] | yes |
| test_1021_mg_option_bundle.py::test_rotated_picks_up_a_mesh_owned_hierarchy | [1]/[4]/[14] | [1]/[4]/[14] | yes |
| test_1021_mg_option_bundle.py::test_rotated_without_a_hierarchy_falls_back_to_gamg | [1]/[26]/[14] | [1]/[26]/[14] | yes |
| test_1021_mg_option_bundle.py::test_strategy_reaches_every_route | 1:1 [5, 10]; 0:0 [5, 10]; 1:1 [5, 10]; [1]/[5]/[14] | 1:1 [5, 10]; 0:0 [5, 10]; 1:1 [5, 10]; [1]/[5]/[14] | yes |
| test_1021_mg_option_bundle.py::test_strategy_report_names_a_user_override | 1:1 [3, 11] | 1:1 [3, 11] | yes |
| test_1021_mg_option_bundle.py::test_strategy_reports_what_it_resolved_to | 1:1 [3, 11] | 1:1 [3, 11] | yes |
| test_1021_mg_option_bundle.py::test_strategy_selects_a_real_smoother_variant | 1:1 [5, 10]; 0:0 [5, 10]; 1:1 [3, 10]; 0:0 [3, 10] | 1:1 [5, 10]; 0:0 [5, 10]; 1:1 [3, 10]; 0:0 [3, 10] | yes |
| test_1021_mg_option_bundle.py::test_strategy_value_pickles_and_copies | 1:1 [3, 11] | 1:1 [3, 11] | yes |
| test_1021_mg_option_bundle.py::test_unset_bundle_keys_keep_the_managed_defaults | 1:1 [3, 11]; 0:0 [3, 11] | 1:1 [3, 11]; 0:0 [3, 11] | yes |
| test_1021_mg_option_bundle.py::test_user_set_bundle_keys_are_honoured[None] | 1:1 [3, 11]; 0:0 [3, 11] | 1:1 [3, 11]; 0:0 [3, 11] | yes |
| test_1021_mg_option_bundle.py::test_user_set_bundle_keys_are_honoured[fmg] | 1:1 [3, 11]; 0:0 [3, 11] | 1:1 [3, 11]; 0:0 [3, 11] | yes |
| test_1022_pc_fallback_observability.py::test_auto_decline_is_recorded_but_stays_silent | 1:4 | 1:4 | yes |
| test_1022_pc_fallback_observability.py::test_clean_solve_has_empty_fallback_record | 1:3 | 1:3 | yes |
| test_1022_pc_fallback_observability.py::test_explicit_gamg_records_nothing | 1:3 | 1:3 | yes |
| test_1022_pc_fallback_observability.py::test_fmg_without_hierarchy_records_unavailable_and_still_warns | 1:3; 1:2 | 1:3; 1:2 | yes |
| test_1022_pc_fallback_observability.py::test_reason_vocabulary_is_closed | 1:2 | 1:2 | yes |
| test_1022_pc_fallback_observability.py::test_record_resets_when_the_preconditioner_re_resolves | 1:3; 1:3 | 1:3; 1:3 | yes |
| test_1022_pc_fallback_observability.py::test_total_transfer_failure_records_and_solves_on_default_pc | 1:9 | 1:9 | yes |
| test_1022_pc_fallback_observability.py::test_transfer_builder_failure_records_the_rbf_rescue | 1:1 | 1:1 | yes |
| test_1022_pc_fallback_observability.py::test_unpatched_adapt_child_solve_records_no_build_failure | 1:1 | 1:1 | yes |
| test_1055_advdiff_supg_api.py::test_estimate_dt_is_accuracy_based_and_resolution_on_request | 1:9 | 1:9 | yes |
| test_1055_advdiff_supg_api.py::test_galerkin_baseline_needs_no_rebuild | 1:9; 1:9 | 1:9; 1:9 | yes |
| test_1055_advdiff_supg_api.py::test_multigrid_is_one_switch_away_on_a_refinement_hierarchy | 1:9; 1:1; 1:9 | 1:9; 1:1; 1:9 | yes |
| test_1055_advdiff_supg_api.py::test_order_ramps_from_one_unless_history_is_planted | 1:9; 1:9; 1:9 | 1:9; 1:9; 1:9 | yes |
| test_1055_advdiff_supg_api.py::test_semi_lagrangian_only_arguments_are_ignored_with_a_warning | 1:9 | 1:9 | yes |
| test_1055_advdiff_supg_api.py::test_solve_takes_the_slcn_signature_and_delta_t | 1:9; 1:9 | 1:9; 1:9 | yes |
| test_1055_advdiff_supg_api.py::test_solves_on_an_adapt_child_with_its_own_preconditioner | 1:9 | 1:9 | yes |
| test_1055_advdiff_supg_api.py::test_theta_is_settable_after_construction_as_on_slcn | 1:9; 1:9 | 1:9; 1:9 | yes |
| test_1055_advdiff_supg_api.py::test_timestep_change_is_a_constant_update_not_a_recompile | 1:9; 1:9 | 1:9; 1:9 | yes |
| test_1055_advdiff_supg_api.py::test_timestep_change_reaches_the_kernels | 1:9; 1:9; 1:9; 1:9 | 1:9; 1:9; 1:9; 1:9 | yes |
| test_1077_quiet_unsetup_fieldsplit.py::test_custom_fmg_rewire_prints_no_banner | 50:50 [3, 10]; 6:6 [6, 7] | 50:50 [3, 10]; 6:6 [6, 7] | yes |
| test_1077_quiet_unsetup_fieldsplit.py::test_helper_is_quiet_on_an_unsetup_split | 1:1 [7, 6] | 1:1 [7, 6] | yes |
| test_1077_quiet_unsetup_fieldsplit.py::test_viscoelastic_solve_prints_no_banner | 1:1 [7, 6] | 1:1 [7, 6] | yes |
| test_1077_quiet_unsetup_fieldsplit.py::test_warm_solve_without_a_linear_solve_prints_no_banner | 50:50 [9, 8]; 0:0 | 50:50 [9, 8]; 0:0 | yes |
| test_1087_fault_split_multigrid.py::test_a_moving_fault_re_splits_the_levels_at_every_position | [1]/[6]/[16]; [1]/[6]/[15]; [1]/[7]/[16] | [1]/[6]/[16]; [1]/[6]/[15]; [1]/[7]/[16] | yes |
| test_1087_fault_split_multigrid.py::test_a_viscous_fault_solves_in_as_few_iterations | [1]/[5]/[15] | [1]/[5]/[15] | yes |
| test_1087_fault_split_multigrid.py::test_iterations_fall_with_refinement_and_the_slip_is_unchanged | [1]/[6]/[15]; [1]/[5]/[15]; [1]/[5]/[15] | [1]/[6]/[15]; [1]/[5]/[15]; [1]/[5]/[15] | yes |
| test_1096_addon_cut_child_tail.py::test_fault_solve_on_the_cut_child_runs_on_the_geometric_tail | [1]/[8]/[15] | [1]/[8]/[15] | yes |
| test_1111_rotated_fmg_coarse_shifted_lu.py::test_a_singular_coarse_level_converges_to_the_svd_answer | [1]/[2]/[7] | [1]/[2]/[7] | yes |
| test_1111_rotated_fmg_coarse_shifted_lu.py::test_the_coarse_solve_is_shifted_lu[annulus] | [1]/[4]/[7] | [1]/[4]/[7] | yes |
| test_1111_rotated_fmg_coarse_shifted_lu.py::test_the_coarse_solve_is_shifted_lu[shell] | [1]/[5]/[17] | [1]/[5]/[17] | yes |
| test_1113_rotated_fmg_one_coarse_factorisation.py::test_one_rotated_solve_sets_the_coarse_level_up_once | [1]/[4]/[7] | [1]/[4]/[7] | yes |
| test_1115_rotated_solve_raises_on_failure.py::test_a_caught_raise_leaves_the_solver_usable | [0]/[0]/[0]; [1]/[4]/[7] | [0]/[0]/[0]; [1]/[4]/[7] | yes |
| test_1115_rotated_solve_raises_on_failure.py::test_a_failed_cold_rotated_solve_is_tolerated_when_asked | [0]/[0]/[0] | [0]/[0]/[0] | yes |
| test_1115_rotated_solve_raises_on_failure.py::test_a_failed_cold_rotated_solve_raises_after_recording | [0]/[0]/[0] | [0]/[0]/[0] | yes |
| test_1115_rotated_solve_raises_on_failure.py::test_a_failed_warm_rotated_solve_keeps_the_state | [1]/[4]/[7]; [0]/[0]/[0]; [1]/[4]/[7] | [1]/[4]/[7]; [0]/[0]/[0]; [1]/[4]/[7] | yes |
| test_1115_rotated_solve_raises_on_failure.py::test_a_tolerated_cold_failure_with_a_datum_does_not_apply_the_lift | [0]/[0]/[0] | [0]/[0]/[0] | yes |
| test_1115_rotated_solve_raises_on_failure.py::test_a_warm_request_on_zero_fields_with_a_datum_is_a_cold_start | [0]/[0]/[0] | [0]/[0]/[0] | yes |
| test_1131_rotated_nullspace_from_mesh.py::test_a_box_declares_no_mode_and_finds_none | [1]/[11]/[4] | [1]/[11]/[4] | yes |
| test_1131_rotated_nullspace_from_mesh.py::test_a_declared_rotation_pinned_by_a_no_slip_wall_is_rejected | [1]/[19]/[10] | [1]/[19]/[10] | yes |
| test_1131_rotated_nullspace_from_mesh.py::test_a_given_normal_is_tested_not_exempt | [1]/[24]/[11] | [1]/[24]/[11] | yes |
| test_1131_rotated_nullspace_from_mesh.py::test_a_given_normal_wall_off_its_circle_is_tested_against_its_normal | [1]/[26]/[13] | [1]/[26]/[13] | yes |
| test_1131_rotated_nullspace_from_mesh.py::test_a_mesh_that_declares_no_rotation_is_not_warned_about | [1]/[19]/[7] | [1]/[19]/[7] | yes |
| test_1131_rotated_nullspace_from_mesh.py::test_a_move_that_keeps_the_walls_keeps_the_declared_mode | [1]/[26]/[7] | [1]/[26]/[7] | yes |
| test_1131_rotated_nullspace_from_mesh.py::test_a_net_torque_still_warns_under_the_default_normal | [1]/[11]/[10] | [1]/[11]/[10] | yes |
| test_1131_rotated_nullspace_from_mesh.py::test_a_seam_between_a_given_and_a_default_wall_keeps_the_rotation_exempt | [1]/[21]/[14] | [1]/[21]/[14] | yes |
| test_1131_rotated_nullspace_from_mesh.py::test_a_segmented_shell_keeps_its_modes | [1]/[66]/[7] | [1]/[66]/[7] | yes |
| test_1131_rotated_nullspace_from_mesh.py::test_a_units_model_shell_solves_with_its_declared_modes[plain_velocity] | [1]/[87]/[6] | [1]/[87]/[6] | yes |
| test_1131_rotated_nullspace_from_mesh.py::test_a_units_model_shell_solves_with_its_declared_modes[unit_velocity] | [1]/[87]/[6] | [1]/[87]/[6] | yes |
| test_1131_rotated_nullspace_from_mesh.py::test_a_wall_moved_off_its_circle_loses_the_exemption[1e-10] | [1]/[19]/[7] | [1]/[19]/[7] | yes |
| test_1131_rotated_nullspace_from_mesh.py::test_a_wall_moved_off_its_circle_loses_the_exemption[1e-6] | [2]/[20]/[7] | [2]/[20]/[7] | yes |
| test_1131_rotated_nullspace_from_mesh.py::test_a_wall_moved_off_its_circle_loses_the_exemption[1e-8] | [1]/[19]/[7] | [1]/[19]/[7] | yes |
| test_1131_rotated_nullspace_from_mesh.py::test_a_wrong_given_normal_beside_a_default_wall_rejects_the_rotation | [1]/[25]/[12] | [1]/[25]/[12] | yes |
| test_1131_rotated_nullspace_from_mesh.py::test_an_add_fault_child_inherits_the_declaration | [1]/[5]/[13] | [1]/[5]/[13] | yes |
| test_1131_rotated_nullspace_from_mesh.py::test_an_annulus_as_built_keeps_its_declared_mode | [1]/[19]/[7]; []/[]/[] | [1]/[19]/[7]; []/[]/[] | yes |
| test_1131_rotated_nullspace_from_mesh.py::test_an_undeclared_box_in_a_units_model_offers_the_cartesian_rotations | [1]/[9]/[4] | [1]/[9]/[4] | yes |
| test_1131_rotated_nullspace_from_mesh.py::test_mixed_given_and_default_normals_remove_the_rotation | [1]/[26]/[13] | [1]/[26]/[13] | yes |
| test_1131_rotated_nullspace_from_mesh.py::test_the_declaration_is_part_of_the_cached_geometry_and_the_adjoint_record | [1]/[19]/[7] | [1]/[19]/[7] | yes |
| test_1131_rotated_nullspace_from_mesh.py::test_the_direct_lu_route_records_its_verdict_on_the_declared_mode | [1]/[None]/[None] | [1]/[None]/[None] | yes |
| test_1131_rotated_nullspace_from_mesh.py::test_the_direct_lu_route_warns_when_a_given_wall_rejects_the_rotation | [1, 1, 1, 1, 1]/[None, None, None, None, None]/[None, None, None, None, None] | [1, 1, 1, 1, 1]/[None, None, None, None, None]/[None, None, None, None, None] | yes |
| test_1131_rotated_nullspace_from_mesh.py::test_the_shell_returns_no_rigid_rotation[analytic_normal] | [1]/[5]/[17] | [1]/[5]/[17] | yes |
| test_1131_rotated_nullspace_from_mesh.py::test_the_shell_returns_no_rigid_rotation[default_normal] | [1]/[11]/[10] | [1]/[11]/[10] | yes |
| test_1134_fac_cover_gate_structure.py::test_an_unsplit_band_over_the_gate_is_declined_and_recorded | 1:3 | 1:3 | yes |
| test_1134_fac_cover_gate_structure.py::test_the_uniform_level_is_declined_and_recorded | 1:3 | 1:3 | yes |
| test_1145_stokes_adjoint_keeps_custom_mg.py::test_a_nonlinear_adjoint_is_the_transpose_of_the_tangent_at_the_state[eta_vx_matrix_route] | 3:3 [5, 25] | 3:3 [5, 25] | yes |
| test_1145_stokes_adjoint_keeps_custom_mg.py::test_a_nonlinear_adjoint_is_the_transpose_of_the_tangent_at_the_state[powerlaw_newton] | 8:8 [6, 24] | 8:8 [6, 24] | yes |
| test_1145_stokes_adjoint_keeps_custom_mg.py::test_a_nonlinear_adjoint_is_the_transpose_of_the_tangent_at_the_state[powerlaw_picard] | 35:35 [5, 28] | 35:35 [5, 28] | yes |
| test_1145_stokes_adjoint_keeps_custom_mg.py::test_a_nonlinear_adjoint_is_the_transpose_of_the_tangent_at_the_state[powerlaw_picard_matrix_route] | 34:34 [5, 25] | 34:34 [5, 25] | yes |
| test_1145_stokes_adjoint_keeps_custom_mg.py::test_the_adjoint_keeps_the_velocity_hierarchy_and_its_fac_smoother | 1:1 [4, 20] | 1:1 [4, 20] | yes |
| test_1146_custom_mg_after_deform.py::test_a_user_smoother_key_survives_an_install | 1:3 | 1:3 | yes |
| test_1146_custom_mg_after_deform.py::test_the_hierarchy_is_installed_again_after_the_pc_is_reset | 1:3; 0:0 | 1:3; 0:0 | yes |
| test_1146_custom_mg_after_deform.py::test_the_hierarchy_is_installed_once_and_again_after_a_deform[poisson] | 1:3; 0:0; 0:0; 1:5 | 1:3; 0:0; 0:0; 1:5 | yes |
| test_1146_custom_mg_after_deform.py::test_the_hierarchy_is_installed_once_and_again_after_a_deform[stokes_velocity] | 1:1 [4, 20]; 0:0 [4, 20]; 0:0 [4, 20]; 1:1 [7, 20] | 1:1 [4, 20]; 0:0 [4, 20]; 0:0 [4, 20]; 1:1 [7, 20] | yes |
| test_1149_custom_mg_hierarchy_lifecycle.py::test_a_deform_kills_the_fac_patch_and_says_so[poisson] | 1:3; 1:5; 0:0 | 1:3; 1:5; 0:0 | yes |
| test_1149_custom_mg_hierarchy_lifecycle.py::test_a_deform_kills_the_fac_patch_and_says_so[stokes_velocity] | 1:1 [4, 20]; 1:1 [7, 20]; 0:0 [7, 20] | 1:1 [4, 20]; 1:1 [7, 20]; 0:0 [7, 20] | yes |
| test_1149_custom_mg_hierarchy_lifecycle.py::test_a_deform_kills_the_patch_on_the_rotated_fault_route | [1]/[3]/[16]; [1]/[5]/[16] | [1]/[3]/[16]; [1]/[5]/[16] | yes |
| test_1149_custom_mg_hierarchy_lifecycle.py::test_a_mover_kills_the_patch_too | 1:3; 1:4 | 1:3; 1:4 | yes |
| test_1149_custom_mg_hierarchy_lifecycle.py::test_a_rebuilt_stokes_snes_lets_its_ksps_go[gauge] | 1:1 [5, 6]; 1:1 [5, 6]; 1:1 [5, 6]; 1:1 [5, 6]; 1:1 [5, 6] | 1:1 [5, 6]; 1:1 [5, 6]; 1:1 [5, 6]; 1:1 [5, 6]; 1:1 [5, 6] | yes |
| test_1149_custom_mg_hierarchy_lifecycle.py::test_a_rebuilt_stokes_snes_lets_its_ksps_go[guard_armed] | 1:1 [5, 6]; 1:1 [5, 6]; 1:1 [5, 6]; 1:1 [5, 6]; 1:1 [5, 6] | 1:1 [5, 6]; 1:1 [5, 6]; 1:1 [5, 6]; 1:1 [5, 6]; 1:1 [5, 6] | yes |
| test_1149_custom_mg_hierarchy_lifecycle.py::test_a_user_block_ordering_survives_the_drop | 1:3 | 1:3 | yes |
| test_1149_custom_mg_hierarchy_lifecycle.py::test_a_zone_patch_survives_a_deform_and_a_topology_change_kills_it | 1:2; 1:3; 1:5 | 1:2; 1:3; 1:5 | yes |
| test_1149_custom_mg_hierarchy_lifecycle.py::test_fac_keys_leave_the_database_and_the_blocks_keep_lu | 1:3; 0:0; 0:0 | 1:3; 0:0; 0:0 | yes |
| test_1149_custom_mg_hierarchy_lifecycle.py::test_gamg_after_a_fac_install_on_an_adapt_child[poisson] | 1:2; 2:17 | 1:2; 2:17 | yes |
| test_1149_custom_mg_hierarchy_lifecycle.py::test_gamg_after_a_fac_install_on_an_adapt_child[stokes_velocity] | 1:1 [2, 200]; 1:1 [18, 12] | 1:1 [2, 200]; 1:1 [18, 12] | yes |
| test_1157_rotated_warm_resolve_at_roundoff.py::test_a_cold_solve_at_a_large_forcing_is_untouched | [1]/[4]/[7]; [1]/[None]/[None] | [1]/[4]/[7]; [1]/[None]/[None] | yes |
| test_1157_rotated_warm_resolve_at_roundoff.py::test_a_genuine_warm_correction_at_low_viscosity_is_solved | [2]/[78]/[7]; [1]/[4]/[6] | [2]/[200]/[7]; [1]/[4]/[6] | NO |
| test_1157_rotated_warm_resolve_at_roundoff.py::test_warm_resolves_with_satisfied_pressure_converge_without_thrashing | [1]/[4]/[7]; [1]/[4]/[7]; [1]/[4]/[0]; [1]/[4]/[0]; [1]/[4]/[0] | [1]/[4]/[7]; [1]/[4]/[7]; [1]/[4]/[0]; [1]/[4]/[0]; [1]/[4]/[0] | yes |
| test_1159_thin_sheet_solve_takes_picard.py::test_a_manifold_sheet_takes_an_untransported_history | 0:0; 0:0; 0:0; [17]/[None]/[None]; 1:2; 1:8; [15]/[None]/[None]; 1:2; 1:8; [15]/[None]/[None]; 1:2; 1:8; [15]/[None]/[None]; 1:2; 0:0; 0:0; [17]/[None]/[None]; 1:2; [15]/[None]/[None]; 1:2; [15]/[None]/[None]; 1:2; [15]/[None]/[None]; 1:2 | 0:0; 0:0; 0:0; [17]/[None]/[None]; 1:2; 1:8; [15]/[None]/[None]; 1:2; 1:8; [15]/[None]/[None]; 1:2; 1:8; [15]/[None]/[None]; 1:2; 0:0; 0:0; [17]/[None]/[None]; 1:2; [15]/[None]/[None]; 1:2; [15]/[None]/[None]; 1:2; [15]/[None]/[None]; 1:2 | yes |
| test_1159_thin_sheet_solve_takes_picard.py::test_picard_stages_a_picard_phase_on_a_manifold_sheet | [78, 75, 92, 73, 30]/[None, None, None, None, None]/[None, None, None, None, None]; [78, 82, 83, 93, 81, 66, 62, 22]/[None, None, None, None, None, None, None, None]/[None, None, None, None, None, None, None, None]; [78, 82, 83, 96, 73, 29]/[None, None, None, None, None, None]/[None, None, None, None, None, None] | [78, 75, 92, 73, 30]/[None, None, None, None, None]/[None, None, None, None, None]; [78, 82, 83, 93, 81, 66, 62, 22]/[None, None, None, None, None, None, None, None]/[None, None, None, None, None, None, None, None]; [78, 82, 83, 96, 73, 29]/[None, None, None, None, None, None]/[None, None, None, None, None, None] | yes |
| test_1159_thin_sheet_solve_takes_picard.py::test_picard_stages_on_a_fault_contact_sheet | [41, 39, 42, 40, 42, 33, 18]/[None, None, None, None, None, None, None]/[None, None, None, None, None, None, None]; [32, 44, 37, 27, 15]/[None, None, None, None, None]/[None, None, None, None, None] | [41, 39, 42, 40, 42, 33, 18]/[None, None, None, None, None, None, None]/[None, None, None, None, None, None, None]; [32, 44, 37, 27, 15]/[None, None, None, None, None]/[None, None, None, None, None] | yes |
| test_1159_thin_sheet_solve_takes_picard.py::test_picard_stages_on_a_fault_contact_stokes_solve | [1, 1, 1, 1, 1, 1]/[9, 9, 9, 8, 7, 5]/[21, 22, 21, 19, 15, 7]; [1, 1, 1, 1, 1]/[9, 9, 8, 8, 5]/[22, 20, 17, 13, 6] | [1, 1, 1, 1, 1, 1]/[9, 9, 9, 8, 7, 5]/[21, 22, 21, 19, 15, 7]; [1, 1, 1, 1, 1]/[9, 9, 8, 8, 5]/[22, 20, 17, 13, 6] | yes |
| test_1159_thin_sheet_solve_takes_picard.py::test_the_gamg_advice_on_a_refined_sheet_works | [167, 173, 203, 160, 56]/[None, None, None, None, None]/[None, None, None, None, None]; [13, 14, 15, 13, 7]/[None, None, None, None, None]/[None, None, None, None, None] | [167, 173, 203, 160, 56]/[None, None, None, None, None]/[None, None, None, None, None]; [13, 14, 15, 13, 7]/[None, None, None, None, None]/[None, None, None, None, None] | yes |
| test_1159_thin_sheet_solve_takes_picard.py::test_the_gamg_advice_on_a_refined_stokes_mesh_works | [1]/[16]/[6]; [1]/[3]/[6] | [1]/[16]/[6]; [1]/[3]/[6] | yes |
| test_1172_moved_refined_mesh_solves_on_moved_geometry.py::test_a_solve_after_a_move_uses_the_moved_geometry[solver_after_move-default_pc-0] | 1:12; 1:14 | 1:12; 1:14 | yes |
| test_1172_moved_refined_mesh_solves_on_moved_geometry.py::test_a_solve_after_a_move_uses_the_moved_geometry[solver_after_move-default_pc-1] | 2:19; 1:22 | 2:19; 1:22 | yes |
| test_1172_moved_refined_mesh_solves_on_moved_geometry.py::test_a_solve_after_a_move_uses_the_moved_geometry[solver_after_move-default_pc-2] | 2:21; 2:27 | 2:21; 2:27 | yes |
| test_1172_moved_refined_mesh_solves_on_moved_geometry.py::test_a_solve_after_a_move_uses_the_moved_geometry[solver_after_move-fmg-1] | 2:7; 1:6 | 2:7; 1:6 | yes |
| test_1172_moved_refined_mesh_solves_on_moved_geometry.py::test_a_solve_after_a_move_uses_the_moved_geometry[solver_after_move-fmg-2] | 2:7; 2:7 | 2:7; 2:7 | yes |
| test_1172_moved_refined_mesh_solves_on_moved_geometry.py::test_a_solve_after_a_move_uses_the_moved_geometry[solver_before_move-default_pc-0] | 1:12; 1:12; 1:14 | 1:12; 1:12; 1:14 | yes |
| test_1172_moved_refined_mesh_solves_on_moved_geometry.py::test_a_solve_after_a_move_uses_the_moved_geometry[solver_before_move-default_pc-1] | 2:19; 2:20; 1:22 | 2:19; 2:20; 1:22 | yes |
| test_1172_moved_refined_mesh_solves_on_moved_geometry.py::test_a_solve_after_a_move_uses_the_moved_geometry[solver_before_move-default_pc-2] | 2:21; 2:22; 2:27 | 2:21; 2:22; 2:27 | yes |
| test_1172_moved_refined_mesh_solves_on_moved_geometry.py::test_a_solve_after_a_move_uses_the_moved_geometry[solver_before_move-fmg-1] | 2:7; 2:7; 1:6 | 2:7; 2:7; 1:6 | yes |
| test_1172_moved_refined_mesh_solves_on_moved_geometry.py::test_a_solve_after_a_move_uses_the_moved_geometry[solver_before_move-fmg-2] | 2:7; 2:7; 2:7 | 2:7; 2:7; 2:7 | yes |
| test_1172_moved_refined_mesh_solves_on_moved_geometry.py::test_a_solve_after_relax_on_a_refined_annulus_uses_the_relaxed_geometry | 2:4; 1:3 | 2:4; 1:3 | yes |
| test_1172_moved_refined_mesh_solves_on_moved_geometry.py::test_an_adapt_after_a_move_starts_its_multigrid_tail_from_the_moved_mesh | 1:2; 1:2 | 1:2; 1:2 | yes |
| test_1174_a_second_add_fault_keeps_the_first.py::test_a_condition_on_each_side_is_not_warned_about | [1]/[10]/[28]; [1]/[8]/[23] | [1]/[10]/[28]; [1]/[8]/[23] | yes |
| test_1174_a_second_add_fault_keeps_the_first.py::test_a_conforming_surface_keeps_the_split_fault | [1]/[7]/[19] | [1]/[7]/[19] | yes |
| test_1174_a_second_add_fault_keeps_the_first.py::test_a_split_fault_with_no_law_is_named_at_solve | [1]/[11]/[22] | [1]/[11]/[22] | yes |
| test_1174_a_second_add_fault_keeps_the_first.py::test_every_solver_is_told_under_the_default_filter | 1:1 [10, 22]; 0:0 [10, 22]; 1:1 [10, 22]; 0:0 [10, 22] | 1:1 [10, 22]; 0:0 [10, 22]; 1:1 [10, 22]; 0:0 [10, 22] | yes |
| test_1174_a_second_add_fault_keeps_the_first.py::test_the_add_on_levels_keep_the_first_fault | [1]/[5]/[16] | [1]/[5]/[16] | yes |
| test_1174_a_second_add_fault_keeps_the_first.py::test_the_thin_sheet_solve_names_a_fault_with_no_law | 1:6; 1:4 | 1:6; 1:4 | yes |
| test_1174_a_second_add_fault_keeps_the_first.py::test_two_calls_solve_as_one_call_does | [1]/[10]/[20] | [1]/[10]/[20] | yes |
| test_1174_a_second_add_fault_keeps_the_first.py::test_two_calls_solve_as_one_call_does_3d | [1]/[4]/[21]; [1]/[4]/[21] | [1]/[4]/[21]; [1]/[4]/[21] | yes |
| test_1176_custom_mg_transfer_after_a_move.py::test_a_base_moved_before_an_adapt_goes_into_the_child_where_it_stands[at-rest] | 1:2 | 1:2 | yes |
| test_1176_custom_mg_transfer_after_a_move.py::test_a_base_moved_before_an_adapt_goes_into_the_child_where_it_stands[wall-raised] | 1:2 | 1:2 | yes |
| test_1176_custom_mg_transfer_after_a_move.py::test_a_fault_cut_into_a_moved_mesh_is_read_where_it_is | [1]/[6]/[15] | [1]/[6]/[15] | yes |
| test_1176_custom_mg_transfer_after_a_move.py::test_a_moved_level_under_the_finest_keeps_its_transfer | 1:3; 1:2 | 1:3; 1:2 | yes |
| test_1176_custom_mg_transfer_after_a_move.py::test_a_moved_quadrilateral_level_is_read_where_it_is | 1:2; 1:2; 1:2 | 1:2; 1:2; 1:2 | yes |
| test_1176_custom_mg_transfer_after_a_move.py::test_a_moved_tetrahedral_level_keeps_its_transfers | 1:3; 1:3; 1:3 | 1:3; 1:3; 1:3 | yes |
| test_1176_custom_mg_transfer_after_a_move.py::test_a_moving_wall_keeps_the_velocity_iterations | 1:1 [3, 17]; 1:1 [3, 17]; 1:1 [3, 17]; 1:1 [3, 17]; 1:1 [3, 17] | 1:1 [3, 17]; 1:1 [3, 17]; 1:1 [3, 17]; 1:1 [3, 17]; 1:1 [3, 17] | yes |
| test_1176_custom_mg_transfer_after_a_move.py::test_a_relax_in_a_call_of_its_own_is_part_of_making_the_mesh | 1:2; 1:2 | 1:2; 1:2 | yes |
| test_1176_custom_mg_transfer_after_a_move.py::test_a_relaxed_adapt_child_is_read_where_the_relax_left_it | 1:2; 1:2 | 1:2; 1:2 | yes |
| test_1176_custom_mg_transfer_after_a_move.py::test_a_reloaded_mesh_is_read_on_its_rebuilt_refinement | 1:3; 1:2 | 1:3; 1:2 | yes |
| test_1176_custom_mg_transfer_after_a_move.py::test_a_split_level_solve_after_a_move_keeps_its_iterations | [1]/[6]/[15]; [1]/[6]/[15]; [1]/[6]/[15]; [1]/[6]/[15]; [1]/[6]/[15] | [1]/[6]/[15]; [1]/[6]/[15]; [1]/[6]/[15]; [1]/[6]/[15]; [1]/[6]/[15] | yes |
| test_1176_custom_mg_transfer_after_a_move.py::test_the_fmg_preconditioner_keeps_its_iterations_over_moves | 1:2; 1:2; 1:2; 1:2 | 1:2; 1:2; 1:2; 1:2 | yes |
| test_1176_custom_mg_transfer_after_a_move.py::test_the_transfers_after_a_move_are_those_before_it[native-deform] | 1:1 [2, 11]; 1:1 [2, 11] | 1:1 [2, 11]; 1:1 [2, 11] | yes |
| test_1176_custom_mg_transfer_after_a_move.py::test_the_transfers_after_a_move_are_those_before_it[placed-deform] | 1:3; 1:5 | 1:3; 1:5 | yes |
| test_1176_custom_mg_transfer_after_a_move.py::test_the_transfers_after_a_move_are_those_before_it[placed-mover] | 1:3; 1:5 | 1:3; 1:5 | yes |
| test_1176_custom_mg_transfer_after_a_move.py::test_the_transfers_after_a_move_are_those_before_it[split-level-deform] | [1]/[6]/[15]; [1]/[6]/[15] | [1]/[6]/[15]; [1]/[6]/[15] | yes |
| test_1240_coarse_levels_move_with_the_finest.py::test_quadrilateral_multigrid_holds_on_a_rising_wall | 1:1 [4, 18] | 1:1 [4, 18] | yes |
