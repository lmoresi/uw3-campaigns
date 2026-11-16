# Findings that need an issue but have none yet

C1's attempt to file an issue on 2026-11-16 was refused by its permission check. Under CLAUDE.md, a finding that no branch fixes is filed. Until Louis decides how these get filed (by him, by allowing C1, or by routing each to a desk as a fix PR with no issue), they are kept here. Each entry names who found it and where the evidence is.

| # | Finding | Found by, where | Status |
|---|---|---|---|
| 1 | Stokes_Constrained with a P3 velocity is about 26% below the essential-wall solution; P2 agrees to 7 digits (4x4 quad box, Left/Right normal held by the constraint vs `add_essential_bc((0.0, None))`; max \|v\| 0.0507 vs 0.0686). On development too; index sets ruled out; suspect the constraint assembly at degree 3. Draft issue text in C1's scratchpad (p3issue.md); the evidence is item 3 of H1's review comment on #1200. | H1, review of #1200 (item 3) | waiting on Louis |
| 2 | #824's remaining defect: `uw.unwrap`'s parameter meanings differ from their docstrings and tutorials 3 and 13 (keep_constants=True selects 'dimensional' mode; apply_scaling has no effect under the default). #1209 fixed only the forwarding. | W1, #1209 body | waiting on Louis (fix or file) |
| 3 | 15 located rows near a fault trace in the fault-MG transfer change with the partition, on development too. | H1, review of #1206 | named in #1206's body; untouched |
| 4 | Two runs of the same development build at np 4 differ by up to 9.5e-14 (plain and constrained Stokes, 3-D box, FMG); the rotated free-slip annulus differs by 4.7e-16 even at np 1 and 2. Within tolerance under Louis's reproducibility principle; recorded, not chased. | H1, review of #1200 (item 4) | informational |
| 5 | test_0768's odd-node-count manifold case always skips (every size tried has an even count); the file fails under `mpirun -n 2` because each rank gets its own tmp_path (harness). | H1, review of #1207 | small; any desk |
| 6 | Case 2a: when only the finest level moves, serial and parallel nest a re-partitioned level on different geometries, so the #1120 repair differs with rank count (x 0.015: serial 0 rows / 13 weak, np 3 31 rows / 2 weak). | H1 and H5, #1206 | in W1's coarse-levels design note (required case 2a); awaits Louis's design decision |

Underworld development team with AI support from Claude Code
