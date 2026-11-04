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
| docs and technical notes hub (from 2026-10-27) | `session_01HxWvn87HYCEJodpgCdaBro`; keeps `DOCS-HUB.md` |
| dev hub (from 2026-10-29): underworld3 PRs, library fixes, library problems raised by sessions | `session_01HxWvn6vA38fdYLUxnxDk4g`; keeps `DEV-HUB.md` |
| hyperion (from 2026-11-04, after the reimage; DOWN again for a second reimage the same day) | `session_01HxWvn92dmiWUj5FX68AZc7` ("hyperion-transient-chipmunk"), a Remote Control session, Claude Code 2.1.318, can message the hub (confirmed); the old session `session_01QZvR7SZKsjcFnzx2aLxn1j` ("hyperion-zesty-dijkstra") is pre-reimage history |
| kaiju | `session_01HX67HY6xwuJivHKLLXrR3H` ("kaiju-anu-edu-au-jiggly-magpie") |
| kaiju, 3-D add-on mesh owner (from 2026-10-31) | `session_01HxWvn87Vw8gzXsEHJ7iF8u` ("kaiju: 3-D add-on mesh"), created by the dev hub on Louis's word; the dev hub's session, its node use accounted there |
| kaiju dev (driver restart fixes) | `session_015H8d4zLWhW1moUQ8u1nMtw` ("kaiju: annulus driver restart fixes"), started by the hub 2026-10-23 |
| laptop (wombat), lid regime | `session_019aromUkeWWPzcL2Kb8365E` ("Lid regime box heating runs") |
| laptop (wombat), technical notes workflow | `session_011S876ckjYqqth1aPyojrhh` ("Notes workbench with git branches"): owns the notes workflow with the hub, revises UWTN 2026-018 |
| laptop (wombat), adjoint notes | `session_018wSha1nV5DddcThnCRoFab` ("CONTRIBUTING.md figure script placement"): UWTN 2026-020/021 |

Messaging: the hub can message kaiju and the laptop (claude-code-remote `send_message`); both can message the
hub. Hyperion's old session could not (its Claude Code was too old to prove a trusted device); the new one runs 2.1.318,
so it may (to confirm in its first reply).
The three hubs cannot message each other (cloud-to-cloud is refused): they coordinate through their files,
each reading the other two at start and at each check-in, and writing to the other hubs in a dated
"For the other hubs" section (see `DEV-HUB.md` "How the hubs talk"). This file's section is below the Open work table.

## Machines and roles

**hyperion**: one big box with a failing system disk (nvme0 throws EIO); a disk rebuild is
scheduled (weekend of 2026-10-25), so /mnt/data may not survive. **Commit and push after every
meaningful change, WIP included; results tables and probe scripts go in the branch.** The hub
checks every 3 h that hyperion's commits are on origin. Use it for
**fast-turnaround parallel development jobs** (tests, probes, np 2-16, minutes, not days).
No long campaigns.
- **Reimage 2026-10-27: `/mnt/data` was backed up and that disk becomes the new root partition, so everything
  below comes back at a different path.** After the reimage: find the restored tree, rebuild the pixi env in
  place (not relocatable), re-point the cache and TMPDIR variables, run `git worktree repair` in each
  worktree, discard the JIT cache. The paths below are the pre-reimage ones.
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
- **The kaiju session's sandbox (2026-11-03 allow-list) cannot resolve the Slurm controller.** A plain
  `squeue`/`sbatch` from the session works; a compound command (`date; squeue`, `squeue | head`) runs inside the
  sandbox and fails with "Unable to resolve kaiju.anu.edu.au". Every "Slurm outage" recorded on 2026-11-02..04 was
  this (kaiju's correction, 2026-11-04); the cluster never failed and nothing is for the admin.

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
- **Examples are scaled and use the units system to non-dimensionalise at the solver level** (the written policy;
  Louis 2026-10-29, "eat your own dog food"). The rollback drivers must adhere: a scaled mode is to be checked (not
  re-run) first, with plate velocities then reported in cm/yr. Governing doc: underworld3
  docs/developer/design/UNITS_SIMPLIFIED_DESIGN_2025-11.md.
- **Every results delivery from a machine the hub schedules (kaiju, hyperion, any server run this way) comes with a
  published artifact** (movies, key figures, the README table) viewable in the Claude app, since Louis reaches
  those sessions only through the app; the hub puts the link in HUB.md and in the report to Louis. The exception
  is collaborative editing of a note, a document or code, which Louis does interactively on the laptop with the
  local filesystem (Louis, 2026-10-29).
- **Examples travel with technical notes (Louis, 2026-10-30).** "This is why we need examples and why we should
  bundle them with the technical notes." Said on the TI Newton stagnation: the TI model is known to behave well,
  so a misbehaviour is a regression or a forgotten configuration, and a bundled, runnable example per note is
  what catches both. A campaign that exercises a library feature checks it first against the library's own
  example or test for that feature at its own settings; a feature with no runnable example is a gap to report to
  the dev and docs hubs.
- **Every exposed knob is a recorded choice (Louis, 2026-11-01).** On learning that the fault placement had
  gathered every fault onto one rank (seams="gather") in every campaign run while the library's cross-partition
  placement (seams="conform", #670) was never wired in: "We spent ages making it possible to spread faults across
  domains so it is disappointing to discover it is not used and has been forgotten. It seems we quickly go from
  not-using to not-considered and then to not-available." Same pattern as the pressure tolerance (the knob existed,
  every run took the library's 1e-4 unexamined) and the TI configuration. Rule: each run's README states the value
  of every solver and placement knob the driver exposes as a choice; the hub keeps a knob table (default, value per
  run family, chosen or taken) current; a library capability the driver never wires is a gap to report to the dev
  hub, with a test owed. **First audit DONE 2026-11-01 (page NRAGaCJ3GXxypNvsAT53wL; data knob_audit.json on kaiju):**
  153 knobs x 6 families (compositional, compositional_fault, thermal, faulted_thermal, earth_run1, TAti_smooth),
  each value explicit / BASE / default from the last segment's argv. Taken by default and it matters: uw_tol 1e-3
  never set (and through the library it fixes the pressure rtol 1e-4 and inner velocity 3.3e-5); pressure rtol
  1e-4 in every family but Earth run 1 and TAti (1e-2), so cross-family timings mix the two; uw_chain 2 everywhere
  faulted but TAti; Newton switches 1e-2 and 0 Picard everywhere but TAti, warm switch 1.0 in the compositional
  runs, TA/TB and the first 10-20 steps of TAf/TBf/TA_age25f/TAc; the cold-retry rule kept a worse cold attempt
  before 5d968c7; uw_dt_mult 20 only from BASE (driver default 3); courant, dt_max, spacing, yield_softness
  defaults everywhere; TAf_env is NOT a clean control for TAti (fault precedence 0/1, pressure rtol, checkpoint
  interval, switches differ). Unwired or hard-coded (12): seams gather + ladder mesher in every attempt (ligament
  and conform never tried); margin_rings 1 and clearance 0.7 against the library's 2 and 0.3; the free-slip
  normal is the analytic unit_r, not the library default normal=None (the geometric, measure-weighted, cross-rank
  normal its docstring recommends), and the analytic path is where the np 32 wall-node defect lives; rotated
  velocity rtol fixed at 0.033 x tol; consistent_jacobian fixed at "continuation"; solver.strategy never set; the
  FAC patch tunable only by UW_FAC_* env vars; yield smoother sqrt, qdegree 3, advection order 1. To make the rule
  bite (approved): the driver writes its full resolved params block into run_info.json at start-up, and the README
  template gets a "choices" block. Test requested: TAc 20 at np 32 with normal=None (-uw_wall_normal geometric):
  if the walls are clean the parallel option existed all along and the defect is confined to the analytic path.
- **Kaiju launcher setting for independent runs (2026-11-01, measured):** three 16-rank jobs per node, --mem=60G,
  no --exclusive, core binding, no socket pinning (pinning has no effect); 2.1x node throughput. Timing studies and
  cost comparisons stay exclusive (a shared node slows each job ~1.45x whether two or three share it). Page
  1CFNXD4TpQLX5jfeTdMN8k v2.
- **The drivers are not underworld3; their decisions live beside them (Louis, 2026-11-02).** "We treat the driver
  for the fault runs as something that is fundamentally part of underworld. But it isn't ... we need to make sure
  these decisions are recorded in places that other claudes and human users can pick them up." The ledger is
  `zg95_lid_regimes/DECISIONS.md` on the campaign branch (e8015a6): every knob the drivers choose, its value, status
  (ruled / measured / taken) and evidence, dated, with the open questions; each run's README choices block points to
  it; the hub updates it whenever a decision changes. HUB.md remains the day-to-day record and the pages the figures.

## Technical notes and documentation: handed to a separate hub (Louis, 2026-10-27)

Louis: "The tech notes and documentation fixes are going to be handled via a different Hub since the
day-to-day flow of that work is quite distinct." From 2026-10-27 this hub no longer coordinates the notes
repo, its branches, reviews or workflow; the notes hub does (`session_01HxWvn87HYCEJodpgCdaBro`, "Underworld Docs and technical notes Hub"; its state file is `DOCS-HUB.md` beside this one).
What stays with this hub is the compute side: figure scripts and records produced on hyperion or kaiju
(fault_mg/uwtn_*, parallel_addon/uwtn_*, kaiju figures_out/) are made on request and reach the notes by
hyperion's pushes to underworld3 or Louis's rsync from kaiju, as before. The section and table below are
frozen as the hand-over state; they are not updated here after this date.

### (frozen) Technical notes workflow (wombat notes-workbench proposal, adopted 2026-10-25)

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
| UWTN 2026-022 Faults on an add-on mesh | `note/faults-on-an-add-on-mesh` 0085faf (figures c0a998a; restart table b9a678e/b9662c3; trench section ebb5a76 → 748ca7f; rebuild spacing 03d1625 → 0085faf; Sandiford bib 2edfb4e) | draft; PEN WITH WOMBAT from 2026-10-26: Louis asked it to rework the prose to the updated CONTRIBUTING "How the notes read"; the hub sends numbers and corrections by message, commits only under figures/src/ | hub (prose), hyperion (figure records), wombat (checks) | kaiju's addon_demo delivered (figures_out/addon_demo/), to come over by Louis's rsync and the notes session's copy; hyperion: (i) fig_iterations records, (j) global peak slip; Louis's items (a),(c),(g) and review of the trench section | 2026-10-26 at 0085faf: validate 0 warnings, check-style clean; preview fails only on the three PNGs awaiting the addon_demo rsync (wombat) |
| UWTN 2026-020 Symbolic FEM and adjoint forms | PR #59 | review, green | wombat adjoint session | Louis's merge | CI green |
| UWTN 2026-021 Adjoint forms in practice | `note/discrete-adjoint` 87fbcb1 | draft, held | wombat adjoint session | the viscosity-floor example's result | |

## Artifacts (results viewable in the Claude app)

| Set | Artifact |
|---|---|
| Compositional slab controls (12 runs: README table, trench_retreat, 12 movies, contact sheet) | https://claude.ai/artifact/HoPEFDDYo4BdiMK8D8Ubvh |
| Compositional slab with a crust fault (4 faulted runs + B1: table, trench_retreat, 5 movies, segments; correction banner on the slip-at-rebuild sentence) | https://claude.ai/artifact/9jQDCwSQLrKvGduwdgtVG4 |
| Normal-crust fault movie (compositional) | https://claude.ai/artifact/DJctapP4niLphKaazzJeK9 |
| Unfaulted thermal slabs (TA, TB, TA_age25 movies) | https://claude.ai/artifact/1pBxnBkYEkHm1RZMLc3F5A |
| Faulted thermal set (table, 4 movies, velocity-ring movies v2, overlay, solver) | https://claude.ai/artifact/NJCoW6npE4kr4D5yXfbqVR |
| Add-on mesh demonstration for UWTN 2026-022 (trench-mesh movie, cost and load tables, rebuild breakdown, rungs8 overlay) | https://claude.ai/artifact/2BFCbPTLgUgDBTHgwjKXee |
| Continent gap analysis (overriding-side surface flow from checkpoints; gap left after rollback for g 0.15-1.0; extent table) | https://claude.ai/artifact/PcRP5QjPT8DSa9rEjkfs4F |
| Thermal comparison page v6: TAti_smooth vs TAf_env vs TAf vs TAc (final TI-vs-split comparison, locator A/B, cost rows, convergence caveat, equivalence paragraph) | https://claude.ai/artifact/TAUT7fi5cM75zkbna7gm9R |
| Fault-division design (the knob removed: rungs = the locator's points at the local cell size, W = BAND_CELLS x mean local h; offline placement check on 80 faults; the draft diff) | https://claude.ai/artifact/UANqhA82AfRoh7fjgrPwYG |
| Side-by-side movies, old run left / recipe v2 rerun right, matched by step (TAf_env vs TAf-v2; Earth run 1 vs run 2): trench window (T, log strain rate) and whole annulus with the surface-velocity ring fixed at 6000; labels step, time, tip depth, vrms, plate speeds. Re-rendered over the whole history at the base | https://claude.ai/artifact/Q1Dq1epuXoEjPnKN7rzcKL |
| Resolution comparison: TAf-v2 at refinement 4 against production (refinement 5), matched by tip depth, evolution and cost tables; cell025 (same resolution, other triangulation) to follow | https://claude.ai/artifact/B83QxCPeYmX2f9HMjx9W4e |
| Recipe v2 production proposal (v5): the v2 table against the old recipe, the full TAf-v2 launch line, the baseline set with costs; TAf-v2's measured 1.92x per step at the same Newton count with the twin comparison at step 30; Earth run 2's departure and the isolation in progress | https://claude.ai/artifact/CDy2RR1fLhBUyPXtUMftNr |
| Ladder-spacing arms for the dev hub: S = h_b and h_b/2 vs production 0.004, re-sampled on restart, TAf 20 and TBf 70 | https://claude.ai/artifact/7cbuaxBnoZrfjdPioMHroT |
| Split-inset test: 1 vs 2 vs 3 rungs (history, 720 offline placements, TAf 40 smoke) | https://claude.ai/artifact/T37Y3MMpYyfgQZbCmuk5YQ |
| Node-packing throughput test on kaiju (1/2/3 x 16-rank jobs per node, same case) | https://claude.ai/artifact/1CFNXD4TpQLX5jfeTdMN8k |
| Driver knob audit: all 153 uw_* knobs against 6 run families (explicit / BASE / default), the taken-by-default list, 12 unwired or hard-coded items | https://claude.ai/artifact/NRAGaCJ3GXxypNvsAT53wL |
| Dev hub's production-tail comparison: chain 2 vs 0, 10 steps from TAf 20 and TBf 70, np 16, development 25d62812 | https://claude.ai/artifact/BWgDzWDzzjDJXQWqVb1jrs |
| Dev hub's #902/#901 scaling check on kaiju (A dev fc67b650, B 96d39f7b, C 94a5c965; np 16/32/52; wall caveats) | https://claude.ai/artifact/ACJ6diJRBCGoBGvCa6aCxM |
| Solver time budget and warm/cold, chain 0 vs 2 (stacked per-step budget; pres_rtol lever; cold/rebuild/warm starts) | https://claude.ai/artifact/LvNXEPD4QNkKtr2V7jDYH2 |
| uw_chain 0 vs 2 at np 16 on development 25d62812 (Louis's production-tail check; patch rows per level and rank) | https://claude.ai/artifact/LiYdWdF3J5pnVPtTU7aDfy |
| Fault realisations in the box: split vs TI band against the mode-II crack (the reference example; sweeps of eta_1/eta_0 and w; wall placement) | https://claude.ai/artifact/Em96SAdVik4gAdhJC5LV7x |
| Split-contact probe (box, straight split fault, pure shear, mode-II crack reference; verdict frictionless) | https://claude.ai/artifact/9Au3HFWLqkHt2geWohQpYa |
| TI-band push-down smoke (no-op check, L0-L3 strength sweep, cost rows, slip on a common probe, director check) | https://claude.ai/artifact/7mau5dPymUCYGPYJCCDnME |
| Robust crust-fit proposal (parabola vs envelope trace vs flexure+envelope on 40 stored checkpoints; failure modes; locator/placement split; generality) | https://claude.ai/artifact/SgZjTP3MdeSxaGRNPup8hG |
| Add-on mesh demo movie, envelope fit, rebuilt every step (30 frames, two fixed windows, per-step table) | https://claude.ai/artifact/3NDYkgLksNA1yuQGdvVrZ3 |

## Open work

| What | Where | State |
|---|---|---|
| Tidal shell / box-fault study | `feature/tidal-shell` fc35972a | waiting on Louis: gravitational topography term, next sweep |
| Hyperion rescue WIP (campaign half) | uw3-campaigns `main-hyperion-2026-10-20-wip` | saved, untriaged; the six underworld3 rescue branches are the dev hub's |
| Library fixes and PRs (stress-transport fix, leak PR #882, rotated-solve diagnostics and parallel add-on in #890, shear-band length scale, headless pyvista, coarse-solve null space, parallel `read_checkpoint`, #891 units dt, pressure rtol default, `zone` docstring) | `DEV-HUB.md` (dev hub) | HANDED OVER 2026-10-29 per Louis; see the hand-over section below. The science half of each stays in this table |
| Lid-regime annulus campaign | uw3-campaigns `zg95-annulus-for-kaiju` 64feaec, MERGED to main as a7792cd on 2026-11-03 (recipe v2 complete: S = one base cell, envelope default; split inset default 1 rung; restart rule -uw_resample_restored auto; wall normal analytic, geometric held; uw_chain default 0 in b440b88; builds from development 25d62812; DECISIONS.md ledger; -uw_split_inset in rungs, default 3, unit and default with Louis; -uw_wall_normal analytic|geometric, run_info explicit/effective + README choices block; -uw_fault_seams gather|conform with the partition/band-ranks record; -uw_pres_rtol default 1e-2 per Louis 2026-11-01; -uw_retry_keep best, -uw_wall_check 1 recording max |v.n| per wall; chain-comment fix in annulus_fault/box_fault, yield_stress_min = -oo for development's #759 refusal; wall-stub, envelope locator, plate_metrics by arc, TI band behind -uw_fault_realisation ti with -uw_ti_smooth/-uw_ti_model band|linear|vep, -uw_bridge_ti, -uw_fault_normal, bridge-own floor flags; ... Earth setup options, -uw_fault_precedence, -uw_marker_rheo_depth, -uw_scaled units mode with physical record columns; all new options default off); library `feature/box-faults-warm` 99259d35 | on kaiju: 11/12 controls done, faulted set relaunching |
| Restart / warm-start fixes + solver record + faulted-mesh checkpoint + docs | merged into `zg95-annulus-for-kaiju` (4955e80); branch head 361657f | done |
| Kaiju docs | underworld-community/uw3-hpc-install-run PR #1 | open |
| Technical notes (2026-018, 2026-020/021, 2026-022) | handed to the notes hub 2026-10-27; frozen state in the section above | not this hub's |
| Slab control set (12 of 12) | kaiju `~/campaigns/zg95/figures_out/slab_control/` (5.9 MB, README with the table) | COMPLETE 2026-10-26; layered_mantle stopped at its 12 h wall at step 128 (records to 120, t 0.0045) |
| Rebuild-spacing comparison (rungs 8 vs 4) | kaiju `addon_demo/rungs8/` (README, overlay.png, trench-cost.png, json, records, scripts) | COMPLETE 2026-10-26: 29 vs 47 rebuilds, 7639 vs 8471 s, trench and slip unchanged; in the note |
| Crust particle sampling (-uw_crust_ppc, -uw_crust_refill_every): particles per cell in the crust layer, NOT a material density | zg95-annulus-for-kaiju 9c7c1e7 (kaiju, Louis's request); both off by default | done 2026-10-26, smoke-tested on the thermal recipe |
| Production multigrid tail for split faults: uw_chain 0 vs default at np 16 on development | kaiju, idle node, from TAf 40 / TAf_env 50, a few steps; records vel its per Newton increment, step time, peak slip, finest-level FAC patch rows per rank | REQUESTED 2026-11-01 (Louis via the notes session). RULING: with #912 (cc839425) the FAC patch blocks run LU on the rotated route; the production tail is the welded base + the split S level with the LU patch on the finest level (uw_chain 0); the drivers' default changes only after kaiju confirms it at np 16 (#892 comment). Wombat fixture: 022 box np 4, LU patch 7 vel its per increment at band ratios 8/16/25 vs 28-76 on the lean chain. Supersedes the #896 D-vs-A check (development now carries #914). Needs 54ad91b's yield_stress_min on development. STARTED 2026-11-01: build development 25d62812 (has #912, #914; also the dev hub's E build), TAf 40, np 16, 4 steps, chain 0 (job 2475) then 2 (2477). First result: on chain 0 the finest level (6 of 7) carries the FAC patch, and in this partition ALL of it is on one rank (rank 4: 3584 owned / 3736 subdomain rows; 15 ranks none), from a hook printing patch rows per level and rank at multigrid configuration. #896 D-vs-A cancelled as superseded. The dev hub's chain 2-vs-0 at TAf 20 / TBf 70 (10 steps) stays queued behind its scaling runs. **DONE 2026-11-01 (page LiYdWdF3J5pnVPtTU7aDfy): chain 0 CONFIRMED at np 16.** Velocity its per Newton increment 5.9 vs 7.7 (-24 %; worst 7-8 vs 7-10); Stokes 448 vs 467 s/step (-4 %); answers identical (vrms 2e-6 rel, slip 0.01, Newton 6/7/6/7), no caps or fallbacks. The annulus's lean chain was already well behaved, so the gain is small against wombat's 7 vs 28-76, but chain 0 is never worse. Patch rows: the finest-level patch sits on rank 4 with all 105 split node pairs: CORRECTED 2026-11-01, this is the GATHER (every placement in annulus_faults.py calls place_fault_ribbon_2d with seams="gather", which moves the band's region onto one rank and carves it there; at depth 0.45, 231 pairs and a 7010-row patch, still one rank), not the partitioner; the library's seams="conform" (#670, the band meshed through the seam, each rank its own side) was never wired into the drivers, even as an option (the LIGAMENT seams deadlocked with the network mesher on 18 Oct and were not retried). So the patch solve is serial on one rank at any np by driver choice. Oddity: on the restart mesh f0 chain 0 had a 3584-row patch and chain 2 none. **Default change (held by the hub for Louis's word on timing): uw_chain=0 in annulus_faults.py and the box drivers once the builds in use carry development's FAC LU (#912); on the leak-fix overlay chain 0 is ~1.5x slower (the earlier control), so the default moves with the build** |
| Solver time budget and warm/cold comparison, chain 0 vs 2 (Louis via the notes session, 2026-11-01: "what is the solver time spent on the coarsest mesh? How efficient is the overall configuration of the solver. It does feel very slow for a 16 core run / single timestep"; and whether warm/cold behaviour compares between the two gridding strategies) | kaiju, from jobs 2475/2477's -log_view and coarse logs (A) plus new runs on a free node from TAf 40 on 25d62812 (B) | REQUESTED 2026-11-01. A: per-step time split for an ordinary and a rebuild step, each arm: coarse solve (which solver, set-up count/time per Newton it, solve time, coarse size), smoothing per level and the FAC patch (rank 4 LU vs the others' wait), other PCSetUp (PtAP, transfers), assembly, add-on placement/rebuild, Schur structure (pressure its per Newton it, total velocity applications, rtols used, whether pres_rtol was the 0.1 x tol default), and F-cycles per step x seconds per F-cycle. B: cold from rest; rebuild step warm from the child's own v,p and from the base v only; ordinary warm; Picard/Newton, vel its (last and total), pressure its, Stokes time, retries, vrms, slip; the pair at -uw_pres_rtol 1e-2 if cheap. One page with a stacked time budget per arm. **DONE 2026-11-01 (page LvNXEPD4QNkKtr2V7jDYH2; runs 2480-2488).** A, chain 0 / chain 2, mean over a rebuild and two ordinary steps (solve 442 / 409 s, step 455 / 424 s): coarse solve 15 / 19 s (3-4 %; the dense SVD, 124 cells, set-up once per Newton increment, 15-20k applications per step); smoothing levels 1-5 182 / 210 s, finest 179 / 139 s (chain 0's finest cycle 0.085 vs 0.057 s, offsetting its fewer iterations; the FAC patch LU 21-28 s per step on rank 4 alone, max/min 165-178, the others wait); PCSetUp/PtAP 1-2 s; assembly 15-17 s; placement 5.4 / 11.1 s per rebuild. **THE COST IS THE SCHUR STRUCTURE: 41-47 pressure iterations per Newton increment at the default pressure rtol 1e-4 (0.1 x tol; TAf ran without -uw_pres_rtol), each an inner velocity solve to 3.3e-5, i.e. 355-418 finest F-cycles per increment, ~2500 per step at ~0.17 s each. At -uw_pres_rtol 1e-2: 12-22 pressure its, 138-169 cycles per increment, solve 182 / 175 s per step (2.3x, -59 %), vrms identical to 6 figures, slip within 0.05.** Untested levers: an inexact inner velocity solve (1-2 F-cycles per pressure iteration); the warm Picard phase. B (step 41; final vrms 1358.92 in every case): cold from rest 6/1 Picard/Newton, 477 / 481 s; rebuild warm from the child's own V,P 4/2, 393 / 405 s; rebuild warm from the base V only 4/2, 407 / 400 s (one 54-iteration pressure solve); ordinary warm 6/1 and 5/1, 390-501 s: even warm steps run 5-6 Picard before one Newton increment because the warm switch (1e-2) is measured against the rest-state residual and the warm iterate starts near 2e-2. No cold retry anywhere. **The two gridding strategies behave the same on every start** (same counts, same answer, times within 3 %). Scaling aside: B and C complete at np 32 and 52 (#902 closed on kaiju); np 32 anomalously slow (~1050 s/step vs ~420 at 16 and 240-360 at 52, first dt differs) under investigation |
| Recipe v2 baselines: **COMPLETE 2026-11-04.** TAf-v2_c (3852/3953, from step 0, base at checkpoint 85) and Earth run 2_c (3858, base at checkpoint 75; continued to the overturn as 3957, the article run), both with the built cut in cold slab at every checkpoint. Base pages and movies from kaiju. | kaiju | done |
| Full overturn run for the article (Louis, 2026-11-04: "soon") | kaiju; Earth run 2 corrected and TAf-v2 carried past the base; estimate ~4x the time to the base, t ~0.001-0.0015, 400-600 steps, ~1-1.5 days per run on one node at np 16 (or ~1 day at np 52 if the wall node is clean) | Louis to pick the case. Watcher base stop optional: STOP_AT_BASE (default 1; 0 logs the base and runs on to -uw_steps), applied 57affaa, blob 6501ae5 verified, merged to main; the watcher writes its choices (STOP_AT_BASE, EVERY, HOT_PAUSE) to the run README beside the driver's block. |
| np 52 for production (Louis's throughput ask) | kaiju 10-step test from TAf-v2 checkpoint 20, np 52 vs 16: wall check, fault-in-slab, -log_view with the one-rank patch's fraction of the step; then the SuperLU decomposed patch if the dev hub says how | DONE 2026-11-04 on f631ce42: np 32 and 52 both 1.19x np 16 on one node (memory-bandwidth bound); FAC patch 2 % (SuperLU not worth it); #935 and #902 verified on the production mesh. Open: a 2-node x 16 point. SuperLU waits on that number. The known np 52 state: 1.44x per step, one unconstrained outer-wall node (v.n 2722), 46-47 GB per node. |
| TI-in-the-ladder fault comparison (one run) | kaiju runs/slab_thermal_fault_TAti_smooth (checkpoints to 90), page v6 https://claude.ai/artifact/TAUT7fi5cM75zkbna7gm9R; design report figures_work/ti_fault/; TI pages 7mau5dPymUCYGPYJCCDnME, box reference Em96SAdVik4gAdhJC5LV7x | COMPLETE 2026-11-01. TAti_smooth at the base (tip on it at checkpoint 85, stopped after 90, job 2469; L1 band strength, chain 0, envelope locator, whole-band mask, smooth band law, 3e-2 Newton switches, keep-best retry from step 61). RESULT: the TI band and the split give the same large-scale subduction: time on base 2.350e-4 vs TAf_env 2.349e-4, tip histories overlie; incoming plate 698 vs 686, P10 0.100 vs 0.096; TI trench and hinge retreat ~20 % less by the base (-7.6 vs -9.5 deg; hinge -4.0 vs -5.1); dips 35-40 in both; TAc later (2.445e-4), slower (580), less plate-like (0.119). Slip medians on each run's own measure (TI 3774 band probe, TAf_env 4200 node jump, TAf 6243), not comparable. COST (+-10 % non-determinism): TAf 455 s/step, 7.0 Newton, 12.7 h; TAf_env 340, 5.6, 9.5 h; TAc 302, 6.7, 6.8 h; TAti_smooth 912, 13.8, 23.0 h recorded (~26 h node time with discarded segments and the hang). CAVEAT: 31 of TAti's 91 steps unconverged (20 in 6-60 under the old retry rule, 15 of them cold-worse; 11 in 61-90 with keep-best, none cold-worse), clustered after rebuilds; the three split/no-fault runs had none. All four at pressure rtol 1e-4; walls clean at np 16. Louis's "all the models seem to do similar things" is answered: the realisations are close in this setting |
| Add-on mesh demonstration movie (fault refit and rebuilt every step, fixed window, 30 frames) | kaiju figures_out/addon_demo/mesh_movie/ (demo-mesh-envelope.mp4, .json, README.md); page https://claude.ai/artifact/3NDYkgLksNA1yuQGdvVrZ3 | COMPLETE 2026-10-29 (job 2375, TA_age25f steps 31-60 on 07667b2, envelope, rebuild every step): 30/30 fits, no welds, 17.9 GB; windows centred at -3.21 deg (slab: -21.0 to 22.6 deg to depth 1.0, tip at 0.87 by step 60; trench: -8.75 to 2.33 deg to 0.24); trench -1.35 -> -5.07 deg; placed dip 32-43 (floor never bound; data 30.9-41.4); fit change 0.003-0.012/step (0.19-0.76 of the 4-rung threshold; production would rebuild every 2-4 steps); rebuild 16.0-16.6 s (build 11.1-11.7, transfer 1.9, to base 2.9) against 131-248 s steps, ~8 %; +524-624 cells on 126,976. The parabola from the same start (2367) OOM'd at step 40. For UWTN 2026-022: the notes hub's to use; files reach the laptop by Louis's rsync |
| Faulted thermal set (TAf, TBf, TA_age25f + fault-free twin TAc, crust sampled at 12 ppc) | kaiju `figures_out/slab_thermal_fault/` (README, overlay.png, solver.png, plate_metrics for all seven thermal runs, fault_compare.json, records) | COMPLETE 2026-10-29, stopped at the base (TAc 80, TA_age25f 90, TAf 100, TBf 110), all on full checkpoints; artifact https://claude.ai/artifact/NJCoW6npE4kr4D5yXfbqVR (table, four movies, overlay, solver); rsync for the files |
| Thermal slab set (TA, TB, TA_age25; TA_Pe3 cancelled) | kaiju runs `runs/slab_thermal_*`, scripts `~/campaigns/kaiju-launch/slab_thermal/` | third segments running since 2026-10-28 01:11 (jobs 2263-2265 from 250 / 240 / 260) to finish at 299; recipe unchanged, overlay-warmdiag; the crust weak layer is broken by the proxy in these runs (decision pending on a redo with -uw_crust_ppc 12) |
| Slab faulted set (B1_crust0.1_nofault, B1_crust0.1_fault, B1_crust1_fault, C1_crust0.1_fault) | kaiju `~/campaigns/zg95/figures_out/slab_fault/` (3.0 MB, README, trench_retreat.png, frames, solver records; segment ledger kaiju-launch/slab_fault/SEGMENTS.md) | COMPLETE 2026-10-26: all four 0-299, records continuous, no KSP-cap hits; faulted runs in three segments each (leak), every restart at match distance 0; figures reach GitHub after Louis's rsync (Waiting on Louis) |
| Memory leak per faulted-mesh rebuild (compute half) | kaiju runs on the `overlay-leakfix` build of `bugfix/faulted-rebuild-leak` 547c2e54; fix validated on kaiju to round-off (6e-10), RSS flat over rebuilds | DONE on the machines 2026-10-27. The library side is PR #882 (A), the dev hub's |

## Library fixes: handed to the dev hub (Louis, 2026-10-29)

From 2026-10-29 the dev hub (`DEV-HUB.md`, `session_01HxWvn6vA38fdYLUxnxDk4g`) owns the underworld3 pull
requests, the library fixes on branches without a PR, and the library problems sessions raise. This hub keeps
the compute side: which machine runs what, the campaign drivers in uw3-campaigns, the evidence a run produces.
A library defect found in a run is recorded here as a one-line "library defect, dev hub picks it up" entry in
the log and the "For the other hubs" section; the defect, its issue and its fix then live in `DEV-HUB.md`.

Rows handed over from "Open work" (state at hand-over; not updated here afterwards):

| What | Where | Hand-over state |
|---|---|---|
| Stress-transport fix | `bugfix/backward-nodes-snapshot-order` adb20e9d | verified on hyperion and kaiju, reviewed, no PR; follow-ups (Eulerian/SUPG ordering, docs, test_1076 renumber) were running on hyperion before the reimage |
| Memory leak per faulted-mesh rebuild | `bugfix/faulted-rebuild-leak` 547c2e54 -> PR #882 | Louis's priority (2026-10-27) was propagation to development; kaiju and the laptop already run the fix; the adversarial points still owed were sub-communicator cleanup and registry consumers |
| Rotated-solve diagnostics | `bugfix/rotated-solve-diagnostics` 210c7307 | written on kaiju, pushed by the hub; dev hub says contained in #890 |
| Parallel add-on distribution | `feature/parallel-addon-distribution` 8fe9ad76 | dev hub says contained in #890 |
| Shear-band length scale | `feature/shear-band-length-scale` 114c472c | second adversarial review owed |
| VE/plastic gap closure, subksp banner | #850-#854 | dev hub says merged 2026-10-28 |
| Headless pyvista without trame (#665) | `bugfix/visualisation-headless-no-trame` 7392233c | no PR |
| Coarse-solve null space (np > 16 on kaiju's 52-core nodes) | `feature/coarse-solve-nullspace` | Louis's ruling 2026-10-28 recorded in DEV-HUB.md; kaiju runs np 16 because of it |
| Parallel `read_checkpoint` bug | found on kaiju 2026-10-21 | not filed; the lid-regime driver is not affected |
| Units model estimate_dt (D1-D7) | issue #891 | filed by this hub 2026-10-29; demos run dimensionless meanwhile |
| Rotated pressure (Schur) KSP rtol default 0.1 x tol | kaiju's A/B: 1e-2 cuts Stokes 28-57 %, answer unchanged to 7e-6 | solver default, Louis decides; the campaign sets it per run with -uw_pres_rtol |
| Split `zone` docstring says TI; it is isotropic weakening | library | docstring fix, to file |
| Hyperion's efficiency items (adopt_hierarchy, recompile) and the six `*-hyperion-2026-10-20*` rescue branches | hyperion, paused by the reimage | untriaged |

## For the other hubs

- 2026-11-04, to the dev hub, from Louis's throughput ask ("Agreed - empirical, but let's try all these options"):
  the inexact inner velocity solve cannot be tested by a driver knob. On the rotated path the velocity sub-KSP rtol
  is fixed in the library at 0.033 x the SNES tolerance (the driver records it as velocity_rtol_rotated); the
  driver's uw_vel_rtol acts on the native path only. Louis wants it measured: please expose the rotated velocity
  rtol (an option or petsc prefix, default unchanged) so kaiju can run arms of 10 steps from TAf-v2 checkpoint 20
  (0.033 x tol as control, then e.g. 0.1 and 0.3 x tol), reporting s per step, MG applications, Newton count and the
  answer's change. This is a solver-stability-sensitive knob: exposure only, no default change without the arms.
- 2026-11-04, to the dev hub: #935 and #902 VERIFIED on the zg95 production mesh by kaiju on development f631ce42
  (np 52: 0 of 1,792 Upper / 1,024 Lower owned wall points missing; custom FMG builds at np 52 with the 124-cell
  coarse level, no fallback; |v.n| 6.1e-13). Add to the issues if useful. Scaling answer to Louis's SuperLU question:
  the one-rank FAC patch is 1.6 % (np 16) / 2.3 % (np 52) of the MG Apply time, so a decomposed patch is not worth
  it on this problem; the step is memory-bandwidth bound (MatSOR, MatMult) and saturates by np 32 on a Gold 6230R
  node. #901 (A-prime) remains ~5 %; the coarse PCSetUp grew 25 -> 59 s from np 16 to 52.
- 2026-11-04, to the dev hub, THROUGHPUT (Louis, via kaiju, who has also messaged you directly): "It drives me
  completely crazy that we are stuck with a very limited number of cores for reasons that appear to be minor bugs
  ... I can run just as fast on a laptop !!" and "We also ran the decomposed patch problem using super_lu and that
  worked well. Ask about that with your co-sessions ... 52 cores plus that super_lu trick and see if we can get it to
  run." Questions for you, answer in DEV-HUB.md: (1) where the SuperLU decomposed-patch work lives (branch, option
  names) and how it is enabled on the FAC fault patch; whether the kaiju image's PETSc (uw3-gadi-development-20261021)
  has superlu_dist; what was measured, against what; (2) the analytic-normal node-set defect (np 24/32/40/52, one
  unconstrained outer-wall node at np 52) and the geometric rigid-rotation mode: fixed on development, or a driver
  workaround, because np 52 is now on Louis's critical path. The hub's numbers for context: np 52 vs 16 on one node
  339 vs 487 s per step (1.44x, Schur-bound; page ACJ6diJRBCGoBGvCa6aCxM); one-rank patch 10-12 % of a np 16 step at
  depth 0.60 and growing linearly with fault length (the number a decomposed patch has to beat); packing 3x16 per
  node 2.1x node throughput. Kaiju runs a 10-step np 52 test (wall check, fault-in-slab, -log_view with the patch
  fraction) against np 16 from TAf-v2 checkpoint 20 once you answer.
- 2026-11-04, to the dev hub and the docs hub: **hyperion is back** (Louis), reimaged, with a Remote Control session
  `session_01HxWvn92dmiWUj5FX68AZc7` (Claude Code 2.1.318). The hub has asked it for a read-only inventory (where
  the old /mnt/data tree came back, the pixi env, GitHub access, whether it can message the hubs) and told it to
  change nothing yet. Its role is open: before the reimage it was fast parallel development (tests, probes, np
  2-16); library work is now the dev hub's, so the dev hub should say what it wants from hyperion, and the docs hub
  whether its "hubs move to hyperion" plan stands. The six `*-hyperion-2026-10-20*` rescue branches and its
  efficiency items remain the dev hub's, untriaged.
- 2026-11-04, to the dev hub: the analytic-normal wall defect is FILED at your request as **underworld3 #935**
  (bug; kaiju's repro: TAc unfaulted, 1 step from checkpoint 20, label_check_hook.py; np 32 drops 3 owned wall
  points, one with no labelled facet on its owner and two WITH one, so two paths lose points; geometric path clean
  on the same mesh). It is the blocker for np 52 (Louis's throughput ask). Related #896, #906.
- 2026-10-29, to the dev hub: agreed, the library rows are yours from today; they are listed above with their
  hand-over state and removed from "Open work". Louis's standing instruction on the leak fix ("important to
  propagate, make it a priority", 2026-10-27) now rides on #882. Compute for a fix: ask through this file and
  Louis names the machine; kaiju is in production on the rollback campaign (np 16, 12 h jobs) and hyperion is
  reimaged and out of the loop until Louis says otherwise (he said otherwise 2026-11-04: hyperion is back). On #457 (closed by #493/#748): noted for the TI-fault
  comparison; kaiju's build is `feature/box-faults-warm` 99259d35, so whether those fixes are in it is the question,
  not the issue's state; kaiju will check its base. No new library defects beyond the list above.
- 2026-10-29, to the dev hub, library one-liner: `constitutive_models.py:3639-3647` (at 547c2e54) still carries a
  "TODO(BUG): the CONSISTENT (Newton) tangent of this model is inconsistent ... TI Newton runs at Picard pace
  (#457)" comment on `TransverseIsotropicFlowModel`, written 2026-07-29 (04379583) before the #493 fix and never
  removed. Kaiju confirmed both its builds contain 22aae82c (#493) and 0b6c9624 (#748). Stale comment to delete;
  it misled kaiju's TI design report.
- 2026-10-29, to the dev hub, library defect (kaiju, bears on the fault-split multigrid PRs #889/#890): custom_mg
  `set_custom_fmg` with UNSPLIT `place_fault_ribbon_2d(split=False)` ladder levels as the coarse tail exhausts node
  memory (170-377 GB at np 16, 127k cells) after "Setup solver" and before the first iteration; split ladder
  levels and an unplaced coarse tail are fine. Not the TI model and not the patch smoother (reproduces with the
  band off, with a plain VP host, with FAC disabled, and with one placed coarse level); points at the hierarchy or
  transfer build (barycentric, cross_partition auto) between unsplit placed levels. Repro on kaiju:
  runs/slab_ti_check2b (TAf checkpoint 40, -uw_fault_realisation ti -uw_ti_check 2), build 547c2e54. The science
  hub works around it with -uw_chain 0 for the TI runs. Please file.
- 2026-10-29, to the dev hub, TO CHECK (not a finding): on the split fault (rotated fault BC, add_fault_bc(0)),
  kaiju's offline estimate of the NORMAL traction differs between the two faces below 0.08 deep (about -0.4 against
  +0.3 of the host yield; estimated from each side's velocity and the smoothed log10 eta field, 0.25w off the cut),
  where a contact must transmit it equally. May be the per-side pressure interpolation in the estimate. A
  library-side face traction from the contact constraint's reaction would settle it; worth a probe when the
  fault-split PRs are reviewed. UPDATE 2026-10-30: the bridge-zone explanation of the split's restraint tested
  negative, so the contact constraint is the prime suspect; the science hub has kaiju running a minimal box probe
  (straight split fault, linear host, simple shear, tractions vs the frictionless answer). Result will be
  recorded here as a finding or cleared. **CLEARED 2026-10-30:** the probe (page 9Au3HFWLqkHt2geWohQpYa, script
  kaiju-launch/ti/split_probe/) shows the split contact frictionless at np 1 and 4; the normal-traction asymmetry
  was the estimate's artefact and does not appear in a linear host. Close the "to check". **REOPENED 2026-10-30:**
  a straight box cannot show it; on an arc or a kinked cut in the same box the per-node contact normals give a
  normal-traction jump across the faces (+0.03/-0.14 of tau_inf on the arc) and one-face shear, and smoothed
  normals remove both. Same signature as the annulus (-0.4/+0.3 of yield on a strongly curved polyline). UPDATE:
  in the annulus (job 2423) smoothed normals change nothing (the trace turns ~1.3 deg per segment; the box needed
  20 deg kinks), so this is a library NOTE for kinked traces, not the annulus mechanism; the annulus normal-traction
  asymmetry stays unexplained and open. Earlier text: This was a probable LIBRARY FINDING: the split contact's normals on a non-straight trace (per-node, default) partly
  lock a frictionless contact; the smoothed trace normal (add_fault normal="trace") restores it. Repro:
  kaiju-launch/ti/split_probe/ (arc and kinked cases). Annulus confirmation (job 2423) pending; bears on #889/#890
  and every faulted annulus result.
- 2026-10-30, to the dev hub, two more library notes from kaiju: (i) TransverseIsotropicVEPFlowModel used purely
  viscous (mu = inf) demands a timestep and is unguarded at rest (tau_y/(2 gdot) -> NaN because
  strainrate_inv_II_min defaults to 0), so a cold start from a checkpoint produces a garbage step; (ii) a split
  run hung after a checkpoint with "evaluate() is rank-local" warnings (job 2413, after writing checkpoint 41), to
  be reproduced before filing.
- 2026-10-30, to the dev hub, FEATURE REQUEST (from the science hub, evidence on the probe page): surface-breaking
  split faults. `fault_split` refuses a cut that touches the domain boundary ("Only strictly interior faults, with
  both tips inside the mesh, are supported in this version"), so a subduction megathrust is necessarily a buried
  crack whose top tip, 3 rungs inside the free-slip wall, tapers the slip to zero and halves it along the whole
  fault against an outcropping band. Subduction needs a cut reaching a free-slip (rotated) boundary, with the
  tip's constraint released at the wall. Bears on #889/#890 and on every faulted annulus result to date.
  **UPDATE 2026-10-30: lower priority.** The box reference shows a free-slip wall pins a dipping fault's end anyway
  (v_n = 0 on both sides), so a band run to the wall slips only 6 % more than one stopped 3 rungs short; the
  earlier "half the slip" estimate is withdrawn. Still useful for geometry (no bridge zone), not for slip.
- 2026-10-30, to the dev hub, library note from the box reference (page Em96SAdVik4gAdhJC5LV7x, script
  kaiju-launch/ti/split_probe/fault_realisations_box.py): a split fault placed by place_fault_ribbon_2d (the ladder)
  slips 10-18 % below the frictionless crack and below the TI band (peak 0.80 at h 1/48, 0.86 at 1/96), where the
  same cut made by Mesh.add_fault reaches 0.96. The ladder placement costs the split 10-15 %; worth a look in the
  #889/#890 review (rung geometry at the cut, or the contact pairs the ladder produces). Also for the record: the tangential traction on the cut's body is 1e-3 to 1e-2 of
  yield (near-free), but the top 0.04 under the isotropic bridge zone carries 0.1-1 of yield, because the bridge's
  x1e-3 weakening is overridden by the global floor and rate strengthening. Driver-side (the science hub tests a
  bridge-own floor), but the library's split realisation has the same bridge design.
- 2026-11-01, to the dev hub, the driver-side knob audit (page NRAGaCJ3GXxypNvsAT53wL) and what it says about the
  library: the annulus drivers use the analytic wall normal (unit_r) everywhere, the path with the wall-node defect,
  where the library default and docstring recommend normal=None; kaiju is testing normal=None at np 32 (if clean,
  the fix for the analytic path is to complete its node set as the geometric path does, and production could switch
  meanwhile). Also from the audit, as library-facing notes: uw_vel_rtol does nothing on the rotated route (its
  velocity rtol is fixed at 0.033 x tol), the pressure factor 0.1 is still the unmeasured TODO now measured twice,
  the drivers' margin_rings 1 / clearance 0.7 differ from the library's 2 / 0.3, and the FAC patch is tunable only
  through UW_FAC_* environment variables. TAf_env is not a clean control for TAti (several knobs differ), a caveat
  now on the comparison page.
- 2026-11-02, to the dev hub: Louis wants the fault recipe and the library changes pushed so the annulus rollback
  experiments restart. For the library, what the experiments need: at np 16, nothing beyond development 25d62812
  (accepted). To run wider: the #902 fix as a PR (bugfix/custom-mg-many-ranks 96d39f7b: without it development's
  custom FMG fails at np 32), the analytic-normal node-set completion (the np != 16 wall-node defect), and #906 (the
  declared rotation null modes, which is also the geometric-normal-with-fault finding). Please put those three in
  your queue with the rollback restart as the reason, and say in DEV-HUB.md what each waits on. The campaign's
  recipe v2 defaults (chain 0, pres_rtol 1e-2, envelope, inset 1 rung, S = one base cell, analytic normal) are in
  zg95_lid_regimes/DECISIONS.md; the campaign branch merges to uw3-campaigns main after the acceptance.
- 2026-11-02, to the dev hub, your ladder-spacing item is DONE (page 7cbuaxBnoZrfjdPioMHroT; reruns re-sampled at
  each S; chain 0, development 25d62812, np 16, 10 steps from TAf 20 and TBf 70; S = 0.0156 with inset 1 rung and
  0.0078 with inset 2, i.e. one base cell in both, against production's 0.004 with 3 rungs). Matching S to the base
  shrinks the serial FAC patch 2-3x (3114-3468 owned rows -> 1580-1870 -> 952-1070; node pairs 87-109 -> 41-51 ->
  19-25) and its solve 2.3-4.5x (22-26 s -> 9-14 -> 5-8 per step); same-node step cost (TBf, n3) 388 -> 346 (-11 %)
  -> 335 s (-14 %). Answer, TBf 70 (mature rollback): vrms within 0.3 %, slip_max -2.5 % (h_b/2) and -4 % (h_b), slip
  from 0.02 down within ~5 %, trench unchanged. TAf 20 (early slab): slip_max at step 30 -10 % and -18 %, vrms -3 %
  and -1.5 %, trench -1.98 / -1.68 vs -2.04 deg; most of the difference is at the top where the cut now starts one
  base cell (~0.020) down. The confounded arms are kept and relabelled. Whether S should become h_b by default is
  Louis's.
- 2026-11-02, to the dev hub, LIBRARY FINDING (kaiju; the same defect as your #906 in a new guise): on the closed
  annulus with GEOMETRIC normals (normal=None) and a placed fault, the solution is the correct flow plus an
  arbitrary RIGID ROTATION. Least-squares rigid rotation fitted to the solver-mesh velocity at TAf 40 step 41:
  analytic normal omega 0.04 (rms|v| 1337.1); geometric inset 1 omega -1543 (rms|v| 3104.5, 1358.7 after removing
  omega x r); geometric inset 3 omega -4743 (8682.4, 1337.1 after removal = the analytic answer exactly). Slip is
  unchanged; vrms carries the rotation. Mechanism (no-solve hook recording the library's normals,
  kaiju-launch/scaling/normal_check_hook.py): the placement inserts band vertices along the base mesh's wall
  edges, 4e-6 to 1.4e-5 inside the circle (on the chord), where the geometric normal is the chord's normal, up to
  0.17 deg from radial; on the unfaulted mesh every wall node is a base vertex (measure-weighted mean of two
  chords = radial) or a chord midpoint (radial), so omega x r is exactly tangent and rigid rotation is an exact
  null mode the route removes; with the fault the mode is INEXACT, _rotated_velocity_null_modes's verified-mode
  test rejects it, and the nearly singular mode is left to the solver, which returns an arbitrary amount. The 19
  "violating" nodes are where that rotation is not tangent to the faceted wall; every node has labelled
  facets; the normals are geometrically right. Not placement labelling, not the fault. Fixes: (i) always remove
  the rigid-rotation mode on a closed circular boundary (the declared Mesh.nullspace_rotations, as #906 says,
  rather than the 1e-8 verified test) or pin the net rotation; (ii) have the placement project new wall
  vertices onto the circle; (iii) driver stopgap, subtract the fitted omega x r after each solve; and the
  analytic-path node-set fix would make analytic safe at all np and sidestep this. Repro runs: kaiju
  scale_isolate_geometric_inset3_TAf_ck40, scale_normalcheck_*; scripts rot.py, viol.py beside the scaling
  scripts. **Campaign consequence: the analytic normal stays the driver default (clean at np 16); Louis's
  geometric ruling is held on this mechanism until #906 or the analytic node set is fixed.**
- 2026-11-03, to the dev hub, a module proposal from Louis: on kaiju's fault-division design (page
  UANqhA82AfRoh7fjgrPwYG; draft f393fd7 on kaiju/fault-division-draft in uw3-campaigns, offline-placed on 80 stored
  faults, never run) he said "This is a lot of design for what is, actually, a simple driver to test a concept. If
  we implement this, then we should consider it part of a plate-boundaries module." The design (every locator
  divides the fault at the local cell size h(s); the ladder on those points verbatim; W = a whole number of local
  cells averaged along the fault, equant by his ruling, i.e. 2h with rungs at h; a division record for restarts;
  the division used stated per build) is therefore yours to weigh as a library module, with the campaign driver
  staying the simple concept-test it is. His principle in his words is in the ledger's principle row.
- 2026-11-03, to the dev hub, a placement observation from kaiju's 320 offline placements (page
  UANqhA82AfRoh7fjgrPwYG): slivers down to 0.11 deg occur in every arm, production v2 included (Earth run 1
  checkpoint 40); every cell under 10 deg lies within 0.004 of the surface and 0.03 of the outcrop, none along the
  cut or at the tip, so it is the band's outcrop meeting the wall, independent of the division and the width. For
  the ladder placement at the wall. Also: the ladder path takes the trace's points verbatim (precomputed samples +
  reach), confirmed on uneven divisions (0.0133-0.0165).
- 2026-11-02, to the dev hub: Louis has ruled the campaign drivers' wall normal to the geometric (library default,
  normal=None) path, "the computed normal is probably the correct default", and the split inset to 1 rung (the one
  element the surface rotation needs; the test showed 3 rungs was a ~10 % physics choice with no evidence behind
  it). The analytic-normal node-set defect stays yours to fix (filed 2026-11-04 as #935); the campaign no longer depends on it. UPDATE the same
  day: the geometric normal FAILS the outer-wall constraint when a fault is present (v.n 8 at 19 node entries,
  vrms doubled; clean without a fault), so the campaign does still depend on the analytic path at np 16 for now;
  kaiju is isolating whether the placement leaves the band's new wall vertices off the circle or unlabelled (a
  placement-side gap) or whether the geometric path itself misbehaves at the band; a finding follows either way.
- 2026-11-02, to the dev hub, your ladder-spacing arms were CONFOUNDED and are rerunning (kaiju): a restart rebuilds
  each crust-law fault from the polyline stored in the checkpoint, already sampled at the writing run's S (0.004),
  and re-samples at the new S only when a detection re-fits; in the S = h_b and h_b/2 arms no re-fit happened in 10
  steps (TAf kept 79 pairs vs 87; TBf 103 vs 109), so those arms changed only the band width W = 2S and the inset,
  not the rung spacing (patch rows 3198 vs 3114 TAf; 3856/3560 vs 3468 TBf). Relabelled "...rungs0.004" with a
  README note; as a band-width/inset contrast they show TBf 70 slip_max 7015 (W = 2 h_b, inset 1 base cell) and
  7081 (W = h_b, inset 2) vs 7265 at production, slip at 0.04-0.08 within 1 %, the top 0.02 lower (cut starts at
  0.0172 vs 0.0127), cost equal. Fix: re-sample restored polylines at the run's S (driver 81db298, rerunning as
  jobs 3378-3381: S = h_b inset 1 rung, S = h_b/2 inset 2, TAf 20 and TBf 70, 10 steps); the hub asked for it to be
  automatic when the checkpoint's S differs from the run's and a no-op otherwise.
- 2026-11-02, to the dev hub, row 2's starting curve (the one-rank FAC patch against fault length; gather, chain 0,
  TAf 40, np 16, overlay F, detection every step; node pairs / owned rows / LU time per step on the one rank while 15
  wait): depth 0.15: 105 / 3584 / 22-26 s; 0.30: 163 / 5010 / 19-26 s; 0.45: 231 / 7010 / 30-34 s; 0.60: 307 / 9278 /
  43-54 s. The patch grows about linearly with fault length and its serial solve time with it: 10-12 % of a 420 s
  step at depth 0.60, growing with the fault. That is the number a decomposed patch has to beat. Run dirs
  runs/scale_kpatch_* and runs/scale_kpart2_*_gather_depth0.45_chain0.
- 2026-11-02, to the dev hub and the docs hub: Louis has approved the campaign's build move to development (today).
  New kaiju runs build from the development head of the day and record it; the uw_chain driver default goes to 0 in
  the same commit (your #892 ruling's condition met). The docs hub's journal entry closes on that commit's sha:
  **b440b88** on lmoresi/uw3-campaigns zg95-annulus-for-kaiju (uw_chain defaults to 0 in annulus_faults.py,
  annulus_fault.py and box_fault.py; acceptance passed, kaiju job 3154).
- 2026-11-02, to the dev hub, Louis on the wall-normal defect: "I'm still puzzled how this could go so wrong and be
  undetected previously. Geometrical / analytic is an obvious work-around, but in cases where there is no such
  value available, is there a latent bug." The hub's answer for your intake: the latent bug is on the
  ANALYTIC-normal path (a user supplies `normal=`), which skips the cross-rank completion of the node set; the
  GEOMETRIC path (`normal=None`, the library default and the one used when no analytic value exists) completes it
  and is correct, so a user without an analytic normal is safe and a user with one is exposed at any partition
  with an orphan wall vertex. Undetected because (i) the tests run at np 1-4 on meshes where every owned wall
  vertex has a labelled facet on its owner, (ii) np 16 on the production annulus happens to have none, and (iii)
  nothing checked v.n after the solve: the defect showed only as a smaller dt. Two asks: a parallel regression test
  with an analytic normal at a partition that has an orphan wall vertex (TAc's mesh at np 32 is one; a box at
  some np will be another), and a post-solve check of the constraint residual in the rotated route itself (max
  |v.n| over constrained nodes, warning when it exceeds a tolerance), so this class cannot pass silently again.
  Also: the drivers' decisions now live in zg95_lid_regimes/DECISIONS.md (campaign branch), Louis's ruling; the
  library-facing rulings in it (pressure rtol, wall normal, chain, inset) are the ones your matrix should cite.
- 2026-11-02, to the docs hub: the campaign drivers' decisions ledger exists at zg95_lid_regimes/DECISIONS.md on
  the campaign branch (Louis 2026-11-02: decisions recorded where other Claudes and people find them; the drivers
  are not part of underworld3). The journal and UWTN 2026-022 can point to it for every knob the drivers chose
  (pressure rtol, chain, inset, seams, wall normal, locator) instead of to hub transcripts or pages.
- 2026-11-02, to the dev hub, row 2 (a patch spread across ranks): nothing can spread it yet (conform needs the
  network mesher, which cannot place an outcropping fault; serial repro with you), so kaiju has queued the
  one-rank patch's cost against fault length as row 2's starting curve: gather, chain 0, TAf 40, np 16, 3 steps,
  depth caps 0.30 and 0.60 (jobs 3069/3070) to go with 0.15 (3584 rows, ~25 s per step on one rank) and 0.45 (7010
  rows). Each run gives the patch's rows and its time per step: the curve a decomposed patch has to beat.
- 2026-11-02, to the dev hub, from kaiju on your ladder-spacing arms (Louis's rung-spacing ruling; chain 0 at S =
  0.0156 and 0.0078 against 0.004, TAf 20 and TBf 70, 10 steps, np 16, build E, slip-profile hook): the S = 0.004
  baselines are done (production's 3-rung inset, 0.012, under one base cell). The first S = h_b and h_b/2 runs went
  out before your inset note with the hard-coded 3-rung inset (three base cells of unsplit top at S = h_b, two at
  h_b/2); the two finished S = h_b runs are kept as "...inset3rungs" (a contrast: TAf arm slip_max 920-1860 vs
  2070-3990 at 0.004, vrms 1021 vs 904 at step 30, trench -2.7 vs -2.0 deg, part of it presumably the deeper
  unsplit top), the h_b/2 runs cancelled; reruns queued with the inset at one base cell (S = h_b with 1 rung, h_b/2
  with 2), jobs 3063-3067. Every arm's README records its inset; each reports the FAC block's rows and time per
  step. The driver's inset is now a knob (uw_split_inset, rungs, default 3 unchanged; patch coming); the unit and
  default are with Louis (above).
- 2026-11-01, to the dev hub, the node-packing answer (page 1CFNXD4TpQLX5jfeTdMN8k; n7, 52 cores / 188 GB, TAf 40,
  np 16, 3 steps, build E, same case 1/2/3 at a time, 60 GB each, non-exclusive, core binding): 1 job 566 s/step
  (6.4 node-steps/h); 2 jobs 835 / 822 s (8.7/h, 1.37x); 3 jobs 841 / 845 / 708 s (13.5/h, 2.1x); ~19 GB per job.
  Recommendation: three 16-rank jobs per node for independent runs on launchers that allow packing (--mem=60G, no
  --exclusive, core binding); timing studies stay exclusive. Caveats: two per node underperformed (Slurm gave each
  job 16 cores plus siblings, probably sharing one socket's bandwidth; the third job ran fastest on the less loaded
  socket), so one more test with --sockets-per-node=1 before packing becomes standard; a lone non-exclusive job
  (566 s) is slower than the exclusive 450-500 s.
- 2026-11-01, to the dev hub, addendum to your k-partitions row from round 2's gather arms (overlay F, TAf 40, np
  16, depth cap 0.45 so the fault deepens 0.15 -> 0.45 at step 42, 3 steps): chain 0's finest-level patch grows from
  3584 to 7010 owned rows (231 node pairs, still one rank), Stokes 390 / 368 / 341 s per step; chain 2 (no patch)
  400 / 459 / 523 s; Newton 6/6/6 vs 6/6/7; vrms differs ~0.6 % at step 43 (the ladders change the rebuilt mesh, so
  not bit-identical); peak memory 21.2 vs 23.2 GB. **A longer fault favours chain 0 by 20-35 % per step even with
  its LU patch serial on one rank**; at the short fault the two were a wash. This is the one-rank-patch baseline to
  hold against a spread patch once conform or a seam-aware ladder exists.
- 2026-11-01, to the dev hub, the analytic-normal wall-node defect: CONFIRMED CONFINED to the analytic path. With
  normal=None (the geometric, cross-rank-summed normal) TAc 20 at np 32 is clean (max |v.n| 1e-8) and gives the same
  answer as the analytic np 16 reference to the printed figures; so the fix is to make the analytic path complete its
  node set across ranks as the geometric path does, and production can use the geometric normal meanwhile (kaiju's
  -uw_wall_normal geometric, 094e4f3). The 1e-8 residual is the check measuring radial v.n against a facet-normal
  constraint, not a violation.
- 2026-11-01, to the dev hub, SERIAL REPRO of the network-mesher failure (kaiju-launch/scaling/network_repro/
  {network_repro.py, taf40_fault.json}; overlay F, np 1, no solve; TAf 40's restored crust fault, 213 spine / 54
  trace points, W 0.008): ladder BUILT (127,705 cells, 52.5 s); network with the driver's spine (through the wall to
  0.02 above) FAILED in 1 s ("an embedded spine lies outside the resolved ribbon faces (trim its ends inside the
  caps)"); network with the spine trimmed to the trace FAILED in 4.8 s ("the ribbon's cavity reached the domain wall;
  the volume must be interior, with clearance to spare"). **So the network mesher cannot place a fault that reaches
  the outer wall, in serial too: conform (via the network mesher) is unusable for surface-reaching faults in 2-D**,
  i.e. every crust-law fault (trace 3 rungs below the surface). The ladder's outcrop/cap handling has no network
  counterpart. The parallel "meshed to no triangles" is the same input failing with a different message. The
  k-partitions question stays unmeasurable in the annulus until the network path handles an outcropping fault or
  the ladder learns conform.
- 2026-11-01, to the dev hub, LIBRARY FINDING: **conform has never been usable in the annulus; the network mesher's
  2-D assembly fails on the crust fault.** Kaiju's conform validation (job 2808: driver 3f2cc34, overlay F b5ea0980
  = development 25d62812 + 96d39f7b, TAf 40, np 16, chain 0, -uw_fault_seams conform so mesher=network): all four
  placement attempts raised "place_thin_volume assembly failed: RuntimeError: the ribbon assembly meshed to no
  triangles" (place_surface.py:6051 via _place_thin_volume_2d:7352), in the rank-0 CAD step (_occ_assembly_2d with
  the spines embedded) before any partition or seam handling, on the first build (the restored TAf 40 fault, depth
  0.15, dip 25, on f0). Not parallel, not conform: the network mesher does not mesh this fault geometry. (The 18 Oct
  ligament+network deadlock was a four-band set; here one fault fails outright.) Kaiju is extracting the trace and
  running the placement in serial as the minimal repro (trace file + script to follow). Consequence for your
  k-partitions row: with today's tools a fault cannot be spread across ranks in the annulus (gather via
  addon_partition always one rank; conform needs the network mesher, which fails at assembly), so "does a split
  patch lose its advantage across partitions" is unmeasurable here until one of those changes. Gather validation
  2807 passed and the record fields (seams, partition, band_ranks, band_cells_per_rank) read correctly; the
  -uw_fault_seams patch goes on the campaign branch as is (default gather; conform fails loudly).
- 2026-11-01, to the dev hub, small library note: place_fault_ribbon_2d refuses seams="conform" without the network
  mesher with the message "seams='ligament' needs mesher='network'" (the text says ligament for conform too). Also
  for the record: conform cannot be combined with the drivers' chain levels (the network mesher's levels do not
  nest), so the first conform runs are chain 0 only.
- 2026-11-01, to the dev hub, CORRECTION and a matrix note: the one-rank FAC patch (and all split node pairs on one
  rank) in every kaiju run is the drivers' seams="gather" placement, not the partitioner; the library's
  seams="conform" (#670) has never run in the annulus. Your matrix row "today the add-on partition gathers each
  fault onto one rank" rests on that driver choice, not on the add-on; kaiju suggests listing conform as a
  capability with its own test, not as a property of the add-on, and the missing test is the same gap as the
  examples rule. Kaiju's round-2 k-partitions runs (overlay F, np 16, conform at depth 0.15 and 0.45, gather at
  0.45, chain 0 vs 2) are the first conform runs in the annulus; a driver patch adds -uw_fault_seams gather|conform
  (default gather) and records seams, band cells per rank and band ranks in every mesh record. Louis's reaction and
  the new standing rule (every exposed knob a recorded choice; knob audit) are in the standing rules.
- 2026-11-01, to the dev hub, your production-tail comparison is DONE (page BWgDzWDzzjDJXQWqVb1jrs; development
  25d62812, np 16, 10 steps from TAf 20 and from TBf 70 in rollback, chain 2 vs 0, jobs 2471-2474): no failures,
  caps, cold retries or unconverged steps on either arm (worst velocity increment 8-12 against a cap of 200);
  identical Newton counts step for step and the same answer at step 10 (vrms 904.46 / 1385.34, slip 3990.9 /
  7265.0, mobility) to the printed figures; velocity work chain 0 vs 2 in F-cycles per velocity solve 7.9 vs 8.2
  (TAf 20) and 8.6 vs 9.9 (TBf 70), last-application its 6.1 vs 7.9 and 7.4 vs 8.9; Stokes per step 544 vs 499 s
  (+9 %) and 385 vs 399 s (-4 %), inside the +-10 % spread; pressure its per increment the same (52, 30); chain 0's
  applied multigrid carries the FAC patch (3114/3264 and 3468/3616 rows) on the one rank that owns the fault,
  28 / 20 s per step; chain 2's has none; walls clean at np 16 in all four. Same conclusion as the TAf 40 check:
  at h_b/S = 3.9 the tails are a wash on speed and the case for chain 0 is robustness. Fault-across-partitions
  runs (overlay F) now starting, then node packing.
- 2026-11-01, to the dev hub, your #902/#901 scaling check is DONE (page ACJ6diJRBCGoBGvCa6aCxM, kaiju). **#902
  closed on kaiju:** development fc67b650 at np 32 fails the custom FMG build ("opportunistic custom-P FMG build
  failed (error code 98)"), falls back, and makes no step in 20 min; with the fix (B 96d39f7b, C 94a5c965) np 32
  and 52 build and complete; np 52 matches np 16 (step-21 vrms 634.62 vs 634.58, slip 2070.8 vs 2071.5, identical
  Newton counts 6/6/9/7/7, velocity its per increment within one). **#901 (C vs B):** coarse cost per Newton
  iteration 6-9x lower (0.32 vs 2.83 s at np 16; 0.85 vs 5.51 s at np 52), not flat with np (per application
  0.10 -> 0.24 ms C, 0.89 -> 1.54 ms B); the coarse level is 3-4 % of a step so the step gains ~5 % (487 vs 513 s at
  np 16, 339 vs 366 s at np 52); the SVD's double set-up on A and B shows (0.47-0.97 s), C's redundant LU ~0.
  np 32 rows marked different state (wall spikes, dt 2.73e-6 vs 3.78e-6); np 52 has one unconstrained outer-wall
  node (v.n 2722) too small to set dt, caveated; np 16 vs 52 is the like-for-like pair. Strong scaling 16 -> 52
  ~1.5x per step (Schur-bound); memory 19 / 32 / 46-47 GB per node at 16 / 32 / 52. The orphan counts
  restrict_unreached drops are not printed by these builds, so none reported. Your production-tail comparison
  (build E, TAf 20 / TBf 70, chain 2 vs 0, 10 steps, np 16) is running (job 2471, first of 4); then the
  fault-across-partitions runs (overlay F, np 16, depth caps 0.15/0.30/0.45, chain 0 vs 2); then node packing.
- 2026-11-01, to the dev hub, LIBRARY FINDING READY TO FILE (rotated free-slip, analytic-normal path, parallel):
  **a wall node is never constrained when its owning rank holds none of the labelled wall facets at it.**
  Mechanism (rotated_bc.py, _boundary_velocity_nodes and build_rotation; in 94a5c965 and still on development
  25d62812): with an analytic normal (add_rotated_freeslip_bc(0, "Upper", normal=unit_r), as the annulus drivers
  do) each rank builds its node list from the closures of the facets in its OWN UW_Boundaries stratum and does
  nothing else; the cross-rank reduction (_sum_facet_normals_across_ranks) and the support-1 candidate set
  (_local_boundary_candidates) run only on the geometric path (normal=None), whose docstring already names this
  case ("a rank can OWN a node every one of whose labelled facets lives on a neighbour"). Each labelled facet
  lives on one rank, so a wall vertex owned by a rank that holds none of its facets is listed by nobody;
  build_rotation on every other rank skips it as not owned; no Q block, no normal row; the node is a free point on
  a free-slip wall and the solve converges with a jet through the wall. Labels are correct. No-solve test
  (label_check_hook.py wrapping _boundary_velocity_nodes; TAc 20, build C, no fault): np 16 0 of 1792 outer / 1024
  inner owned wall points missing; np 32 exactly the three spike nodes: (-2.0022, -0.9642) owner 14, facet on 10;
  (-0.4677, -1.1292) owner 13, facet on 12; (1.2222, 0) owner 23, facets on 5 and 22. Solving gives v.n 7926 /
  12146 / 10385 at exactly those points, 1e-13 elsewhere. Partition-specific (np 16 none, np 32 three; np 24/40
  queued). **Suggested fix:** complete the node SET across ranks on the analytic path too (mark labelled-closure
  points in a velocity-sized vector, ADD over the point SF as _sum_facet_normals_across_ranks does, take every
  nonzero point, evaluate the analytic normal at its coordinate); regression test: an annulus with analytic-normal
  free-slip walls at an np where a wall vertex's owner holds none of its facets (TAc's mesh at np 32), max |v.n| on
  the walls, failing first. **Rank-count sweep (kaiju, wall_vn.py, TAf 20 faulted step unless noted): np 16 clean;
  np 24 three nodes (inner 202.5 and 247.5 deg, v.n ~10,480; outer 102.9, 3272); np 32 two faulted / three on TAc;
  np 40 three (inner 270 and 292.5, ~10,900; outer 218.6, 6543); np 52 one (outer 64.3, 2722, too small to set dt,
  which is why np 52 matched np 16). EVERY count except 16 is affected. The inner-wall spikes sit at multiples of
  22.5 deg, the coarse mesh's 16 inner-wall vertices: a hint for the regression test. PRODUCTION IS CLEAN: all
  campaign runs are np 16 and their latest checkpoints have |v.n| <= 1.1e-12 on both walls (TAf 100, TAf_env 100,
  TBf 110, TAc 80, TAti_smooth 75, Earth run1 80), across many rebuilds, so np 16 is the clean partition, not luck
  at one step.** Repro (5 min, no solve): BUILD=C N=32 SRC=TAc CKPT=20 STEPS=1
  APPTAINERENV_UW_LABEL_CHECK=1 APPTAINERENV_UW_LABEL_CHECK_EXIT=1 kaiju-launch/scaling/scale.sh; with a solve,
  wall_vn.py on the run dir; runs/scale_labelcheck_TAc_C_np{32,16}. Bears on every rotated free-slip result at a
  partition with such a vertex, and on #889/#890. Driver mitigation: -uw_wall_check 1 (433696b, kaiju/wall-vn-record,
  patch coming) records max |v.n| per wall and warns. Earlier entries (superseded) follow.
- 2026-11-01, to the dev hub, LIBRARY DEFECT, CONFIRMED on the unfaulted case (parallel rotated free-slip at wall
  nodes shared between ranks): TAc checkpoint 20, base mesh only, rotated free-slip, np 32, one step: three wall
  nodes break the constraint with v.n almost all of |v| (inner wall (-0.4677, -1.1292) v.n 12146, shared by ranks
  12/13; inner wall (1.2222, 0) v.n 10385; outer wall (-2.0022, -0.9642) v.n 7926), each a jet through the wall
  with the interior nodes beside it raised; the faulted TAf at np 32 shows the first and third. At np 16 |v.n| <=
  4e-13 on every wall node including the 57 shared ones; at np 32 only 2-3 of ~75 shared wall nodes fail. So the
  constraint is MISSING at those nodes, not slightly wrong: a vertex absent from the wall label on its owning rank,
  or absent from the rotated route's constrained-row set. Not the faults, not to_base. Repro:
  kaiju-launch/scaling/scale.sh SRC=TAc CKPT=20 BUILD=C N=32 STEPS=1 APPTAINERENV_UW_DT_PROBE=1, then wall_vn.py on
  the run dir (runs/scale_wallspike_*). Kaiju runs the no-solve labelling test next (distribute at np 32; for each
  bad vertex on its owner: in the wall label? velocity row constrained?) and reports which; Louis asked the
  question directly. Every rotated run's walls are now checked with wall_vn.py; a max |v.n| column is coming to
  the solver record. Earlier (superseded) entry follows. PROBABLE LIBRARY DEFECT (parallel rotated free-slip), from your scaling job: at np
  32 the Stokes solution carries velocity spikes at a few WALL nodes on PARTITION BOUNDARIES (build C 94a5c965 and
  B 96d39f7b identically; TAf checkpoint 20, one step): largest base |V| 11288 at r 1.2222 (inner wall, ~248 deg,
  a node shared by ranks 12 and 13) and 8183 at r 2.2222 (outer wall, ~206 deg, rank 14), far from the fault and
  band, against a physical maximum of 2901 at np 16; the spikes are in the solver-mesh velocity itself (two
  copies of the shared node in the h5), to_base passes them faithfully; vrms differs 0.1 %, mobility 1.407 vs
  1.390, slip the same, Newton converged in 6 both. They set dt (2.73e-6 vs 3.78e-6), so the np 32 scaling rows
  solved a different state; np 52 is clean and matches np 16. Likely the rotation or normal constraint at wall
  nodes shared between ranks in the rotated route; it may also explain np 32's 2.5x step cost. Repro: kaiju
  runs/scale_dtprobe_C_np{16,32}, probe kaiju-launch/scaling/dt_probe_hook.py (UW_DT_PROBE=1). Kaiju is isolating
  it now (unfaulted case at np 32; other rank counts with shared wall nodes; v.n and the reaction at the spike
  nodes) before it goes over as a finding.
- 2026-11-01, to the dev hub: solver time budget at np 16 on development 25d62812 (page LvNXEPD4QNkKtr2V7jDYH2):
  the rotated route's pressure KSP rtol default 0.1 x tol costs 41-47 inner velocity solves per Newton increment
  (~2500 finest F-cycles per step); at 1e-2 the step is 2.3x faster with the answer unchanged to 6 figures. Second
  measurement of the same lever (first 10-28). The TODO(MEASURE) on that default now has its measurement; Louis
  decides the library default, the hub puts the driver default to him today. Also measured: the dense SVD coarse
  solve is 3-4 % of a step (#901's gain bounded by that at np 16); the finest-level FAC patch LU is 21-28 s per step
  on one rank with the others waiting; the warm Newton switch is measured against the rest-state residual so warm
  steps run 5-6 Picard iterations starting near 2e-2 (a possible library improvement: switch on the warm iterate's
  own residual); np 32 on the scaling job is anomalously slow on both builds (kaiju investigating).
- 2026-11-01, to the dev hub and the docs hub (Louis's production-tail ruling, #892): kaiju CONFIRMED chain 0 at
  np 16 on development 25d62812 (page LiYdWdF3J5pnVPtTU7aDfy): 5.9 vs 7.7 velocity its per increment, 448 vs 467 s
  per step, identical answers. The partitioner puts the whole finest-level patch and all split node pairs on one
  rank at np 16 (serial patch solve; a scaling term for you). Oddity for you: on the restart mesh before any step
  chain 0 had a 3584-row patch and chain 2 none. The drivers' uw_chain default moves to 0 when the campaign's
  builds move to development (the hub holds the timing for Louis); no driver default changes in any patch yet.
- 2026-11-01, to the dev hub, two observations from kaiju: (i) the finest-level FAC patch at np 16 on development
  25d62812 (chain 0, TAf 40) is installed but entirely on one rank (rank 4 holds all 3584 owned rows; 15 ranks
  none), so the patch solve is serial in effect at np 16; whether that is the partition keeping the band whole
  or something to balance is yours to judge; the chain 0-vs-2 numbers follow. (ii) A faulted restart twice hung
  for ~17 min after reading a checkpoint and before the mesh build (jobs 2413 and 2465, with "evaluate() is
  rank-local" warnings in the first); not yet reproduced deliberately.
- 2026-11-01, to the dev hub, from the scaling job: your recipe's -log_view records nothing because petsc4py is
  initialised without sys.argv and the option is added after start-up; kaiju fixed its wrapper with
  petsc4py.init(sys.argv). Possibly also coming: the rotated loop's cold Picard giving up after 6-8 iterations at
  rel 0.1 while still converging (line-search-stall exit), to be confirmed by kaiju. **CONFIRMED 2026-11-01 (library
  finding):** in the rotated free-slip loop (rotated_bc.py:1600, _SNES_DIVERGED_LINE_SEARCH) a Picard increment
  that does not reduce ||F^|| ends the phase; but a frozen-tangent increment is not a descent direction for ||F^||,
  so the monotone backtracking test stops Picard phases that are still converging (kaiju: step 46 cold retry,
  |F| 3.14e4 -> 2.50e4 -> 2.45e4 over five full steps, then one non-improving increment and exit at rel 5.5e-2;
  step 41 backtracked 1 -> 0.5 -> 0.25 -> 0.062 -> 0 at rel 8.5e-2). Remedies to weigh: a non-monotone window
  (accept a few non-improving Picard steps), or switch to Newton on a Picard stall instead of exiting. Records in
  kaiju runs/slab_thermal_fault_TAti_smooth.
- 2026-11-01, to the dev hub, three library notes from kaiju: (i) the Newton switch is clamped to
  max(newton_switch_rtol, tolerance), so a switch below the solver tolerance silently means pure Picard; it cost
  the science hub a day of a stalled TI run before kaiju read it in the library. Worth a warning when the clamp
  acts. (ii) development 1dc500ea (#759) refuses a yield stress that reads fields without a stated floor; every
  zg95 driver died at its first build on fc67b650 until yield_stress_min = -oo was stated (54ad91b on the campaign
  branch; a local commit on TAf's driver for the scaling job). Drivers moving to development need this; the TI
  VEP path may need its own floor (untested). (iii) node packing on kaiju (your question): 52 cores / 188 GB per
  node (378 on n3), a 16-rank TAf job peaks ~22 GB, so three fit (48 cores, ~66 GB) if launchers drop
  --exclusive/--mem=0 for --mem=60G and socket binding; the OOM history was the TI chain-level defect, not
  packing; the coarse SVD limits a job's speed, not the count; the risk is memory bandwidth (the third job
  straddles sockets). Kaiju recommends 2 per node (one per socket) now and 3 only after a throughput test at
  1/2/3 per node, which the hub has approved after the scaling queue. Scaling job state: four builds (A dev
  fc67b650, B 96d39f7b, C 94a5c965 which carries 57d87783 not 96d39f7b, D f7914a92 for #896), singleton queue
  devhub_scaling excluding n1; A np16 rerunning after the yield-floor refusal (job 2451); then B/C at 16/32/52,
  A at 32, then #896 D vs A at np 16 from TAf 40. Page to follow.
- 2026-10-31, to the dev hub: your three compute requests (scaling job with 96d39f7b as build B; the #896 fix
  f7914a92 vs development at np 16; the three-16-rank-jobs question) are relayed to kaiju as idle-node work below
  the TAti diagnosis and resume; results come back here with pages. Builds from development fc67b650 for new work,
  pinned builds kept for running comparisons. Sending the scaling job straight to kaiju on Louis's word was fine;
  for node and priority accounting, please route further kaiju compute through this file (or say here that you
  sent it), and account the 3-D session's nodes in DEV-HUB.md. Also answered above: the TI-split equivalence is
  closed (box reference), with the ladder-placement note and the downgraded surface-breaking request.
- 2026-11-01, to the docs hub: CORRECTION for 022: where the hub said the finest-level FAC patch sits on one rank
  because the partitioner keeps the band's cells together, the cause is the drivers' seams="gather" placement (every
  campaign run); the library's conform placement was never used in the annulus. Chain page v5 has it; the first
  conform runs are in the dev hub's round 2.
- 2026-10-31, to the docs hub: the chain-comment off-by-one in the drivers is relayed to kaiju for the next patch.
  The fault realisations box example (below) is ready for a home beside the note.
- 2026-10-30, to the docs hub: a candidate bundled example for the fault notes is being written on kaiju
  (kaiju-launch/ti/split_probe/): the frictionless mode-II crack in a box under pure shear, solved with the split
  fault and with a TI band, against the analytic slip, with a README stating the pass criterion. It is the direct
  check of UWTN 2026-017's split-vs-TI equivalence claim. It belongs in the library's scripts/sessions tree beside
  the note; the hub will pass it on when kaiju reports. DONE: fault_realisations_box.py + README.md +
  run_realisations.sh in kaiju-launch/ti/split_probe/ (page Em96SAdVik4gAdhJC5LV7x). Result: the TI band at
  eta_1/eta_0 <= 1e-3, w = W reproduces the crack within 10 %; the ladder-placed split is 10-15 % under. UWTN
  2026-017's equivalence claim holds in the box. The files reach the laptop by Louis's rsync; they want a home in
  scripts/sessions beside the note.
- 2026-10-30, to the docs hub and the dev hub (Louis's ruling, standing rules): examples are bundled with the
  technical notes, because a feature known to behave well (here the TI fault model under Newton) can regress or
  be misconfigured without a runnable example to show the reference behaviour. For the docs hub: each note
  carries a runnable example at the note's settings (UWTN 2026-018 for the TI/split fault multigrid is the first
  case). For the dev hub: a yielding-TI Newton example/test is the regression gate for #889/#890; kaiju is checking
  the kaiju build against whatever exists now and will report whether a gap exists. **Result (2026-10-30):
  test_1066 and test_1052 pass on 547c2e54, no regression. GAP: no test or example exercises the purely viscous
  yielding TI (TransverseIsotropicVEPFlowModel with finite yield_stress and no elastic term), and the library's
  own annulus example falls back to an isotropic zone when yielding is on. Both a test and a bundled example are
  owed; kaiju's smoke on the VEP model (job 2412) will say whether that path converges under Newton.**
- 2026-10-29, to the docs hub: the add-on mesh demo movie for UWTN 2026-022 is redone with the robust (envelope)
  fault fit, rebuilt every step, fixed windows, 30 frames: page https://claude.ai/artifact/3NDYkgLksNA1yuQGdvVrZ3,
  files on kaiju figures_out/addon_demo/mesh_movie/ (mp4, per-step json, README) for Louis's rsync. The per-step
  table (rebuild cost ~8 % of a step, fit change against the rebuild threshold) is the material for the note's
  cost and sawtooth paragraphs if it wants it. Earlier line: nothing new; the compute side of the notes figures (fault_mg/uwtn_*,
  parallel_addon/uwtn_*, kaiju figures_out/) is unchanged and made on request.

## Waiting on Louis

- **Refinement 6 for TAf-v2 (2026-11-04):** the test of whether production (refinement 5) is converged; trench and
  slip moved 35-45 % from ref4 to ref5. Estimate ~3-4.5 days on one node (+/- 30 %), ~70-90 GB; a 3-step probe is
  running to pin it down, and the 2-node x 16 result may shorten it. Louis decides whether to run it.

- **Hyperion's second reimage (2026-11-04: "the OS was installed on the wrong disk"):** identify the failing drive by
  health, not name, before the installer touches a disk. Serials: nvme0 S65XNF0R608481 (today: root, nvme0n1p4, holds
  ALL the data), nvme1 S65XNE0R602587 (nvme1n1p4 1.5T, formatted 2026-11-02, empty). October's record calls the
  failing disk "nvme0" with no serial; names can swap between installs. The hub asked hyperion for SMART / nvme
  smart-log per serial (read-only); hyperion could not (sudo prompts; smartctl and nvme-cli not installed), so Louis
  runs them. Hyperion's evidence without sudo: both PM9A1 2 TB, same firmware; nvme0 = PCI 10000:01:00.0, nvme1 =
  10000:02:00.0; journalctl -k over the 6 boots since 2026-11-02 shows no I/O, medium, EXT4 or nvme reset errors on
  either. October (claude-mirror transcripts): nvme0n1p3 was / with ext4 errors 2026-10-18, nvme1n1p1 was /mnt/data;
  no serials then. Inference, not proof: same PCI slot order, so today's nvme0 is probably October's failing
  drive, i.e. the OS is on it. SMART's error log decides. **The ~210 GB at /home/lmorese/lmoresi must be copied somewhere that survives
  first** (underworld3 19G, all committed and matching its remote branches as of the last fetch; Simulations 93G;
  hyperion-rescue-2026-10-20 94G, frozen, copy whole; claude-mirror incl. pre-reimage-2026-11-04/). After: data on
  the good disk mounted at /mnt/data so the pixi env and worktree paths work unchanged; install git, gh, pixi.

- **Earth run 2's departure: CAUSE FOUND 2026-11-04 (Louis, from the movies; kaiju measured it).** Recipe v2's
  spacing default quadrupled the rebuild threshold without anyone choosing it: `needs_rebuild` tests the built cut's
  gap to the detected polyline against `uw_rebuild_rungs` x S, and S went from 0.004 to h_b = 0.0156, so rungs 4
  became 0.0625 where the old recipe's was 0.016. The detected fault stays in cold slab in every run; the BUILT cut
  drifted into hot mantle (Earth run 2: 43 % of the cut at step 20, 69 % at 60; TAf-v2: 0 % at step 30, 100 % at
  45). Isolation 3843 at step 30: only -uw_spacing 0.004 closed the gap (it also restores the old threshold); inset 3
  did not. **Both baselines cancelled on Louis's instruction and restarted with -uw_rebuild_rungs 1 (= 0.0156):
  TAf-v2_rr1 job 3849 from checkpoint 20, Earth run2_rr1 job 3850 from checkpoint 5.** TAf-v2's 1.92x was measured
  while its cut was still in the slab; re-measured on the restart. Ledger row and open item: DECISIONS.md 8c5a95f.
  **Restarts validated and the fix is in (2026-11-04):** on 3849/3850 the built cut has 0 % hot mantle at every
  checkpoint; gap 0.005-0.010 on Earth (detection every step), 0.018-0.021 on TAf (five steps of drift before the
  rebuild its detection triggers; TAf_env reached 0.026 the same way, so not a second half of the fix). Kaiju's
  series applied (blobs verified): 3486eeb driver (`uw_rebuild_cells` 1.0 base cells, both needs_rebuild branches,
  fixed-dip depth 2 cells, `uw_rebuild_rungs` refused with a message, choices record carries the threshold as a
  distance); 76f161b analysis/fault_in_slab.py + launch/kaiju_v2/baseline_job.sh (FAULT line per checkpoint, WATCH
  above 0, pause above 10 %, first acceptance lines); 9e69c6b ledger row, Open item closed. Merged to main.
  TAf-v2 re-measured: 2.03x TAf_env per step over steps 1-30 (199 vs 405 s; rebuilds 3 vs 5, Newton 5.0 vs 5.3); a
  rebuild step costs 231-243 s against 193-224 s, so the gain did not come from not rebuilding; the drifted run was
  slower (Newton 6.6). Proposal page v6. Consequence: launch/slab_kaiju/common.sh (historical, rate law) passes
  -uw_rebuild_rungs 8 and is now refused; annulus_fault.py and box_fault.py keep their own knob, untouched.

- The `uw_spacing` question: **ANSWERED 2026-11-03 (Louis): the knob is wrong in principle.** "The along-fault
  resolution is set by the discretisation of the fault, the fault width is set by the local mesh size (... an
  average of some sort seems sensible here). What is going wrong in our model is that we are also defining the
  fault and its discretisation as a knob we can control. Generally this is not true - the ladder is built from the
  fault points and we can see if that is sufficient or not, but we generally can't just change it." Recorded as the
  principle row in the ledger; kaiju drafts the removal (rungs = the locator's points at the local cell size; W =
  the local cell size, so one cell wide against v2's two; the record states the division used; the restart rule
  re-divides only when the mesh differs) with an offline placement check at W = h_b, no driver change or run until
  Louis sees the page. **DESIGN READY (page UANqhA82AfRoh7fjgrPwYG; draft f393fd7 on kaiju/fault-division-draft over
  main 7efb5ef, compiles, not run):** every locator divides at the measured local cell size h(s) (uniform in
  u = integral ds/h; uw_spacing and resample_polyline deleted); W = BAND_CELLS x the arc-length mean of h along the
  fault (length-weighted across faults); chain levels take every 2^k-th point; the restart rule compares a
  "division" record saved in each checkpoint (bit-identical no-op; existing checkpoints re-divided once); the
  record states the division used; every other use of S becomes h (inset, keep_apart, split nudge, rebuild
  hysteresis, restart tolerance, wall-check and damage reach); h gathered from every cell, partition independent.
  Offline on the 80 stored faults: a one-cell band (W = h_f) builds all 80 on the first attempt (one margin ring,
  clearance 0.7, width x1), as do v2 (W = 2S), rungs at h with W = 2h, and rungs at h/2 with W = h; rung-to-cell
  ratio 0.83-1.04; the measured h is 0.0155-0.0161 (nominal 0.0156) so the rungs barely change from v2 and the
  material difference on the uniform annulus is the width halving (band ~15 % fewer cells, fill ~35 % fewer). Aspect:
  at W = h with rungs at h the band cells are h/2 across by h along (aspect 2, smallest interior angle 26.6 deg
  against 45 at aspect 1); the mesher docstring's "about 2 elements across width" is W = 2h (v2's); aspect 1 at
  W = h needs rungs at h/2 (22 -> 42 rungs, 85 -> 137 band cells). Slivers (worst 0.11 deg, in v2 on Earth run 1
  checkpoint 40) are in every arm: all cells under 10 deg lie within 0.004 of the surface and 0.03 of the
  outcrop, none along the cut or at the tip: the band's outcrop meeting the wall, independent of division and
  width (dev hub). Effect on slip, vrms and the solver unmeasured until a run is approved. **RULED 2026-11-03 (Louis): "This is a lot of design for what is, actually, a simple driver to test a
  concept. If we implement this, then we should consider it part of a plate-boundaries module. I'd say - make the
  ladder equant if given the choice. The half-width is one cell (I think) and so the discretisation along the
  length would be similar."** So BAND_CELLS is 2 (W = 2h, rungs at h: recipe v2 as accepted), the draft is shelved
  as design input for a library plate-boundaries module (dev hub), and the baselines run on v2: TAf-v2 and Earth
  run 2 launched from the pinned 64feaec clone (kaiju to report job ids); TAc-v2 only if Louis asks. Earlier
  framing: 1b: "the fault would
  carry its own resolution (it comes triangulated / as a divided line) and this is how we create the ladder. No S
  parameter defines the along-strike resolution." Recipe v2's default is one base cell via `uw_spacing 0`, which
  you accepted on the hub's question; the notes session points out the two may not agree and has asked you. If
  the knob goes, the ladder is placed on the trace's own division (which may well be one base cell) and the
  drivers lose the parameter; nothing changes until you say. The ledger row now quotes your words rather than the
  "S = h_b" form, which was the dev hub's working reading.

- **Kaiju's write allow-list (2026-11-03):** Slurm answers again, but ~/campaigns and ~/uw3 are read-only to the
  kaiju session (its sandbox allows writes only under its working directory ~/+Claude and $TMPDIR). Kaiju now
  clones and runs under ~/+Claude/kaiju (clones/, runs/, launch/), reading the builds and the old run dirs in
  place; the recipe v2 acceptance is running from there (job 3830). Either widen the allow-list to ~/campaigns (and
  ~/uw3 for new overlays) or accept ~/+Claude/kaiju as the new root; the hub records whichever you choose and the
  ledger's machine section names it. The old results stay where they are either way. (The recipe v2 acceptance
  passed from that root on 2026-11-03, job 3830; the ledger names ~/+Claude/kaiju as the run root pending your
  choice.)

- **Recipe v2 and the restart of the rollback experiments (Louis, 2026-11-02: "I want to start pushing the changes to
  the fault recipe and library so that I can start running the annulus rollback experiments again").** Plan: (1)
  kaiju lands the last default (S = one base cell), runs the whole-recipe acceptance on one commit, and the hub
  merges the campaign branch into uw3-campaigns main (74 commits, 198 files, no conflicts with main's hub files) so
  the recipe is where people look; (2) kaiju proposes the baseline set on recipe v2 (TAf-v2, Earth run 2, TAc-v2 if
  cheap) with costs, and Louis picks; (3) library: at np 16 nothing is pending (development 25d62812 passed the
  acceptance); the items that widen the experiments are the dev hub's #902 fix (np > 16 custom FMG, branch
  96d39f7b, no PR yet), the analytic-normal node set (np != 16), and #906 (geometric normal with a fault); the open
  PR queue (#780, #861, #862, gthyagi's set) is unrelated to the rollback runs and waits on Louis's approvals.
  **For Louis: pick the baseline set when kaiju's page is in; the merge to main goes ahead after the acceptance
  unless you say otherwise.** **BLOCKED 2026-11-02 evening: the kaiju session now runs in a filesystem sandbox**
  (~/campaigns read-only: driver clones, run dirs, launchers; the Slurm controller does not resolve through the
  sandbox's proxy, so squeue and sbatch fail). Kaiju can pin no clone, submit no job, launch nothing; it built and
  compiled the spacing patch in a temporary clone and wrote the proposal page. This is a settings change on
  Louis's side, for Louis to lift. Until then: the spacing patch (b21c264) is HELD by the hub, saved, not applied;
  the whole-recipe acceptance and the merge to main wait; the baseline set waits on both. Correction to the spacing
  evidence: velocity iterations per increment did NOT change with S (TBf 7.34 / 7.54 / 7.22; TAf 6.08 / 5.93 / 6.24);
  the gain is fewer Newton increments over 10 steps (79 / 71 / 65 on TBf) and the 3.2x smaller serial patch, -14 %
  per step net. The ledger row says so.

- Rung spacing default: **DECIDED 2026-11-02, one base cell** (Louis: "1 base cell is efficient in terms of solver
  iteration which I thought quite positive", and accepting that the one-rung inset is then one base cell deep so a
  young fault's near-surface slip is 10-18 % lower than the old recipe: "I think this is OK"). Kaiju sends the
  default derived from the refinement, with the iteration counts in the ledger. Earlier framing: Evidence on page
  7cbuaxBnoZrfjdPioMHroT: the serial FAC patch shrinks 3x and its solve up to 4.5x, the step 14 % cheaper on the
  same node; mature rollback (TBf) answer within 0.3 % in vrms and 4 % in slip_max, trench unchanged; an early slab
  (TAf 20) loses 10-18 % of slip_max and the trench moves 0.06-0.36 deg, mostly because the cut's top sits one base
  cell (~0.020) down instead of 0.005. Hub's reading: the cost case is modest at np 16 (the patch is 5 % of a step)
  and the near-surface answer changes more than the chain or tolerance choices did, so the choice is physics (how
  finely the fault's slip near the surface is resolved) more than cost; h_b/2 (inset 2 rungs = one base cell) is
  the compromise with half the patch and the smaller change. No change until you rule; the knob is recorded.

- Restart rule (restored polylines re-sampled at the run's S when the checkpoint's S differs; no-op otherwise):
  **PASSED 2026-11-02:** unchanged S bit-identical to the first acceptance (vrms 1358.918800, slip 5877.766414, to
  ~1e-10); S = h_b re-samples 2 polylines (15 pairs at f8), walls clean. Goes in with the inset-1 default (series
  split; the wall normal held).
- Split inset: **DECIDED 2026-11-02, 1 rung** (Louis: "logical set back based on the purpose, appears to be safe");
  kaiju sends the default patch with the chain-2/4S caveat; the faulted thermal set and Earth run 1 (at 3 rungs)
  understate slip by ~10 % against the new default, to be said wherever they are cited. Earlier: Louis asks for 1
  rung if possible and whether 3 is more accurate or less likely to break. No evidence on record (3 was a placement margin in the first driver); kaiju tests
  inset 1/2/3 offline on all stored faults (placement successes, refusals, welds) and one 3-step smoke at 1 vs 3
  (slip near the top, face traction, vrms, Newton, build time, bridge coverage); if 1 places as reliably with the
  same answer, 1 rung becomes the default. **TEST DONE (page T37Y3MMpYyfgQZbCmuk5YQ): half met.** History: 3.0 S
  arrived bare in the first box driver (b38c1b9, 15 Oct), no comment, no failure behind it. Placement: 80 stored
  faults x 3 insets x 3 levels, 720 placements: finest level 80/80 at every inset, first attempt, same time; 2S
  80/80; 4S at 1 rung 2 refused (Earth run 1, "the fault touches the domain boundary") and 4 fell back, so 1 rung
  is safe with chain 0 (now the default) and occasionally refuses with chain 2. Smoke (TAf 40, chain 0, 3 steps,
  development): the cut's top at 0.0048 (1 rung) vs 0.0126 (3); slip +11-16 % in the top 0.02, +6-9 % at 0.04-0.08;
  slip_max 6546 vs 5878; vrms 1380.09 vs 1358.92; normal traction in the top 0.04 ~1.6 % less compressive; Newton
  6/9/6 vs 6/7/6; build time equal; the 1-rung bridge still reaches the surface (66 cells to 0.0083). **So the inset
  is a physics choice worth ~10 % in slip: 3 rungs locks a little more of the top.** If the inset only stands in
  for the unrotatable surface DOFs, 1 rung (with chain 0) best approximates a fault reaching the surface. Default
  is Louis's; the patch is one line. Earlier framing: Your ruling via the dev hub: the
  tip depth is not a physical length but the one element the surface rotation needs, in mesh units. The driver
  hard-codes 3 rungs (0.012 at production's S 0.004). Two readings: one LADDER rung (the solver mesh at the fault
  has spacing S, so 3 rungs is already conservative and the default stays) or one BASE cell (the dev hub's and the
  notes session's reading, 0.0156 at production, so the default would move from 3 to h_b/S = 3.9 rungs and stay
  fixed as S changes, which is what the ladder-spacing arms hold). Kaiju's patch makes it a knob in rungs with the
  default unchanged; say which unit and value the default takes.

- Wall normal: **DECIDED 2026-11-02, geometric** (Louis: "the computed normal is probably the correct default");
  **HELD ON EVIDENCE the same day:** the one-step acceptance with the geometric normal AND a fault (TAf 40, np 16,
  driver 06e3afd) FAILS: the fault slips identically (slip_max 6545.5 vs the analytic inset-1 smoke's 6545.6) but
  the OUTER wall breaks the constraint (v.n up to 8.19 at 19 node entries, |v|max 9215 vs 5792), vrms doubles
  (3103.5 vs 1380.1), mobility 1.238 vs 1.299; inner wall clean. The geometric normal was clean on the unfaulted
  base at np 16 and 32, so the failure needs a fault, probably where the band or bridge meets the outer wall (the
  placement's new wall vertices off the circle, or a facet unlabelled, skewing the geometric nodal normal). Kaiju
  is isolating (inset 3 with geometric; the violating nodes' positions, ownership, band/base, on-circle or chord,
  the computed normal against radial, their labelled facets; the unfaulted base at np 16 from the same checkpoint).
  The geometric default does not go in until understood; the analytic normal stays the default at np 16 (clean),
  and np != 16 runs are on hold or explicit. **SOLVED the same day:** the geometric normal with a fault admits an
  arbitrary rigid rotation (an inexact null mode the route's verified test rejects), because the placement's
  wall vertices sit on chords with non-radial normals; the flow itself is identical to the analytic answer once the
  rotation is removed. A library finding (the #906 class), recorded for the dev hub above. Inset-1 confirmation
  (job 3455) PASSED: vrms 1380.09, slip 6545.55, walls clean, equal to the smoke. Earlier framing follows.
- **Driver default for the free-slip wall normal: geometric (the library default, normal=None) instead of the
  analytic unit_r (2026-11-01, hub recommends YES).** Kaiju: TAc 20, one step, build C: with the geometric normal np
  32 is clean (max |v.n| 1e-8, 0 nodes) where the analytic normal gave v.n 12,146 at three nodes; the answer is the
  same as the analytic np 16 reference to the printed figures (vrms 565.33, mobility 1.380, dt 4.44e-6, Newton 5)
  and identical at np 16 and 32. So the drivers had a working parallel option all along; the library's own
  guidance (CLAUDE.md: leave normal=None) says the same. One-word default change; the constrained normal at wall
  vertices changes by round-off only. Meanwhile every new run at np other than 16 sets -uw_wall_normal geometric
  explicitly.

- -uw_pres_rtol 1e-2 as the campaign default: **DECIDED 2026-11-01 (Louis: "Feel free to try the lax pressure
  tolerance")**; kaiju sends the default patch; running jobs keep their pinned drivers, new runs take 1e-2; the
  library default stays with the dev hub. Patch 8ac3ed6 APPLIED as fa3accc. (Earlier text:) Measured twice: the
  10-28 cost-lever A/B (-28 to -57 % Stokes, answer to 7e-6) and today's time budget on development (2.3x faster,
  vrms to 6 figures, slip within 0.05). The pressure solve at 1e-4 is 41-47 inner velocity solves per Newton
  increment and the whole reason a 16-core step takes 450 s. Driver change only; the library's rotated-path
  default (0.1 x tol, TODO(MEASURE)) is the dev hub's with the same evidence. Also for a later decision: measure
  the warm Newton switch against the warm iterate's own starting residual rather than the rest state, since every
  warm step now runs 5-6 Picard iterations it may not need; and an inexact inner velocity solve.

- **TI vs split equivalence (2026-10-30):** the buried tip explains about half the TI-split slip difference; the
  rest is the band's blunt tips and through-width shear. Options: (a) stop here, report TAti vs TAf_env as the
  implementation comparison with this characterisation (hub's recommendation: the brief was one comparison and
  you want to finalise); (b) one more smoke with a narrower footprint and no tip overhang (small flag, ~1.5 h);
  (c) treat the split as the reference and tune the TI band's L-level to match the split's slip rather than
  frictionless. Also: the faulted thermal results are a lower bound (split slipped at ~0.4-0.5 of a
  surface-breaking fault); whether that needs saying in the note is the docs hub's, the number is on the page.

- **Build move: GO (Louis, 2026-11-02).** New campaign runs build from current development (the leak fix, A/B/C,
  #912 and #914 are on it); the pinned leak-fix overlay 547c2e54 is retired for new work; running comparisons and
  restarts keep their pinned builds; every README records its build. The driver default `uw_chain` goes to 0 in the
  same commit (kaiju's held patch). Acceptance: the one-step TAf 40 check at np 16 on the fresh development build
  (walls clean, answer to the printed figures against the 25d62812 chain-0 run). **ACCEPTANCE PASSED (kaiju job
  3154): step 41 vrms 1358.9188, slip 5877.77, mobility 1.2870, Newton 6, walls 1e-12; equal to the reference to the
  printed figures; README reads underworld3 25d62812, uw_chain 0 default.** Driver commit for the default: b440b88;
  branch head bf18312. Development's head on 2 Nov is still 25d62812 (#912, #914, the leak fix via #882).
- Earth production run: **GO (Louis to kaiju, 2026-10-29: "Looks like we can go with this to get more steps. The
  continent is fine to deform, honestly. They do that, unless they are cratons.")** Launched as job 2374 (n2):
  runs/slab_earth_run1, launcher kaiju-launch/earth/production.sh, driver 07667b2 pinned in zg95-earth-prod,
  leak-fix overlay, np 16 exclusive, 12 h, at most 130 steps, checkpoints every 5, stop_at_base.sh (EVERY=5) stops
  one checkpoint after the tip reaches 0.95. Settings: D 0.12, Ra 2.386e7, buoyancy -0.5, continent x1 (deforms),
  -uw_pres_rtol 1e-2 (go given without comment; recorded in the README as the setting used), -uw_fault_fit envelope.
  **COMPLETE 2026-10-30 (page v7, top section: ring movie, frames, table; files figures_out/earth/run1/):** stopped
  by Louis's rule at checkpoint 80 (tip 0.952 at 75; t 0.00038); 81 steps all converged, 6.8 Newton, 225 s/step,
  5.1 h, 20 rebuilds. Gap 0.76 -> 0.64 d (continent edge 19.3 -> 9.8 deg, trench -6.7), no overlap, fault-continent
  0.62 -> 0.51. Trench rolls back to -6.7 by step 55 then stalls; hinge -4.2; vrms 219 -> 980 (55) -> 651. Fault
  found at every detection; dip settles 37-42; the floor bound 13 of 81 (data down to 28); max trench gap 0.133
  against tol 0.15 (close); slip median 1382, max 4131. One build refused at step 55 (2S placement assembly
  failure), guard kept the previous fault, step 56 rebuilt normally. Plateness by arc: fore-arc strip P10 1.00
  throughout; continent 0.16 (deforming, as accepted); incoming plate 0.85 at step 20 then 0.17-0.30 from step 30
  as it speeds up to 1000-1340.
- Crust-fit locator: **SETTLED 2026-10-29 by the go on the Earth plan, which named the envelope**; flexure stays an
  offline overlay option. (Earlier framing: envelope trace or flexure+envelope for the demo rerun and the faulted runs?) Kaiju's offline results above. Hub's reading: the envelope wins on the evidence (40/40,
  monotone, 100x more stable to particle dropout, no free parameters at their bounds); the flexure gives the
  physical reading you asked for but its two parameters are not constrained by the hinge alone. Two sub-points:
  the envelope's 30 deg floor on the near-surface slope overrides the data at 11 of 40 (data say 24-30 deg; the
  parabola had placed 44-57), so the floor's value, or whether to have one, is a choice; and the demo's per-step
  trace change (0.006-0.016) sits at the 4-rung rebuild threshold, which matters for production rebuild spacing,
  not for the every-step demo.

- Thermal slab + faults: the crust-base fault law is in (d0dca11, laptop); kaiju has it pinned. **Decision needed:
  which thermal cases take a fault, and when** (a fault forms only once the slab has reached the cap depth 0.15;
  the FAULT flags are unchanged). The swarm stays pervasive (5 % of a faulted step); a crust-only repopulated
  swarm would be a driver-level change after the fault law, only if Louis wants the physics stated that way.
- Thermal runs: Louis ruled 2026-10-26 "a manageable difference, I would not try to change this": no Picard
  warm-up, no recipe change; kaiju restarts past each wall with the recipe as launched. TA_Pe3 cancelled.
  Style, ruled 2026-10-26: "We want it to drive the plate, not worried about rollback per se." The thermal
  slab driving the plate in (v_plate 1800-2350) is the wanted behaviour; rollback is not the target.
  Faulted thermal cases: DECIDED 2026-10-28, see the faulted thermal set row (TAf, TBf, TA_age25f + the
  fault-free twin TAc with the same crust sampling; the existing TA/TB/TA_age25 stand as the scientific result).
- Earth-like setup, RULED 2026-10-29 (Louis): start the continent further from the trench (it may be pulled in
  once the slab is mature; too early would spoil the experiment); the smoke's 0.15 d gap closed 3 deg in 19
  steps. Kaiju sets a larger gap (0.5-1.0 d proposed) with the third-of-the-box extent from where it starts.
  Kaiju's analysis (2026-10-29, nothing run): -uw_over_gap 0.75 with -uw_cont_extent 2.4315 (extent is an angle
  from the trench, so 2.094 + g/2.2222 keeps a third of the box from the continent's start; starts 19.3 deg, far
  edge 139.3 deg, ridge patch 178-182 clear). Surface points advected with checkpointed wall velocities keep
  0.30 d of gap after 100 steps in TAf/TA_age25f converging flow (g 0.5 keeps 0.15, g 1.0 keeps 0.58) and
  ~0.6 d in Earth-type flow (smoke3 closed 0.02-0.03 d in 19 steps; the method reproduces its 3 deg closure at
  g 0.15). Hub accepted 0.75 within Louis's ruling. **Smoke 4 DONE 2026-10-29 (job 2371, 20 steps, parabola
  locator, driver 259ee09):** gap held at 0.71-0.75 d (continent edge 19.28 -> 16.88 deg, trench 0 -> -1.88
  placed; smoke 3's 0.15 gap had closed to 0.10-0.12 over the same steps), dynamics as smoke 3 (vrms 219 -> 404,
  ~5 % higher; fault at step 5, dip 55 -> 37, slip 1600-1800; plates +809/-849 at step 19), 177 s/step mean, 59
  min, 22 GB, no welds; no crust particle within 0.01 of a continent particle, fault 0.6 from the continent (smoke
  3: 0.05). Parabola's stored trench again ahead of the placed one (-2.44 vs -1.05 at step 15); later Earth runs
  take -uw_fault_fit envelope once chosen. Correction: smoke 3 vrms was 209-389, not 210-348. Page v3
  https://claude.ai/artifact/JqKKdhnbQgYR7QMW3sRxBw. The Earth setup now has all of Louis's rulings in and is
  ready for a production-length run once the locator and the remaining choices (D, Ra, buoyancy) are settled.
  **Production plan drafted (kaiju 2026-10-29, page v4 top section, no run):** ~100 steps to the base (smoke 4's tip
  0.21 -> 0.365 in 19 steps at ~0.010/step; TAf took 83 steps from 0.365 to the base), allow 100-130 with Louis's
  stop rule; 177 -> 220 s/step, 5-8 h, one 12 h segment at np 16 exclusive on the leak-fix overlay; checkpoints
  every 5 steps (20-26 frames); -uw_fault_fit envelope, detection every step, rebuild rungs 4, floor 30 recorded;
  records per step (placed trench/dip, slip, vrms, plates, cost), per checkpoint (gap_check.py: continent edge,
  gap, overlap, fault-continent distance), tip_depth.py; driver cdf44c1 + key-clearing 8ac52ed pinned. Full flag
  line on the page with [D] 0.12, [Ra] 2.386e7, [buoyancy] -0.5 at the smoke values. Plateness split into
  oceanic/continental arcs: DONE 2026-10-29 (plate_metrics.py now in the repo at
  zg95_lid_regimes/figures/kaiju/scripts/, 07667b2; key-clearing fix f217bdb; driver blob 59d2e6b). **Result for
  Louis (smoke 4, step 19; signed median v, P10, med/max):** incoming oceanic plate +742, 0.88, 0.97; fore-arc
  oceanic strip -947, 1.00, 0.99; continent -436, 0.14, 0.51 (smoke 3: -543, 0.14, 0.57). The continent's surface
  speed falls from -870 at its trench-side edge to -190 at its far edge 120 deg away: at x1 viscosity, strong only
  through its 145 km thermal lid, it deforms internally over its width and does not move as a plate. If a rigid
  continent is wanted it needs a thicker lid (older uw_cont_age) or a compositional factor > 1, against the
  "not inherently stronger" ruling. Whole-surface columns unchanged. Page v5. **Lid check (kaiju, offline on
  smoke 4 step 19, page v6):** the lid flows viscously, it does not yield. Surface strain rate 240 at the
  trench-side edge falling smoothly to 86 at the far edge (mean 149, not concentrated at the fault side); the
  yield-limited rate at mid-lid is ~1.3e4 (1.8e3 in the thin edge), so 50-150x below yield; yield ratio >= 0.98
  everywhere, yielding fraction 0. The FK law with deta 4e3 caps the coldest lid at 4000x the interior. Lid
  present at step 19: T = 0.5 at 0.036-0.042 (105-120 km; 0.035-0.038 at step 0), thinning to 0.02 within 2 deg
  of the trench-side edge. Either lever stiffens it: a compositional factor x10-100 on the continent (gated as
  the markers are) or a thicker lid (older uw_cont_age).
- Earth-like public demonstration setup: rulings implemented (fault precedence mask, marker depth gate; the
  upper-mantle channel via -uw_asth 0.1 from 0.12 to 0.231; lm_eta 1; continent x1, buoyant -0.5, lid age 0.000625).
  Smoke 3 (20 steps): vrms 210-348 against smoke 2's 40-72 and TAf's 440-540, so the channel restores most of the
  speed; fault forms ~step 5, dip 55->36, slip 600-1400; 4-7 Newton its, 100-260 s/step; a bright shear ring at
  the channel base; no crust/continent overlap, fault-to-continent 0.048 against the band's 0.016. Page v2
  https://claude.ai/artifact/JqKKdhnbQgYR7QMW3sRxBw. **Choices for Louis**: the marker gate depth D (kaiju proposes
  0.12 d, the plate's thermal base and channel top; 0.05 d ~145 km is the alternative); Ra if the remaining speed
  gap matters; the buoyancy value; pres_rtol; the fixed ridge; a distinct render colour for entrained material
  (renderer change) if wanted.
- Graded, relaxed base mesh (Louis, 2026-10-28): AGREED; UNASSIGNED since the laptop went inactive (kaiju could
  take it after the Earth setup). The laptop was to design and implement a lithosphere-graded
  coarse base (h 0.0156 in the top ~0.2 d, 2-4x coarser below, FMG tail nested through the grading) and relaxes
  the coarse base (smoothing and flips) to remove the refinement's triangle pattern seen in the movies; behind
  flags, default off; 4-rank smoke on the TA line; mesh figures before/after; patch via the hub.
- **Cost levers, measured (kaiju 2026-10-28), decisions for Louis:** (B) the rotated solve's pressure (Schur) KSP
  runs at rtol 0.1 x uw_tol = 1e-4 inside a 1e-3 nonlinear solve (inner velocity 0.033 x tol; outer FGMRES 1 it;
  the library marks the 0.1 margin TODO(MEASURE)). A/B, 10 steps from TA checkpoint 100, np 16: pressure rtol
  1e-4 37 its/increment, 2675 s; 1e-3 25 its, 1933 s (-28 %); 1e-2 15 its, 1427 s (-47 %, +10 % nonlinear its);
  solutions within 6e-5 in vrms/vsurf/mobility, all converged, outer still 1 it. FAULTED CHECK DONE (TAf from checkpoint 20, 10 steps, Picard on): pressure its 52 -> 20, Stokes -57 %
  (510 -> 218 s/step), nonlinear and Picard its identical step by step, answer within 7e-6 (vrms, vsurf, mobility,
  slip_max), events identical. A faulted step at 1e-2 (~220 s) costs less than the unfaulted twin at the default
  (~317 s): Louis's target met. Kaiju and the hub recommend -uw_pres_rtol 1e-2 for everything that follows;
  the running faulted set stays at the default for its clean twin comparison. DECISION for Louis. The library default (0.1 x tol in
  rotated_bc) should become tol: a solver default change with this as its evidence, for hyperion when back.
  (A) the mesh is Annulus(cellSize 0.5, refinement 5), uniform h 0.0156: 126976 cells, ~511k P2 velocity and
  64k pressure dofs; 7.7 cells across the plate, 5-6 across the slab core. Refinement 4 (h 0.031, 3.8 cells across
  the plate, crust doubles) is too coarse. The library's Annulus grades only linearly in radius (cellSizeOuter /
  cellSizeInner): 2x coarser at the base gives ~68k cells (53 %), 4x ~36k (28 %) at the same surface h; the
  ruling's lithosphere-focused grading needs a gmsh size field (library or driver-built base). The laptop has
  the graded+relaxed base task; linear radial grading is the quick first step.
- **Units-policy check done (kaiju): -uw_scaled reproduces the dimensionless TA to round-off (vrms 3e-13 over 5
  steps at np 4; faulted path 6e-15 at step 0, 2e-8 after a rebuild), but only with a driver workaround for a
  library bug, so the units route is not clean end to end.** Library findings for the normal route (failing
  test, then fix; hyperion when back, or whoever Louis names): D1 BLOCKING: in a units model mesh.X.coords is
  dimensional, and solvers.py:403 (direction-aware crossing time) and advection_diffusion_eulerian.py:682 (first
  accuracy estimate) take it as model units: dt 3.4x too large from step 0 and V evaluated ~6e6 outside the
  mesh, silently (the #267 trap of the boundary contract); the driver's -uw_units_dt_local 1 recomputes the
  estimates on model-unit coordinates. D2: estimate_dt() returns a quantity in seconds, so float() of it is
  seconds. D3: uw.non_dimensionalise(swarm.coords) raises TypeError (units.py:888); no public swarm coords_nd.
  D4: a dimensionless unreduced product (km^3/m^3) comes out 1e9 wrong through non_dimensionalise and
  unwrap(dimensional); Pint .to("dimensionless") is right. D5: Integral/BdIntegral.evaluate() return the
  non-dimensional value labelled with physical units. D6: reference scales carry 1e-14 round-off. D7:
  uw.Param(2900, units="km") with an int drops its units. **Physical reading** (d 2900 km, kappa 1e-6): one
  velocity 1.088e-3 cm/yr, one time 266,500 Myr; TAf plate 0.83 cm/yr (peak 1.02), hinge retreat 20.6 km/Myr,
  slab on the base at 58.6 Myr; TAc 0.65 / 11.1 / 64.0; TBf 1.02 / 21.0 / 72.0; TA_age25f 0.60 / 17.3 / 61.3;
  slip 8.7-9.8 cm/yr; Ra 2.386e7 implies basal viscosity 2.48e21 Pa s, interior ~2e22, surface ~1e25; tau0
  528 MPa, tau1 24.3 MPa/km (0.75 rho g); plate age 933 Myr, 343 km thick. Verdict: the mantle side is
  Earth-like (viscosity, friction, slab sinking ~3 cm/yr, trench slip ~9 cm/yr); the plates are not (too slow
  at 0.8 cm/yr, too old and thick, cohesion ~5x high). Page https://claude.ai/artifact/TTiLccEcSv7iLJNV7ZH97n.
  DECIDED (Louis 2026-10-29: "File as a bug, fall back to dimensionless for the demo"): filed as underworld3
  issue #891 (D1 the bug, D2-D7 listed in it; label bug). The demonstrations run dimensionless; physical units
  come from post-processing with the chosen scales (slab_metrics' -uw_depth/-uw_kappa columns); -uw_scaled
  stays on the branch as the check only.
- **Crust-base fit: RULED 2026-10-29 (Louis): "we just did not come up with a robust enough fitting model."** The
  wall-stub is a stop-gap; kaiju designs a robust fit (anchored at the trench, lower envelope of the crust
  cluster to the cap, monotone in depth, smooth, deterministic between detections, stored = placed geometry),
  tests it offline on the stored checkpoints where the parabola failed and succeeded (artifact), then
  implements behind a flag. The demo rerun waits for it. **Louis, to kaiju directly, 2026-10-29:** (1) fit a
  flexural profile through the crust and subduction zone, "close to the shape we expect to see"; (2) a continent
  colliding with the subduction zone is a valid case, not to be avoided forever, and the fault detection must
  still work there; the fit is today a special case for one slab in an annulus, a general case (new faults forming,
  several slabs, ultimately 3D) will be needed, not a priority, but "don't optimise the fitting so much that it is
  not possible to generalise." Kaiju folds both in: a flexural candidate tested offline beside the envelope trace,
  and a generality section in the proposal. **PROPOSAL READY 2026-10-29 (kaiju, offline on all 40 stored
  crust-swarm checkpoints, nothing coded in the driver; artifact SgZjTP3MdeSxaGRNPup8hG).** Parabola 29/40 fits
  (11 none, all from step 45 on), 27 monotone, trace moves 0.75 when 10 % of particles are dropped, stored != placed.
  Envelope trace 40/40, all monotone, 0.0055 under the 10 % drop, stored = placed: subducted crust deeper than
  1.25 thicknesses, marched up from the cap in 0.0025 depth steps, base = Gaussian-weighted 10th percentile toward
  the incoming side in the connected run nearest the previous base, smoothed by a local quadratic; above 0.02 it
  extends at its own top slope with a 30 deg floor (binds at 11/40 where the data say 24-30 deg); checked against
  the particle trench (gap 0.04-0.10, tol 0.15); demo step change 0.006-0.016 against the 4-rung rebuild
  threshold 0.016. Flexure (ct + A e^(-u/a) cos(u/a) on the envelope's base points to 0.07; trench at u = pi a/2 by
  construction; straight cut to 2 thicknesses then the flexed base; hands to the envelope at 0.06, blended
  0.05-0.07): 40/40, 0.014 under the drop, trenches within 0.5 deg of the envelope; but A and alpha poorly
  determined from the hinge alone (A at its bound 18/40, jumps 0.05 to 0.8 between demo steps), 10-15 deg steeper
  near-surface dip on young hinges, does not apply below the hinge, collision changes the bending; constraining
  it needs the incoming plate's flat base in the fit or alpha tied to lid thickness. **Kaiju recommends** the
  envelope trace as the locator behind -uw_fault_fit envelope, flexure as a hinge option once constrained, stored
  geometry always the placed polyline. **Hub: kaiju implements the envelope behind the flag (default off, parabola
  unchanged), smokes 10 steps from demo checkpoint 30 against the offline trace, patches; the demo rerun and the
  production choice wait on Louis (below).** APPLIED 2026-10-29: e37bb84 (cont_extent comment) + cdf44c1
  (envelope locator, -uw_fault_fit envelope, -uw_fault_top_dip_min 30, -uw_fault_trench_tol 0.15; parabola stays
  the default; fault record carries locator, raw trace, trench gap, unfloored top dip, floored flag); blobs
  0725bbe -> 984dd71 -> 320cb04 verified. Smoke (job 2372, TA_age25f from 30, 10 steps, rebuild every step):
  trench -1.35 -> -2.98 deg at 0.15-0.24 deg/step, dip 43 -> 34.5, top dip from data 41 -> 33, floor never
  bound, trench gap 0.06-0.08, 184-246 s/step, 5-7 Newton its, builds 11-12 s, 17 GB, +330-410 cells; the
  driver's trace equals the offline envelope at all 10 steps (lateral difference 0.0000) and stored = placed
  at every record. The parabola demo from the same checkpoint had the trench at -5.2 by step 38 and OOM'd after
  39. Known wrinkle: switching -uw_fault_fit back to parabola mid-run keeps stale envelope keys in the fault
  dict (harmless). Earlier detail:
- Crust-base fit, two driver items (kaiju 2026-10-29): the fit fails at about a third of late detections
  in the faulted thermal runs (TAf 8 of 21, TBf 9 of 23, TA_age25f 4 of 19; a failed fit keeps the old fault) not for
  lack of crust (one connected cluster of 566-698 particles reaching 0.18, below the 0.15 cap) but because one
  parabola cannot describe the broad thermal hinge: it meets the surface near-tangentially and is rejected when
  it turns away or up. Worse, on successful detections in that phase the STORED theta and dip are the parabola's
  near-tangent surface crossing (TBf steps 40-54: -22.5 deg, dip 12; TAf 40-64: -19.5, dip 18-19; TA_age25f 60-74:
  -21, dip 18), while the trace actually placed always starts at the trench (-2.4 to -5.3 deg, depth 0.012-0.013),
  so the dynamics and comparisons stand but every "fault at X deg, dip Y" quoted from faults[0] or theta_trench
  in that phase is wrong (the "fault flattens to dip 18-23" in earlier reports is the parabola's crossing, not the
  placed fault). Items: (1) fall back to the slab-top isotherm (T 0.5-0.6, trench side) when the crust fit fails;
  (2) record the trench and dip from the placed trace, not from the parabola's crossing above the wall.
- NEXT TEST after the faulted thermal set (Louis, 2026-10-28): the crust at x0.001 is "very, very weak"; faulted
  models need not have it so weak. Run the faulted thermal recipe with -uw_crust_weak 0.1 and 1 against
  fault-free twins, so the fault's own contribution to surface velocity, plateness and rollback is readable (the
  compositional set: under crust x0.1 the fault was redundant; with crust x1 it doubled the retreat).
- **TI-fault comparison: settings for Louis to decide** (kaiju's design report, read-only, at kaiju
  ~/campaigns/zg95/figures_work/ti_fault/TI_DESIGN_REPORT.md). Findings: the driver always splits (no realisation
  switch); the library's TI band (FaultNetwork realisation "ti") has a constant linear eta_1 and its apply()
  replaces the whole rheology, so it needs driver work; the TI VEP model yields only eta_1; the TI Newton tangent
  is inconsistent (#457, Picard pace) so a cost comparison is biased against TI. The split's `zone` is isotropic
  weakening (uw_eta_w on viscosity and yield in the top ~0.016), not TI as its docstring says. Crust and fault
  weakening MULTIPLY today (1e-6 in crust-marked zone cells), masked in TBf by the viscosity floor and rate
  strengthening (at most 10x in ~10 cells). Proposal: crust factor linear in (1 - M), M = zone (split) or the band
  footprint (TI); a yielding band (eta_1 capped at f_b tau_y, f_b 1e-2, band regularisation 0.1, floor 0.1)
  rather than strain weakening; eta_I = eta_1/w ~25-40 (band stress 1-2 % of the mean yield stress at TBf's slip),
  eta_1 0.2-0.3 at w = W = 0.008; eta_0 the host law without the crust factor. Run: TBti = TBf + TI flags, stopped at
  the base, against TBf and a TBc twin (TB predates the crust sampling); slip by a velocity-jump probe on both;
  cost compared from step 10. Decide: f_b, eta_1/w, w, the mask rule, and whether the #457 tangent fix comes first for a fair cost
  comparison. **Louis 2026-10-29: the split fault is frictionless, zero shear strength on the slip surface; the TI
  band can only approximate that.** So eta_1/w and f_b are not physical choices: take them as small as the solver
  tolerates (conditioning, Newton convergence) and report the residual band shear stress as the approximation
  error against zero; kaiju's 1-2 % of the mean yield stress is the starting point, to be pushed down in the smoke.
  SET 2026-10-29 (kaiju proposed, hub accepted): w = W = 0.008; crust factor linear in (1 - M) with M the whole
  band (band | bridge zone), the same mask -uw_fault_precedence uses for the split since eec8682, not the 0.6 w
  footprint; the push-down steps f_b, eta_reg_b and the in-band floor (eta_1 >= 0.1) together by factors of 3,
  since band stress ~ f_b tau_y + eta_reg_b 2V/w, recording band stress (integrated, and as a fraction of the
  host's mean yield at depth), slip, Newton and linear its, Stokes time, stopping when either solve degrades.
  Nothing left for Louis on TI settings. Order: envelope fit smoke, Earth smoke 4 report, then TBti.
  **2026-10-29 hub changes:** TA family instead of TB (TAf and the crust-sampled twin TAc exist; TB has no twin).
  **Library block:** any unsplit placed coarse MG level OOMs the first solve (defect recorded for the dev hub in
  "For the other hubs"); TI runs therefore use -uw_chain 0 (band on the finest level, unplaced coarse tail), with a
  split control at chain 0 (TAf restarted from 40, same steps) so the implementation cost is separated from the
  missing coarse placement (one-step restart from TAf 40: split chain 2 13 GB / 6 Newton / 204 s; unsplit chain 0
  12 GB / 9 Newton / 374 s). TI path (kaiju/ti-band on 07667b2, 53b5218 + d0a22c9, patch with the smoke): unsplit
  placement to 0.5 rung inside the wall; host VP viscosity = eta_0 of a TransverseIsotropicFlowModel; on the
  footprint eta_1 = max(eta_min_b, min(eta_0, f_b tau_y/(2 gdot) + eta_reg_b)); director = nearest segment's
  normal; mask = whole band; slip by velocity-jump probe at +-(w/2 + h); band stress terms recorded separately.
  **TAf_env:** TAf rerun with the envelope locator (6-8 h, one node) approved by the hub for like-for-like physics,
  since TAf's parabola fits failed late; it doubles as the locator A/B on the thermal set. Louis may cancel.
  **Push-down smoke DONE 2026-10-29 (page 7mau5dPymUCYGPYJCCDnME; TAf checkpoint 40, 6 steps per level, chain 0):**
  no-op check exact (TI band off = VP host, vrms to 1e-14, same Newton and residual). Levels (band stress as a
  fraction of the host's mean yield; f_b / eta_reg_b = eta_min_b): L0 1e-2/0.1: 1.2-1.4 %, 13 Newton, 541 s; L1
  3.3e-3/0.033: 0.42-0.50 %, 12.7 Newton, 629 s; L2 1.1e-3/0.011: warm starts failed at 42 and 43, not converged
  (1800 s); L3 3.7e-4/0.0037: 0.05 %, 8-13 Newton, 691 s, all 6 steps (non-monotone, marginal). The f_b term is
  ~70 % of the residual at every level. **L1 chosen** (deepest reliable). Cost, steps 41-46 (Newton / Stokes s):
  split chain 2 one-step restart 6 / 175; TAf as run (other driver) 6.2 / 376; split chain 0 control 7.3 / 351;
  TI chain 0 L1 12.7 / 629: chain 0 costs the split ~1.5x, TI ~1.8x the chain-0 split, mostly Newton. Slip on
  the same probe (+-0.0196): split control 3030-3915 (its node jump 1226-2378 reads lower, the probe takes the
  cells round the cut too); TI L0-L3 4340-7520, 1.6-2x the split, vrms 10-20 % higher: the band weakens a width w
  of material, the split a line plus its bridge. Director check: eta_1/eta_0 median 0.0089, alignment 1.00,
  no loss at the stub kink. **Series applied as f14c1ec, d580732, cd06325, 852c6aa (blobs verified); head 852c6aa.
  TAti GO (hub) at L1, chain 0, envelope, on 852c6aa, one node.** TAf_env running (job 2390). Equivalence
  (TI slips 1.6-2x the split) put to Louis. **Slip-rate profile (kaiju, page v3) REVERSES the width reading:** the
  TI jump is localised (97-99 % within the +-0.6w footprint) while the split's is spread (53 % within +-0.6w, 75 %
  within +-1w; the cut itself takes ~1330 of 2719, the rest is distributed shear in the host on the incoming side
  from -2w to the cut). So a narrower band is not the lever; the TI plane simply passes about twice the motion,
  and the question is what restrains the split (bridge zone, contact constraint, or the weak crust beside the
  band taking the shear). Kaiju asked for the tangential traction on the split faces (zero if truly frictionless;
  else a library finding) and a crust/bridge overlay on the profile by depth band. **TAti RUNNING as job 2398**
  (852c6aa pinned in zg95-tati, L1, chain 0, envelope, precedence 1, pres_rtol 1e-2, checkpoints every 5, from
  step 0, stop_at_base EVERY=5). **Split restraint (kaiju, page v4, offline on the chain-0 control 42-45):**
  geometric, the cut is LOCKED AT THE TOP by the bridge zone. Tangential traction estimate on the faces (2 eta
  t.E.n from each side's own velocity, 0.25w off the cut, eta from the smoothed log10 eta): body 0.04-0.12 deep
  1e-3 to 1e-2 of the host yield (median 1.1-1.3 % against 4.6-9 % in the host 2w away), i.e. close to free; top
  0.04 under the bridge 0.1-1 of yield. Jump by depth band (split / TI L1): below the bridge 2900 / 6607; body
  2203 / 5549; tip 652 / 1735; the split's one-sided host shear is present at every depth and the crust along
  the same normals is the same in both runs (0.3-0.5 particles per probe), so the crust-beside-the-fault guess
  is NOT supported. Mechanism: the bridge's x1e-3 weakening is undone by the global floor (1) and rate
  strengthening (10), as the TI design report found; a crack locked at one end slips less along its length and
  the host takes the rest; the TI band outcrops with its own floor (0.033) and has no lock. **Hub: one-smoke
  test approved behind a flag (bridge-own floor and regularisation, defaults = host, the split unchanged): the
  chain-0 control from 40 with the bridge at the TI L1 values; plus an offline count of how much of each
  faulted thermal run's fault lay in the bridge zone, since a locked top biases those results. The bridge
  rheology for production is then Louis's split-side choice.** **Bridge test NEGATIVE (job 2399, page v5):** with
  the bridge at 0.0333/0.0333 the jump rose only 5-12 % (below bridge 3251 vs 2900; body 2313 vs 2203; tip 704
  vs 652; TI L1 6607/5549/1735), the top-0.04 face traction did not drop, the one-sided shear is unchanged. The
  bridge is not the restraint; the contact constraint is the next suspect. Flag applied as 4aa798c (default
  unchanged). Bridge share of fault length in the thermal set: TAf 20 % (9-25), TA_age25f 19 % (9-23), TBf 19 %
  (9-65; 65 % at 40-50 = the stale near-tangent parabola fault). **Hub asked kaiju for a minimal library probe:**
  a box with one straight split fault, linear host, wall-driven simple shear, np 1 and 4; slip, tangential and
  normal face tractions against the analytic frictionless answer; also with the cut reaching the wall. If the
  contact carries shear it is a library defect with a two-minute repro for the dev hub (#889/#890). **PROBE DONE
  2026-10-30 (page 9Au3HFWLqkHt2geWohQpYa): the contact is FRICTIONLESS.** Unit box, 45 deg split fault a = 0.12,
  linear host, pure shear by the walls' normal velocity (simple shear resolves to zero on 45 deg); peak slip
  0.96-0.97 of the frictionless mode-II crack (0.93 at the measured far stress), identical at np 1 and 4; the
  face shear-traction estimate halves with h (0.21 -> 0.10 of tau_inf), i.e. the O(h) error of the estimate;
  normal traction continuous and equal to the library's reaction. **The annulus restraint is the BURIED UPPER
  TIP:** the library refuses a cut touching the boundary ("only strictly interior faults ... supported"), so
  the split's top tip sits 3 rungs (0.012) inside the wall, its slip tapers to zero there and is lower along the
  whole length, and the host beside it shears to make up the difference; this matches every annulus measurement
  (top traction, half the TI slip at every depth, one-sided shear, bridge test +5-12 %). The annulus face
  traction (~1 % of yield) is within the method's error, not friction. The TI band outcrops. So TI vs split was
  surface-breaking vs buried: **hub approved the like-for-like smoke (TI with -uw_ti_trace_inset 3, chain 0, L1,
  from 40)** and an offline mode-II taper estimate of how much the buried tip cost the faulted thermal runs.
  **Buried-TI smoke (job 2403, page v6): NO MATCH.** Jump over +-2w, steps 42-44 (0.012-0.04 / body / tip): split
  2746 / 2096 / 491; TI L1 buried 3674 / 4066 / 1353; TI L1 outcropping 6340 / 5260 / 1500. Burying removes 42 % of
  the TI excess near the top and 23 % in the body; the buried band still passes 1.3-2.8x the split. It is also
  the hardest variant to solve (15-23 Newton, 620-1886 s; step 41 failed warm and cold; hit its wall in step 45).
  What is left, most plausibly: the tips (the split's slip vanishes at one node; the band ends bluntly with its
  footprint overhanging the trace end by half a rung, a softer process zone) and the band's own through-width
  shear. A narrower footprint/overhang smoke would test the tips (needs a small flag). **Hub: held for Louis;
  the one-comparison brief is served by TAti vs TAf_env plus this characterisation.** Thermal-set bound (mode-II
  taper, surface-breaking fault of length L = interior crack of half-length L by the mirror wall; buried = half-
  length (L - d)/2, a lower bound): buried/surface-breaking mean slip TAf 0.42 (0.40-0.46), TBf 0.43 (0.19 at
  40-50, the stale fault), TA_age25f 0.43; integrated 0.36-0.37. The annulus split/outcropping-TI ratio
  (0.38-0.44) is close to this. **TAti cost (2026-10-30, 2 h 45 in):** step 5; every step converged but 15-23
  Newton (3-6 Picard then 12-18 Newton increments at ~100 s), 1400-2300 s/step, ~45 h to the base; band residual
  0.35 %. Likely cause: hard sympy Min/Max kinks in the band law (eta_1 = max(eta_min, min(eta_0, eta_y))) where
  the host yield uses the library's smooth softmin; chain 0 adds per-iteration cost. **Hub: no 45 h chain.** TAti
  runs to its 12 h wall as the reference; kaiju implements the smooth band law behind -uw_ti_smooth (softmin +
  softplus floor, the host's delta) and compares 5 steps from step 0 on the free node; if slip and vrms match to a
  percent with Newton under ~10, TAti restarts from step 0 on the smoothed law with chained segments; else TAti
  pauses for Louis's equivalence choice. TAf_env fine: step 43, tip 0.69, ~400 s/step, base in ~5 h.
  **Smooth band-law smoke (job 2404, steps 0-4, -uw_ti_smooth 1 = the host's _combine_yield softmin and
  _apply_floor):** physics identical to 1e-5 (vrms, slip, residual 0.348 %); Newton mean 13 vs 19 (-35 %), Stokes
  4940 vs 7173 s (-31 %); step 1 (first solve after the fault forms) still 21 Newton, steps 2-4 at 9-11. ~30 h to
  the base instead of 45. **Hub: TAti RESTARTED from step 0 on the smooth law, chained 12 h segments afterany on
  the last checkpoint, stop watcher; 2398 stopped (its checkpoints kept as the hard-law reference). Reversible if
  Louis's equivalence choice changes the spec. The smooth form should become the TI default once every TI run is
  on it. Patch a00a10b APPLIED as 67dd2c8 (blob 7373694 verified), default off.** TAti_smooth: run dir
  runs/slab_thermal_fault_TAti_smooth, segment 1 job 2405 (n2) from step 0, driver pinned in zg95-tati-smooth;
  chain supervisor kaiju-launch/ti/TAti_smooth_chain.sh detached on the login node (runs stop_at_base EVERY=5 per
  segment, ends at the base, else submits the next 12 h segment from the last complete checkpoint, at most 5
  segments; log chain.log; stop = kill the supervisor then scancel). 2398 cancelled after step 6 (checkpoints 0, 5
  kept; README says why). **TAf_env DONE (job 2390): base at checkpoint 90, stopped after 100 (t 0.000255), 101
  steps, 5.6 Newton, 340 s/step, 9.5 h, no refusals or welds. Locator A/B (page TAUT7fi5cM75zkbna7gm9R):** trench,
  hinge and tip histories nearly overlie TAf (parabola) and TAf_env (envelope); plateness the same (P10 0.088 vs
  0.096; TAc 0.119); t on base 0.000224 vs 0.000235 (TAc 0.000245); but slip median 6243 vs 4200 (late max
  6000-9000 vs 4000-6000) and incoming plate 760 vs 686 (TAc 580): the parabola's late faults were stale or ran
  along the surface and slipped more freely. Dips 31-37 in both. 25 % cheaper per step on the envelope. **The
  envelope run is the reference for the thermal set from here; TAf's slip and plate speed are overstated by
  ~50 % and ~10 %.** Both carry the buried tip (~0.42 of a surface-breaking fault). **TAti_smooth segment 1:** step
  7 at 3 h; steps 0-5 as the smoke; after the rebuild at step 5 (trench +0.3, dip 67) step 6 did NOT converge (19
  Newton, driver carries on) and step 7 took 17 Newton / 1765 s; ~2.7 steps/h, 3-4 segments (36-45 h). Hub's pause
  trigger: two consecutive unconverged steps or more than two in any ten; kaiju to check whether the rebuild
  Picard switch fires on the TI path (a cold Newton on the moved kink would explain the post-rebuild trouble).
  **Checked: the switch fires (step 6: 5 Picard to 9.2e-3, switch at 1e-2, then Newton 9.08e-3 -> 9.02e-3 and
  given up; cold retry the same); Newton stagnates at ~1 % per iteration with 3-14 line-search cutbacks per step
  while Picard converges steadily: an INCONSISTENT TANGENT is the suspect (the TI model's eta_1 depending on the
  resolved shear through the director; #493/#748 covered the frozen-coefficient case). Hub: kaiju runs
  -snes_test_jacobian on the checkpoint-5 TI state (hard, smooth, and the VP host as control) and restarts the
  chain from checkpoint 5 with the Newton switches at 1e-3 (Picard carries the solve nearer tolerance) as the
  workaround. Supervisor v2 with the pause trigger is attached. Parallel non-determinism noted: Newton counts
  differ run to run at equal vrms, a caveat on every cost row. **Louis 2026-10-30: "a regression or a forgotten
  configuration - we know it behaves well."** Forgotten-configuration candidate: the driver's band builds a
  user-written yield into shear_viscosity_1 of the plain TransverseIsotropicFlowModel, whereas the library's TI
  VEP model yields on eta_1 itself with a validated tangent (kaiju's design report noted the model). Kaiju
  redirected: rebuild the band on the library's TI VEP model (f_b tau_y, eta_reg_b, eta_min_b as its yield
  parameters; same director), Jacobian test on hand-rolled, library and VP-host control, 5 steps from checkpoint
  5; and run the library's own yielding-TI example/test on the kaiju build as the regression check. A pass on
  the library model restarts the chain on it; a failure is a regression for the dev hub with the repro and the
  test that should have caught it. **Louis to kaiju 2026-10-30 on the comparison page:** (1) legend incomplete and
  tiny (fixed, page v2); (2) "what we know works is the split plus TI to the surface so the physics is not
  actually as different as you assume. However, I suspect this means we did not add the TI damage to the surface
  correctly"; (3) "all the models seem to do similar things" (kaiju corrected him: that figure is the locator
  A/B, no TI run in it yet). **On (2) the code confirms it: the split's bridge from the cut's top to the surface
  is an isotropic x uw_eta_w zone (undone by the host floor and eta_reg), copied from the library's zg95_annulus
  example, which uses a TI bridge only in linear-viscous runs and falls back to isotropic with yield ("the TI
  model has no yield stress without elasticity"). So NO faulted thermal run had TI damage to the surface; the
  locked top is that isotropic bridge, which re-reads the buried-tip finding (the taper estimate stays as the
  bound).** Kaiju implements -uw_bridge_ti (the bridge painted as a TI weak plane, director from the surface
  stub, yielding as the TI band) behind a flag; hub ordered its smoke to wait for the TI law that passes the
  Jacobian/regression checks, and asked kaiju to find the exact "split plus TI to the surface" configuration
  in the library's scripts/tests (model class, elastic term or not, tangent, floor, regularisation) and use its
  settings as the reference. **FOUND (kaiju, page v3):** scripts/sessions/fault_mg/zg95_annulus.py --arm split:
  plain TransverseIsotropicFlowModel, eta_0 = eta(T), eta_1 = 1e-3 eta_0 on the ladder's cap and last rungs above
  the cut's tip, one constant director, frictionless contact, tol 1e-5, 3 Picard, Newton switch 1e-2, no floor,
  no regularisation, no elastic term, and ONLY without yielding (with --yield0 > 0 it swaps to an isotropic zone;
  "no yield stress without elasticity" means the plain TI model has no yield parameter). A purely viscous
  yielding TI exists (TransverseIsotropicVEPFlowModel is viscoplastic whenever yield_stress is finite) but no
  library test exercises it without elasticity (test_1052 uses elasticity). **Regression check: test_1066 (TI
  tangent oracle) and test_1052 (VEP, TI VEP yield) pass on 547c2e54 (12 passed): NO REGRESSION; the stagnation
  is the configuration, our hand-written yielding eta_1.** Tangent oracle on our cases: the VP host 6.7e-11;
  hand hard / hand smooth / linear eta_1 pending. Running: 2412 the TI band on the library's TI VEP model
  (-uw_ti_model vep; director as a column, 4c09942) 5 steps from TAti_smooth checkpoint 5; 2413 the bridge smoke on
  the reference law (split + -uw_bridge_ti 1 -uw_ti_model linear, eta_1 = 1e-3 eta_0 over the bridge on the
  yielding host), TAf checkpoint 40, chain 0, 6 steps. Local commits b554cf4, 3d82360, 4c09942 on kaiju/ti-smooth
  over 67dd2c8; patches with the results. **RESULTS (kaiju, 2026-10-30):** tangent oracle: VP host 6.7e-11, hand
  smooth band 8.0e-11, linear eta_1 = 0.01 eta_0 1.5e-10 (hand hard still running): the TI TANGENT IS CONSISTENT,
  the stagnation is not a tangent bug. Library TI VEP model (2418): needs the director as a column and a dummy
  timestep (any VE class demands one even at mu = inf), then stalled warm (1.1e-2) and the cold retry started at
  NaN (tau_y/(2 gdot) at rest; strainrate_inv_II_min defaults to 0): dev-hub note. TI band on the REFERENCE
  linear law (eta_1 = 1e-3 eta_0, 2419, from TAf 40): also hard, 7-19 Newton, step 42 unconverged warm and cold,
  slip 5060-7500 like L1: the Newton difficulty comes with a 1e-3-anisotropic band on this mesh, not with yield
  (the reference script's TI was a small constant-director patch on the cap; ours is the whole curved band with
  per-cell DG0 directors). Split + TI BRIDGE on the reference law (2413): step 41 vrms 1181.4 vs control 1182.6,
  slip 1126 vs 1350, clean convergence: **the bridge is NOT the restraint** (Louis's point 2 answered: adding TI
  to the surface changes nothing here; job then hung after checkpoint 41 with "evaluate() is rank-local"
  warnings). **NEW PRIME SUSPECT: the split's per-node contact normals on a curved trace.** Box probes (pure
  shear, a = 0.12, h 1/48; peak slip, |tau|/tau_inf on the faces, sigma_nn): straight 0.2308, 0.21/0.21, 0/-0.01;
  arc default normals 0.2205, 0.30/0.18, +0.03/-0.14; arc smoothed normals 0.2260, 0.22/0.18; kinked (2 x 20 deg)
  default 0.2007, 0.34/0.13; kinked smoothed 0.2200, 0.21/0.18. With per-node normals a non-straight frictionless
  contact is partly locked (one-face shear, a normal-traction jump the contact should not allow); smoothed
  normals restore the straight behaviour (+2.5-10 % slip). The annulus cut is strongly curved (dip ~70 -> 18) on a
  polyline with default normals. Running 2423: the split from 40 at chain 0 with -uw_fault_normal trace (the
  library's smoothed normal of the stored polyline). Local commits b554cf4 (-uw_ti_model vep), 3d82360
  (-uw_bridge_ti), 4c09942 (VEP director column, -uw_ti_model linear), 9974022 (VEP timestep), 42a04fa
  (-uw_fault_normal trace), all default off; patches with 2423. **2423 RESULT: trace-smoothed normals change
  NOTHING in the annulus** (vrms, slip and Newton identical to 0.1 % over steps 41-43): the annulus trace turns
  ~1.3 deg per segment where the box needed 20 deg kinks to lock; the box result stays a library note for kinked
  traces, not our mechanism. **Eliminated:** contact friction, the bridge (isotropic floor and TI), contact
  normals, the tangent, director discontinuity. **Left:** (a) how each realisation ends at depth (deep-tip band
  ratio 2.8x; the footprint overhangs the trace end), (b) a 2-cell band at eta_1/eta_0 = 1e-3 may simply not equal
  a zero-width frictionless crack at this resolution. **Hub approved the decisive box comparison:** split vs TI
  band (unsplit placement, w = W, eta_w, trace director) on the straight-cut pure-shear probe against the crack
  solution, with sweeps of eta_1/eta_0 (1e-2..1e-4) and w (W/2..2W) and a buried-vs-to-the-wall variant; written as
  the reference example (script + README with the analytic answer and pass criterion), the candidate bundled
  example for the fault notes (UWTN 2026-017's claim). **BOX REFERENCE DONE (page Em96SAdVik4gAdhJC5LV7x;
  kaiju-launch/ti/split_probe/fault_realisations_box.py + README):** both realisations ladder-placed as the driver
  does, slip measured the same way, against the crack at the measured far stress, PASS = peak and mean within
  10 %. TI band at eta_1/eta_0 <= 1e-3, w = W: mean 0.96-1.03 PASS (UWTN 2026-017's claim HOLDS); 1e-2: 0.94; w = W/2:
  0.93; w = 2W: 1.15 (too compliant). Ladder-placed split: peak 0.80-0.86, mean 0.87, 10-18 % below the band and
  below the crack, improving with h; a split cut by Mesh.add_fault reaches 0.96, so the LADDER PLACEMENT COSTS THE
  SPLIT 10-15 % (dev-hub note). Wall placement as the annulus (spine through the wall, trace stopped 3 rungs in):
  split 0.78, band 0.91 against the buried crack; a band run TO the wall slips only 6 % more than one stopped 3
  rungs short. **RETRACTION (kaiju): a free-slip wall is not a mirror plane for a dipping fault** (v_n = 0 on
  both sides pins the fault's end, since slip on a 45 deg fault has a wall-normal component), so the "buried tip
  costs the split ~half its slip (0.42)" bound for TAf/TBf/TA_age25f is WITHDRAWN; opening the fault to the
  surface gains little, consistent with the TI bridge changing nothing. Retraction notes on the TI page (v7) and
  the comparison page (v4). **CONCLUSION: the annulus TI-split gap (~2x slip, vrms +15 %) and the TI band's Newton
  cost are SETTING-SPECIFIC** (the yielding T-dependent host beside the fault, the curved hinge, the deep tip in a
  yielding slab; in the linear box both solve in one pass). TAti vs TAf_env over the run is the physics answer.
  **Hub: equivalence investigation CLOSED here; no further smokes.** 2423 finished identical to its control.
  Five-patch series APPLIED as fc491c6 (b554cf4 -uw_ti_model vep; 3d82360 -uw_bridge_ti; 4c09942 VEP director
  column + -uw_ti_model linear; 9974022 VEP timestep; 42a04fa -uw_fault_normal trace; blobs 3961971 -> afab640
  verified; all default off; one hand-typed context line corrected by kaiju). Comparison page v5 carries the
  equivalence paragraph. **TAti_smooth:** segment 2 (job 2407, n2) restarted from checkpoint 5 on the 1e-3
  switches, supervisor v3; step 16 at 3 h 13; 10 of 11 steps converged this segment (step 7 failed, 16 Newton;
  step 6 converged on redo); 1006 s/step, 9-20 Newton; dip 67 -> 33-41, slip 467 -> 1234; ~35 more steps to
  TAf_env's base time, segment 2 ends ~19:43 at ~step 47, a short segment 3 finishes ~21:00-22:00. Supervisor v3
  checks the pause trigger at segment ends only (kaiju checks by hand). Split + TI bridge smoke (2413) hung and
  was cancelled; a rerun is still owed if ever wanted (the box says it will change nothing). **PAUSED 2026-10-30
  19:44 at the segment-2 boundary (reported to the hub 2026-10-31, a day and a half late):** segment 2 reached step
  53 (t 1.7e-4; TAf_env's base at 2.35e-4), newest checkpoint 50; the trigger found 21 unconverged steps (7, 21,
  22, 25, 29-36, 38-43, 46, 47, 51: from step 29 roughly every other step, stopping after 9-19 Newton at 1e-2 to
  5.5e-2 relative; converged steps 11-34 Newton). vrms 515 -> 1409, dip 38-44, trench -0.7 -> -4.0, slip 1234 ->
  ~4500 (+-20 % step to step), dt 4.7e-6 -> 1.9e-6; ~30 steps (~7 h) to the base. **Hub decision: bounded
  diagnosis on checkpoint 50 (Newton switch 1e-4 with more Picard; pure Picard to tolerance; 1e-3 with a cold
  restart on failure; two steps each), then resume today from 50 on the best setting that converges every step
  with the trigger kept, else on the cheapest with the trigger report-only and an unconverged-step column, rows
  caveated.** Process: a supervisor pause is an event to message the hub at once, not at the next boundary.
  **DIAGNOSED AND RESUMED 2026-10-31/11-01 (kaiju):** root cause: the library clamps the Newton switch to
  max(newton_switch_rtol, tolerance) and uw_tol = 1e-3, so the "1e-3 switches" were PURE PICARD, never Newton;
  late in the run Picard stalls at 1.3-1.7e-2 (just above the 1e-2 cold switch), so neither phase reached
  Newton. Variants on checkpoint 50 (2 steps): pure Picard (switch 1e-4 clamped) step 51 NOT converged;
  warm 1e-3 + cold restart into Newton at 3e-2 converged after the retry (1469 s); **Newton switches at 3e-2
  everywhere: both steps converged first time, 13 and 16 its, 616 + 739 s, vrms and slip within 1e-4 of the
  chain's unconverged steps (so those were close to the answer).** Resumed from checkpoint 50 as job 2452 (n2,
  11-01 07:24) with -uw_warm_newton_switch 3e-2 -uw_rebuild_newton_switch 3e-2 -uw_newton_switch 3e-2; ~30 steps,
  ~7 h, likely one segment. Supervisor v4: trigger counts only steps after 50, read every 10 min mid-segment,
  kaiju watching chain.log. Build overlay-leakfix 547c2e54, driver a00a10b. **TRIGGER 11-01 08:54:** steps 61 and
  62 (after the rebuild at detection step 60; steps 51-60 all converged) failed consecutively: warm Newton
  crawled 2.6e-2 -> 2.0e-2 / 1.3e-2, the cold retry stopped after 6-8 Picard its at 0.12 / 0.056, and **the
  driver kept the cold result unconditionally even though it was worse (a bug in FaultedMesh.solve)**; vrms
  1409 -> 1326, slip 6362 -> 3862 at step 61, partly rebuild, partly the unconverged answer. **Hub: stop 2452,
  keep checkpoint 60 (last fully converged); fix = keep whichever attempt ends with the lower residual (default
  on, both attempts recorded); resume from 60 on 3e-2 with the trigger report-only and an unconverged column;
  test cold-into-Newton at 1e-1 on rebuild steps (2 steps from 60) alongside and fold it in at the next
  checkpoint if clean. Audit for the page: every earlier failed step's warm and cold residuals and which was
  kept. Cold retry stopping at rel 0.1 after 6-8 its (line-search-stall exit?) to confirm: a dev-hub note if so.**
  Scaling: B np32 running; -log_view was empty because petsc4py started without sys.argv (fixed in the wrapper
  with petsc4py.init(sys.argv); the dev hub's recipe has the same gap); A/B np16 rerunning. **RESUMED 11-01 as job
  2465 (n2) from checkpoint 60** on driver a00a10b + 5d968c7 (the keep-the-better-attempt fix alone, -uw_retry_keep
  best; "last" = old behaviour), switches 3e-2, supervisor v4 REPORT_ONLY; each record carries "kept" and both
  attempts. Rebuild-switch test (1e-1 on rebuild steps, 2 steps from 60) running as 2467. **Audit:** every
  unconverged step kept the cold retry; in 15 of 20 the cold result was worse than the warm (warm/cold |F| ratio
  down to 0.08: step 25 kept 1.44e-2 over a warm 1.08e-3); warm finals 1.1e-3 to 3.6e-2 (median 1.3e-2), kept
  7.97e-3 to 8.5e-2; the slip see-saw (+-20 %) tracks steps kept at cold rel 4e-2 to 0.12, so part of it is the
  accepted residual, not physics. Full table on the final page. **Line-search stall CONFIRMED:** every attempt
  ends with alpha 0, the rotated loop's not-improved exit (rotated_bc.py:1600), not max_it; e.g. step 46 cold:
  five full Picard steps reducing |F| 3.14e4 -> 2.45e4, one non-improving increment, exit at rel 5.5e-2.
  Patch 1a8387a (fix, default on) to come with the next batch; caveat: the restored info's U may be the solver's
  shared iterate holding the cold answer; the TI path reads only restored fields; a split fault_slip after a
  warm keep is untested. **CLOSED, no code change:** on TAf_env 50 with a forced warm keep (test branch), the
  recorded slip from the kept info's U equals a recompute from the restored fields exactly (4936.814) and differs
  from the cold answer (4914.255); U and the reaction vector are created per solve. No split run in the campaign
  has ever needed a cold retry. **Patch 6691223 APPLIED as ca2eee5 (blob 11ac6d9), -uw_retry_keep best default.**
  Rebuild-switch test (1e-1 on rebuild steps) FAILED: neither step converged and both were worse than 3e-2; not
  folded in. Segment 4 (2465) hung 17 min after reading checkpoint 60 before the mesh build (as 2413 did);
  cancelled; segment 5 = job 2469 (n2) from 60, report-only; step 61 unconverged but the warm attempt kept (|F|
  1.21e4 vs cold 5.22e4). (#457: RESOLVED 2026-10-29: #457 is closed, fixed in #493 and #748, and both kaiju builds, 99259d35 and
  the 547c2e54 leak-fix overlay, contain 22aae82c and 0b6c9624; the "tangent fix first" question drops. Kaiju's
  TI design report corrected. A stale TODO(BUG) comment in the library had misled it: dev hub one-liner below).
- Slab recipe decisions: (1) continue layered_mantle from checkpoint 120 (333 s/step, 12 h buys ~130 steps)?
  (2) try a Picard warm-up on ordinary steps (-uw_warm_newton_switch 1e-2, as rebuilds use) for the layered
  mantle, where ordinary warm steps start at F0 = F_ref and damped Newton crawls (step 17: 26 its, 20 cutbacks)?
  (3) a check run for the crust x1 + fault case with fewer rebuilds (-uw_rebuild_rungs 8)? Kaiju is idle.
- (moved to the notes hub 2026-10-27) the technical-notes judgement items, the workbench tool go-ahead,
  PREVIEW_TOKEN, PR #59 and the hub-push-test deletion.
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
- (moved to DEV-HUB.md 2026-10-29) who takes the parallel `read_checkpoint` bug and the other no-PR fixes.

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
- 2026-10-26: **Louis (via the notes session): the kaiju slab runs go into UWTN 2026-022 as the moving-fault
  demonstration**, the discussion on partitioning and solver efficiency; 2026-022 now precedes 2026-021 in the
  writing order. Hub drafted the section (ebb5a76): the crust-base fault following a retreating trench, four
  300-step runs at np 16 (a split step costs an unfaulted step; 27 rebuilds cost 7 % of the run, 47 cost
  27 %; 1 Newton it per step; no cap hits), the fit's sensitivity, two figures declared; the rebuild leak stated
  as a defect in "What it costs". Kaiju asked for: the add-on mesh at four steps of the 47-rebuild run from the
  solver_mesh checkpoints; wall per step by phase plus cells per process at each rebuild (recorded or
  re-measured at np 16); a per-rebuild cost breakdown (refine / conform+split / partition / solver setup /
  first solve, one instrumented rebuild if needed); records.json and solver_summary.csv for the five runs; all to
  figures_out/addon_demo/ for Louis's rsync and the notes session's copy.
- 2026-10-26: **addon_demo delivered by kaiju** (figures_out/addon_demo/: trench-mesh.png, trench-cost.png, json/csv,
  scripts, records for five runs 0.7-1.9 MB each, README). Mesh figure (recorded): steps 10/100/200/290 of
  B1_crust1_fault, trench -0.9/-10.8/-24.1/-28.9 deg; base edges > 0.1 from the trace identical 100 % at every
  step; the add-on adds 432-566 cells to the base's 126976. Costs (recorded): ordinary step 24.2 s (transfer
  1.6, stokes 14.8, rest 7.9), rebuild step 48.6 s (build 11.6, transfer 2.3, stokes 25.6: the rebuild solve
  starts with Picard). Breakdown (re-measured, 21 builds at np 16): no refinement at a rebuild (placed band);
  conform+split 9.0 s (carve/fill/sew 4.3, new meshes 2.5, cut 1.3-1.5, split 0.5); partition 1.5; solver setup
  4.0 (1.0 constructor, 1.4 compiling, 1.1 transfers); first solve 20 (2.3 fields, 18 Newton). Load (re-measured,
  7 checkpoints): base partition 12x8192 + 4x7168 on every level; finest max/mean 1.03 to step 100, 1.08-1.09
  from 150 when the band sits on a full rank; gather moved 0-102 cells; transfer misses rank-local only; no
  fallbacks. Findings for the library (to hyperion after the leak): adopt_hierarchy's alignment of the base
  levels is superseded by set_custom_fmg's levels (0.8-2 s per rebuild wasted, 7-17 % of the build); the
  solver's functions recompile on every rebuild (1.4 s). Instrumented driver kaiju/addon-timers 6f53c8c
  (-uw_addon_timing, off by default), patch requested for the branch. Cost table confirmed; C1: KSP 5/20,
  12082 s. Note updated locally (held: wombat's push hold on note/faults-on-an-add-on-mesh).
- 2026-10-26: **thermal runs at step 20** (kaiju): the slabs founder from the start and sink faster than B1 (tip
  0.5 by t 0.00013-0.00015 against B1's ~0.0004); the plate moves from the outset (v_plate 700-950; B1 started
  at rest); the hinge moves in the rollback sense (3.6 -> 2.0 deg in 20 steps); the tip curls to the overriding
  side; T_core 0.03 -> 0.13-0.15 (the thin stretched tip, not diffusion); the one-cell crust breaks into blobs
  along the slab top (continuous in B1); plastic strain confined to the trench corner; the hot top does not
  dominate; mantle turning over beside the slab, vrms 370-440. Solver steps 11-20 as 1-10 (4-13 Newton its,
  F0/F_ref 0.55-0.8, pres 40-59, vel 7-10, 160-580 s). Renders in figures_work/slab_control/thermal_*/. Step 50
  in ~3 h.
- 2026-10-26: kaiju's -uw_addon_timing measurement mode pushed as c147c9d (addon_timing.py wraps library calls
  from the driver with an exclusive-time clock; off by default; a restart with -uw_addon_timing N forces N
  rebuilds and writes addon_timing.json). Deviation recorded: the module uses mpi4py directly for its
  allgather/Allreduce; acceptable in a measurement-only module, to be replaced if the library offers a helper.
- 2026-10-26: wombat repaired note/faults-on-an-add-on-mesh (force-with-lease with Louis's OK: 2edfb4e = ebb5a76 +
  the Sandiford_2019 bib entry, which the hub had wrongly said was present) and reviewed the trench section;
  hub pushed 9d5c6c3 (kaiju's measured numbers in prose, captions and alt text) and e73fc7f (one nonlinear
  iteration per step, Newton ordinary / Picard after a rebuild; overhead measured one way, 7 % for 27 rebuilds
  and 14 % for 47, the 27 % stated as the rebuild steps' share; sensitivity cut to mechanisms; the runs named
  demonstrations of the mesh, not a subduction result). Kaiju asked to add a slip panel with rebuilds marked to
  trench-cost.png and the per-rebuild drop ratio to the README.
- 2026-10-26: kaiju's slip panel overturns "a rebuild halves the slip" as a general statement. B1_crust1_fault,
  slip at the rebuild step over the step before, 46 rebuilds: median 1.55, range 0.20-3.52, 17 below 1. Two
  regimes: steps 6-41 (first 8 rebuilds) every rebuild drops it (median 0.43) and it climbs back over ~4 steps
  while slip falls from ~430 (step 3) to ~20 (step 45); steps 141-296 (last 24) a sawtooth the other way, the
  slip peaking ON the rebuild step (1.5-2x, 3.5 once) and decaying until the next. Kaiju's untested reading: a
  rebuild re-fits the fault to the damage and the fit ages between rebuilds; to check against the trace-to-band
  spacing before anyone states it. Note corrected to the measured regimes without the mechanism (e6189fb).
  trench-cost.png now has three panels; trench_cost.json carries the ratios.
- 2026-10-26: **Louis: one run at a different rebuild spacing.** Kaiju launches B1_crust1_fault with
  -uw_rebuild_rungs 8, otherwise identical to the 47-rebuild baseline, and records rebuild count and wall,
  warm-start cost on and after rebuild steps, the trace-to-built-fault distance at every detection, slip
  ratios and sawtooth amplitude, trench retreat and fault geometry against the baseline. Output
  addon_demo/rungs8/ with an overlay figure. The sawtooth is the trade-off between surgery, warm start and
  the fault ageing between fits; a sweep (2, 8, 16 rungs) was proposed and Louis chose one run first.
- 2026-10-26: rungs8 run launched (job 2247, strict A/B on 0fb51f9; run_info confirms driver and uw3 99259d35).
  Steps 0-10 identical to the baseline (rebuilds at 1, 6, 11; slip and vrms to 1e-4; wall the same), because
  every early detection gap (9-17 rungs) exceeds both thresholds; first divergence expected at step 46.
  rungs_compare.py reconstructs from records.json the Hausdorff gap between fitted and built traces at each
  detection (checked: the baseline rebuilt exactly when the gap exceeded 4 rungs at all 59 detections,
  segment restarts included), warm-start cost on rebuild/+1/+2 steps, slip ratios, sawtooth amplitude, trench
  history, geometry. Caveat: a segment restart always rebuilds, so rungs8's leak restarts add rebuilds; reported
  separately. Baseline reference: 47 rebuilds, 8471 s, rebuild steps 2290 s (mean 48.7); Stokes per step
  rebuild 25.7 / +1 17.9 / +2 15.7 / ordinary 13.6 s; velocity its 6.2 / 4.9 / 3.9 / 3.3 (the warm-start cost
  is in the linear iterations and the Picard step, not in nonlinear iterations, all 1 at F0/F_ref ~1); gap at a
  triggering detection median 6.6 rungs (4.1-18.5); slip ratio median 1.55; sawtooth amplitude median 0.89.
- 2026-10-26: wombat's second review of the trench section (phase bands vs breakdown, 24 s vs 19-25 s, per-level
  cell counts, 24th rebuild, "peak slip rate" and 46 vs 47) fixed in d41d224.
- 2026-10-26: **thermal runs at step 50** (kaiju): the slab founders in about half B1's model time (tip at the base
  by t ~0.0003 against 0.0007; TA_age25 tip 0.95 at step 60) but sinks as a straight radial slab with the plate
  conveyed into it (v_plate 1800-2350 at t 0.00025, B1 210 at the same t), hinge retreat 3.4 deg against B1's
  4.6 over t 0.00025. T_core 0.13 -> 0.18-0.19, cold mass growing as the plate feeds in; the one-cell crust
  stays in blobs down the slab top with a plastic-strain band below the trench; the hot top does not dominate
  (mantle cells beside the slab, vrms 700-850 vs B1 330). Solver steps 21-50: TA 8-11 Newton its, 280-440 s;
  TB 8-17, 340-640 s; TA_age25 5-12, 170-460 s; pressure its down to 32-42, velocity 7-10; yielded fraction
  unchanged; dt ~3.4e-6; the wall ends near step 110-120 (t ~0.0005). Renders in
  figures_work/slab_control/thermal_*/ (steps 0-50 every 10).
- 2026-10-26: Louis: the thermal slab should drive the plate; rollback is not the target. Thermal runs continue
  unchanged; kaiju leads its reports with plate velocity, descent and the solver record. Watch item: the crust
  blobs against the crust-base fault fit, to be smoked before a faulted thermal run.
- 2026-10-26: **rungs8 complete** (kaiju, strict A/B on 0fb51f9; two segments, restart at 151 at match distance
  0, its forced rebuild excluded). Rebuilds 47 -> 29 (-38 %), wall 8471 -> 7639 s (-9.8 %), rebuild-step wall
  2290 -> 1402 s, mean rebuild step 48.7 vs 48.3 s; identical to step 45, diverging at 46. Warm start per rebuild
  unchanged (Picard 1; vel KSP 6.2/6.0 on the rebuild, 4.9/5.0, 3.9/3.7, ordinary 3.3/3.0; Stokes 25.7/24.9,
  17.9/17.4, 15.7/15.0, 13.6/12.6 s; pressure 15.2-15.7 throughout; every step 1 nonlinear iteration at
  F0/F_ref 0.99-1.00). Ageing: gap at a triggering detection median 6.6 vs 10.6 rungs (0.026 vs 0.042); over
  all 59 detections 5.6 vs 7.7; slip ratio at a rebuild 1.55 (n 46) vs 1.65 (n 28); sawtooth amplitude 0.89 vs
  0.81; slip_max mean over 150-299 39.6 vs 41.5; trench at 299 -28.96 vs -28.93 deg, largest difference 0.40
  deg at step 260; depth at the 0.15 cap throughout; dip at rebuilds median 87.9 vs 84.6. Reading: the baseline
  rebuilt more often than the slab needed; the sawtooth is set by the ageing between fits, not the frequency.
  In the note (figure rebuild-spacing.png from overlay.png). Louis has asked kaiju directly for denser crust
  particles (-uw_crust_ppc) with an optional plate-surface top-up (-uw_crust_refill_every), off by default.
- 2026-10-26: **pen on 2026-022 passes to the wombat workbench**: Louis updated CONTRIBUTING.md "How the notes read"
  and asked wombat to rework the note to it. The hub makes no edits to the article, captions or metadata until
  wombat says so; numbers and corrections go by message, figure material only under figures/src/.
- 2026-10-26: **densely SAMPLED crust pushed** (9c7c1e7; particles per cell, no change to buoyancy or any material property; kaiju at Louis's request): -uw_crust_ppc N seeds the crust layer on
  its own lattice (~N per cell) at -uw_init slab; -uw_crust_refill_every K tops up the plate-surface crust where
  it has thinned. Smoke 1 (TA + ppc 12, refill 2, np 16, 6 steps): crust particles 15485 vs 4015, swarm +3 %,
  advection +0.2 s/step, refill a no-op until the crust thins. Smoke 2 (TA checkpoint 50 + FAULT flags, 6
  steps): the crust-base fit works on the thermal crust, which is a coherent particle line; the "blobs" were
  the per-cell P1 proxy at 0.5 where cells hold 0-1 particles. F0 at -2.1 deg, dip 34 (the hinge is a broad
  bend above the 0.15 cap), rebuilt at 52, retargeted at 56; slip 3754-4816, vrms 770-1006, Newton 8-13,
  500-850 s/step. **Caveat**: crust weakening reads that proxy, so the uniform-swarm thermal runs (TA, TB,
  TA_age25) carry a weak layer broken where the proxy is; -uw_crust_ppc keeps it continuous. Louis decides the
  faulted thermal cases and whether the running thermal set should be redone with the densely sampled crust.
- 2026-10-26: wombat's rework of 2026-022 to the updated "How the notes read" is drafted on the workbench
  (unsaved, under Louis's review; hub edits held): four figures kept (stack, iterations, trench-mesh,
  trench-cost), moving-fault.png and rebuild-spacing.png dropped with their numbers kept in the text (the
  rungs8 records still ship in figures/src/rungs8/); the restart material and its table moved to an
  appendix; the cost shares separated (14 % = the 47-rebuild run's rebuild extra over its own wall, 1174 of
  8471 s; 7 % = the 27-rebuild run against the no-fault run, 6 % of its own wall, 519 of 8324 s); alt texts
  unchanged with kaiju's numbers.
- 2026-10-26: Louis: "dense" in the crust change means particles per cell, not a physical density affecting
  buoyancy. HUB wording tightened; the driver's option comment already says particles per cell.
- 2026-10-26/27: **rebuild leak fixed on hyperion** (bugfix/faulted-rebuild-leak 547c2e54): a dropped faulted mesh is
  freed, serial and parallel; growth per rebuild on the 20-rebuild fixture 53.7 -> 0.1 MB (np 1), 56.0 -> 0.1 MB
  (np 2), matching kaiju's constant 7 GB/node per rebuild. Causes: the default Model's mesh and solver
  registries held strong references (now weak; mesh variables stay owned, purged when their mesh dies); SymPy
  caches held coordinate symbols that held their mesh (now weak); mesh variables kept their constructor
  arguments including the mesh (discarded once used); in parallel petsc4py never ran its collective cleanup of
  freed PETSc objects, so a new mesh now runs it on its own communicator. Regression tests test_0077 and
  parallel/test_0078 (39.6 MB per rebuild before). Kaiju asked to build overlay-leakfix and run a 30-step
  A/B against the baseline at np 16 (records to tolerance, RSS flat, step times) before it becomes the
  production overlay. The fix touches core library behaviour (registries, caches, PETSc cleanup), so it
  needs the adversarial review and the tier-A suites before a PR; the review also decides whether the
  collective cleanup inside Mesh construction is safe for meshes on sub-communicators. Hyperion is going back
  to the coarse-solve design.
- 2026-10-27: **leak fix validated on kaiju; overlay-leakfix is the production overlay for faulted runs.** Two
  30-step restarts of B1_crust1_fault from checkpoint 150 at np 16, overlay-leakfix (547c2e54) against
  overlay-warmdiag (99259d35), same driver 0fb51f9, run side by side: slip within 6.3e-10, vrms 4.8e-12, events,
  rebuild kinds, Newton and KSP its identical at every step. RSS per node at the rebuild steps 151-176: leakfix
  13.6 -> 18.5 GB (jumps +2.7 once after the restart, then +0.49, 0.00, 0.17, 0.08; ~12 MB/rank, plateauing),
  control 16.3 -> 50.5 GB (+6 to +7 per rebuild). Time: 30-step totals 879.9 vs 886.2 s; mesh build +0.3 s
  (3 %) for the collective cleanup, invisible per step. A 300-step faulted run no longer needs memory segments.
  **Finding on restarts, corrected by kaiju 2026-10-27**: a segment restart that lands on a rebuild differs from
  the uninterrupted run by a factor 2 in slip_max at step 151 (8.83 vs 17.99) at 5e-4 in vrms, shrinking over
  the following steps (slip within 20 % at 162, vrms within 0.5 %). The driver already does the right thing
  (restores V,P onto the checkpoint's own mesh at match distance 0, then the ordinary rebuild path; the two
  overlays agree to 6e-10, so it is deterministic). It is the section-5 restart drift, the Stokes solver's own
  state that a restart cannot rebuild (~5e-4 in vrms), shown by a one-Picard rebuild solve at uw_tol 1e-3 in
  the most sensitive quantity. Written into RESTART_AND_RECORDS.md §5 as a known limitation (2a4b21a):
  compare across a segment restart in vrms, events and trench history, not in slip_max at single steps. The
  library question (solver-side state) is hyperion's determinism probe. NOT a driver item.
- 2026-10-27: thermal runs hit the wall at 02:03 (TA 143, TB 131, TA_age25 161) and restarted unchanged from 140,
  130, 160 (jobs 2260-2262).
- 2026-10-27: **Louis: memory leak fixes are important to propagate; make it a priority.** Hyperion told to take
  bugfix/faulted-rebuild-leak to a PR against development ahead of the coarse-solve design: cherry-pick the fix
  onto a development-based branch (the box-faults-warm copy stays for kaiju's overlay), confirm the two
  regression tests fail before and pass after on development, tier-A serial and np 2/4 plus the parallel
  suite, the adversarial review (collective PETSc cleanup in Mesh construction on sub-communicators; consumers
  of the Model registries' strong references), then the PR with the fixture and kaiju numbers and the review
  posted. The laptop told to build its dev environment from 547c2e54. Kaiju already runs it for faulted work.
- 2026-10-27: **Louis: technical notes and documentation move to a separate hub.** This hub stops coordinating
  the notes repo (branches, reviews, workflow, Louis's judgement items); the notes section and table are frozen
  as hand-over state. Compute-side figure production on hyperion and kaiju remains requestable here; the open
  compute items for the notes are hyperion's (i) shipped records for fig_iterations and (j) the global peak
  slip at np 8 for 2026-022, and the three 2026-018 figures (parallel-pipeline, load-per-processor,
  band-through-the-boundary), all queued behind the leak-fix PR. The wombat notes sessions are told.
- 2026-10-27: **hyperion reimaged tonight, offline 12-24 h from ~30-60 min after 2026-10-27 (Louis).** Hyperion told
  to shut down cleanly: nothing new; commit and push everything (WIP included) in every worktree and confirm no
  unpushed commits; write scripts/sessions/HANDOVER-2026-10-27.md (branches and heads, leak-fix PR state, coarse
  solve state, queued items, non-git material on /mnt/data, the env recipe) and push it; final transcript
  message lists pushed heads for the hub to verify. The leak-fix PR to development pauses where it stands;
  kaiju runs the fix as overlay-leakfix meanwhile and nothing in production depends on hyperion. After the
  reimage: Louis recreates /mnt/data/lmoresi if the second drive did not survive; the hub walks the new
  session through the "Machines and roles" recipe (pixi env dev, caches and env vars on /mnt/data,
  OMP_NUM_THREADS=1), the hourly ~/.claude mirror and the Simulations symlink still await Louis's approval.
- 2026-10-27: the laptop's faulted-annulus environment is on underworld3 547c2e54 (bugfix/faulted-rebuild-leak;
  env amr-dev, run scripts repointed). Smoke on the B1 checkpoint (step 60, 4 ranks, 3 steps, F0 formed and
  rebuilt): step-63 checkpoint fields bit-identical to the previous library (c1107957, feature/box-faults, so
  the switch also brings the rotated-solve residual reporting). The laptop moves to development when
  hyperion's PR merges.
- 2026-10-27: Louis: the /mnt/data backup is running; that disk becomes the new root partition, so hyperion's data
  returns at a different path. Hyperion asked to list every absolute-path dependency in its hand-over file (pixi
  env, cache and TMPDIR variables, ~/.bashrc lines, Simulations, worktree .git paths, the rescue directory).
  The "Machines and roles" recipe is marked pre-reimage.
- 2026-10-28: **thermal runs, second segments complete** (kaiju): TA to 255, TB 246, TA_age25 266 at the 01:11 wall, no
  failures, every step converged; third segments from 250/240/260 (jobs 2263-2265). At the latest checkpoints
  (t 0.0011-0.0012): the slab reached the base at step 70-80 (t 0.0003-0.0004) and lies along it, spreading
  toward the overriding side (crust 63-73 deg along the base); the plate keeps driving (v_plate peaked
  1800-2350 at 40-50, fell to ~600 when the slab hit the base, now 720-1060), hinge moved only 5-6 deg, the
  steep part below the trench (dip ~80) continuously fed, T_core 0.21-0.25; cold mass peaked 0.030-0.032 at
  120-150 and is 0.016-0.025 as the draped slab warms; hot plumes rise on both flanks of the spreading slab,
  one nearly to the surface on the overriding side (TA 250) where the hot top offers no lid; vrms 480-590.
  Solver segment 2: Newton median 9-10 (4-18), 340-410 s/step median, cutbacks 5-6, pressure KSP 38-41.
  Movies refreshed in figures_out/slab_movies/thermal_*.mp4; renders in figures_work/slab_control/thermal_*/.
- 2026-10-28: **Louis: the thermal runs are scientifically fine; run a similar set with the fault in place** to see
  whether it changes the surface velocity, the surface plateness and the rollback rate (faster rollback would
  help the fault-infrastructure demonstration). GO to kaiju: TAf, TBf, TA_age25f with -uw_crust_ppc 12
  -uw_crust_refill_every 5 and the FAULT flags, plus TAc (TA with the crust sampling, no fault) as the fair
  twin, since TA's weak layer was broken by the proxy; fresh -uw_init slab, np 16, 300 steps, overlay-leakfix,
  driver 2a4b21a, hot top unchanged for comparability. Metrics per checkpoint for all seven thermal runs:
  v_plate, a plateness measure (kaiju proposes and states it), hinge position and rate, tip depth; faulted
  runs add fault geometry per rebuild, slip_max and the solver record. The redo-with-sampling decision is
  thereby settled: TAc is the one redo, as the control.
- 2026-10-28: faulted thermal set launched on kaiju (jobs 2277-2280, 12:27), 300 steps, np 16, 12 h wall,
  overlay-leakfix, driver 2a4b21a in its own pinned clone; the original thermal runs' third segments
  (2263-2265) continue on n2-n4. Steps 0-10 report next, then at each wall.
- 2026-10-28: Louis proposes a continental crust region over part of the hot top on the overriding side (buoyant,
  strong; "similar physics from the mantle point of view but a more justifiable cause"). Design requested from
  the laptop against the driver's existing over marker; no run yet.
- 2026-10-28: **continent design from the laptop** (driver 2a4b21a). The `over` marker already exists on the crust
  swarm, independent of the slab marker: a surface layer uw_over_comp_thick (0.1) thick from uw_over_gap behind
  the trench to uw_ridge_over; it multiplies viscosity AND yield stress by uw_over_eta and enters the body force
  as a temperature DEFICIT uw_over_dT (positive = denser), gated off for negative values; no thermal state (the
  hot-top Dirichlet still holds above it); advected, checkpointed, re-seedable at a restart. Smallest change:
  allow uw_over_dT < 0 (buoyant); new uw_over_extent (arc length from uw_over_gap; 0 = to uw_ridge_over);
  new uw_over_lid (1: the hot-top window excludes the continent, surface T 0, slab-state age uw_age_over flat
  under it with tanh edges; the lid grows over ~100 steps on a restart). Interactions: crust and continent never
  overlap at seeding; the crust law takes its trace from crust particles only; for the line/rate laws add a
  refusal of candidates whose trench angle lies inside the continent; mobility and lid-depth metrics stay
  comparable only for a small continent, else split the wall integral into oceanic and continental arcs.
  Cost: <1 % of a step; laptop smoke 4 ranks, 12 steps, ~25 min (needs the exact TA flag line from kaiju,
  requested); a TA + continent run costs the same as TA on kaiju.
- 2026-10-28: Louis: the subducting plate is thermal plus a thin crust that is weak only (x0.001 on viscosity and
  yield, no buoyancy); that is very weak, and faulted models need not have it so weak: a crust-strength sweep
  (x0.1, x1) with and without the fault is the next test after the current faulted thermal set. A buoyant crust
  (signed deficit on the crust marker with an eclogite-style depth cut-off) was offered and not taken up.
- 2026-10-28: faulted thermal set, steps 0-6: fault formation clean in all three (F0 at -0.4 deg, dip ~47 on the
  straight initial slab, depth 0.150, 61 points; first rebuild 12 s; TA_age25f re-targeted at step 5 to dip 55);
  slip 900-1300 from step 1; vrms 480-545 against TAc's 410-460 (the fault decouples the plate); step 0 identical
  to TA, TAc reproduces TA's step 0. Cost: rebuild steps 3-7 its (Picard start) 280-730 s; ordinary warm steps
  15-23 its, 1300-2200 s (the Newton crawl, twice as bad with the fault's jump in the plate); TAc 7-15 its,
  ~500 s. Decision on -uw_warm_newton_switch 1e-2 put to Louis.
- 2026-10-28: **Louis: the faulted set must be quicker; finalise soon.** GO to kaiju: stop 2277-2280 at checkpoint
  10, restart all four with -uw_warm_newton_switch 1e-2, everything else identical; report after 5 steps
  (its, s/step, projection, continuity across the restart) and, if still slow, where the time goes and the step at
  which the thermal set's interesting phase ended, as a candidate stopping point.
- 2026-10-28: Louis: stop the faulted thermal set once the slab is on the base; a restart can continue it. Kaiju
  told: run each to the first checkpoint after tip depth 0.95 plus one interval, full checkpoint, then the
  comparison figures (v_plate, plateness, hinge, slip, solver record) over the common window against TAc and TA,
  and the per-step cost before and after the Picard switch in the README.
- 2026-10-28: Louis asks whether the mesh (h 0.0156 uniform, set by the one-cell crust, ~8 cells across the plate)
  is needed for the TBL, and whether the 40-60 pressure iterations per increment come from an inner tolerance
  too tight for a 1e-3 nonlinear solve (the notes record the Schur rtol as 0.033 x tol). Kaiju reports the
  mesh numbers and the solver settings and runs a tolerance A/B on two free nodes. Runs use 16 of 52 cores per
  node because of the coarse-solve null-mode limit (hyperion's item, paused).
- 2026-10-28: Louis agrees with the graded refinement of the base and asks for mesh relaxation of the coarse base
  to remove the triangle artefacts of regular refinement visible in the whole-annulus movies. Design and
  implementation to the laptop (driver owner): graded coarse gmsh base, relaxed before the hierarchy is built so
  the FMG levels stay nested and the fault ladder's placement is unchanged; the one-cell crust keeps h at the
  surface; old checkpoints need not reload on the new base.
- 2026-10-28: **Picard switch applied to the faulted thermal set** (TAc stopped at 20 -> job 2302; TAf at 10 -> 2304;
  TA_age25f at 10 -> 2303; TBf hands over at its step-10 checkpoint; all at match distance 0; flag in ARGS, READMEs
  record the handover). Faulted ordinary steps ~3x faster: TAf 4-8 its, mean 407 s (was ~1300); TA_age25f 4-8
  its, 420 s (was 1000-1800); TAc 5-6 its, 317 s (was ~480). Nonlinear its now equal the twin's (5.5 vs 5.8);
  the remaining 1.3x is per iteration (75-85 s vs 52 s), in the linear solves on the faulted mesh plus a rebuild
  every 5 steps (11 s); kaiju splits it into velocity/pressure KSP at the step-20 checkpoints. Continuity across
  the restart: vrms 498.9 -> 500.0 (TAf), 421.9 -> 438.8 (TA_age25f, mid-swing), 536.9 -> 565.3 (TAc, rising);
  slip carries the documented restart sensitivity. Faults re-target at the broad-bend shallow dips (34, 38).
  Projection: to the stop point (step ~90-100) ~10 h, one wall segment; even to 299 ~33 h, so the stop at the
  base is a content choice (the unfaulted set's plate velocity recovered by steps 150-200 if that phase is
  wanted). Tolerance A/B (jobs 2312 current, 2313 pressure rtol 1e-3) running; third variant waits for a node.
- 2026-10-28: kaiju answered the cost questions (see Waiting on Louis): pressure rtol 1e-4 is tighter than a 1e-3
  nonlinear solve can use; 1e-3 saves 28 % of Stokes time and 1e-2 47 % with the same answer; the mesh is uniform
  h 0.0156 (7.7 cells across the plate), refinement 4 too coarse, linear radial grading available now, a
  lithosphere size field not. -uw_pres_rtol patch and a faulted 1e-2 check requested; the running set unchanged.
- 2026-10-28: the laptop lid-regime session (session_019aromUkeWWPzcL2Kb8365E) is INACTIVE: a follow-up on the
  graded base (Annulus grades only linearly in radius via cellSizeOuter/cellSizeInner; refinement 4 too coarse;
  -uw_pres_rtol coming) could not be delivered. The continent design request and the graded/relaxed base brief
  were delivered earlier and are its open tasks. Resend the follow-up when the session is back or a new one is
  named.
- 2026-10-28: -uw_pres_rtol and -uw_vel_rtol pushed (b99c323 on the branch; kaiju's 762c5e7 re-recorded by git am): the Schur pressure KSP tolerance of the
  rotated solve settable from the driver; defaults unchanged (0.1 x tol) until Louis rules. Faulted 1e-2 check
  queued on kaiju for a free node.
- 2026-10-28: **faulted pressure-tolerance check** (kaiju, jobs 2324/2325, TAf from checkpoint 20, 10 steps, np 16,
  overlay-leakfix, Picard on, driver tree b99c323): -uw_pres_rtol 1e-2 against the default 1e-4: nonlinear its
  identical step by step (72 in 10 steps, Picard 4-6), pressure its 46-57 -> 19-22, velocity 7.3-8.6 both, outer 1,
  converged (rel_final 3.6e-4 both), Stokes 5104 -> 2175 s (-57 %), answer within 7.1e-6 in slip_max and 3e-6 in
  the bulk metrics, events identical. The fault's extra cost was the Schur solve (52 vs 37 its at the default);
  at 1e-2 a faulted step (218 s) is cheaper than the unfaulted twin at the default (317 s). Recommendation
  1e-2 for everything that follows. Stop-at-base watcher running on the faulted set (tips 0.48 at step 20,
  TAc 0.74 at 40).
- 2026-10-29: **faulted thermal set stopped at the base** (kaiju): TAc 80, TA_age25f 90, TAf 100 (t ~0.00025-0.00027),
  TBf restarted from 90 to finish ~110. Character: the fault changes the dynamics: vrms 1300-1580 in the faulted
  runs at steps 40-60 against TAc's 560-740; slip_max 6000-8600; the stored dip 18-19 is the parabola's surface crossing, not the placed fault (see the crust-fit item); the trench
  retreats (TA_age25f -8.2 deg by step 90 against TAc's -4.8 at 80), the rollback Louis said would help the
  demonstration; plateness P10 0.06-0.12 during the descent in all runs (TA recovers to 0.6-0.7 once its slab sits
  on the base). Solver before/after the Picard switch: TAf 14.0 its, pres 56, 1225 s -> 6.2, 44, 418 s; TBf 15.7,
  56, 1551 -> 7.6, 52, 636; rebuilds TAf 9, TBf 6, TA_age25f 12. Wall time now set by the shrinking dt
  (~1.8e-6 vs 4.5e-6) as the faulted flow speeds up.
- 2026-10-29: **faulted thermal set complete and delivered** (kaiju). Louis's question answered: the fault makes a
  material difference to surface velocity and rollback, not to plateness. TAf vs its twin TAc at t 0.00024:
  plate speed median 760 vs 594 (+28 %), peak 938 vs 736; hinge rate -4.9 vs -2.6 deg per 1e-4 t (1.9x), trenches
  8-11 deg retreated at the stop vs 4.8; base arrival t 0.00022 vs 0.00024; plateness P10 ~0.10 in both, med/max
  0.25 vs 0.32 (the fault speeds the near-trench part most). TBf, TA_age25f same pattern (TBf peak 1123, 1.7x TB;
  hinge -5.0 / -4.1 vs -1.5 / -1.2). The crust sampling alone matters: TAc beats TA (base 0.00024 vs 0.00031, hinge
  -2.6 vs -1.5), so the fault effect is measured against TAc. Fault: forms at -0.4 deg dip 47; the stored dip 18-23 by steps 40-60 is the parabola's near-tangent
  surface crossing, not the placed trace (which starts at the trench); depth at the 0.15 cap, slip_max peak 8000-9000 at
  t 0.00017 settling 5000-7000, 11-12 rebuilds per run. Cost after the Picard switch: TAf 6.2 its / pres 39 /
  371 s, TBf 8.0 / 38 / 525, TA_age25f 6.0 / 38 / 320, TAc 6.0 / 34 / 224; a faulted step ~1.5x the twin
  (rebuilds + 15 % more pressure its), which -uw_pres_rtol 1e-2 would mostly remove. Plateness measure: P10 and
  med/max over the plate surface from 170 deg behind the trench to 5 deg short of it. All runs end on complete
  checkpoints; restarts possible for the post-arrival phase.
- 2026-10-29: Louis: kaiju results are hard to view except through the Claude app, so every report of results from
  kaiju must come with an artifact. Standing rule added; kaiju told to publish one for the faulted thermal set
  (movies and figures) and one each for slab_control, slab_fault and addon_demo. Existing artifact:
  fault_B1_crust1_fault movie https://claude.ai/artifact/DJctapP4niLphKaazzJeK9.
- 2026-10-29: the artifact rule extends to hyperion and any server the hub runs as a pseudo-scheduler; the exception
  is collaborative editing (notes, documents, code), done interactively on the laptop. Hyperion is told when it
  is back.
- 2026-10-29: faulted thermal set artifact published by kaiju: https://claude.ai/artifact/NJCoW6npE4kr4D5yXfbqVR
  (headline, comparison table at t 0.00024, four whole-annulus movies to each stop, overlay.png, solver.png).
  Movies also in figures_out/slab_movies/thermal_fault_*.mp4 and thermal_TAc.mp4. Backfill pages for slab_control,
  slab_fault and addon_demo to follow.
- 2026-10-29: Louis: the rollback experiments should follow the policy that examples are scaled and non-dimensionalised
  by the units system at the solver level; do not re-run, but check that a scaled version works, with plate
  velocities in cm/yr. Kaiju (idle) tasked: a scaled mode behind a flag in annulus_faults.py with reference scales as
  quantities, dimensionless numbers derived and printed, physical columns in the records, verified against the
  dimensionless TA to round-off over 5 steps at np 4, plus a conversion table of the faulted-set headline numbers
  (illustration: d 2900 km, kappa 1e-6 give one velocity unit ~1.1e-3 cm/yr, so v_plate 760 ~ 0.8 cm/yr and
  t 0.00024 ~ 64 Myr). Any hand non-dimensionalisation the driver is forced into is a library finding.
- 2026-10-29: kaiju (now titled "kaiju: rollback experiments"): velocity-ring movies added to the faulted-thermal
  artifact (v2): surface horizontal velocity as a ring, trenchward positive, 6000 drawn at 0.2 d; the plate
  (700-1100) is a small offset, the big trenchward signal is the hot overriding surface drawn into the corner
  flow. Renderer patch (-uw_vring H, -uw_vring_vmax; off by default; a7d339a on f46eaa3, the branch's renderer
  is unchanged since) requested again: the patch body was missing from the message. **Why the stronger plate
  (TBf) looks like TAf**: the yielded fraction is identical in all four runs (0.014-0.015 / 0.034-0.036) because
  tau0 and tau1 were scaled with Ra by the same deta^0.25, so the yield/buoyancy ratio is common; a larger deta
  stiffens the unyielded core, not the yielding plate. A more rigid, lower-strain-rate plate needs a higher
  tau/Ra or less strain weakening (uw_weak_min). Louis is discussing that test with kaiju directly.
- 2026-10-29: velocity-ring renderer option pushed (20b50e8; renderer blob identical to kaiju's a7d339a): -uw_vring H
  draws the surface tangential velocity as a ring outside the outer wall on whole-annulus strain frames, trenchward
  positive, -uw_vring_vmax at height H; off by default.
- 2026-10-29: kaiju published the backfill artifacts (slab_control, slab_fault, addon_demo) and an unfaulted-thermal
  movies page; an Artifacts index is now a section of HUB.md. The slab_fault README's "each rebuild roughly halves
  the slip" corrected in the committed copy on zg95-annulus-for-kaiju (two regimes, median 1.55 over 46 rebuilds);
  kaiju to fix its figures_out copy.
- 2026-10-29: Louis asked kaiju directly for an Earth-like public demonstration setup (670 km viscous layering,
  a continental block over 1/3 of the overriding side in place of the hot top, the ridge fixed at 9 o'clock as a
  T = interior patch); kaiju has it on kaiju/earth-setup with a 10-step smoke running. The laptop's continent
  design (buoyancy sign gate, |dT| 0.5-0.7 to out-float the lid, own cold surface, fault-law exclusion, split
  wall integrals) passed to kaiju. The continent task is closed on the laptop; the graded/relaxed base is
  unassigned.
- 2026-10-29: Louis: redo the add-on-mesh movie for demonstration from a strong-plate checkpoint with rollback
  established, the fault updated every timestep, ~30 frames, smoothly evolving meshes, the background (window)
  fixed so the untouched base mesh is evident. Kaiju tasked (TBf checkpoint proposed; flags to force a rebuild per
  step; checkpoint every step; fixed window; artifact).
- 2026-10-29: Louis: one comparison run with the TI-in-the-ladder fault (non-linear weak rheology) against the split
  fault, on rollback numbers; the fault weakness takes precedence over the crust weakening, and how the two combine
  in the slipping-fault case is itself unclear. Kaiju to report the driver's TI realisation and rheology, how crust
  and fault weakening combine today in both realisations, a precedence mask, equivalence settings (2026-017: band
  strength is eta_1/w; eta_1/w ~0.1 matched a frictionless split), and a run plan (TBf's setup); Louis decides
  the settings before the run.
- 2026-10-29: kaiju's TI-fault design report (see Waiting on Louis). Notable: the split's `zone` docstring calls it a
  TI zone but it is isotropic weakening; crust and fault weakening multiply (bounded by the floor); the TI tangent
  issue #457 biases cost comparisons; no test solves TI with rotated free-slip walls, so a smoke on one TBf state
  comes first. Louis decides settings before code is written.
- 2026-10-29: Earth-setup patches pushed (8eb5644 + e5f661c; the second applied after kaiju corrected a hand-copied
  line; tree equals kaiju/earth-setup). Smokes: earth_smoke (slab 0.35, neutral continent net heavy with its lid,
  10 steps, vrms 60-67, 3-6 its, 100-180 s) and earth_smoke2 (slab 0.2, continent -0.5 buoyant, 20 steps, vrms
  39-72, 1-3 its, 35-85 s). The x30 lower mantle slows the whole circulation ~7x. Choices listed for Louis.
- 2026-10-29: kaiju: Earth clone at e5f661c; crust/continent overlap check clear (0 shared particles, min distance
  0.073 -> 0.046 over 19 steps) but the continent is drawn toward the trench (3.7 -> 0.9 deg) and will reach it
  in a longer run, where its x100 would compound with the crust factor; a precedence rule is needed there too.
- 2026-10-29: Louis rules on the Earth setup: continent not stronger (buoyant, weak or neutral composition, strong
  only thermally); fault rheology always wins; crust and continent at depth have mantle rheology but stay tracked;
  weaken the upper mantle (asthenosphere channel, lithosphere anchored) instead of stiffening the lower mantle.
  Kaiju tasked.
- 2026-10-29: Earth patch 1/2 pushed (fault precedence -uw_fault_precedence 1, DG0 band mask zeroing crust, continent
  and slab factors in the band and zone; -uw_marker_rheo_depth D with tanh fade; both off by default; blob e2d2595
  as kaiju's). Patch 2/2 (-uw_scaled, the units check, rebased) awaited. Smoke 3 results above.
- 2026-10-29: Earth patch 2/2 pushed (9359128): -uw_scaled (units mode; off by default; blobs fb70d26 /
  0b0e4f9 / 53cf376 as kaiju's). Units check and library findings recorded under Waiting on Louis. Note the
  check-only -uw_units_dt_local path uses mpi4py directly (measurement code, as with addon_timing).
- 2026-10-29: demo movie: the first attempt (TBf from checkpoint 80, rebuild every step) built only 5 meshes in 30
  steps because the crust-base fit FAILED at 26 of 30 detections ("no slab top reaching the cap from the
  surface; the fault keeps its place"), and with no new fit needs_rebuild sees a gap of 0. Over the whole faulted
  thermal set the fit failed from step 45 on in TBf and TAf (TA_age25f from 65): about a third of the late
  detections kept the old fault. Worth stating in the note where rebuild frequency is quoted. Rerun from
  TA_age25f checkpoint 30 (steps 31-60, trench -0.4 -> -4.4 deg, fit succeeding); rendering follows. Driver item
  for later: a fallback when the crust does not reach the cap (slab-top isotherm).
- 2026-10-29: kaiju's crust-fit tallies and failure mode (see Waiting on Louis): the parabola, not the crust sampling,
  is the limit on a broad thermal hinge, and the stored fault angle and dip in that phase are the parabola's
  surface crossing rather than the placed trace. Earlier "dip 18-23" statements in this file and in reports are
  corrected to that reading; the faulted-set dynamics and comparisons stand. Tallies are in the slab_thermal_fault
  and addon_demo READMEs on kaiju.
- 2026-10-29: Louis: file the units finding as a bug, the demo falls back to dimensionless. Filed
  https://github.com/underworldcode/underworld3/issues/891 (estimate_dt's crossing time and first accuracy
  estimate read dimensional coordinates as model units; D2-D7 listed in it). Kaiju told: demonstrations
  dimensionless, physical columns by post-processing, -uw_scaled check-only.
- 2026-10-29: kaiju confirms no launch script passes -uw_scaled (all runs dimensionless; the check stays on
  kaiju/units-scaled); Louis's ruling added to the units page. Demo movie run rebuilding the fault every step
  from TA_age25f checkpoint 30, rollback under way, ~1.7 h to finish.
- 2026-10-29: **demo run killed at step 40 by the crust-fit's surface end** (kaiju): the parabola met the wall
  near-tangentially and crust_fault_points followed it along the surface out to -34 deg (192 of 269 points
  outside the domain); the chain levels were refused, the build fell back to welding (+~3000 cells on the top
  level) and the step hit the OOM killer at 186 GB. Stored theta -30.7 against -3.0 for the placed trace;
  kaiju's quoted dips 34/30/26 were stored values again (placed dips 57 -> 44 at -0.3 to -1.3 deg). Fix in
  smoke: the fault starts where the parabola enters the wall nearest the fitted points, a straight stub along
  the chord above it to 0.02 above the wall, theta and dip recorded from that crossing (which also fixes the
  stored-vs-placed recording and should cut the late fit failures). Patch to the hub if the smoke passes; the
  demo reruns from checkpoint 30 on the fixed driver so every frame comes from one driver.
- 2026-10-29: Louis: start the continent further from the trench; the crust-curve fitting needs a robust model, not
  a patch. Kaiju tasked with both (design first for the fit, offline tests on stored checkpoints, artifact, then
  flag, smoke, patch); the demo movie rerun waits for the robust fit.
- 2026-10-29: kaiju's wall-stub patch d85c25c applied as 259ee09 on zg95-annulus-for-kaiju (blob fb70d26 -> 0725bbe
  verified) and pushed. Kaiju corrected its earlier report: the step-39 fit ran just under the surface, not above
  it, so the first crossing fix changed nothing (smoke 2368 OOM'd identically); the welded build was the failure
  signal (no weld in ~300 earlier faulted builds). Smokes 2369/2370 above. Stop-gap only; robust fit design in
  progress.
- 2026-10-29: kaiju continent-gap analysis (artifact PcRP5QjPT8DSa9rEjkfs4F): -uw_over_gap 0.75, -uw_cont_extent
  2.4315 recommended, no driver change needed; hub accepted within Louis's "further away" ruling and asked for the
  next Earth smoke on it.
- 2026-10-29: Louis: a dev hub (`session_01HxWvn6vA38fdYLUxnxDk4g`, `DEV-HUB.md`) owns underworld3 PRs, library
  fixes and library problems raised by sessions. Read its "For the other hubs"; added it to the session table;
  handed over the library-fix rows of "Open work" (hand-over section above, pointer row in the table); answered in
  this file's new "For the other hubs" section. #850-#854 merged (were listed open here); #457 closed (bears on
  the TI comparison; kaiju to check its build). Hubs coordinate through files: cloud-to-cloud messaging is refused.
- 2026-10-29: kaiju: #457 fixes present in both library builds (finding only); TI design report corrected; stale
  TODO(BUG) comment on TransverseIsotropicFlowModel recorded as a library one-liner for the dev hub. Louis to kaiju
  on the crust fit: try a flexural profile; keep the fit generalisable (several faults/slabs, continent at the
  trench, 3D); recorded under the crust-base fit decision.
- 2026-10-29: kaiju's robust crust-fit proposal delivered (artifact SgZjTP3MdeSxaGRNPup8hG; scripts
  kaiju-launch/crust_fit/, results figures_work/crust_fit/). Hub: implement the envelope behind -uw_fault_fit
  (default off), smoke, patch; demo rerun and production choice to Louis. Earth smoke 4 (gap 0.75, extent 2.4315,
  clone zg95-earth4 at 259ee09) running as job 2371; cont_extent comment 9df8bff rides the fit patch.
- 2026-10-29: Louis on the TI comparison: the split fault is frictionless (zero shear strength); the TI band
  approximates it. f_b and eta_1/w become "as small as the solver tolerates" with the residual band stress
  reported; recorded under the TI decision item; kaiju told.
- 2026-10-29: TI settings set (mask = whole band as the split's precedence mask; joint push-down of f_b,
  regularisation and floor). Envelope locator committed on kaiju (63f8d30 local, base 259ee09); 10-step smoke
  from demo checkpoint 30 running (job 2372) with compare_smoke.py against the offline trace and a stored = placed
  check from records. Rebuild threshold with the envelope: compare against the last built fault, 4 rungs, no
  hysteresis (particle noise a third of the threshold). Earth smoke 4 still running.
- 2026-10-29: envelope locator series applied (e37bb84, cdf44c1) and pushed; branch head cdf44c1. Smoke 2372
  passed (details under the crust-fit decision). Demo rerun and production locator still wait on Louis.
- 2026-10-29: Earth smoke 4 done (gap 0.75 holds at 0.71-0.75 d over 20 steps, dynamics unchanged from smoke 3);
  recorded under the Earth-like setup decision; page v3. Kaiju corrected smoke 3's vrms range (209-389).
- 2026-10-29: Earth production plan drafted by kaiju (page v4); recorded with a GO/NO-GO item for Louis. Kaiju asked
  to split plate_metrics into oceanic and continental arcs before the run.
- 2026-10-29: kaiju's key-clearing fix and plate_metrics.py (split into oceanic and continental arcs) applied as
  f217bdb and 07667b2, pushed; head 07667b2. Finding: the continent at x1 deforms internally (surface speed -870 to
  -190 across its 120 deg); added to the Earth go/no-go item for Louis.
- 2026-10-29: kaiju's lid check: the continental lid flows viscously 50-150x below yield; either a compositional
  factor or a thicker lid would stiffen it. Recorded under the Earth setup; Louis's go/no-go item unchanged.
- 2026-10-29: Louis gave the go to kaiju directly; Earth production run launched (job 2374) with the continent left
  at x1 ("fine to deform ... unless they are cratons"). The go settles the envelope locator; the demo movie rerun
  started on the second node. Both recorded above.
- 2026-10-29: demo rerun launched as job 2375 (envelope, every step, 30 frames); renderer ready. Chain levels not
  checkpointed: finest level only, no rerun for them (hub decision).
- 2026-10-29: Earth production (job 2374) progress at step 12: envelope formed F0 at step 0 (the initial crust already
  reaches the cap; the parabola had waited to step 5), so the fault slips from step 1 and vrms is ~250 over steps
  1-11 (smoke 4: 216 pre-fault); trench -0.36 -> -2.71 deg by step 11; dip 56-63 -> 32-34 by step 8; floor bound
  once (step 9, 29.8); trench gap 0.003-0.063; 8 builds in 12 steps at 4 rungs (11-12 s each); 138-256 s/step, 3-7
  Newton; no welds, refusals or rejected fits. Demo rerun (2375) on n3 at ~40 min.
- 2026-10-29: demo movie delivered (job 2375; artifact 3NDYkgLksNA1yuQGdvVrZ3); Open work row closed; flagged to the
  docs hub in "For the other hubs". Kaiju moves to the TI comparison on the free node.
- 2026-10-29: kaiju's TI path implemented (local, patch with the smoke) but any unsplit placed coarse MG level OOMs
  the first solve: library defect recorded for the dev hub; TI runs at -uw_chain 0 with a chain-0 split control.
  No-op checks (TI band off vs VP host, chain 0) running (2388/2389); push-down follows. TAf_env rerun approved.
- 2026-10-29: TI push-down smoke done (page 7mau5dPymUCYGPYJCCDnME); four-commit TI series applied and pushed (head
  852c6aa); TAti go at L1 on chain 0. TI slips 1.6-2x the split on a common probe: equivalence question to Louis.
- 2026-10-29: TAti launched (job 2398). Slip-rate profile: TI localised, split spread; the split is the restrained
  one. Kaiju asked to measure the tangential traction on the split faces and overlay crust/bridge on the profile.
  Three kaiju jobs in flight: Earth 2374, TAf_env 2390, TAti 2398.
- 2026-10-29: kaiju: the split fault is locked at the top by the bridge zone (global floor and rate strengthening
  override its weakening); the crust-beside-the-fault guess not supported. One-smoke test with a bridge-own floor
  approved behind a flag; bridge-zone share of the faulted thermal runs' faults to be counted. Normal-traction
  asymmetry on the faces passed to the dev hub as "to check".
- 2026-10-30: Earth production run 1 complete at the base (81 steps, 5.1 h; page v7). Bridge test negative (the
  split's restraint is not the bridge zone); flag applied as 4aa798c; minimal split-contact probe asked of kaiju;
  dev-hub item updated. TAti (2398) and TAf_env (2390) continue.
- 2026-10-30: split-contact probe: frictionless; the annulus restraint is the buried upper tip (library cannot cut
  to the wall). Dev-hub "to check" cleared; feature request for surface-breaking split faults recorded. Like-for-
  like TI smoke (buried band) and a taper estimate for the thermal set asked of kaiju.
- 2026-10-30: buried-TI smoke: no match (burying removes 23-42 % of the TI excess); the rest is the band's tips and
  width. Thermal-set bound: the buried split slipped at ~0.4-0.5 of a surface-breaking fault. Next smoke held
  for Louis (options recorded). TAti and TAf_env continue.
- 2026-10-30: TAti far too slow (15-23 Newton, ~45 h to the base; hard Min/Max kinks in the band law suspected).
  Hub: no chained 45 h run; smooth band law behind a flag tested against the first 5 steps on the free node, then
  restart or pause. Recorded under the TI item.
- 2026-10-30: smooth band law: same physics, a third off the cost; TAti restarted on it from step 0, chained (~30
  node-hours, node otherwise idle); hard-law 2398 stopped. Patch a00a10b pending in full form.
- 2026-10-30: smooth band-law patch applied as 67dd2c8; TAti_smooth chained run live (segment 1 job 2405, supervisor
  on the login node). Branch head 67dd2c8.
- 2026-10-30: TAf_env at the base; locator A/B: large-scale evolution and plateness independent of the locator, but
  the parabola overstated slip ~50 % and plate speed ~10 %; envelope run is the thermal-set reference. TAti_smooth:
  one unconverged step after the first rebuild; pause trigger set; rebuild Picard switch on the TI path to check.
- 2026-10-30: TI Newton stagnation after rebuilds: the Picard switch fires; the tangent is suspect. Jacobian test and
  a 1e-3 Newton-switch restart from checkpoint 5 asked of kaiju; a library finding goes to the dev hub if the TI
  tangent fails the test.
- 2026-10-30: Louis: the TI issues are a regression or a forgotten configuration; examples must be bundled with the
  technical notes (standing rule added; passed to the docs and dev hubs). Kaiju redirected to the library's TI VEP
  model and its own TI example as the reference before any further driver workaround.
- 2026-10-30: Louis (to kaiju): the known-good configuration is the split plus TI to the surface; the driver's
  bridge is isotropic (copied from the library example's yield fallback), so no faulted run had TI at the surface.
  -uw_bridge_ti in implementation; smoke waits for the validated TI law; the reference configuration to be found
  in the library's own scripts.
- 2026-10-30: reference configuration found (fault_mg/zg95_annulus.py --arm split: linear TI eta_1 = 1e-3 eta_0 on the
  cap above the cut, no yield in the TI part); library TI tests pass on kaiju's build (no regression); stagnation
  is our hand-written yielding eta_1. Smokes 2412 (TI VEP model) and 2413 (split + TI bridge on the reference law)
  running. Test/example gap for purely viscous yielding TI recorded for the dev and docs hubs.
- 2026-10-30: TI tangent consistent (oracle 1e-10); TI VEP model unusable as is (dev-hub note); TI band hard to
  converge even on the linear reference law; the TI bridge changes nothing (bridge cleared). New prime suspect: the
  split's per-node contact normals on a curved trace partly lock the contact (box repro on arc and kinked cuts);
  "to check" reopened as a probable library finding; annulus confirmation with smoothed normals running (2423).
- 2026-10-30: director smoothness ruled out as the TI band's Newton trouble (DG0 director angle change between
  neighbouring footprint cells: median 0.07-0.66 deg, max 8.2 at the stub joint on a young fault, nothing over 5 on a
  mature one). Smooth-director smoke held. Waiting on 2423 (split with trace normals).
- 2026-10-30: 2423: smoothed contact normals change nothing in the annulus; contact normals eliminated. Box
  comparison split vs TI band against the crack solution approved and running, written as the reference example
  for the fault notes (flagged to the docs hub).
- 2026-10-30: box reference done: TI band reproduces the crack (2026-017's claim holds), ladder-placed split 10-15 %
  under (dev-hub note); buried-tip bound RETRACTED (free-slip wall pins a dipping fault's end regardless); the
  annulus TI-split gap is setting-specific. Equivalence investigation closed; TAti vs TAf_env over the run is the
  answer. Surface-breaking feature request downgraded. Reference example flagged to the docs hub.
- 2026-10-30: five-patch TI series applied (head fc491c6). TAti_smooth on segment 2 at step 16, converging bar one
  step, base expected tonight. Comparison page v5. Only segment-boundary notes from kaiju until the base.
- 2026-10-31: TAti_smooth paused since 2026-10-30 19:44 (21 unconverged steps of 53); hub: bounded diagnosis on
  checkpoint 50 then resume today. Dev hub's compute requests (#902 scaling with 96d39f7b, #896 fix comparison,
  node-sharing question) and the docs hub's chain-comment item relayed to kaiju; 3-D kaiju session recorded.
- 2026-11-01: TAti_smooth root cause: Newton switch clamped to the tolerance, so the 1e-3 runs were pure Picard;
  resumed from checkpoint 50 at 3e-2 switches (job 2452, both diagnostic steps converged, ~7 h to the base).
  Patches 54ad91b applied (chain comment; yield_stress_min = -oo for development). Dev-hub notes: the clamp, the
  #759 refusal, node packing (2 per node now, throughput test later). Scaling job on four builds queued.
- 2026-11-01: TAti trigger at steps 61-62 after a rebuild; driver bug found (cold retry kept even when worse than the
  warm attempt). Stop, fix (keep the better attempt), resume from 60 report-only; rebuild-switch test alongside;
  audit of earlier failed steps for the page. -log_view gap noted for the dev hub.
- 2026-11-01: TAti resumed from 60 with the keep-best fix (job 2465); audit shows 15 of 20 unconverged steps kept a
  worse cold result, explaining part of the slip see-saw; line-search stall confirmed as the rotated loop's
  not-improved exit on Picard (library finding for the dev hub). Rebuild-switch test running (2467).
- 2026-11-01: Louis (via the notes session): production tail for split faults ruled (uw_chain 0 with the LU patch
  once #912 is in); kaiju asked to confirm at np 16 on development, chain 0 vs default, before any driver default
  changes. Relayed; Open work row added; supersedes the #896 check.
- 2026-11-01: keep-best patch applied (ca2eee5); split check closed; rebuild-switch test failed (not folded in);
  TAti segment 5 running report-only after a restart hang; Louis's chain-0 check started on development 25d62812,
  FAC patch found all on one rank at np 16 (dev-hub observation).
- 2026-11-01: Louis's chain-0 check done: confirmed at np 16 (-24 % velocity its, -4 % step time, identical answers);
  patch all on one rank by partition. Default change to 0 held until the builds in use carry #912; passed to the
  dev and docs hubs and the notes session.
- 2026-11-01: Louis (via the notes session) asks for the solver time budget (coarsest-mesh time, overall efficiency
  at 16 cores) and a warm/cold comparison between chain 0 and chain 2; relayed to kaiju as an Open work row.
- 2026-11-01: Louis's solver questions answered (page LvNXEPD4QNkKtr2V7jDYH2): the Schur pressure solve at rtol 1e-4 is
  the cost; 1e-2 gives 2.3x with the answer unchanged; chain 0 and 2 behave the same warm and cold; the coarse SVD is
  3-4 %. Hub recommends -uw_pres_rtol 1e-2 as the campaign default now; passed to the dev hub for the library default.
- 2026-11-01: the notes session found three points to reconcile on the budget page before UWTN 2026-022 cites it:
  chain 0's 21-28 s FAC patch per step is too dear for a 503-row LU (likely the 3584-row f0 patch, i.e. the arms
  were not on the same mesh in steps 41-43); the "-24 % velocity iterations" is a last-application figure while
  total F-cycles per step are nearly equal (2489 vs 2527); solve times were quoted as step times. Relayed to
  kaiju; the budget page is provisional until it replies. **RESOLVED (budget page v3, chain page v2):** (1) the
  chain page's patch table was misattributed: each solve configures two multigrids; the applied one
  (rotfs1_fieldsplit_vel_) has on chain 0 a finest-level patch of 3584 owned / 3736 subdomain rows on rank 4 and
  on chain 2 NO patch; the 465/503-row patch belongs to the solver's own prefix, applied 50 times in 3 steps. Both
  arms solved steps 41-43 on the same rebuilt mesh f8, so the budget stands; chain 0 = welded base + patched
  finest level (patch 21/28/25 s per step, ~10 block applications per F-cycle at ~1 ms, rank 4 alone), chain 2 =
  split ladders, no patch, cheaper finest cycles (0.057 vs 0.085 s). (2) On the totals there is NO difference in
  velocity work: 8.65 vs 8.74 F-cycles per velocity solve (7.92 vs 8.50 at pres_rtol 1e-2); the -24 % holds for
  the last application of each increment only. (3) Wording fixed. **Hub's reading: on the annulus at np 16 the
  two tails are a wash (solve 442 vs 409 s in the budget runs, 448 vs 467 on the chain page, within the +-10 %
  run-to-run spread); the case for chain 0 is robustness (no ladder surgery on coarse levels, no refusals or
  welding), not speed; the FAC patch on one rank is its cost.** np 32 dt anomaly: the Stokes answer differs 0.1 %
  in vrms but dt is 28 % smaller; kaiju suspects an outlier in the base velocity that to_base transfers back,
  not a different solve; probe running.
- 2026-11-01: budget/chain pages corrected (v3/v2): same mesh in both arms, patch table misattributed, velocity
  work equal on the totals; chain 0 vs 2 is a wash on speed, chain 0 wins on robustness. pres_rtol 2.3x unchanged.
  np 32 dt anomaly suspected in the to_base transfer, probe running.
- 2026-11-01: the notes session posts the correction on underworld3 #892 itself (its earlier kaiju comment said both
  arms carried the same 465-row patch and that the difference was the coarse levels alone; both wrong); the hub
  posts nothing there. The pressure-tolerance lever stays with the science hub (campaign default, Louis) and the
  dev hub (library default). 022's annulus paragraph matches the corrected reading.
- 2026-11-01: np 32 dt anomaly explained: velocity spikes at wall nodes on partition boundaries in the rotated
  free-slip solution itself (not the transfer); probable library defect recorded for the dev hub; kaiju isolating
  (unfaulted case, other rank counts, v.n at the spike nodes). Scaling page: np 16 vs 52 like-for-like, np 32
  marked as a different state.
- 2026-11-01: wall spikes confirmed on the unfaulted base mesh at np 32: the rotated free-slip constraint is missing
  at 2-3 shared wall nodes (library defect, dev-hub entry upgraded). Kaiju's labelling test given the go; a wall
  |v.n| check becomes a standing record column. Dev hub's fault-across-partitions test on overlay F (25d62812 +
  96d39f7b, local merge) at rank counts whose walls check clean.
- 2026-11-01: wall-spike mechanism confirmed: the rotated route's analytic-normal path builds its node set from each
  rank's own labelled facets only, so a wall vertex whose owner holds none of its facets is never constrained.
  Finding with fix and test recorded for the dev hub, ready to file. Driver record column -uw_wall_check coming.
- 2026-11-01: -uw_wall_check patch applied (ee38b39, default on; validated: TAc np 32 flags 3 nodes, np 16 clean).
  Rank sweep: every count except 16 has unconstrained wall nodes (np 52's too small to set dt); inner spikes at the
  coarse mesh's 22.5-deg vertices. All production runs (np 16) verified clean to 1e-12 at their latest checkpoints.
- 2026-11-01: dev hub's scaling check done (page ACJ6diJRBCGoBGvCa6aCxM): #902 closed on kaiju (np 32/52 build and
  match np 16 with the fix; development fails at np 32); #901 coarse cost 6-9x lower, ~5 % per step; strong scaling
  ~1.5x from 16 to 52. Recorded for the dev hub. TAti_smooth at step 81, ~6 steps from the base.
- 2026-11-01: Louis: go on the lax pressure tolerance; -uw_pres_rtol 1e-2 becomes the campaign default (patch coming
  from kaiju). The notes session asks for the annulus band ratio h_b/S on f8 and each arm's level cell counts, to
  reconcile 022's box sweep (LU patch 4-11x better) with the annulus (equal work); relayed to kaiju.
- 2026-11-01: pres_rtol default patch applied (fa3accc; head). Band ratio for 022: h_b/S = 3.9 on the annulus (0.0156 /
  0.004), below the box sweep's 7.9-24.8, which reconciles equal annulus work with the box's 4-11x; hierarchies on
  chain page v4; relayed to the notes session. Notes session asks what pressure tolerance the addon_demo trench
  runs and the restart-table runs actually used; relayed to kaiju.
- 2026-11-01: tolerance provenance for 022 (kaiju, from logs): the addon_demo trench runs and the restart-table runs
  all used the library defaults, outer 1e-3, pressure 1e-4, inner velocity 3.3e-5 (no -uw_pres_rtol anywhere; the
  rungs8 build counts are records.json's n_built and may differ from "rebuilds" by the initial build). Relayed to
  the notes session.
- 2026-11-01: TAti_smooth at the base; TI-vs-split comparison COMPLETE (page v6): same large-scale subduction (base
  time, plate speed, plateness within a few %), TI rollback ~20 % less, TI 2.7x the split's step cost with a third
  of its steps unconverged after rebuilds. Open work row closed.
- 2026-11-01: dev hub's production-tail comparison done (page BWgDzWDzzjDJXQWqVb1jrs): chain 0 holds on TAf 20 and
  TBf 70 (same answer, a wash on speed, robustness case); recorded for the dev hub. Fault-across-partitions runs
  starting.
- 2026-11-01: CORRECTION: the one-rank fault patch is the drivers' seams="gather", not the partitioner; conform (#670)
  never wired in. Louis: "disappointing to discover it is not used and has been forgotten ... not-using to
  not-considered and then to not-available"; recorded choices become a standing rule; kaiju audits every exposed
  knob against production values; round-2 k-partitions runs with conform queued; seams-record patch coming.
- 2026-11-01: the notes session posts the gather addendum on #892 (its earlier comment gave "the fault lies inside one
  partition"); the hub posts nothing. From its code reading, relayed to kaiju for round 2: seams other than gather
  require mesher="network" (the ladder only takes gather), so conform changes the mesher too; and on development
  25d62812 gather at np > 1 first runs addon_partition.partition_addon (band region on one rank, load diffused to
  10 %) so the placement moves nothing, while on 99259d35 the placement itself gathered. 022 now describes it so.
- 2026-11-01: kaiju's first conform arms (2794-2798) failed at placement ("seams='ligament' needs mesher='network'":
  the library's message says ligament for conform too, a wording bug for the dev hub); no step wasted. Fix:
  -uw_fault_seams conform selects the network mesher and refuses chain levels (they do not nest), so the conform arm
  is chain 0 only and the comparison is placement+mesher. Mesh record gains "partition" (gather via
  addon_partition.partition_addon on development; gather by the placement on 99259d35; conform; serial). Patch is
  now 3f2cc34 (replaces the unsent b987b6a), sent only if the conform smoke 2808 builds in parallel with the band on
  more than one rank (the network mesher deadlocked with ligament seams on 18 Oct). Kaiju noted two pinning slips
  (a commit in a clone with a running job; a re-clone under a job), neither affecting a result; one fresh clone per
  commit from now on.
- 2026-11-01 check-in on the other hubs' files. Dev hub to the science hub (10-31): the unsplit-tail memory defect is
  filed as #893; the surface-breaking split request belongs on #553 (open since August); the drivers' uw_chain
  default waits on #892 and Louis (now: on the build move). Dev hub history note on #892: on the rotated path the LU
  block solve was never in effect from the day it became the default (891c9bb0, 2026-09-03); every fault result on a
  rotated solve since then ran ILU(0) blocks. Dev hub has filed #918 (silent cover gate), #919 (addon_partition
  static mark, fix held), #920 (rotated path's max_it 50 ignores snes_max_it), #921 (structural rows left out of the
  patch with fac_zone on a TI band). Not yet visible in DEV-HUB.md: the analytic-normal wall-node finding and the
  Picard line-search stall; both stand in this file's "For the other hubs" for its next read. Docs hub to the
  science hub (11-01): the production tail is ruled, kaiju's np 16 record is on #892 (issuecomment-6552218825,
  corrected), the default moves to 0 with the campaign builds, and the driver commit's sha closes the journal's
  2026-11-01 decision entry when it exists; the chain-comment item is moot once chain 0 lands.
- 2026-11-01: knob audit delivered (153 knobs x 6 families); run_info resolved params and README choices block
  approved; normal=None test at np 32 requested; TAf_env-not-a-clean-control caveat to the comparison page; the
  unwired list passed to the dev hub.
- 2026-11-01: conform validation failed at the network mesher's assembly ("meshed to no triangles") before any
  parallel work: conform has never been usable in the annulus; k-partitions question unmeasurable for now. Gather
  validation passed with the new record fields; patch 3f2cc34 to be sent as is; serial repro for the dev hub
  requested.
- 2026-11-01: seams-record patch 3f2cc34 applied as 9378e11 (blobs e402259 -> d5c4a74 exact) and pushed; default
  gather unchanged, conform fails loudly, every build records seams, partition mechanism, band cells per rank and
  band ranks. Next from kaiju: the wall-normal switch, the choices record, the serial mesher repro.
- 2026-11-01: wall-normal switch and choices record applied (0dbd4ce, 3f8f39c -> head 094e4f3; blobs 70876bf, 728f1a4,
  90aeec4 exact). Geometric normal fixes the np 32 defect with the same answer: default change put to Louis
  (recommend yes); interim rule: np != 16 runs set geometric explicitly. Serial network-mesher repro: a fault
  reaching the wall cannot be placed by the network mesher at all; conform unusable for surface-reaching faults in
  2-D. Both for the dev hub.
- 2026-11-01: round-2 gather arms: a longer fault (depth 0.45) favours chain 0 by 20-35 % per step even with the
  serial patch; recorded for the dev hub. Node-packing test running (1/2/3 jobs per node on n7).
- 2026-11-01: node-packing test done (3 jobs per node = 2.1x node throughput; page 1CFNXD4TpQLX5jfeTdMN8k); one
  socket-pinning test approved before packing becomes standard. Kaiju's science-hub queue is empty. Open: the
  uw_chain and wall-normal defaults (Louis), the wall-node and network-mesher findings (dev hub).
- 2026-11-01: socket-pinning test: no effect (2 pinned 838/833 s vs 835/822 unpinned; 3 jobs 827/838/706 vs
  841/845/708); the ~1.45x per-job slowdown on a shared node is node-wide (clock, memory system), not placement; a
  third job costs nothing more per job; the third job's ~15 % speed advantage unexplained. Packing becomes the
  standing launcher setting for independent runs. Kaiju's queue is empty; waiting on Louis's two held defaults.
- 2026-11-02: Louis's rulings via the dev hub read: no corridor refinement ("let's try to avoid opening up too many
  new directions"); the split tip depth is one element in mesh units, not a physical length. Kaiju's ladder-spacing
  arms for the dev hub recorded; the hard-coded 3-rung split inset becomes a knob (patch coming); the unit and
  default (rung vs base cell) put to Louis.
- 2026-11-02: split-inset knob patch applied (580022f, blob 3531a78; default 3 rungs unchanged). Row-2 patch-cost
  curve against fault length queued for the dev hub.
- 2026-11-02: Louis: (1) automate the inset at 1 rung if possible, evidence for 3? (kaiju tests 1/2/3); (2) the
  wall-normal defect: how undetected, latent bug when no analytic normal exists? (answer and two asks to the dev
  hub: the geometric path is the safe one; a parallel test at an orphan-vertex partition and a post-solve
  constraint check in the rotated route); (3) the drivers are not underworld3: decisions must be findable, so
  zg95_lid_regimes/DECISIONS.md is created (e8015a6) and is a standing rule.
- 2026-11-02: Louis: go on the build move. Kaiju told: build from current development for new runs, retire the
  leak-fix overlay for new work, send the uw_chain 0 default patch with the ledger pointer, run the one-step
  acceptance check. Recorded for the dev and docs hubs; ledger to be updated with the commit.
- 2026-11-02: build move accepted (job 3154 passes); kaiju's series applied: choices block points at DECISIONS.md,
  uw_chain default 0 (b440b88); its ledger patch reconciled by hand into the hub's ledger edits; head bf18312.
  Journal closure sha passed to the docs hub.
- 2026-11-02: split-inset test done: 1 rung places as reliably as 3 with chain 0 (not with chain 2 at 4S), but the
  answer differs by ~10 % in slip (3 rungs locks more of the top); no evidence ever stood behind 3. Default to Louis.
- 2026-11-02: kaiju's ladder-spacing arms were confounded (restored polylines keep the checkpoint's S); relabelled and
  rerunning with re-sampling on restart (hub: automatic when S differs, no-op otherwise). Row-2 curve: the one-rank
  patch grows linearly with fault length, 10-12 % of a step at depth 0.60. Both recorded for the dev hub.
- 2026-11-02: Louis rules: split inset 1 rung; wall normal geometric. Kaiju sends both default patches with the ledger
  rows and a one-step acceptance; recorded for the dev hub.
- 2026-11-02: acceptance of the two new defaults: the restart rule and inset 1 pass; the geometric wall normal FAILS
  with a fault present (outer-wall constraint broken, vrms doubled) though clean without one. Series split: restart
  rule + inset 1 go in now; the geometric default is held on evidence pending kaiju's isolation.
- 2026-11-02: kaiju's split series applied exactly (df92f37 the restart rule, 28aaf5e the inset-1 default; blobs 3e0ba76,
  ad69d1d, ledger de55653); head 99049b5. The ledger records the inset ruled, the restart rule, and the wall normal
  as ruled geometric but held on job 3447. Confirmation run 3455 (analytic + inset 1) and the wall-normal isolation
  pending from kaiju.
- 2026-11-02: wall-normal failure solved: geometric normals + placed wall vertices on chords make rigid rotation an
  inexact null mode, left to the solver (omega -1543 / -4743; flow identical after removal). Library finding for the
  dev hub (the #906 class). Analytic stays the default; Louis's geometric ruling held on the mechanism. Inset-1
  confirmation passed.
- 2026-11-02: dev hub's ladder-spacing arms done (re-sampled reruns): S = h_b shrinks the serial patch 3x and the
  step 14 % with the mature answer within 0.3 % vrms / 4 % slip and the early slab's slip 10-18 % lower (cut deeper).
  Recorded for the dev hub; the rung-spacing default put to Louis. Kaiju's queue is empty.
- 2026-11-02: Louis rules S = one base cell and wants the recipe and library changes pushed to restart the rollback
  experiments. Kaiju: S default, whole-recipe acceptance, baseline proposal page. Hub: merge the campaign branch to
  main after the acceptance. Dev hub: #902 PR, analytic node set, #906 named as the library items that widen the
  experiments; np 16 needs nothing more.
- 2026-11-02: kaiju sandboxed (read-only ~/campaigns, no Slurm): acceptance and launches blocked; for Louis. Spacing
  patch b21c264 held unapplied in the hub's scratchpad until the acceptance; proposal page CDy2RR1fLhBUyPXtUMftNr
  recorded. Correction: velocity its per increment unchanged with S; the gain is Newton increments and the patch.
- 2026-11-03: Louis: the sandbox issues are no longer a problem. Kaiju told to verify write access and Slurm, pin
  b21c264 on 6633afa, run the whole-recipe acceptance, and report; on a pass the hub applies the held spacing patch
  and merges the campaign branch to main; baselines wait on Louis's pick.
- 2026-11-03: Slurm back; ~/campaigns still read-only to the kaiju session (allow-list = ~/+Claude only). Acceptance
  running from ~/+Claude/kaiju (job 3830, 6633afa + b21c264, development 25d62812, np 16, -uw_fault_fit envelope set
  explicitly). Gap found: the driver's locator default is still parabola; kaiju to send the envelope-default patch
  for recipe v2 after the acceptance. Allow-list decision for Louis.
- 2026-11-03: recipe v2 acceptance PASSED (job 3830: vrms 1318.24, slip 5724, Newton 5, walls 1e-12, 161 s/step, patch
  1168 rows). The held spacing patch (b21c264) and the envelope-default patch (2ab14e4) applied to the branch (head
  64feaec; blobs 95e9c34, fd6950f); the campaign branch MERGED into uw3-campaigns main (a7792cd, no conflicts): the
  recipe, drivers, scripts, figures and DECISIONS.md are on main. Caveat recorded: parabola runs (TAf, TBf,
  TA_age25f) restarted on the new driver need -uw_fault_fit parabola explicitly. Proposal page v2 has the
  acceptance and the launch line; the baseline pick is Louis's.
- 2026-11-03: kaiju holds a verified clone of 64feaec (~/+Claude/kaiju/clones/zg95-v2-64feaec, blob fd6950f; envelope
  and spacing defaults confirmed) for the baselines; proposal page v3 carries the flagless launch line. Nothing
  launched; waiting on Louis's pick. (main's head b4e6801 is the HUB.md commit after the merge; zg95_lid_regimes is
  identical to 64feaec.)
- 2026-11-03: the notes session: 022 cites main now; the spacing page's "S = h_b or h_b/2" was the dev hub's reading,
  not Louis's words; Louis's decision 1b (journal a4e5852) says no S parameter defines along-strike resolution,
  which the uw_spacing knob may conflict with. Ledger row corrected to quote Louis (c8df8a9, merged to main); the
  question put to Louis (the notes session has asked him too).
- 2026-11-03: spacing page v2 and proposal page v4 corrected: Louis's two remarks quoted verbatim, the S form named as
  the dev hub's reading, decision 1b quoted and the knob question marked open, the Newton-vs-velocity iteration
  fact beside his quote. Drivers and the 64feaec clone untouched; kaiju holds for the baseline pick.
- 2026-11-03: Louis clarifies 1b: the fault's own points set the along-fault division, the local mesh size the
  width; neither is a knob; the ladder is built from the fault points and sufficiency is observed, not set.
  Ledger principle row added and merged to main; uw_spacing marked for removal; kaiju drafts the design with an
  offline placement check at W = h_b. Baselines: v2 now or after the removal is Louis's call.
- 2026-11-03: notes session: 022's "spacing is a parameter" clause rewritten to the fault's own points; whether 022
  keeps its W = 2S runs or reruns at W = local cell size is put to Louis; a journal follow-up to 1b drafted for the
  docs hub. Library facts for the knob removal relayed to kaiju: the ladder path takes the trace's points verbatim
  (place_thin_volume with a precomputed (samples, reach) pair; no arclength resampling through
  place_fault_ribbon_2d), so the locator's points are the rungs as given; at W = h_b with rungs ~h_b the band cell
  aspect is 2 against the mesher docstring's "about 2 elements across width", to be weighed on the design page.
- 2026-11-03: kaiju's fault-division design ready (page UANqhA82AfRoh7fjgrPwYG; draft f393fd7, compiles, not run):
  one-cell band places on all 80 faults; rungs barely change from v2; the width halves; aspect 2 vs the mesher's
  preference for 2 cells across; outcrop slivers in every arm (dev hub). Two choices for Louis: BAND_CELLS 1 or 2,
  and the baselines on v2 or on the draft.
- 2026-11-03: Louis: the division design is too much for a concept-test driver; if implemented it belongs in a
  plate-boundaries module; make the ladder equant (half-width one cell, rungs similar), which is recipe v2 as
  accepted. Draft shelved for the dev hub as module input; ledger updated and merged; baselines TAf-v2 and Earth
  run 2 ordered on v2 from the pinned clone.
- 2026-11-04: baselines running: TAf-v2 job 3841 (n2), Earth run 2 job 3842 (n3), pinned 64feaec, single 12 h
  segments with in-job stop and pause rules (the login-node supervisor cannot run under the sandbox). Division
  record patch (a2caa30, record only) applied as a87bc9d and merged to main; the draft division design stays on
  kaiju/fault-division-draft as module input.
- 2026-11-04: Louis corrects the design page's "unmeasured": the ladder evaluation already found the cut on the
  fault's own nodes with one cell either side best, and no benefit to more cells in the band. Ledger principle row
  carries his words (merged to main); kaiju amends the page and withdraws the one-cell candidate; the notes session
  asked for the evaluation's citation. Baselines unaffected (already W = 2h).
- 2026-11-04: fault-division page v3 and the draft branch (c291d57 on kaiju/fault-division-draft) carry Louis's
  ladder-evaluation ruling: BAND_CELLS 2, the one-cell variant withdrawn (its placement check kept as a record),
  "unmeasured" replaced by the ruling. Baselines 3841/3842 before their first checkpoint; watch.log quiet.
- 2026-11-04: the ladder evaluation Louis cited is underworld3 #595 (2026-08-17, the cut-in-band configuration):
  the cut on the fault's own nodes with one cell either side snaps nothing (slip 0.4315, angles kept) where the
  centre-line cut pinched the band (13 deg, slip 0.4290); scripts on wombat only, no note or journal entry; the
  "no more cells" half unmeasured and recorded as recollection. Ledger cites it; merged to main.
- 2026-11-04: #595 cited on the design page (v4) and the draft branch (3402ad0). Baselines: TAf-v2 at step 2 (~180
  s/step), Earth run 2 at step 4 (~88 s/step), 3-4 Newton each, watch.log quiet.
- 2026-11-04: Louis agrees: the #595 evaluation's scripts and write-up (wombat only) come into scripts/sessions beside
  the note that cites it; the notes session instructed, the docs hub to route; the ledger's citation gains the
  commit when it lands.
- 2026-11-04: #595's evaluation placed by the notes session with UWTN 2026-022 (figures/src/cut_in_band_595: the
  scripts, modules, caches, write-up and a cache-only reproduction of the numbers), unsaved on the wombat
  workbench until Louis saves 022; ledger citation updated and merged to main.
- 2026-11-04: baselines at checkpoint 5, every step converged, walls 1e-13, watch.log quiet. TAf-v2 vs TAf_env: vrms
  500-533 vs 534-547, slip_max 924-1255 vs 1100-1247, Newton 4-5 vs 5, step 162-214 s vs 395-428 (2.3x, as
  estimated); division F0 14 rungs at 0.0153 (resample rounds the count), W 0.03125, dip 60.5. Earth run 2 vs run 1:
  vrms 253-283 vs 245-255, slip_max 644-1031 vs 452-648 (early top-of-fault sensitivity, compare at the base),
  Newton 3-5 vs 3-6, step 87-156 s vs 138-256; division 17 rungs at 0.0159, dip 30 (the floor). ETA: TAf-v2 ~5 h,
  Earth run 2 ~2.5 h.
- 2026-11-04: Earth run 2 diverging from run 1 (slip 3.4x at step 45) while TAf-v2 tracks its twin; not a baseline
  until the cause is found; three one-knob arms from run 1's checkpoint 20 ordered (band width via -uw_spacing
  0.004, inset 3, v2 as is). Slurm resolution failing again from the kaiju session (second time); for Louis
  (WITHDRAWN below).
- 2026-11-04: Slurm answered again (WITHDRAWN below: never an outage). Isolation arms queued as job array 3843
  (a: v2 as is; b: -uw_spacing 0.004; c: -uw_split_inset 3), 10 steps each from run 1's checkpoint 20 on the v2
  build; (d) -uw_detect_every 5 follows if neither b nor c closes the gap. Proposal page v5 carries TAf-v2's 1.92x
  and Earth run 2's departure. Baselines: TAf-v2 near step 36, Earth run 2 near step 50, watch.logs clean.
- 2026-11-04: side-by-side movies (Louis asked kaiju; page Q1Dq1epuXoEjPnKN7rzcKL, render jobs 3847/3848). No
  breakoff, no stagnant lid in any run. TAf-v2 and TAf_env are the same evolution. Earth run 2 follows run 1's slab
  path but reaches each stage in ~2/3 of the model time with plates 1.5-2x faster; from step 20 a stronger, wider
  high-strain-rate zone along the fault and under the trench (fits the band-width suspicion). Late: run 1's
  overriding plate stops (-36 at step 55) and its trench stalls; run 2's is still at -2882. Arms 3843 at steps 24-26.
- 2026-11-04: CAUSE of the Earth departure found. Louis, from the movies: the new recipe frequently has the fault in
  the hot mantle. Kaiju: the built cut (state "traces") drifts from the detected polyline because recipe v2's
  S = h_b made rungs 4 a rebuild tolerance of 0.0625 (old: 0.016); the detected fault itself stays in slab. Arms:
  only -uw_spacing 0.004 closes the gap (confounded with the threshold); inset 3 does not. Baselines 3841/3842
  cancelled on Louis's instruction, restarted as 3849/3850 with -uw_rebuild_rungs 1. Ledger 8c5a95f. Ordered from
  kaiju: threshold as a distance (one base cell, both branches), fault_in_slab.py into the repo and its hot-mantle
  fraction into the in-job watch as an acceptance criterion; the 1.92x re-measured. Lesson for the knob table: a
  default expressed in another knob's unit changes meaning when that knob's default changes.
- 2026-11-04: the threshold alone is the fix (restarts 3849/3850: 0 % hot mantle at every checkpoint). Kaiju's
  rebuild_cells series applied and merged to main (3486eeb, 76f161b, 9e69c6b; blobs bcced6f/1d9c660/d5d72d0/82cd923
  verified). TAf-v2 corrected 2.03x per step (proposal v6). The 1.92x on the cancelled run stood with its cut in the
  mantle; corrected the gain is larger, not smaller.
- 2026-11-04: CORRECTION (kaiju): there was no Slurm outage, on any day. Every failed squeue was a compound command
  the managed policy ran inside the sandbox, which cannot resolve kaiju.anu.edu.au; plain squeue always worked, as did
  Louis's. The "recurrence" items for Louis are withdrawn; the rule is in the kaiju machine section. Running: 3849
  (TAf-v2_rr1, n2), 3850 (Earth run 2_rr1, n3); 3851 renders the corrected-run side-by-side movies (n4).
- 2026-11-04: Louis wants throughput ("52 cores plus that super_lu trick"); questions to the dev hub (SuperLU
  decomposed patch; the np 52 wall node) in For the other hubs; kaiju asked them directly too. TAf-v2 rerun from
  step 0 on 9e69c6b (job 3852): the restart 3849 had inherited steps 1-20 with the loose threshold (initial fault
  built until step 11 vs 6). Louis wants a full-overturn run soon (~1-1.5 days per run at np 16); he picks the case.
- 2026-11-04: Earth run 2 reruns from step 0 too (job 3858): its restart's inherited steps 1-5 kept the initial
  fault with gaps to 0.0745 (would have rebuilt at 2, 3, 4 under the old threshold); the hub's checkpoint-gap
  argument was wrong, kaiju checked the step records. Lesson: a clean checkpoint does not certify the steps before
  it; the inherited range must be checked step by step. A first attempt (3857) died in 12 s: --export without ALL
  kept the Apptainer/PMIx environment from the ranks; fixed with --export=ALL in SRUN_OPTS. np 52 test running
  (3854/3855). Base-stop patch applied (57affaa) and merged.
- 2026-11-04: the analytic-normal wall defect filed as underworld3 #935 at the dev hub's request (kaiju's text; the
  hub files because kaiju has no GitHub credentials, by design).
- 2026-11-04: Louis: hyperion is up again with a claude remote-control service. New session
  session_01HxWvn92dmiWUj5FX68AZc7 (connected, 2.1.318); asked for a read-only inventory; no work assigned until Louis
  and the dev hub set its role.
- 2026-11-04: Louis: go ahead with the PRs for #935 and #902 (he told the dev hub too: "Yes to both PRs, zero for
  #936", DEV-HUB a29184d). The dev hub's integration session opens them: #935 after its review round 2, #902 after a
  development merge and serial checks, #936 as its own small PR; merge order on green #902, #935, #936. The hub does
  not open them (no duplicates). Kaiju's np 52 re-measure waits for a build carrying #902 and #935 (development
  after the merges, or the merged branches as a test build if the dev hub names one); the 1.44x and kaiju's np 52
  failure (#902's DMCreateInterpolation) predate both fixes.
- 2026-11-04: kaiju's early np 52 read (3941 np 52 on n2, 3942 np 16 control on n7; TAf-v2 fresh, 15 steps,
  25d62812) avoids both defects: #902 by a coarser base (-uw_cell 0.25 -uw_refinement 4, 448 coarse cells, finest
  114,688), #935 by the integration session's driver workaround (workaround_analytic_normal_nodes.py,
  addon-matrix-2026-11 3ade599; label check at np 52: 0 owned wall points missing on every level). Not production's
  mesh (walls about half as finely resolved), so it compares np 16 with np 52 on that mesh only; the merged-build
  test uses production's 0.5 / refinement 5. Let run (2 nodes, ~1 h). 3854 finished: the np 16 production-mesh
  reference. Baselines: TAf-v2_c (3852) ~step 45, Earth run 2_c (3858) ~step 50, built cut in slab at every
  checkpoint (hot 0.0, gap 0.003-0.024). 3849/3850 stopped at their bases (checkpoints 90, 80), superseded, kept.
- 2026-11-04: Louis: "I'd like to see the evolution at this resolution to see how well resolved it is." Kaiju asked
  to carry the coarse-base TAf-v2 (3941, np 52, cell 0.25 / refinement 4, #935 workaround) to the base as its own
  run with the 57affaa watcher; a resolution table of both meshes (where they actually differ, since h_b is
  0.0156 in both); a side-by-side movie against TAf-v2_c matched by tip depth; vrms / slip / trench / plate speeds
  against tip depth; fault-in-slab for both; on a page.
- 2026-11-04: kaiju CORRECTION: the cell 0.25 / ref 4 mesh is NOT coarser at the walls (identical: 1,792 Upper /
  1,024 Lower P2 points); it has the same h_b, S, W, ~10 % fewer cells overall and is ~10 % finer in the trench
  region (another gmsh base triangulation; refinement uniform in both, no grading). So production vs cell025 tests
  sensitivity to the base triangulation at the same resolution, not resolution. 3951 (cell025, np 16, from step 0,
  57affaa) runs on as that noise floor. For Louis's resolution question the hub ordered TAf-v2 at -uw_cell 0.5
  -uw_refinement 4 (production's base, h_b = S = 0.0312, W = 0.0625; band widens with the cell by the recipe), np
  16, from step 0; refinement 6 waits on #902/#935 (np 52), kaiju to estimate its cost. Page three-way. On cell025
  np 52 is SLOWER than np 16 (430 vs 310 s per step, same answer): suspect the 448-cell coarse level's dense SVD on
  every rank (#901); -log_view from 3941/3942 to confirm, then to the dev hub as the case for #901's A-prime PR.
- 2026-11-04: TAf-v2_c (3852) PAUSED by the fault-in-slab trigger (built cut hot fraction 0.18 at checkpoint 50, 0.052
  at 55; gap 0.0222 = 1.4 h_b). The hot part is the cut's deep end, 0.09-0.15 deep along the slab's warm top margin;
  the top 0.06 is cold. TAf_env on the old recipe had the same (13 of 94 samples hot at checkpoint 50). Hub's
  decision: the whole-cut 10 % was the hub's mis-specification; the drift test is the gap. Resume from checkpoint 55
  on 57affaa with HOT_PAUSE 0.30 as a recorded stopgap, kaiju reading each FAULT line by hand (pause if gap > 2
  base cells or top-0.09 hot > 10 %). Watcher patch ordered: top/deep hot fractions separately for built and
  detected, gap in base cells, pause on top hot > 0.10 or gap > 2 cells, deep end WATCH only; ledger row. Detect
  every step for TAf (option c) not taken: a cadence change against the twin, unmotivated. ref4 (3952) launched
  (0.5 / ref 4, h_b 0.03125, np 16, n4). Refinement 6 estimate: ~508k cells, ~2.0M P2 dofs, ~75-80 GB at np 16,
  ~15 min per step, ~8x the steps; behind #902/#935.
- 2026-11-04: TAf-v2_c resumed from checkpoint 55 as job 3953 (57affaa, HOT_PAUSE 0.30 stopgap, kaiju's hand checks).
  At checkpoint 50 the DETECTED fault is cold at depth (0 % hot) and only the built cut's deep end is hot (47 %;
  TAf_env 37 %): the five-step lag across the gradient, not the locator. Watcher patch applied as 4c32f77 (kaiju
  fa390e1; blobs 7ab8f3a / bce66dd / 596073d verified) and merged (1fd3c96): pause on top-0.09 hot > 0.10 or gap >
  2.0 base cells, deep end WATCH only, ledger row. Kaiju flagged the first checkpoint's gap (1.94 cells: the initial
  fault against the first fit); hub ruled a grace (GAP_GRACE = first checkpoint, WATCH not pause) rather than a
  higher limit; patch applied as 23f509d (kaiju 4fb23d2; blobs 637e988 / 74a0d87 verified) and merged. New
  launches and resumes after a pause use it; 3953 stays on the 57affaa stopgap to the base with hand checks.
- 2026-11-04: **Earth run 2_c (3858) reached the base** (tip on base at checkpoint 75, stopped after 80). ACCEPTANCE:
  built cut 0.0 hot, gap 0.0161; every FAULT line 5-80 0.0 hot. Kaiju continued it to a full overturn as job 3957
  (same dir, from checkpoint 80, 23f509d, STOP_AT_BASE=0, up to 400 steps, 72 h; estimate t ~0.0015, ~250 steps,
  15-20 h). Driver file unchanged 9e69c6b..23f509d (watcher/tools only). Louis had been asked to pick the overturn
  case (Earth or TAf-v2); whether he chose Earth is to confirm. Base page (run 2_c vs run 1) next.
  ref4 (3952) paused at checkpoint 30 on the old whole-cut rule (0.136 at checkpoint 25; by 23f509d's split top
  0.097, deep 0.171, gap 1.47 cells); resumed on 23f509d as 3955. The top came within 0.003 of HOT_PAUSE at this
  resolution, where the gap in model units is twice production's: to be stated on the resolution page. ref4 costs
  15-25 s per step against 180-230 s at refinement 5. TAf-v2_c (3953) hand checks: checkpoints 60/65 0.0 hot, gap
  1.11/1.20 cells. sbatch "I/O error writing script/environment" recurred once and succeeded on retry: intermittent,
  controller side, nothing for the admin unless it persists.
- 2026-11-04: hyperion going down again for a second reimage (Louis: OS installed on the wrong disk). Its inventory:
  everything of value on the root disk nvme0n1p4 (~210 GB), nvme1n1p4 empty; repos clean and pushed; worktrees
  repaired; ~/+Simulations symlink; claude-mirror pre-reimage copy. Hub asked for per-serial SMART before any wipe.
- 2026-11-04: Louis on the overturn case: "Probably "Earth" ... that is the more "realistic" and likely to be more
  useful". 3957 (Earth run 2_c past the base, 23f509d, STOP_AT_BASE=0, n8, from 18:50) is the article run; TAf-v2_c is
  not continued past its base (the hub's "both" default withdrawn). ref4 (3955) paused at checkpoint 45 after its tip
  reached the base at 40 (top 0.111, deep 0.795, gap 2.0 cells; checkpoint 55 clean, ACCEPTANCE): complete, no
  resume; reached the base in about half the steps (~doubled dt). development f631ce42 carries #937 (#902) and #938
  (#935), both merged green (DEV-HUB); kaiju built an overlay (~/+Claude/kaiju/uw3/overlay-dev-f631ce42) and runs the
  merged-build np 16 vs np 52 test on the production mesh, exclusive, no workarounds, plus np 32 if a node is free.
- 2026-11-04: resolution page (B83QxCPeYmX2f9HMjx9W4e): ref4 ~17x cheaper to the base (0.25 h vs 4.4 h; 23 vs 197 s
  per step; 40 vs 80 steps); same slab shape at matched depth, but it runs ahead (vrms peak 1521 at t 1.2e-4 vs
  ~1440-1500 at 1.8e-4; plates 5323 vs 3631; base at t 1.89e-4 vs 2.20e-4) and at the base the trench has retreated
  less (-5.3 vs -8.1 deg) and the fault slipped less (2382 vs 4273). Kaiju: a fast preview of the descent, not a
  substitute where trench and slip matter; cause suspected to be the one-cell band at twice the physical width
  (a hypothesis: it is confounded with the lid and slab boundary layers at half the cells). Hub's note: two points
  cannot show production is converged; a 35-45 % change in trench and slip from ref4 to ref5 means ref5 itself may
  be off by a fair fraction of that, so refinement 6 (np 52, now possible on f631ce42) is the test of production.
  Movie page v5 (Q1Dq1epuXoEjPnKN7rzcKL): TAf-v2_c tracks TAf_env (step 70: tips 0.915 at t 2.0e-4, vrms 1289 vs
  1335); the step-10 straight cut is gone. Earth overturn 3957 clean at checkpoints 85/90/95; TAf-v2_c near its base
  (checkpoint 80: 1 % whole-cut hot, gap 1.16 cells). Merged-build test: np 52 (3959) running, np 16 (3960) and np 32
  (3961) queued. cell025 (3951) slow (448-cell coarse level), at checkpoint 5.
- 2026-11-04: **TAf-v2_c (3953) at the base** (tip on base at checkpoint 85, stopped after 90). Hand checks 60-90:
  0.0 whole-cut hot except 0.01 at 80; gap 1.0-1.23 base cells throughout. Not continued (Earth is the overturn
  run). Both recipe v2 baselines are now complete at the base with the built cut in the slab. Base movies against
  TAf_env re-rendering for the movie page. Earth overturn (3957) checkpoint 100 clean, gap 0.16 cells.
- 2026-11-04: **merged-build scaling (f631ce42, production mesh, no workarounds; 3960/3961/3959).** #935 verified on the
  production mesh at np 52 (0 owned wall points missing); #902 verified (custom FMG builds at np 52, no fallback);
  outer-wall |v.n| 6-7e-13 at all counts; fault in slab at all counts. s per step 223 / 187 / 189 at np 16 / 32 / 52
  (1.19x at 32 and 52). MG Apply 85-87 % of the time; MatSOR 1.45x and MatMult 1.17x from 16 to 52, VecScatterEnd
  up 220 -> 380 s: memory-bandwidth bound, the node saturates by np 32. The one-rank FAC patch is 1.6-2.3 % of the
  time: the ceiling on a decomposed SuperLU/MUMPS patch, not worth doing. Levers on kaiju, in order: resolution
  (ref4 ~17x, with caveats), packing np 16 runs (2.1x node throughput), fewer MG applications (warm Newton switch,
  inexact inner solve). More ranks per run is not one. Hub: kaiju's ref6 estimate (~8x the steps) contradicts its
  own ref4/ref5 pair (2x); ref6 should be ~160 steps to the base, ~35-40 h on one node; kaiju to restate. A 2-node x
  16 np 32 point ordered (bandwidth vs TCP scatter) for single long runs. ref6 waits on Louis.
- 2026-11-04: ref6 estimate restated by kaiju: ~160 steps to the base (2x, agreed), but ~9x per step from ref4 to
  ref5 (23 -> ~200-220 s, extra MG level and bandwidth-bound smoothers on a 4x working set), so ~30 min per step at
  np 16, ~25 at np 32; ~3.5-4.5 days to the base at np 16, ~3 at np 32 (+/- 30 %); memory ~70-90 GB at np 16. The
  hub's 35-40 h was wrong (it used kaiju's earlier 4-5x per step). Hub authorised a 3-step ref6 probe (fresh, np 32
  or 16, f631ce42 / 23f509d, one exclusive node) to pin it down; the run itself waits on Louis. 2-node x 16 point
  queued as 3971 (IPoIB TCP over ib0, not RDMA).
- 2026-11-04: Louis on the throughput levers: "Agreed - empirical, but let's try all these options." Queued on
  f631ce42 / 23f509d: 3971 (2 nodes x 16); 3972 (ref6 probe, np 32, steps 0-3); one packed job of three 16-rank
  runs from TAf-v2 checkpoint 20 (control, -uw_warm_newton_switch 3e-2, 1e-1; pack3_*), re-measuring packing
  against exclusive 3960 and the switch's saving and answer change. The ledger's warm-switch lever was the switch's
  reference (the rest-state residual, so warm steps run 5-6 Picard iterations); the arms raise its value instead, a
  proxy for the same effect. Inexact inner velocity solve: library-fixed on the rotated path; passed to the dev
  hub (For the other hubs).
