# Bringing the fault-split work onto `development`

**Status**: integration map and plan from the docs hub, 2026-10-28. Louis's ruling: the
work is being written up (UWTN 2026-018 and 2026-022), a published note implies the
functionality is not experimental, so what the notes describe must operate now and
reach `development` soon. Nothing here is merged yet; the candidate head is built and
compiles but is untested.

## The branches, and how they relate

Every October fault branch descends from one root, cut from `development` at
`f414da63` (14 October). `development` has moved 160 commits since; every branch below
merges onto today's `development` (7222caf3) cleanly on its own.

```
development f414da63
└── feature/fault-split-multigrid (54)        the method: split-level hierarchy, side-aware
    │                                          transfer, per-level frames, orphan drop; the
    │                                          ThinSheet solver, manifold solves, extrude; the
    │                                          zg95 annulus driver; subsystem + design docs
    ├── feature/parallel-addon-distribution (+50)   hyperion: the add-on partitioned once,
    │   │                                            parallel transfers into a split finest,
    │   │                                            adversarial review done (docs/reviews/2026-10)
    │   └── bugfix/custom-mg-empty-rank (+2)         custom-P MG and the cut on ranks holding no
    │       │                                        coarse cells (regression tests)
    │       └── feature/coarse-solve-nullspace (+16) WIP coarse-solve benchmarks behind
    │                                                UW_ROTATED_COARSE, UWTN figure scripts,
    │                                                the hyperion hand-over. NOT for development.
    └── feature/box-faults (+1) → feature/box-faults-warm (+2)   laptop: the split-ladder tail
        │                                            and driver rules (c1107957); the rotated
        │                                            solve's residual history and line-search
        │                                            record (99259d35); the Newton-switch fix
        │                                            (dd6be744, identical to hyperion's 371d3bd1)
        └── bugfix/faulted-rebuild-leak (+11)        the leak fix, reviewed and validated on this
                                                     base; kaiju's production overlay
```

Beside the tree, three small branches on `development` itself:

| branch | commits | what | state |
|---|---|---|---|
| `bugfix/faulted-rebuild-leak-dev` | 13 | the leak fix cherry-picked onto development 7222caf3 | tier A serial 1499 passed; parallel np 2 159 passed, np 4 167 passed; **review 3's four should-fix findings not yet addressed** (`scripts/sessions/rebuild_leak/README.md`) |
| `bugfix/warm-start-newton-switch` | 1 | the Picard-to-Newton switch measured against the rest-state reference | done, tested (test_1018) |
| `bugfix/rotated-solve-diagnostics` | 2 | kaiju's residual and line-search reporting | verified on hyperion |

The two lineages diverged in the same files, so merging them pairwise looks like
thirteen conflicts; against their true common base the whole divergence is **one hunk in
`rotated_bc.py`** (the laptop appends the residual history where hyperion widened the
cold-start condition for a datum-only sheet) and one adjacent-addition conflict in
`test_1018` (the laptop's diagnostics test). The laptop's library delta beyond the root
is 28 lines, all in `rotated_bc.py`.

## What the notes stand on

| Note | Pinned to | Describes | Lands with |
|---|---|---|---|
| UWTN 2026-022 Faults and patch-refinement of the mesh (branch `note/faults-on-an-add-on-mesh`) | `feature/coarse-solve-nullspace @ e135429f` (figures), sources on `parallel-addon-distribution`, `rotated-solve-diagnostics` 210c7307, `box-faults-warm` 371d3bd | the static base and ephemeral add-on, refining and cutting, the levels carrying the fault, moving the fault, warm starts and restarts, the trench, costs and refusals, parallel | the root, the parallel-addon lineage, the rotated-solve diagnostics and switch, the leak fix (the restart and rebuild costs) |
| UWTN 2026-018 Faults in parallel: partitioning the add-on once (`note/faults-in-parallel`) | `feature/parallel-addon-distribution @ 8fe9ad76` | the add-on frame, one partition for the add-on, the transfers, the band through the partition boundary, what is refused | the parallel-addon lineage |

Checked 2026-10-28: every identifier in the two notes' code spans exists in the
integrated tree, and the "Using it" recipe of 2026-022 (`base.adapt`,
`child.add_fault`, `add_fault(..., split_levels=False)`, `stokes.add_fault_bc`,
`stokes._rotated_freeslip_info`) resolves there. Neither recipe runs on `development`
today: `fault_mg.py`, `split_levels` and the add-on partition are all branch work.
Once merged, each note's `software_version` moves to the `development` merge commit
(HUB.md item (e) for 2026-018).

## The candidate head

Built in the hub's scratch worktree, `d81a2588`, as merges in this order onto
`development` 7222caf3, each a merge commit, none a rebase:

1. `bugfix/custom-mg-empty-rank` (carries the root and the parallel-addon lineage): clean.
2. `bugfix/warm-start-newton-switch`: clean.
3. `feature/box-faults-warm`: the one hunk in `rotated_bc.py` resolved by keeping both
   (history append, then the widened condition); `test_1018` takes the laptop's
   diagnostics test beside hyperion's switch test.
4. `bugfix/rotated-solve-diagnostics`: the same hunk, HEAD kept.
5. `bugfix/faulted-rebuild-leak-dev`: clean.

Both resolved files compile. One `rnorm_history.append`, one diagnostics test, one
switch test: nothing duplicated. **Not built, not run.** The head exists only in this
session until it is pushed as `feature/fault-split-integration`.

Left out on purpose: `feature/coarse-solve-nullspace` (measurement code and a design
awaiting Louis's decision: MUMPS with null-pivot detection as the rotated-path coarse
default, SVD as the fallback). Its UWTN figure scripts (`scripts/sessions/fault_mg/`,
8a74053b and 1c6ce485) can be cherry-picked onto the integration head if the notes need
them in the repository the note cites.

## The pull requests

One topic per PR, in landing order; each gets its adversarial review before it opens.

| | PR | Base | Review state | Blocks |
|---|---|---|---|---|
| A | `bugfix/faulted-rebuild-leak-dev`: a dropped faulted mesh is freed | development | reviews 1 and 2 done; **review 3's four should-fix items open** (gc timing against the collective snapshot loop; `Swarm.mesh` by id; the enhanced wrapper not owned by the mesh; `MeshVariable.__del__`'s explicit destroy) | the fixes, then the suites again |
| B | `feature/fault-split-multigrid`: split-level fault multigrid and the thin-sheet solver | development | **no review record found on the branch**; the parallel-addon review covered its own delta only | an adversarial review of the root (parallel rank asymmetry, the manifold solves, the tier of the 15 new tests) |
| C | `bugfix/custom-mg-empty-rank` head (parallel-addon + empty-rank) plus the three small branches, i.e. the candidate head minus A and B | B's branch, retargeted to development when B merges | parallel-addon reviewed 2026-10-17 with fixes; the empty-rank fixes carry regression tests; the merged `rotated_bc.py` needs one reviewer's read | B |

B and C can open together as a stacked pair, so reviewers see each delta on its own
while the integration is testable as one head. If Louis prefers one PR for speed, it is
the candidate head with A folded in; it is then 180 commits and 40 source files, and the
review is the three reviews above done at once.

## Validation, and who runs it

The hub cannot build. The candidate head needs, on a machine with a PETSc environment:

1. `./uw build`; `pytest -m "level_1 and tier_a"` serial; `tests/parallel` at np 2 and 4;
   the fault and multigrid tests by name (`test_1086`, `test_1089`, `test_1095` to
   `test_1099`, `test_0077`, `test_0078`, `test_1018`, `test_1058`).
2. The 2026-022 recipe as written, on the head, at np 1 and np 8: slip and iteration
   counts against the note's figures (`figures/src/README.md` on the note branch holds
   every number).
3. The kaiju production case as an overlay built from the head: the 30-step restart
   A/B that validated the leak fix (slip to 1e-9, memory flat).

Where: the laptop (wombat) has an environment on 547c2e54 and can build the head and run
1 and 2 at np 1 to 4; kaiju runs 3 and the np 8 column of 2 as an overlay; hyperion,
when it is back from the reimage, owns review 3's fixes (A) and the review of B. The
science hub holds the machine sessions; this hub holds the head, the PR bodies and the
notes' re-pin.

## Decisions (Louis, 2026-10-28)

1. **Pushed**: `feature/fault-split-integration` is d81a2588 on underworld3. The work is
   spun off to the laptop: build, suites, review 3's fixes on the leak, the review of
   the root, and the PRs. Hyperion's reimage is slower than expected and is not waited
   for.
2. **Multiple PRs, resolved rapidly.** A, B, C as above. A documentation PR does not
   wait for the full test suite before acceptance (the docs build is enough).
3. **Coarse solve: not MUMPS as the default** (good on Linux, breaks on the Mac).
   Deal with the rotation null space explicitly and let PETSc's defaults handle the
   coarse level; a coarsest level that is too large is a hierarchy that was not built
   coarse enough, which has happened before, not a case for a heavier solver.
   `feature/coarse-solve-nullspace` stays a measurement branch; the null-space work is
   a separate item. Journal entry: `2026-10-28-coarse-solve-null-space-first-petsc-defaults-not-mumps`.
4. Reviews and fixes are real work and the laptop does them.

## Progress (laptop session `session_01HxWvn5rMK67zasgirdXszQ`)

**2026-10-28, validation of d81a2588 complete.** Tier A serial 1515 passed, 0 failed;
parallel np 2 156 passed, 2 failed; np 4 187 passed, 2 failed; the fault and multigrid
tests by name all pass. Both failures predate the head: `test_0078` reads
`/proc/self/statm` (macOS; made portable on A) and `test_1063_constrained_freeslip_parallel[ti]`
(37.7525 against 37.0780 at rtol 0.01, identical on development 7222caf3). UWTN 2026-022's
fixture reproduces to ten digits in slip and exactly in iteration counts; the "Using it"
recipe runs (serial 7 velocity iterations, slip 0.15916181; np 4 5 iterations, slip
0.15916189) but its level count depends on the rank count because `base.adapt`'s
intermediate levels are partition-dependent when `h_far` sits above the base's finest
cell, on development too. Journal entry
`2026-10-28-fault-split-integration-head-reproduces-uwtn-2026-022`.

**Development moved 38 commits** (#846, #850 to #853) since the head's base: the root,
the parallel lineage and box-faults-warm now conflict with it in `systems/solvers.py`,
`systems/ddt.py` and `constitutive_models.py`; A, the warm-start switch and the
diagnostics still merge clean. The laptop resolves a development merge on B's and C's
branches before each opens.

**A**: review 3's four fixes pushed with regression tests (a206fb17; a new parallel
`test_0079` hangs on the unfixed branch as the review predicted); `test_0078` made
portable (fcbc5f6e). Suites running, then the re-review and the PR. The laptop asked
Louis directly whether `scripts/sessions/rebuild_leak/` (two probes, eight `.jsonl`
run records) stays in A, against his 2026-10-15 ruling that keeps campaign drivers and
run outputs out of underworld3; its proposal is README findings into
`subsystems/model-orchestration.md`, the rest to uw3-campaigns.

**2026-10-29.** **A is open: underworld3 #882** (base development). Review 3's four
findings fixed with fail-first tests, a fourth round found and fixed four more (a proxy
callback re-pinning a mesh, stats temporaries' vectors, repeated and rank-0-only
collections in the snapshot path, test tiers). Louis ruled library and docs only, so
`scripts/sessions/rebuild_leak/` left the branch (kept in `~/+Simulations/rebuild_leak`
on the laptop); the findings are in `subsystems/model-orchestration.md`. Suites: tier A
serial 1494 passed, 0 failed; parallel np 2 164 passed, np 4 172 passed; the only
failure is `test_1063[ti]` (#826), as on development. Issues left open from the
reviews: #866, #867, #868. (Correction to the head's earlier parallel counts: np 2
176 passed / 2 failed / 14 skipped; np 4 187 / 2 / 3.)

**B** (`feature/fault-split-multigrid` 3ecbf6e7) is development-merged and reviewed
twice; final suites running, then it opens. Louis's rulings of 2026-10-28 on B's
review: (1) `objective_order` defaults to 1 for every solver as on development, and
ThinSheet selects Cayley itself; (2) every `scripts/sessions` file leaves B and C,
`scripts/sessions/fault_mg` included (`library_c.py` and the UWTN 2026-022 figure
scripts; copies in `~/+Simulations/fault_split_mg_scripts` and
`~/+Simulations/fault_split_c_scripts` on the laptop) **so the notes may not cite
those underworld3 paths: the scripts go to uw3-campaigns when Louis says, and the
notes' `figures/src/` already carries its own copies**; (3) `test_1081` and
`test_1084` are tier C, reported and not gated. Measured on B: a rotated free-slip
solve on an adapted annulus with custom FMG takes 18 velocity iterations serial and
197 at np 4 on development, 3 and 4 on B (the per-level wall rotation), same answer;
journal entry `2026-10-29-per-level-wall-rotation-...`. The development merge had
dropped the base refusal of a rotated adjoint (#846) so a manifold ThinSheet solved the
unrotated transpose; fixed in B (52ac7820).

**C** (`feature/fault-split-integration`, laptop-local 4698938f, not yet pushed): B's
new commits and A merged in (six conflicts resolved; development's ETD Maxwell-time
code kept over the lineage's 9e97670b, which made the same repair; `test_1093`
removed as a duplicate of development's `test_1053`). Its review found two must-fix
(the faults-in-convection capability guide still said `picard=N` raises and gave the
`newton_switch_rtol=1.0` workaround; the campaign drivers), both fixed; the should-fix
items mostly filed. One finding in the hand-resolved `rotated_bc.py` hunk: the widened
datum-only cold-start condition takes its reference from the lifted iterate, costing
one extra increment on a linear datum-only solve (answer right); under continuation
it may skip Picard, unmeasured. The hub's advice: leave the resolution, measure the
continuation case, fix in its own small PR after C (journal entry
`2026-10-29-datum-only-cold-start-reference-...`).

**B's review (2026-10-28) was not a quick PR.** Must-fix items reported: `test_1091`
matches no CI glob (`check_test_coverage` exits 1); `test_1087` asserts one method beats
another (Charter forbids); `test_1081` and `test_1084` would gate every PR at 13 and 7
minutes; ThinSheet's `L` and `c_b` are built with the name-shared `uw.expression`, so
a user's own `L` is reset to 1; rank-local raises before collectives in
`split_tail_levels` and the manifold `build_rotation`. **Two items change solver
behaviour for users with no fault and need Louis's ruling before B opens**: (i)
`custom_mg` `drop_orphans=True` on every hierarchy discards coarse FAC patches and
routes every rotated free-slip custom-FMG solve (annulus, shell) through
`rotated_split_transfers`, with no benchmark evidence; (ii) a Jaumann default change
(`objective_order` cayley) visible to Stokes users. The full list and B's plan follow
once A is open.
