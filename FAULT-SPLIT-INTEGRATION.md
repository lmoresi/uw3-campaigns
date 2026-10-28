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

## What needs a decision

1. Push `feature/fault-split-integration` (d81a2588) to underworld3 now, so the head
   survives this session and the machines can build it. The hub's standing rule is to
   push only its own branch; this needs a yes.
2. Stacked B and C, or one PR.
3. The coarse-solve default (MUMPS against SVD), which decides whether
   `feature/coarse-solve-nullspace` follows as D or stays a measurement branch.
4. Who reviews B: a fresh session against the root's diff, or Louis.
