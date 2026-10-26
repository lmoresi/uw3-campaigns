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
| laptop (wombat), technical notes workflow | `session_011S876ckjYqqth1aPyojrhh` ("Notes workbench with git branches"): owns the notes workflow with the hub, revises UWTN 2026-018 |
| laptop (wombat), adjoint notes | `session_018wSha1nV5DddcThnCRoFab` ("CONTRIBUTING.md figure script placement"): UWTN 2026-020/021 |

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

## Technical notes workflow (wombat notes-workbench proposal, adopted 2026-10-25)

1. One branch per note, `note/<slug>`, on Underworld-Technical-Notes/underworldcode.org. The branch is the
   note; the pen holder is recorded in the table below. Nobody pushes to main; a PR only when Louis asks.
2. Hub access: the Claude GitHub App is installed on the Underworld-Technical-Notes organisation
   (Louis, 2026-10-25) and the hub pushes to `note/<slug>` itself (verified with a throwaway branch). The
   `relay/` route in uw3-campaigns is retired; it remains the fallback if access lapses.
3. Figures: hyperion commits each script with its PNG to underworld3 under
   `scripts/sessions/<area>/uwtn_<id>/` and pushes. Wombat copies them in one commit (scripts to
   `articles/<slug>/figures/src/`, PNGs to `articles/<slug>/figures/`), naming the underworld3 hash. If
   hyperion can push to the notes organisation (untested), it pushes that commit to `note/<slug>` directly.
   PNGs never travel through hub patches.
4. Checks before any review request, run on wombat: `pixi run validate`, `pixi run check-style`, and
   `python3 scripts/preview_build.py --slugs <slug> --base-url /x`; results and hash reported to the hub.
   PR previews are broken until PREVIEW_TOKEN is regenerated (Louis).
5. IDs: allocate only after fetching every branch; push the metadata.yml carrying the ID the same day.
6. Fetch before every push; never force-push. Wombat's planned workbench tool (`scripts/note.py`,
   awaiting Louis's go-ahead) refuses to overwrite commits it has not seen.
7. State: `metadata.yml status:` is canonical. The table below keeps one row per note.
8. Conventions: commit messages "UWTN <id>: <what>"; figure scripts in `figures/src/`, launchable
   examples in `examples/`; every figure and table ships its script; `software_version` pinned to the
   underworld3 commit the numbers came from. The `myst.yml` toc block is generated; do not edit it.

| Note | Branch, head | Status | Pen | Waiting on | Last checks |
|---|---|---|---|---|---|
| UWTN 2026-018 Faults in parallel: partitioning the add-on once | `note/faults-in-parallel` da848fa | draft | wombat workbench | 3 figures (hyperion: parallel-pipeline, load-per-processor, band-through-the-boundary); Louis's answers Q1-Q4 | 2026-10-25 validate 0 warnings, check-style clean |
| UWTN 2026-022 Faults on an add-on mesh | `note/faults-on-an-add-on-mesh` 24ae608 (figures c0a998a; restart script b9a678e; restart records b9662c3; drift clause 24ae608) | draft, complete but for hyperion's (i),(j) and Louis's items | hub (prose), hyperion (figure records), wombat (checks) | hyperion: shipped records for fig_iterations (i), global peak slip at np 8 (j); Louis's items (a),(c),(g) | 2026-10-26 at 24ae608: validate 0 warnings, check-style clean, preview build passes; the 4e-4 clause verified against the shipped records, uw_tol 0.001 recorded for the saved-child pair (wombat) |
| UWTN 2026-020 Symbolic FEM and adjoint forms | PR #59 | review, green | wombat adjoint session | Louis's merge | CI green |
| UWTN 2026-021 Adjoint forms in practice | `note/discrete-adjoint` 87fbcb1 | draft, held | wombat adjoint session | the viscosity-floor example's result | |

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
| Lid-regime annulus campaign | uw3-campaigns `zg95-annulus-for-kaiju` d0dca11 (crust fault law, renderer, checkpoint-traces fix, restart_table.py, kaiju figure folders, whole-annulus trace width, crust-base fault trace); library `feature/box-faults-warm` 99259d35 | on kaiju: 11/12 controls done, faulted set relaunching |
| Restart / warm-start fixes + solver record + faulted-mesh checkpoint + docs | merged into `zg95-annulus-for-kaiju` (4955e80); branch head 361657f | done |
| Kaiju docs | underworld-community/uw3-hpc-install-run PR #1 | open |
| Parallel `read_checkpoint` bug | found on kaiju, 2026-10-21 | not filed or fixed yet; the lid-regime driver is not affected |
| Technical notes (2026-018, 2026-020/021, 2026-022) | see "Technical notes workflow" table above | in progress |
| Slab control set (12 of 12) | kaiju `~/campaigns/zg95/figures_out/slab_control/` (5.9 MB, README with the table) | COMPLETE 2026-10-26; layered_mantle stopped at its 12 h wall at step 128 (records to 120, t 0.0045) |
| Thermal slab set (TA, TB, TA_age25, TA_Pe3) | kaiju jobs 2224, 2225, 2227, 2228 (n2-n5); scripts `~/campaigns/kaiju-launch/slab_thermal/`, runs `runs/slab_thermal_*` | launched 2026-10-26 at Louis's direct request in the kaiju session; 300 steps, 12 h wall |
| Slab faulted set (B1_crust0.1_nofault, B1_crust0.1_fault, B1_crust1_fault, C1_crust0.1_fault) | kaiju `~/campaigns/zg95/figures_out/slab_fault/` (3.0 MB, README, trench_retreat.png, frames, solver records; segment ledger kaiju-launch/slab_fault/SEGMENTS.md) | COMPLETE 2026-10-26: all four 0-299, records continuous, no KSP-cap hits; faulted runs in three segments each (leak), every restart at match distance 0; figures reach GitHub after Louis's rsync (Waiting on Louis) |
| Memory leak per faulted-mesh rebuild | library, found on kaiju 2026-10-26; hyperion investigating (bugfix branch from feature/box-faults-warm) | open: a constant ~7.0 GB/node (0.44 GB/rank at np 16) per rebuild, fresh or old process alike, about one faulted mesh's full footprint: each rebuild appears to retain the previous child (or its DM/Mat/KSP) in full; drift between rebuilds 40-135 MB/node/step, also without a fault |
| Rotated-solve diagnostics | underworld3 `bugfix/rotated-solve-diagnostics` 210c7307 (on 371d3bd) | written on kaiju, pushed by the hub; hyperion runs the suites |

## Waiting on Louis

- Thermal slab + faults: the crust-base fault law is in (d0dca11, laptop); kaiju has it pinned. **Decision needed:
  which thermal cases take a fault, and when** (a fault forms only once the slab has reached the cap depth 0.15;
  the FAULT flags are unchanged). The swarm stays pervasive (5 % of a faulted step); a crust-only repopulated
  swarm would be a driver-level change after the fault law, only if Louis wants the physics stated that way.
- Thermal runs: Louis ruled 2026-10-26 "a manageable difference, I would not try to change this": no Picard
  warm-up, no recipe change; kaiju restarts past each wall with the recipe as launched. TA_Pe3 cancelled.
- Slab recipe decisions: (1) continue layered_mantle from checkpoint 120 (333 s/step, 12 h buys ~130 steps)?
  (2) try a Picard warm-up on ordinary steps (-uw_warm_newton_switch 1e-2, as rebuilds use) for the layered
  mantle, where ordinary warm steps start at F0 = F_ref and damped Newton crawls (step 17: 26 its, 20 cutbacks)?
  (3) a check run for the crust x1 + fault case with fewer rebuilds (-uw_rebuild_rungs 8)? Kaiju is idle.
- Technical notes, answers needed (from the wombat workbench report, 2026-10-25):
  - 2026-018: (1) title "Faults in parallel: partitioning the add-on once" OK? (2) re-measure the parallel
    split-level iteration counts (13 Oct, before partition-once) on hyperion? (3) wall times 65/34/25 s
    quoted, the 72/38/30 read as "before" and left out: correct? (4) software_version moves to a
    development sha on merge.
  - 2026-022: (a) three "route" passages (the weights-of-five/NaN clamp story, the nearest-node repair,
    the zero pivot under rotated walls): keep as motivation or cut to rule plus reason?
    (c) `stokes._rotated_freeslip_info` is a private attribute in a published note; (d) the restart
    table needs a script (kaiju annulus runs); (f) link 018 from the parallel paragraph once 018 is
    published; (g) check iterations.png alt text against the made figure (wombat rewrote it from the
    figure; a look by Louis closes it). Done by the hub: (b) the 017 link reworded, (h) the
    hierarchy sentence limited to what the figure measures; (e) software_version pinned by wombat.
- Delete the empty branch `hub-push-test` on Underworld-Technical-Notes/underworldcode.org (points at
  36e15f7, already in note/faults-on-an-add-on-mesh): the hub's proxy refuses ref deletions and wombat
  treats a remote deletion as yours to approve. `git push origin --delete hub-push-test`.
  - The wombat workbench tool (`scripts/note.py`, `pixi run note sync`) awaits your go-ahead.
- Regenerate PREVIEW_TOKEN in Underworld-Technical-Notes/underworldcode.org (rejected since after 2 Oct; every PR preview fails, production deploy unaffected). Merge PR #59 (UWTN 2026-020) when ready.
- When kaiju's slab_movies/ is ready, re-run the rsync (it asks for a password, so from a terminal, not a
  Claude Code prompt): `rsync -av louis@kaiju.anu.edu.au:/home/louis/campaigns/zg95/figures_out/ /Users/lmoresi/+Simulations/zg95/kaiju_figures/`
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
- 2026-10-25: **notes workflow adopted** (section above). Wombat workbench applied the hub's 2026-022 patch
  (notes-repo hash a43535f; git am re-records the committer) and pushed 36e15f7 with mechanical fixes (toc
  line dropped as generated; classification.yml entry; one rewrap; figures/src/). It revised 2026-018
  (d93b855): re-centred on partition-once, the split-through-the-seam kept only as the rejected comparison,
  the September figures removed (no scripts, and one drew the rejected route), three figures pending from
  hyperion. Both notes validate clean. Questions for Louis are under "Waiting on Louis".
- 2026-10-25: the laptop pushed zg95-annulus-for-kaiju dd8efcb (b039759: the iteration strip plots vel_its,
  not the outer ksp_its; dd8efcb: slab_fault figures with the parabolic crust fault). Recipe and flags
  unchanged. Laptop smoke on the pushed driver: B1 fault at -8.3 deg / dip 50, first build 5 velocity its,
  ordinary 3-5, same-set rebuild 4, slip 740-850 vs plate 800-970; C1 -6.4 deg / dip 41, slip 840-930; both
  Newton-converged. **GO sent to kaiju for the four faulted cases on dd8efcb.**
- 2026-10-25: hyperion confirmed alive by reading its transcript (the two scheduled check-ins fail with
  ACCESS_DENIED when they fire): bugfix/visualisation-headless-no-trame 7392233c and
  feature/coarse-solve-nullspace bdc87294 are on origin; it has started the 2026-022 figures.
- 2026-10-25: **faulted set launched on kaiju** (jobs 2187-2190, see Open work). The fault flags follow BASE's
  `-uw_fault_law none -uw_max_faults 0`, so the later values win, as in run_stage_b_comp.sh. Kaiju reports the
  first fault build and first rebuild iteration counts per run when they appear.
- 2026-10-25: Louis installed the Claude GitHub App on Underworld-Technical-Notes; the hub pushes note
  branches directly from its clone (`/home/user/underworld-technical-notes/underworldcode.org`, now tracking
  origin's note/faults-on-an-add-on-mesh at 36e15f7). relay/ retired.
- 2026-10-25: **2026-022 has its figures.** Hyperion made stack.png, iterations.png and moving-fault.png at
  library e135429f (feature/coarse-solve-nullspace, scripts/sessions/fault_mg/uwtn_2026_022/ with a README of
  every number) and re-measured the draft's claims: split 5/5/4 against welded 8/13/18 at tolerance 1e-6
  (the draft's 6/5/4 vs 13/18/23 was the 13 Oct state; the welded tail improved), viscous k=3 5 vs 12,
  moving-fault steps at np 8 0.3-0.6 / 0.75-0.9 / 4.5-4.8 s (serial 0.8-1.4 / 1.1-1.2 / 6.0-6.5 s), the
  junction replay stops for a side-assignment reason not the ligament closing, the 3-D two-level sheet
  now places but keeps no split coarse level. Wombat copied figures and records into the note and rewrote
  the affected text to match (c0a998a); the hub fixed the hierarchy sentence and the 017 link (015c1c0).
  2026-018 (da848fa) uses the same serial numbers. The restart table still needs a script (kaiju).
- 2026-10-25: **faulted runs 2187-2189 died at step 0** (kaiju): checkpoint() wrote "traces" from the
  detection's fault list, which at a formation step holds the new fault before the mesh has it (the rebuild
  comes at the next step), so faulted.pieces["F0"] raised KeyError on rank 0 and the ranks hung. A fresh slab
  start with -uw_detect_start 0 forms F0 at step 0, always a checkpoint step; the laptop's smoke tests from
  step 60 could not see it. Kaiju's fix ("traces" lists faulted.faults, the faults built into the saved
  mesh; "faults" keeps the detection list) tested at np 16 for 2 steps (job 2191), sent as a patch, pushed
  by the hub as **0fb51f9**; relaunch of the three cases requested; 2190 (no fault) unaffected. The laptop
  is informed. Kaiju also asked for zg95_lid_regimes/analysis/restart_table.py, the script behind the
  2026-022 restart table.
- 2026-10-25: faulted set relaunched on kaiju (2192-2194 on 0fb51f9). Kaiju wrote
  zg95_lid_regimes/analysis/restart_table.py (regenerates RESTART_AND_RECORDS §5's table from the six run
  records, with provenance; output matches: 36/783, 17/387, 4/103 against uninterrupted 4/95, 4/94, 4/101;
  vrms within 4.1e-4, events identical for the two warm designs); hub pushed it as 788f481 and put the script
  into UWTN 2026-022's figures/src/ (b9a678e). Provenance caveat: the i3 pair's run_info.json driver_commit
  is stale (a worktree HEAD); the note cites the run paths. Trimmed records (steps 3580-3600) requested from
  kaiju to ship with the note.
- 2026-10-25: kaiju prepared `~/campaigns/zg95/figures_out/restart_table/` (249 KB): the six runs' records
  trimmed to steps 3580-3600, run_info.json or PROVENANCE.txt per run, README; restart_table.py run from that
  directory reproduces the table exactly. It reaches the note through Louis's rsync and the wombat workbench.
- 2026-10-26: **faulted set healthy at step 10** (kaiju, 0fb51f9, np 16). In every faulted run F0 forms at step 0
  on the crust (dip 46-49, depth 0.149-0.150, 61 points), is built at step 1 (changed-set rebuild, warm: 1
  nonlinear it, 6-7 velocity its, build 11-12 s, Stokes 20-28 s), and the step-5 detection steepens the dip
  (46->57, 48->61, 49->58) so a same-set rebuild follows at step 6 (1 / 4-6 its, Stokes 18-23 s). Ordinary
  steps 2-5 velocity its, Stokes 10-17 s; all Newton-converged in 1 nonlinear iteration. Within 1-2 its of
  the laptop smoke at np 4. Two observations for Louis: (1) slip_max halves at each same-set rebuild
  (608->302, 404->166, 440->196) and recovers over about 4 steps: the transferred velocity's jump does not
  follow the moved fault, costing no iterations but visible in slip, so the slip record carries a rebuild
  artefact; (2) |F0|/F_ref is 1.0 on every step, warm starts included: with -uw_dt_mult 20 the fields move
  enough per step that the previous solution is no closer than rest, so the warm start buys nothing in this
  recipe (and need not, at 1 nonlinear iteration). layered_mantle runs to its wall (~05:20).
- 2026-10-26: **memory leak per faulted-mesh rebuild** (kaiju). B1_crust1_fault (2193) OOM-killed at step 136
  after rebuild 24 on a 188 GB node; RSS 1.5 GB/rank with one build (2190, 179 steps) against 8.7-10.3 GB/rank
  with 17-21 rebuilds: ~0.4 GB/rank, 6.7 GB/node per rebuild. The driver dels the previous FaultedMesh and
  gc.collects, so the library keeps old children or their PETSc objects alive. Hyperion has it as a priority
  task (fixture first, then the driver at np 2; regression test first). Kaiju runs the faulted set as restart
  segments (fresh process each; the faulted-mesh checkpoint restores at match distance 0 and the same rebuild
  follows): 2195 from 130, 2197 from 140, C1 to be restarted near 200; records continuous. For the 2026-022
  note: if the leak is not fixed before publication, it is a limit to state in "What it costs".
- 2026-10-26: leak, interim (kaiju): the particle count is flat (380928 in every checkpoint, faulted or not).
  On a fresh process a rebuild costs ~0.02 GB/rank and the process sits at the fault-free 1.2-1.5 GB/rank; the
  0.4 GB/rank figure was the average over a 140-step, 21-rebuild process. The growth compounds over a
  process's life (per-step on the faulted path, or per-rebuild growing with the meshes retained). Kaiju fits
  node RSS against step and n_built on four live runs for 90 min; hyperion told to shape its fixture run
  for that distinction.
- 2026-10-26: **leak fit (kaiju, 90 min of node RSS on four runs)**: a constant 6.96-7.24 GB/node per rebuild on
  fresh and old processes alike (0.44 GB/rank), linear not compounding (the interim "compounds" and the
  "+0.02 GB" sample are withdrawn: that sample preceded the rebuild step's operator allocation). The size is
  one faulted mesh's footprint at np 16, so each rebuild looks to retain the previous child or its PETSc
  objects in full. Between rebuilds 40-135 MB/node/step, present without a fault too. Passed to hyperion.
  Segment totals agree (~20 GB base + 7 GB per mesh). Three of the four slab cases are complete to step 299.
- 2026-10-26: **slab faulted set complete** (kaiju, 0fb51f9, overlay-warmdiag, np 16; 300 steps each, Newton 1
  per step throughout, velocity its build 6-7 / rebuild 4-6 / ordinary 2-5, 26-28 s/step, 2.2-2.4 h per run).
  Segments: B1_crust0.1_fault 2192+2197+2198, B1_crust1_fault 2193+2195+2200, C1_crust0.1_fault
  2194+2199+2201, nofault 2190 alone. Readings (trench retreat in layer depths): crust x0.1 no fault 0.62 d by
  t 0.0032; crust x0.1 + fault IDENTICAL trench history to its no-fault twin (fault forms at step 0, tracks
  the trench through 27 rebuilds, slips heavily, median 484, yet adds nothing at plate scale: with a weak
  crust the fault is redundant); crust x1 + fault (no weak crust) DOUBLES the retreat, 1.16 d by t 0.0046, 29
  deg of trench motion, slab flattens to 53 deg, 47 rebuilds, slip falls from 434 to a steady 15-50 as each
  rebuild halves it; C1 + crust x0.1 + fault 0.76 d by t 0.0053 against 0.56 d without. **Caveat for the
  science**: the crust x1 + fault case rebuilds every ~5 steps and its slip is dominated by the rebuild
  transfer effect (the old jump does not follow the moved fault), so its doubled retreat is not yet a clean
  result; a run with fewer rebuilds (-uw_rebuild_rungs 8) or a transfer that carries the jump is the check.
  Figures: kaiju figures_out/slab_fault/, to GitHub via Louis's rsync and the laptop's commit (the hub does
  not ask a session to use Louis's ssh access). layered_mantle to its wall (~05:20) then slab_control is final.
- 2026-10-26: **slab controls complete, 12 of 12; kaiju idle.** layered_mantle (-uw_deta 3e4 -uw_asth 0.1
  -uw_buoy_T 1) stopped at its 12 h wall during step 128 (records and checkpoints to 120, t 0.0045, 333 s/step
  mean, no KSP-cap hits in 121 steps). Its 26-iteration step 17 is the LINE SEARCH, not the switch: an
  ordinary warm step goes straight to Newton (uw_warm_newton_switch 1.0) with F0 = F_ref = 2.7e5 (the fields
  move a lot per step), and damped Newton crawls (20 cutbacks, alpha to 0.03, 1591 s); steps 8, 10, 15, 18,
  26, 32, 106 look the same, median 3 its. A Picard warm-up on ordinary steps is the likely fix (recipe
  change, Louis). Physics: the slab sinks as a near-vertical sheet in place, no rollback (trench 0 to +0.04 d),
  the weak crust stripped into blobs in the wedge; the slab warms to T 0.5-0.6 so slab_metrics' cold test
  understates its tip depth (0.27) and mass; judge from the frames. Folders ready to rsync together:
  figures_out/{slab_control 5.9 MB, slab_fault 3.0 MB, restart_table 249 KB}.
- 2026-10-26: **Louis: whole-annulus movies of the slab runs**, the fault drawn at a width legible at that scale
  (separate from the zooms' width). Kaiju renders all 16 runs from their checkpoints with the laptop's
  movie_annulus/render_annulus (branch 788f481), adding the smallest renderer option if the mode or the
  full-scale fault width is missing (patch via the hub; the laptop informed). Output
  figures_out/slab_movies/ with README and a contact sheet; delivery by Louis's rsync.
- 2026-10-26: Louis rsynced figures_out/{slab_control,slab_fault,restart_table} to the laptop (kaiju asks for a
  password, so the rsync is Louis's, from a terminal). The notes workbench shipped the restart-table records
  with the note (b9662c3: six trimmed run records, provenance files, README; restart_table.py reproduces the
  table from figures/src/ exactly, first-step vrms 3.4e-15, later steps 4.1e-4); the hub added the later-step
  agreement clause (24ae608). The lid-regime session is asked to commit slab_control and slab_fault to
  zg95-annulus-for-kaiju for GitHub links.
- 2026-10-26: the laptop committed kaiju's slab_control and slab_fault folders to zg95-annulus-for-kaiju
  (52275dc, 138 files, under zg95_lid_regimes/figures/kaiju/). Links:
  https://github.com/lmoresi/uw3-campaigns/blob/zg95-annulus-for-kaiju/zg95_lid_regimes/figures/kaiju/slab_control/trench_retreat.png
  https://github.com/lmoresi/uw3-campaigns/blob/zg95-annulus-for-kaiju/zg95_lid_regimes/figures/kaiju/slab_fault/trench_retreat.png
  and the READMEs beside them. Movies follow the same route when kaiju has them.
- 2026-10-26: whole-annulus movies under way on kaiju. Renderer patch from kaiju pushed as f46eaa3:
  -uw_trace_width <px> for whole-annulus frames (0 keeps the zoom tuple) and a movie_annulus fix (a frame-only
  renders directory produced a movie with no frames). Movies: the strain frame's left two panels (T with
  streamlines and marker outlines; log10 strain rate) at native 1600 px, trace 6 px, 31 frames per run from the
  10-step checkpoints (layered_mantle 13), ~6 s at 5 fps; the 10-step cadence is coarser than the ~5-step
  rebuild interval, so the fault jumps between frames. Test job 2202 (B1_crust1_fault), then the other 15.
  Output figures_out/slab_movies/ with README and contact sheet; Louis's rsync brings them over.
- 2026-10-26: **whole-annulus movies done** (kaiju): 16 mp4s in figures_out/slab_movies/ (25 MB; 1.4-1.8 MB each,
  layered_mantle 0.6), render f46eaa3 with -uw_panels strain -uw_zoom 0 -uw_trace_width 6, left two panels at
  native 1600x860, h264 5 fps, 31 frames per run (layered_mantle 13); README with the table and
  contact_sheet.png (first and last frame per run, 2200x2008). Frame 0 of a faulted run has no trace (the
  fault is built at the first rebuild after step 0); at step 150 the 6 px trace reads as a short red/white
  stub at the trench. One movie (fault_B1_crust1_fault) viewable in the browser:
  https://claude.ai/artifact/DJctapP4niLphKaazzJeK9. Louis's rsync brings the folder to the laptop; the
  lid-regime session then commits it beside the figure folders.
- 2026-10-26: **Louis, in the kaiju session: the compositional slab is not for publication** (no thermal
  buoyancy); the goal is foundering like B1 with thermal diffusion and buoyancy. Kaiju launched four thermal-slab
  runs on B1's recipe with -uw_buoy_T 1 -uw_comp_dT 0 -uw_comp_eta 1 (no slab marker), Frank-Kamenetskii
  viscosity eta = deta^(1-T), plate age 0.0035 (thermal deficit matching the compositional 0.05), Ra, tau0 and
  tau1 scaled by deta^0.25 (interior Ra 3e6, B1's yield/buoyancy ratio), hot top kept for now ("a giant
  mid-ocean ridge", to be backed off next). Cases: TA deta 4e3; TB deta 1e4; TA_age25 plate age 0.0025;
  TA_Pe3 interior Ra 9e6. Driver 460e49d, overlay-warmdiag. The compositional controls and faulted set stand
  as the solver-behaviour record and the method demonstration.
- 2026-10-26: the laptop flags that the crust fault law needs a new trace source for the thermal slab (no slab
  marker to contour; the driver's guard refuses it). Options: a T isotherm or the crust marker's lower side.
  Listed under Waiting on Louis; the laptop makes the change when the recipe is settled.
- 2026-10-26: **Louis: keep the crust marker in the thermal slab; the fault targets the base of the crust layer**
  (Sandiford & Moresi 2019). The marker need not be a pervasive swarm: populated/repopulated into the upper
  elements, entrained by the slab. Laptop makes the fault-law change; kaiju reports what the thermal recipe
  seeds now.
- 2026-10-26: kaiju: the thermal runs 2224-2228 carry the crust marker and weakening (x0.001 on eta and tau_y,
  one cell thick, fading below 0.5); only the slab and over markers are off. Recipe as launched: buoy_T 1,
  Frank-Kamenetskii deta 4e3 (TB 1e4), Ra and tau scaled by deta^0.25 (interior Ra 3e6, TA_Pe3 9e6), plate age
  0.0035 (TA_age25 0.0025), hot top kept. The swarm is still pervasive; the crust-only repopulated swarm Louis
  described is a separate change.
- 2026-10-26: **crust-base fault law** (laptop, d0dca11 on zg95-annulus-for-kaiju). With the crust marker on, the
  trace is the BASE of the crust layer from the crust particles (subducted ones gathered to every rank,
  clustered by theta, the cluster nearest the trench, or the deepest for a new fault so stripped blobs cannot
  seed one; a parabola in the cluster's principal frame offset to its lower envelope, 9 in 10 particles above).
  Without a crust marker the slab-marker contour remains (B1_crust1_fault still runs); the guard refuses only
  neither-marker runs. Smoke (4 ranks, B1 from 60, checkpoint every step): crust x0.1 F0 at -9.0 deg, dip 42,
  57 points, build 5 its, ordinary 4, slip 864-918 (the slab-top trace gave 736-849: the base is one cell
  deeper, at the real interface); crust x1 path F0 at -8.2 deg, build 7, slip 366-430. Thermal recipe needs
  nothing more (one-cell crust resolved to +-0.005; ~70 subducted crust particles over 0.15 d). Swarm kept
  pervasive: advection 6.9 s of a 126 s faulted step on 4 ranks. Kaiju told to pin d0dca11 and wait for
  Louis's choice of thermal faulted cases.
- 2026-10-26: thermal runs at step 7 after 55 min, Newton converging every step but slow (TA vrms 404, dt 5.8e-6,
  5-9 its, 270-415 s/step; TB 5-12 its, 300-560 s; TA_age25 3-10, 175-570 s; TA_Pe3 vrms 1206, dt 1.9e-6, 6-9
  its). Yielding in the Frank-Kamenetskii plate costs the iterations, ~2x flow speed costs the dt; the wall
  ends near step 90-100 (t 0.0005); kaiju continues by restart. The crust is laid along the slab's top face at
  step 0 and the initial slab is 0.35 long, so the crust base is already below the 0.15 cap: the fault gate is
  met from the start and a faulted thermal run can begin from step 0 or any checkpoint. Kaiju reports deepest
  crust particle, T-based tip, Newton its, hinge rate at steps 10-50. kaiju-fault-drivers pinned at d0dca11.
- 2026-10-26: TA_Pe3 cancelled (Louis). **Why the thermal runs are slow** (kaiju, from record["solver"], steps
  0-10; script kaiju-launch/slab_thermal/solver_table.py): both, mostly the nonlinear part, and the new
  ingredient is YIELDING, not bigger jumps. B1's plate never yields (yield_frac 0), so B1 is effectively linear
  Stokes; the thermal plate yields over 1.5 % of the domain, 3.7 % of the lid. Linear: 3.2x B1 per Newton
  iteration (51-57 s vs 17 s), all of it in the pressure Schur solve with the 1/mu-mass preconditioner (pres its
  44-60 mean / 54-72 max vs B1 21-23; velocity FMG 6-8 mean vs 4-6, fine). Nonlinear: 3-14 Newton its per
  step vs 1 (~7x, dominant): warm steps go straight to damped Newton (picard 0), F0/F_ref 0.7-1.0, 2-7
  cutbacks, alphas 0.5/0.25, F falls to 0.3 F0 then stalls at 0.1-0.4 F0 for 3-6 its before quadratic
  convergence; TA step 8: 11 its, 6 cutbacks, 567 s. Step 0 (cold, 3 Picard + 1 Newton) converged in 4 its
  with no cutbacks in every run: direct evidence for -uw_warm_newton_switch 1e-2 at the restarts. Stokes is
  96-98 % of the step. Realised log10 eta (P1 field, a lower bound on the one-cell crust): B1 spans 3.1 decades
  (-0.6 to 2.5), thermal 4.1-4.7 (TA -0.4 to 4.2, TB 0.0 to 4.7), max falling by step 10 as yielding caps the
  cold surface. B1's true kaiju numbers are vel 5-6 / pres 21-23, not the 3-5 / 12-14 quoted earlier.
- 2026-10-26: Louis: the thermal runs' cost is manageable; no recipe change. Kaiju continues TA, TB, TA_age25 by
  restart with the flags as launched.
