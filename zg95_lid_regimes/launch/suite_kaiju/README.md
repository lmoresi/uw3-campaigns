# The annulus regime suite for kaiju

Four runs from checkpoint 3910 of `ra3x_tau1x1.50_lines` (t 0.4696, Ra 2.73e6,
tau1/Ra 1.5, mobile lid with two faulted downwellings), varying the two things the
laptop runs said matter: how strong the intact lid is, and how weak the layer under
it is. Every run has the asthenosphere channel, the surface yield stress raised so
the skin does not yield everywhere, stronger strain weakening, the fault depth cap
tied to the lid base and the clearance rule.

| run | Ra | tau1/Ra | tau0 | weak_min | asthenosphere | refinement |
|---|---|---|---|---|---|---|
| ra3e6_t1.5_asth | 2.73e6 | 1.5 | 6.075e4 | 0.25 | 0.1 in 0.3-0.7 d | 4 (d/32) |
| ra3e6_t3.0_asth | 2.73e6 | 3.0 | 6.075e4 | 0.25 | 0.1 in 0.3-0.7 d | 4 (d/32) |
| ra1e7_t1.5_asth | 9.1125e6 | 1.5 | 6.075e4 | 0.25 | 0.1 in 0.25-0.7 d | 5 (d/64) |
| ra1e7_t3.0_asth | 9.1125e6 | 3.0 | 6.075e4 | 0.25 | 0.1 in 0.25-0.7 d | 5 (d/64) |

`common.sh` holds the shared flags; each `run_*.sh` adds its own and launches. Set
`UW3_WORKTREE` (a checkout of underworld3 `feature/box-faults` at c1107957 or later,
built), `UW3_CAMPAIGNS` (this repository), `ZG95_RUNS` (the output root) and `NP`
(ranks, from the scaling tests) in the environment. The checkpoint set to copy into
each run directory before launching: `annulus.mesh.00000.h5`, `annulus.mesh.03910.xdmf`,
`annulus.mesh.*.03910.h5`, `state_03910.json`, `records.json` (22 MB).

Open point: the d/64 runs restart a d/32 checkpoint onto a finer base
(`read_timestep` remaps by coordinate); check the first record against the d/32
one (T_mean, q_top, vrms within a few per cent) before trusting the run.
