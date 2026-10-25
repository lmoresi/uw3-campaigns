# Hub: state of Louis's Underworld work across machines

The cloud hub session keeps this file current. It is the single point of truth for which
machine does what, what is running, what is open, and what waits on Louis. Read it before
acting. Newest entries in the log at the bottom win over anything above them that they
contradict.

## Restarting the hub

The hub is a Claude Code cloud session on `underworldcode/underworld3`. It holds no state that
is not in this file, on GitHub, or in session transcripts. If it dies:

1. Start a new cloud session on `underworldcode/underworld3` with this prompt:
   > You are the hub that coordinates Louis Moresi's Underworld work across his machines.
   > Read `HUB.md` in lmoresi/uw3-campaigns (main) and follow it. The previous hub was
   > `<session id below>`; read its transcript (claude-code-remote `list_events`) only for
   > detail this file lacks. Then confirm the state to Louis in a few lines.
2. Approve the "reach my other sessions" card when the new hub first messages a machine. The
   grant is per session.
3. The new hub tells each machine session its session id, and updates this file.
4. Re-arm any check-ins (scheduled tasks are bound to the session that made them).

| | Session id |
|---|---|
| hub (current) | `session_013CgVT1Gx9WTvaZVqU58HsQ` |
| hyperion | `session_01QZvR7SZKsjcFnzx2aLxn1j` ("hyperion-zesty-dijkstra") |
| kaiju | `session_01HX67HY6xwuJivHKLLXrR3H` ("kaiju-anu-edu-au-jiggly-magpie") |
| kaiju dev (driver restart fixes) | `session_015H8d4zLWhW1moUQ8u1nMtw` ("kaiju: annulus driver restart fixes"), started by the hub 2026-10-23 |
| laptop (wombat), lid regime | `session_019aromUkeWWPzcL2Kb8365E` ("Lid regime box heating runs") |

Messaging: the hub can message all three. Kaiju and the laptop can message the hub. Hyperion
cannot (its Claude Code is too old to prove a trusted device), so the hub reads its transcript.

## Machines and roles

**hyperion**: one big box with a failing system disk (nvme0 throws EIO); a disk rebuild is
scheduled (weekend of 2026-10-25), so /mnt/data may not survive. **Commit and push after every
meaningful change, WIP included; results tables and probe scripts go in the branch.** The hub
checks every 3 h that hyperion's commits are on origin. Use it for
**fast-turnaround parallel development jobs** (tests, probes, np 2-16, minutes, not days).
No long campaigns.
- Everything lives on the second drive under `/mnt/data/lmoresi/`: the `underworld3` clone,
  `Simulations` (symlinked from `~/+Simulations` once Louis approves), the caches, and
  `claude-mirror`. Nothing of value goes on nvme0.
- Pixi env `dev` (conda-forge PETSc 3.25). It needs `PIXI_CACHE_DIR`, `RATTLER_CACHE_DIR`,
  `XDG_CACHE_HOME`, `UW_JIT_CACHE_DIR` and `TMPDIR` pointed at `/mnt/data/lmoresi/...`, plus
  `OMP_NUM_THREADS=1`.
- The rescue copy of the old disk is in `/mnt/data/lmoresi/hyperion-rescue-2026-10-20/`. It is
  frozen; do not modify it.

**kaiju**: a Slurm cluster. Use it for **long runs and campaigns**.
- All of n1-n8 are up since Louis's resume on 2026-10-23 (n3 is bigmem, 378 GB). Each node has 52 cores (Slurm counts 104 CPUs) and 140-188 GB.
- Underworld3 runs in Apptainer. Use the personal image `~/uw3/images/uw3-gadi-development-20261021.sif`
  (the shared site images are stale and have no g++), and run a branch as an overlay built
  inside it. See [uw3-hpc-install-run kaiju/container](https://github.com/underworld-community/uw3-hpc-install-run/tree/main/kaiju/container)
  (PR #1).
- Overlays: `~/uw3/overlay-bn` (bugfix/backward-nodes-snapshot-order) and
  `~/uw3/overlay-box-faults` (feature/box-faults c1107957).
- Submit from home (`/tmp` is node-local). All I/O goes through the login node's NFS. There is
  no scratch filesystem.
- **There are no GitHub credentials on kaiju.** Fixes come to the hub as `git format-patch`
  output, and the hub pushes them.

**wombat (laptop)**: development only since 2026-10-23, no production runs (8-core budget).
Commits to uw3-campaigns only when Louis asks. The lid-regime campaign moves to kaiju.

## Standing rules (Louis)

- Never `pip install -e`. Work on side branches, never development or main of underworld3.
  Push after every commit. Run `git show --stat HEAD` before every push.
- Every bug fix ships the regression test, shown failing first. Run an adversarial review before
  every PR. Open PRs only when Louis asks.
- Fix rather than flag. Solver tuning only with benchmarks. No direct LU. A silent GAMG fallback
  is a misconfiguration. Everything parallel-safe.
- Never rebalance the base mesh. One nested ladder hierarchy for split and TI faults.
- No default changes until Louis has seen evidence. The JOSS paper is frozen.
- Commit messages end with "Underworld development team with AI support from Claude Code" and
  carry no Co-Authored-By line.
- Show figures through GitHub links. Write useful machine knowledge back to
  underworld-community/uw3-hpc-install-run. If a container must be built, use conda PETSc.

## Open work

| What | Where | State |
|---|---|---|
| Stress-transport fix | underworld3 `bugfix/backward-nodes-snapshot-order` | d77bc9d2 (recreated after the disk failure, identical to 6549d30b); verified on hyperion and kaiju. Follow-ups running on hyperion: Eulerian/SUPG ordering, docs, renumber test_1076, review. No PR yet. |
| VE/plastic gap closure | PRs #851 #852 #853 #854 | open |
| subksp banner #827 | PR #850 | open |
| Parallel add-on distribution | `feature/parallel-addon-distribution` 8fe9ad76 | pushed, no PR |
| Shear-band length scale | `feature/shear-band-length-scale` 114c472c | second adversarial review owed |
| Tidal shell / box-fault study | `feature/tidal-shell` fc35972a | waiting on Louis: gravitational topography term, next sweep |
| Hyperion rescue WIP | underworld3 branches `*-hyperion-2026-10-20*`, uw3-campaigns `main-hyperion-2026-10-20-wip` | saved, untriaged |
| Lid-regime annulus campaign | uw3-campaigns `zg95-annulus-for-kaiju` 361657f (restart fixes and ffmpeg fallback merged); library `feature/box-faults-warm` 99259d35 | on kaiju; slab production awaits Louis's case list |
| Restart / warm-start fixes + solver record + faulted-mesh checkpoint + docs | merged into `zg95-annulus-for-kaiju` (4955e80); branch head 361657f | done |
| Kaiju docs | underworld-community/uw3-hpc-install-run PR #1 | open |
| Parallel `read_checkpoint` bug | found on kaiju, 2026-10-21 | not filed or fixed yet; the lid-regime driver is not affected |
| Technical note UWTN 2026-022 "Faults on an add-on mesh" (M3/F3 settled: this is the serial method) | Underworld-Technical-Notes/underworldcode.org `note/faults-on-an-add-on-mesh` 948bb02 (local to the hub; push refused, see Waiting on Louis) | first draft written 2026-10-25; three figures declared, to be made on hyperion |
| Technical note UWTN 2026-018 "Faults in parallel" revision | `note/faults-in-parallel` 168ad65 | brief sent to the wombat notes-workbench session (session_011S876ckjYqqth1aPyojrhh) 2026-10-25; it also owes the hub a notes-workflow proposal |
| Adjoint notes UWTN 2026-020 / 2026-021 | PR #59 (green, awaiting Louis's merge) / `note/discrete-adjoint` 87fbcb1 (held until the viscosity-floor example has a result) | wombat session session_018wSha1nV5DddcThnCRoFab |
| Slab control set (11 of 12) | kaiju `~/campaigns/zg95/figures_out/slab_control/` (5.5 MB, README with the table) | done; layered_mantle runs to its 12 h wall (~step 50, t 0.005) and is added after |
| Slab faulted set | kaiju `~/campaigns/kaiju-launch/slab_fault/` | waits for the laptop's slab_fault figure hash on e009873 |
| Rotated-solve diagnostics | underworld3 `bugfix/rotated-solve-diagnostics` 210c7307 (on 371d3bd) | written on kaiju, pushed by the hub; hyperion runs the suites |

## Waiting on Louis

- Install the Claude GitHub App for the Underworld-Technical-Notes organisation (https://github.com/apps/claude/installations/select_target), so the hub can push note branches; until then the hub hands patches to the wombat notes session.
- Regenerate PREVIEW_TOKEN in Underworld-Technical-Notes/underworldcode.org (rejected since after 2 Oct; every PR preview fails, production deploy unaffected). Merge PR #59 (UWTN 2026-020) when ready.
- rsync the slab controls to the laptop: `rsync -av louis@kaiju.anu.edu.au:campaigns/zg95/figures_out/slab_control/ ~/+Simulations/zg95/kaiju_figures/slab_control/`, then the laptop commits them to zg95-annulus-for-kaiju.
- Make uw3-campaigns public (agreed), so kaiju can clone it.
- rsync the laptop's checkpoint-3910 set to kaiju `~/campaigns/zg95/runs/ra3x_tau1x1.50_lines_laptop_3910/`.
- rsync kaiju:campaigns/zg95/samples/i3_sample/ to the laptop's ~/+Simulations/zg95/kaiju_samples/i3_sample/.
- Approve commands in the new kaiju dev session.
- Choose the first kaiju sweep (the laptop session recommends tau1/Ra 2.5-3 at Ra x3, from 3570/3580).
- Hyperion: approve the `~/.bashrc` env lines and phase 3 (Simulations symlink, hourly
  `~/.claude` mirror, local notes).
- Update Claude Code on hyperion and restart its session there (restores hyperion -> hub messages).
- Get the hyperion rescue's 449 MB `claude/` directory off the machine.
- Whether the parallel `read_checkpoint` bug goes to hyperion as the next fix.

## Log

- 2026-10-18: hyperion's system disk failed. The hub recreated the unpushed stress-transport
  fix (d77bc9d2) and pushed it; it was later verified identical to the original.
- 2026-10-19/20: recovered the hyperion sessions' work from transcripts. Everything committed
  was already on GitHub; the transcript-only material went to Louis.
- 2026-10-20: rescued hyperion's surviving files to /mnt/data (92.1 of 92.1 GB; 9 files
  unreadable). Fresh clone and build on /mnt/data; 1494 tier-A tests pass.
- 2026-10-21: the stress-transport fix was verified on hyperion (49 passed; test_1076 fails
  without the fix). Kaiju surveyed: the site images are stale; a personal image plus an overlay
  runs any branch (test_1076 3 passed at np 1 and 2), documented in uw3-hpc PR #1. Kaiju got its
  feature/box-faults overlay; the annulus smoke test passes at 8 ranks.
- 2026-10-22: roles set (hyperion for fast development, kaiju for campaigns). Hyperion started
  the stress-transport follow-ups. The lid-regime drivers were pushed (e258447). Kaiju's rules:
  no credentials, fixes go to the hub as patches. Louis agreed to make uw3-campaigns public.
  This file was created.
- 2026-10-23: uw3-campaigns made public; kaiju cloned zg95-annulus-for-kaiju and wrote its launch
  scripts (~/campaigns/kaiju-launch/, uncommitted). The first patch came through the hub:
  kaiju/movie-ffmpeg-fallback 9f7a2e2. **All eight kaiju nodes went down together at 17:22 on
  10-22 ("Node unexpectedly rebooted")** and need `scontrol update NodeName=n[1-8] State=RESUME`
  from an admin. Job 2070 is queued behind that. Restart layout: kaiju's
  `~/campaigns/zg95/runs/ra3x_tau1x1.50_lines/` mirrors the laptop run and kaiju only reads it.
  Kaiju restarts in a sibling directory, `..._kaiju3580`, because the driver truncates
  records.json and would overwrite the laptop's later checkpoints.
- 2026-10-23 (later): Louis resumed the kaiju nodes, and all eight are idle (n1-n4 are back too).
  The laptop is now for development only; kaiju is production for lid-regime. The checkpoint set is
  in `~/campaigns/zg95/checkpoints/ra3x_tau1x1.50_lines/` (records to step 3910), and kaiju may
  reorganise it. Bootstrap job 2070 OK (8 ranks, convection steps 6.5-13 s, 2.8 GB rss). Fresh
  faulted test 2071 OK (10 steps, ~60 s/step, 4.4 GB rss) but too short to trigger a fault
  rebuild. Restart check 2072 (3580 -> 3600 against the laptop's records) is running.
- 2026-10-23: Louis's ruling: validate scaling to more cores before any science runs on kaiju.
  Rank-count study from the 3580 restart, 15 steps (covering the laptop's rebuilds at 3582 and
  3592), at np 8 (job 2072), 16, 32, 52 (one node, one rank per core) and 104 (2 nodes over
  IPoIB). Measured per run: per-phase step times, Newton and KSP iterations, placement time and
  refusals, memory, and agreement with the laptop. Results go to kaiju runs/ and NOTES.
- 2026-10-23: the laptop run stopped at checkpoint 3910 (t 0.4696, four faults) and moves to kaiju.
  zg95-annulus-for-kaiju now carries c7741c4 (strain panels in the renderer) and 22f69c2
  (asthenosphere channel, `-uw_fault_cut_lid`, a four-run suite in `launch/suite_kaiju` starting
  from 3910). Nothing launches until the scaling results set NP. Two driver restart defects were
  found in job 2072: the first step after a restart is cold (33 Newton iterations vs 3), and the
  `refused` set is not checkpointed. Both were handed to a new kaiju dev session
  (`session_015H8d4zLWhW1moUQ8u1nMtw`), on branch kaiju/annulus-restart-fixes, rebased on 22f69c2,
  delivered as a patch through the hub. The scaling study (jobs 2072-2077, np 8/16/32/52/104) is
  running.
- 2026-10-23 (scaling, interim): the campaign does NOT scale past one node's worth of ranks yet.
  - np 104: IndexError in `custom_mg._colocate_level` on ranks with no cells of the 124-cell
    coarsest level, then a hang.
  - np 32 and 52: the custom-P FMG build fails with a PETSc "new nonzero" error in
    DMCreateInterpolation and falls back to the default preconditioner; no step finished in 1.6 h.
  - np 8 and 16 work; np 16 ordinary steps run about 2.3x faster than np 8 (2072 likely shared
    hyperthreads; clean reruns are 2083 and 2084).
  - The cold first step after a restart takes 33 Newton iterations at every np.
  - Kaiju vs laptop over 3581-3600 agrees to about 1e-3, but a 0.006 change in fault depth (below
    the 0.008 threshold) moved a rebuild from 3592 to 3597, so threshold decisions are sensitive
    to rounding.
  Both custom_mg bugs went to hyperion on `bugfix/custom-mg-empty-rank` (from
  parallel-addon-distribution), the empty-rank bug with a regression test.
  Also: the dev session's `git checkout main` in the shared clone broke four jobs. Production now
  runs from its own clone `~/campaigns/zg95-drivers`. Rule: never switch a checkout you didn't
  create.
- 2026-10-23 (scaling, final): np 16 is the working point: 99 s per ordinary step, 2.8x the laptop,
  efficiency 0.75 against np 8, agreeing with the laptop to 1e-3 with identical rebuilds. np >= 32
  is blocked on the custom_mg bugs (hyperion is fixing them). Write-up:
  kaiju `~/campaigns/zg95/runs/SCALING_2026-10-23.md`.
  **Louis's rulings: no production runs until (1) the multigrid is bulletproof and (2) warm
  starting is understood.** Rebuild steps take 23-27 Newton iterations even with a warm start
  (ordinary steps take 4). The laptop session is diagnosing why (a discarded warm start via
  has_solution, the guess near the moved fault, lock-and-release continuation, the pressure
  gauge). The kaiju dev session holds its warm-start item until then and finishes checkpointing
  the refused set.
  zg95-annulus-for-kaiju is now at db179bd: a rate-based fault law, a slab initial state, rollback
  metrics, and the `launch/slab_kaiju` scan (10 runs). Louis's priority is fault evolution, with the
  slab experiment as the clean test bed.
- 2026-10-23: Louis's diagnosis of the np >= 32 failures: the coarse level is too small for the
  rank count (Annulus cellSize 0.5, refinement 4, so a 124-cell coarsest level). Kaiju is rerunning
  with `-uw_cell 0.25 -uw_refinement 3` (same finest cell, 496-cell coarsest level) at
  np 16/32/52/104 (jobs 2085, 2087-2089), seeded without the old mesh file. The library side, to
  make the multigrid bulletproof, stays with hyperion: the empty-rank fix and agglomeration of the
  coarse levels onto fewer ranks (design proposal first), or at least a clear error instead of a
  hang.
- 2026-10-23: **warm start diagnosed** (laptop session). The driver does transfer V,P on a rebuild
  (zero_init_guess=False), but it switches Picard -> Newton at `uw_rebuild_newton_switch` = 1e-2
  RELATIVE to that solve's own |F0|. Picard contracts at ~0.91 per iteration, so even a good warm
  start runs 20-37 Picard iterations before ~5 Newton iterations; the warm start is wasted. The
  proposed fix is an absolute switch: keep a cold-scale |F| reference (saved in state_N.json),
  start Newton at once when |F0_warm|/|F_ref| < 1e-2, with a guarded Picard fallback. The kaiju
  dev session tests A (as is) against B (Newton at once) at np 16 through the 3582 and 3592
  rebuilds, then folds the fix into kaiju/annulus-restart-fixes along with checkpointing the
  refused set.
- 2026-10-23: **the root cause is in the library.** In `utilities/rotated_bc.py` the rotated
  nonlinear loop's convergence test already uses `ref = max(r0, |F(rest)|)` (the warm-start rtol
  cure), but its Picard->Newton switch still uses the solve's own `r0`. The fix is
  `switch_rtol * ref`. Hyperion does it first on `bugfix/warm-start-newton-switch` (from
  development), with a regression test shown failing, and checks other switches for the same
  inconsistency. Kaiju tests the one-liner as a local overlay against the campaign (A vs C at
  np 16 through the 3582 and 3592 rebuilds). The driver-side absolute switch is dropped if C works.
- 2026-10-23/24: library fixes pushed by hyperion (no PRs):
  - bugfix/warm-start-newton-switch 371d3bd: a warm re-solve switches to Newton at iteration 0
    instead of 12 (test in test_1018); rotated 133 passed, fault/contact 65 passed.
  - bugfix/custom-mg-empty-rank aed17e23 and bfae3e65: custom-P MG, the fault cut and the
    provenance transfer on ranks holding no coarse cells.
  - bugfix/backward-nodes-snapshot-order adb20e9d: Eulerian histories fixed, the test renumbered
    to 1102, review done.
  **Coarse-solve finding (kaiju):** the free-slip annulus leaves a rotation null mode, so the FMG
  coarse level is a dense SVD on one rank. With a 448-cell coarse level, np 16 costs 70-80 s per
  Newton iteration (20-25 s with 124 cells), np 52 costs 178 s, and np 104 did not finish. More
  ranks make it slower. Hyperion is to design a scalable coarse solve: an explicit null space
  plus MUMPS, telescope or redundant LU, measured before building. Kaiju is testing both fixes as
  a box-faults overlay at np 16 and at np 32/52 with the 124-cell coarse level. The kaiju dev
  session's patch is now just the refused set and decision state.
- 2026-10-24: Louis's ruling: **testing belongs to kaiju; the laptop is informed only.** It hears
  about solver-recipe changes (the warm-start switch, a possible side-aware transfer, the coarse-solve
  redesign) and changes nothing until the hub reports them validated. Kaiju runs the clean A/B
  (371d3bd1 cherry-picked alone onto c1107957, np 16) and the band-residual probe (job 2100).
  From the driver: only same-set rebuilds (moved or shortened fault) are warm-started; a changed set
  and the first step after a restart are cold by design. warm_start evaluates the old V,P at the new
  nodes, so the old jump lands on the wrong side in the band the fault sweeps.
- 2026-10-24: **band probe (kaiju job 2100) confirms Louis's argument.** After the driver's 3582
  same-set update, the warm-start |F̂| is 5.3e4, 58% of the cold 9.2e4. Velocity rows carry it all,
  100% of it within 0.08 of the old/new fault spines (7% of the DOFs; 52% within 0.01). The far
  field arrives converged. Expected consequence: the switch fix (371d3bd1) alone saves only a few
  Picard iterations, because the warm r0 is barely below the rest-state reference; the clean A/B
  (2101 vs 2099) will confirm it. Next lever: a fault-attached transfer (map band nodes by
  arc length and signed normal distance from the new spine onto the old spine, blended to the
  direct transfer outside the band), assigned to the kaiju dev session after the refused-set item.
- 2026-10-24 (probe 2100 complete, overlay-test includes 371d3bd): after a same-set fault update
  the warm transfer leaves |F̂| at 58% (3582 update) or 24% (slight move) of the cold residual, all
  of it within 0.08 of the fault traces (7% of DOFs), 74-79% within 0.01 after one iteration. Solves
  on overlay-test: cold 33 its / 628 s; 3582 update warm 18 its / 410 s (switch at 12; was ~25-28
  on the current library); slight move 9 its / 198 s (switch at 4). So 371d3bd helps but cannot
  switch at 0: the warm r0 is 24-58% of the rest-state reference, so Picard still grinds a
  band-localised residual down globally. Three remedies in motion: (a) the fault-attached transfer
  (kaiju dev session); (b) Newton from iteration 0 on the warm start (kaiju probe, cheap test);
  (c) a band-local pre-solve (FAC patch; the band label already exists) if (a) and (b) fall short.
- 2026-10-24: the empty-rank fix does NOT unblock np 32/52 on the 124-cell coarse level (kaiju
  2097/2098, identical failure counts). That is a second bug: PETSc's nested interpolation between
  custom_mg levels (DMPlexComputeInterpolatorNested) fails on preallocation at np 32+, the barycentric
  transfer fails first, the FMG build falls back, and the ranks deadlock. Handed to hyperion with the
  coarse-solve design; a gathered coarse communicator would address both this and the serial SVD.
  Kaiju's Newton-from-0 probes (2102: switch 1.0; 2103: 2 Picard then Newton) are running.
- 2026-10-24: hyperion disk rebuild imminent. Rule: nothing uncommitted on hyperion; push after
  every change; measurement scripts and results in the branch. Hub vigilance check every 3 h.
- 2026-10-24: **clean A/B at np 16 (kaiju 2101 vs 2099)**: the warm-start switch fix alone cuts the
  3582 same-set rebuild from 27 to 19 nonlinear iterations (Picard 21 -> 14; 618 -> 456 s, -26%);
  ordinary steps unchanged (3-6 its). The first step after a restart is still cold (33 its). No
  changed-set rebuild occurred in 3581-3595. Correction: the 3592 rebuild flip is NOT
  partition-dependent; runs agreeing to 1e-6 in vrms put F0 at 0.116 or 0.108, so
  strain_band.fit_fault_lines has a near-tie that decides a rebuild. Told the laptop (fault
  tracking). Newton-from-0 probes (2102/2103) still running.
- 2026-10-24: **switch-criterion probes (kaiju 2102/2103) rule out remedy (b).** Newton from
  iteration 0 on a warm rebuild is worse: 3582 update 26 its / 1320 s (vs 18 / 410 with the
  1e-2*ref switch); slight move 46 its / 1583 s (vs 9 / 198). Two Picard then Newton: 42 its on the
  big update, 8 on the small one. All monotone, no rises, but 20+ iterations of 2-10% decreases at
  34-51 s each: damped Newton far from the basin. Reading: the band-localised residual after a
  fault update is outside Newton's basin; the yield nonlinearity in the band needs Picard first,
  which is cheap and makes the big early gains. The 1e-2*ref switch (371d3bd) stays. The remedy
  must shrink the band residual itself: the fault-attached transfer (dev session) or a band-local
  solve. Kaiju is idle.
- The laptop fixed the 3591 detector flip (uncommitted, awaiting Louis): depth hysteresis of two
  detection-grid rows (0.016), since the grid row spacing 0.0078 equals the 2S rebuild threshold.
- 2026-10-24: **Louis: kaiju owns the fault-update warm-start problem** and is to find a reliable
  way forward. The main kaiju session measures and designs (lines of attack in order: fault-attached
  transfer; band-local pre-solve; lock-and-release; warm-starting the cold cases, i.e. the restart's
  first step and the changed-set rebuild; whether the strain/yield-state transfer matters as much as
  V). The kaiju dev session implements driver changes and coordinates with it directly. Library
  changes come to the hub as patches with regression tests. The laptop stays informed only.
- 2026-10-24: **warm-start milestone 1 (kaiju 2110/2111; `runs/WARMSTART_2026-10-24.md`).**
  - The fault-attached transfer does NOT help (A: 17 -> 15 its; B: identical). The same-set
    residual is the physics change at the moved fault tip, not a misplaced jump. Dropped.
  - The plastic-strain carry-over matters as much as V (zeroing it: 2.4-3.8x |F̂0|, 20% different
    converged V). Keep it.
  - With 371d3bd, the cold cases warm-start fine, agreeing with cold to 1e-5: spawn 34 -> 11 its
    (772 -> 267 s); retire 30 -> 16 (607 -> 243 s); restart's first step from the checkpointed base
    V 33 -> 17 (663 -> 430 s). The driver's "failed on forming a second fault" comment does not
    reproduce. The dev session implements both (drop the same-set condition on warm_start; warm f0
    from V_b), then designs a faulted-mesh checkpoint (V, P, fault state) so a restart is an
    ordinary step.
  - Remaining same-set cost (A: 12 Picard + 5 Newton): kaiju continues with a band-local pre-solve
    and lock-and-release. Library: 371d3bd is the enabler; merge it.
- 2026-10-24: **warm-start milestone 2 (kaiju).** Lock-and-release does not pay: a penalty weld via
  add_fault_bc wrecks the FMG conditioning (the locked solve never finished its first linear solve
  in 1h45m); a topological weld is the retire+spawn pair, ~27 its against 17 for the direct warm
  rebuild. A band-local pre-solve cannot be prototyped in-process: it needs library work (SNES NASM
  with the band as a subdomain, or a band-restricted Picard/Newton on the rotated loop's Q with a
  sub-matrix solve); build it only if same-set updates still dominate after the driver changes.
  Recommendation stands: merge 371d3bd; driver warm-starts changed-set rebuilds and the restart;
  faulted-mesh checkpoint; detector hysteresis (laptop has it, uncommitted). Kaiju idle until the
  dev session's driver patch exists, then the 15-step A/B.
- 2026-10-24: **ZG95 slab recipe settled on the laptop: a compositional slab** (no thermal slab
  founders; the hinge is a free pivot and the core warms before rollback). Particle markers on a
  swarm over the base mesh (crust, slab, overriding plate), with `-uw_comp_dT`, `-uw_comp_eta`,
  `-uw_buoy_T`, `-uw_over_*`, `-uw_crust_weak`; refinement 5 (127k cells, 381k particles), fault-free
  (`-uw_max_faults 0`), 75 s/step at 4 laptop ranks, Newton 1 iteration. B1/B2/C1 results in the
  laptop's report. Uncommitted on the laptop, awaiting Louis's confirmation to push to
  zg95-annulus-for-kaiju; the dev session rebases its warm-start patch on top afterwards. Louis wants
  these runs on kaiju; the warm-start and MG conditions don't bind (no faults, np 16 works).
- 2026-10-25: the laptop pushed the compositional-slab driver: zg95-annulus-for-kaiju 878b9c2
  (8 files, +677). Kaiju starts the np 16 smoke test (fresh clone pinned at 878b9c2; the Ra x3 clone
  stays at e258447). The dev session rebases its warm-start patch onto 878b9c2.
- 2026-10-25: **slab smoke test passed on kaiju** (job 2114, np 16, 878b9c2): 31 s/step (laptop 75 s
  at 4 ranks), Newton 1 it, ~1 GB/rank, 380,928 particles conserved through advection and checkpoint,
  restart from step 5 reproduces steps 6-9 (vrms 9e-5, M 1e-3 on the first step then 1e-5). Metrics
  qualitatively match B1 (steepening to vertical). No quantitative check: the laptop's B1 records are
  not in git (runs/ is gitignored). Gotcha: `-uw_init slab` silently ignores `-uw_restart`; restarts
  need `-uw_init checkpoint`; a guard goes to the dev session. Production estimate: 120 steps ~65 min
  per case at np 16, one node each, up to 8 side by side. Waiting on Louis's case list.
- 2026-10-25: **Louis's purpose statement for the annulus rollback experiment: show how the solvers
  behave in moving-fault situations, and be a good example; best science plus visualisation plus
  solver numbers, instrumented and recorded.** Division: kaiju (main) writes the per-step "solver"
  sub-record spec and the analysis figure spec; the kaiju dev session implements the record in the
  driver and analysis/solver_record.py; the laptop builds the solver/band visualisation panels and
  the movie. Results and solver tables go to a wiki campaign page when runs exist.
- 2026-10-25: solver-record spec written by kaiju (`runs/SOLVER_RECORD_SPEC.md` on kaiju): per-step
  record["solver"] (kind, warm/cold, F0/F_ref, Picard/Newton its, KSP per increment, per-phase wall,
  pc_fallbacks, mesh stats at rebuilds), run_info.json per run, and analysis/solver_record.py (five
  panels, events marked through all). Relayed to the dev session to implement. Three fields need a
  small library change ([LIB-1]: rotated loop returns fnorm_rest, ref, rnorm_history, line-search
  alpha); kaiju writes that patch for the hub to push as bugfix/rotated-solve-diagnostics.
- 2026-10-25: the laptop built the solver visualisation (uncommitted, awaiting Louis): `-uw_panels
  solver` (mesh with old/new fault traces, strain rate, plastic strain, an iteration strip with
  rebuild/spawn/retire/cold markers), `-uw_band 1` (before/after zoom on a moved fault with the
  tangential velocity jump against depth), and the movie. Tested on the Ra x3 run (67 checkpoints).
  Limitation: the solver's split mesh is not checkpointed, so the mesh panel shows the base mesh;
  writing the solver mesh at checkpoints goes into the dev session's checkpoint design.
- 2026-10-25: pushed bugfix/rotated-solve-diagnostics 210c7307 (kaiju's LIB-1 patch: fnorm_rest, ref,
  rnorm_history, line_search_alpha in the rotated result dict; test written first). Hyperion runs
  the rotated and parallel suites on it. The laptop mapped the solver-record field names into its
  renderer and will draw the checkpointed solver mesh (annulus.solver_mesh.NNNNN.h5) when present.
- 2026-10-25: pushed kaiju/annulus-restart-fixes 4485bea (dev session's 3 commits, tree verified
  identical): decisions (k, n_built, refused, last_damage, built) in state_N.json and restored;
  -uw_restart beats -uw_init slab; changed-set rebuilds warm-start; the restart's first solve
  warm-starts from V_b. Test (np 16, 3580 -> 3600, restart at 3590): first step 33 -> 17 its,
  events identical restart vs uninterrupted, fault geometry 1.8e-6, slip 2e-4. Needs 371d3bd in the
  library. Kaiju runs the 15-step A/B for total wall saving. Item 3 design accepted: solver mesh +
  V/P checkpointed (reload verified exact), swarm through the same restore, loud failure on missing
  files.
- 2026-10-25: pushed the solver-record set (b0147e1): record["solver"] per step (kind, warm/cold,
  F0/F_ref, Picard/Newton its, KSP per increment, per-phase wall, pc_fallbacks, mesh at rebuilds),
  run_info.json per run, analysis/solver_record.py (figure + summary CSV + wiki table). Tested on
  kaiju (job 2122): all fields filled. With the library's 210c7307 the F_history / line-search
  fields fill too. Kaiju's A/B and the slab runs use b0147e1 + overlay-diag, so they are
  instrumented from the start. The dev session is on item 3 (solver-mesh + V/P checkpoint).
- 2026-10-25: pushed underworld3 feature/box-faults-warm 99259d35: the campaign's library lineage
  (box-faults + the warm-start switch + the rotated-solve diagnostics), so instrumented runs point at
  a public commit. Kaiju's overlay for it is overlay-warmdiag (overlay-diag lacks box-faults and
  cannot import the driver). The restart A/B runs: 878b9c2/overlay-warmonly vs b0147e1/overlay-warmdiag,
  3580 -> 3590 then a 5-step restart.
- 2026-10-25: **restart A/B (kaiju 2131/2132 vs 2140/2141, np 16).** New driver b0147e1 on
  feature/box-faults-warm vs old 878b9c2: the first step after a restart 34.5 -> 18 its, 736 -> 460 s
  (-37%); total 3153 -> 2992 s even with one extra rebuild (like-for-like about -15%); ordinary steps
  unchanged (4 its, ~95 s). The old driver's restart LOSES fault state: slip_max jumps 6% with no
  geometry change and it skips the 3592 rebuild; the new one follows the laptop (slip_max 35.269 vs
  35.245, vrms 1.2e-3). Kaiju recommends merging b0147e1 into zg95-annulus-for-kaiju; an uninterrupted
  3580->3595 check (job 2148) confirms restart == uninterrupted on the new driver. Figure:
  `runs/ab_restart_compare/solver_record_ab.png` on kaiju.
- 2026-10-25: pushed 460e49d (item 3 + analysis fixes): each checkpoint writes the solver's faulted
  mesh (annulus.solver_mesh.NNNNN.h5) and its V, P; a restart rebuilds the mesh and seeds the DOFs
  by position (exact match at np 16 and np 8), so the first step is an ordinary warm step: 4 its,
  3e-15 from the uninterrupted run at step 3591 (was 17 warm from V_b, 33-36 cold). A missing
  checkpoint file fails loudly. Known residual: a 4e-4 drift from 3592 on, from projection and
  advection solver states that start from zero after a restart; a fix (edot_plastic on the faulted
  mesh + solver `.state` restore) is in test. solver_record.py marks restarts in old records, plots
  trench shift rather than absolute angle, labels empty panels. Kaiju adds a 460e49d row to the A/B.
- 2026-10-25: **final restart table (kaiju, np 16, 15 steps 3581-3595, restart at 3590).** Per
  restart step: old driver 36 its / 799 s (cold); b0147e1 19 / 470 (warm from V_b); 460e49d 4 / 115
  (an ordinary warm step from its own solver-mesh checkpoint; vrms 4e-8 from uninterrupted). Totals
  3153 / 2992 / 2311 s. Figure `runs/ab_restart_compare/solver_record_ab3.png` on kaiju.
  **The remaining blocker for restart == uninterrupted is the detector knife-edge**, not the restart:
  fields differing by 1e-8 flip F0's fitted depth 0.108/0.116 (and theta by 0.1 deg, dip by 0.7 deg),
  which decides a rebuild and leaves slip 7% apart after. The laptop's uncommitted depth hysteresis is
  the fix; theta/dip under review. Also seen: the pressure KSP at its 200 cap on one step (3595 of
  run 2148), to watch in production. Sample run for the renderer: kaiju
  `~/campaigns/zg95/samples/i3_sample` (52 MB), to rsync to the laptop.
- 2026-10-25: **detector finding (laptop, on the Ra x3 checkpoints with driver 460e49d).** The
  rebuild thresholds are 0.41 deg (4 rungs) and 2 deg dip. At a FIXED field, fit_fault_lines over
  RANSAC seeds spreads 0.33-0.65 deg in theta and 2.7-5.4 deg in dip, at or above those thresholds.
  In the run, F0's fitted theta swung +-0.25 deg and dip +-1 deg per detection, and 10 of 11
  detections over 3540-3600 triggered a rebuild: most rebuilds are fit noise, not fault motion.
  Seeding is already deterministic, so a tie-break does nothing; the fit stops short of its fixed
  point (best-of-400 random candidate, two refinement rounds). Measured fix: iterate the weighted-axis
  refinement to a fixed inlier set (spread falls to 0.04-0.17 deg, 0.2-1.2 deg; all seeds find the
  same six lines); then a deterministic candidate grid over (theta, dip) so the fit is a function of
  the field alone; then theta/dip hysteresis like depth's. Nothing changed in the driver yet.
- 2026-10-25: the 4e-4 post-restart drift is NOT in the auxiliary solvers (checkpointing their state
  changed nothing). With u identical to 6e-16 and fields to 1e-11, the Stokes starting residual
  differs by 6e-4 between a solver with 10 prior solves and a fresh one: solver-side state enters
  the rotated residual evaluation. Library determinism probe handed to hyperion (reuse_operator /
  cached Ahat, gauge datum, continuation state). Restart stands at: exact first step, identical
  events, drift <= 4.1e-4 against uw_tol 1e-3. The dev session writes RESTART_AND_RECORDS.md and is
  then free.
- 2026-10-25: pushed RESTART_AND_RECORDS.md (3345ce7): the checkpoint set, the restart order and
  fallbacks, every record["solver"] field, run_info.json, solver_record.py usage, and the measured
  restart numbers. kaiju/annulus-restart-fixes is complete (8 commits); the dev session is free.
- 2026-10-25: slab example figures on zg95-annulus-for-kaiju dbec55d (`zg95_lid_regimes/figures/slab/`:
  B1/B2/C1 at steps 20, 60, 119 + README; trench_retreat.png to follow). The old launch/slab_kaiju
  scan is stale (thermal-slab baseline, which never founders). Proposed new scan on the
  compositional baseline, one change each: comp_eta 30; comp_dT 0.25; slab_length 0.2 and 0.5;
  dip 60; crust_weak 0.01; overriding plate at over_gap 0.3 and at over_eta 1000; and one run with
  the mantle structure back (deta, buoy_T 1, asth 0.1). 200-300 steps each. The stage-3 fault at
  the plate contact waits on Louis's law/placement choice.
- 2026-10-25: **Louis: add faults to the slab runs, following the weak crust layer.** The laptop
  designs and implements the crust-following fault (geometry from the crust marker contour, law
  and crust-weakening choice to be proposed, the overriding-plate contact). Kaiju prepares, without
  launching, the fault-free control set at 300 steps: B1, B2, C1 and the nine-run compositional
  scan (twelve runs, two waves). trench_retreat.png is on the branch at 347b947.
- 2026-10-25: **stage-3 fault design (laptop, fault law "crust"), building now.** Geometry: at each
  detection the crust marker's proxy on the polar grid gives the sub-surface crust centreline,
  chained from the trench, resampled at the rung spacing to the depth cap (0.15 d); the polyline is
  the fault spine (curved spines are accepted by the placer). Rebuild when any point moves more
  than 4 rungs (0.016); expect a same-set rebuild every 4-5 steps in B1 (8 rungs for cheaper
  production). No line fit, so no knife-edge. Law: the split fault with its bridge band, no rate
  fitting; first runs at crust_weak 0.1 (the crust locates the fault, the fault carries the
  decoupling). Test: B1 (crust 0.001, no fault) vs crust 0.1 no fault vs crust 0.1 + fault, plus
  crust_weak 1 (passive marker). Overriding plate: no special case; the rule covers its contact.
  Records and band view unchanged. Smoke test: 4 ranks from B1/C1 checkpoint 60.
- 2026-10-25: **Louis: run the cases.** Kaiju launched the twelve-run fault-free control set (B1, B2,
  C1 + the nine-run compositional scan; 300 steps, np 16, driver 460e49d, instrumented; 7 then 5
  runs, ~5.5 h). On completion kaiju renders each run, runs slab_metrics and solver_record, and
  assembles `~/campaigns/zg95/figures_out/slab_control/` (< 15 MB) for Louis to rsync to the laptop,
  which commits it so the renders reach him as GitHub links. The layered-mantle run keeps both
  compositional and thermal buoyancy.
- 2026-10-25: **stage-3 "crust" fault law built and smoke-tested on the laptop (uncommitted, awaiting
  Louis).** Correction to the design: the fault polyline is the SLAB marker's 0.5 contour (its top,
  where the crust rides), since the one-cell crust picture is too smeared to chain; the law needs
  the compositional slab. Smoke (4 ranks from checkpoint 60, crust_weak 0.1, cap 0.15, 12 steps):
  B1 formed F0 at step 61, cold build 6 velocity its, **same-set warm rebuild at 72 = 4 its, an
  ordinary step's count**; C1 similar (5 its). Newton 1 every step. Production flags on BASE:
  `-uw_fault_law crust -uw_max_faults 1 -uw_fault_depth_max 0.15 -uw_crust_weak 0.1
  -uw_detect_start 0 -uw_detect_every 5` (+ `-uw_rebuild_rungs 8` for fewer rebuilds). Comparison
  set: B1 / crust 0.1 no fault / crust 0.1 + fault / crust 1 + fault.
- 2026-10-25: crust-fault smoke renders on zg95-annulus-for-kaiju dbebbbf (`figures/slab_fault/`).
  Slab controls: comp_eta_30 finished (300 steps, no KSP-cap hits); wave 2 started with dip_60.
  Library bug found on kaiju (worked around): visualisation.initialise() catches only RuntimeError
  when setting the trame backend, so headless pyvista without trame raises ImportError and every
  render crashes. Fix handed to hyperion (bugfix/visualisation-headless-no-trame).
- 2026-10-25: Louis (in the laptop session) chose a PARABOLA for the crust fault: fitted to the slab
  marker's 0.5 contour below depth 0.012, used as the fault from 0.02 above the wall to the 0.15 cap,
  the placement handling the surface as before (cut stops three rungs inside the wall, top in the
  ribbon's TI zone). Smoke (4 ranks, B1 from step 60, crust x0.1, 7 steps): cold build 6 linear
  its then 3-5; slip 734-849 against plate 800-970, so the fault carries nearly all the decoupling
  (wiggly contour: 480-600). Driver, renderer and movie still uncommitted, awaiting Louis's word.
  Slab controls: 5 of 12 done, no KSP-cap hits; layered_mantle is ~16x slower per step (12-13 Newton
  its, T-dependent viscosity) and will reach ~step 90 of 300 at its 12 h wall; default is to let it.
- 2026-10-25: **Louis: merge what other sessions need.** Merged kaiju/annulus-restart-fixes (4955e80)
  and kaiju/movie-ffmpeg-fallback into zg95-annulus-for-kaiju; head 361657f, pushed. The laptop is
  told to commit and push its crust fault law, renderer, movie and hysteresis on top (rebasing on
  361657f). Kaiju prepares the faulted set (B1 crust 0.1 no fault; B1 crust 0.1 + fault; B1 crust 1
  + fault; C1 crust 0.1 + fault) from the branch head once the laptop's push lands.
- 2026-10-25: the laptop pushed zg95-annulus-for-kaiju e009873 (3463bbd crust fault law, parabola fitted to
  the slab top and run to the surface, "points" rebuild rule; e009873 solver panels, iteration strip, band
  view, movie layout) on 361657f, on Louis's word in that session. slab_fault figures are being
  regenerated (B1 and C1 from step 60, 4 ranks, crust x0.1); the hash goes to kaiju for the faulted set.
- 2026-10-25: **kaiju slab controls done, 11 of 12**: 300 steps each, exit 0, no KSP-cap hits, Newton 1 per
  step, 24-38 s/step (B2 79), 2-3.2 h each (B2 6.6 h), ~27-30 GB per node. Readings (trench shift in layer
  depths): B1 reaches the stage-A target 0.175 d at t 0.0004 and 0.56 d by 0.0022; B2 (x1000) 4.7x slower to
  the target but furthest (0.80 d by 0.0070); an overriding plate halves the rate (C1), over1000 nearly
  suppresses it (peak 0.23 d, then the trench advances); comp_eta_30 fastest start then stalls at 0.41 d;
  slab_0.2 most retreat (0.95 d), slab_0.5 least (0.35 d); dip_60 and crust_weak_0.01 indistinguishable from
  B1. layered_mantle is very uneven (step 16: 4 Newton its, 192 s; step 17: 26 its, 1604 s; ~840 s/step mean)
  and stops at its wall near step 50, t 0.005; its 26-iteration step is to be read from the solver record.
  Folder `~/campaigns/zg95/figures_out/slab_control/` (README table, trench_retreat.png, per-case frames,
  solver_record.jpg, solver_summary.csv, slab_metrics.json).
- 2026-10-25: **Louis: wrap up with the technical note for the add-on-top fault approach**; the FMG/parallel
  draft to be revised by the wombat notes session. Decision on WRITING-PLAN's M3/F3 overlap: UWTN 2026-022
  "Faults on an add-on mesh" (new, hub) is the serial method (static base, ephemeral child, split add-on
  levels, moving fault, warm start and restart, limits); UWTN 2026-018 "Faults in parallel" (draft of 8 Sep,
  branch note/faults-in-parallel) is the parallel half and needs re-centring on the October partition-once
  design (the split no longer cuts through the seam; the conform mode stays for the band). F3 is absorbed by
  the two. The hub allocated 2026-022 with scripts/new_article.py after fetching all branches, wrote the
  first draft (commit 948bb02, local), and briefed the wombat notes-workbench session on the 2026-018
  revision and on a written workflow proposal (branch ownership, hyperion figures into examples/, who runs
  pixi validate/build). The hub cannot push to that organisation (Claude GitHub App not installed there):
  the draft goes to the wombat session as a patch.
