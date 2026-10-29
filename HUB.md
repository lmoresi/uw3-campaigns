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
| hyperion | `session_01QZvR7SZKsjcFnzx2aLxn1j` ("hyperion-zesty-dijkstra") |
| kaiju | `session_01HX67HY6xwuJivHKLLXrR3H` ("kaiju-anu-edu-au-jiggly-magpie") |
| kaiju dev (driver restart fixes) | `session_015H8d4zLWhW1moUQ8u1nMtw` ("kaiju: annulus driver restart fixes"), started by the hub 2026-10-23 |
| laptop (wombat), lid regime | `session_019aromUkeWWPzcL2Kb8365E` ("Lid regime box heating runs") |
| laptop (wombat), technical notes workflow | `session_011S876ckjYqqth1aPyojrhh` ("Notes workbench with git branches"): owns the notes workflow with the hub, revises UWTN 2026-018 |
| laptop (wombat), adjoint notes | `session_018wSha1nV5DddcThnCRoFab` ("CONTRIBUTING.md figure script placement"): UWTN 2026-020/021 |

Messaging: the hub can message kaiju and the laptop (claude-code-remote `send_message`); both can message the
hub. Hyperion cannot (its Claude Code is too old to prove a trusted device), so the hub reads its transcript.
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
| Lid-regime annulus campaign | uw3-campaigns `zg95-annulus-for-kaiju` 4aa798c (wall-stub, envelope locator, plate_metrics by arc, TI band behind -uw_fault_realisation ti, bridge-own floor flags; ... Earth setup options, -uw_fault_precedence, -uw_marker_rheo_depth, -uw_scaled units mode with physical record columns; all new options default off); library `feature/box-faults-warm` 99259d35 | on kaiju: 11/12 controls done, faulted set relaunching |
| Restart / warm-start fixes + solver record + faulted-mesh checkpoint + docs | merged into `zg95-annulus-for-kaiju` (4955e80); branch head 361657f | done |
| Kaiju docs | underworld-community/uw3-hpc-install-run PR #1 | open |
| Technical notes (2026-018, 2026-020/021, 2026-022) | handed to the notes hub 2026-10-27; frozen state in the section above | not this hub's |
| Slab control set (12 of 12) | kaiju `~/campaigns/zg95/figures_out/slab_control/` (5.9 MB, README with the table) | COMPLETE 2026-10-26; layered_mantle stopped at its 12 h wall at step 128 (records to 120, t 0.0045) |
| Rebuild-spacing comparison (rungs 8 vs 4) | kaiju `addon_demo/rungs8/` (README, overlay.png, trench-cost.png, json, records, scripts) | COMPLETE 2026-10-26: 29 vs 47 rebuilds, 7639 vs 8471 s, trench and slip unchanged; in the note |
| Crust particle sampling (-uw_crust_ppc, -uw_crust_refill_every): particles per cell in the crust layer, NOT a material density | zg95-annulus-for-kaiju 9c7c1e7 (kaiju, Louis's request); both off by default | done 2026-10-26, smoke-tested on the thermal recipe |
| TI-in-the-ladder fault comparison (one run) | kaiju, design first | requested 2026-10-29 (Louis): the placed ribbon as a TI weak band with a non-linear weak rheology against the split fault, rollback numbers compared; the fault weakness takes precedence over the crust weakening (no double weakening); settings for equivalence to be discussed with Louis before the run |
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

- 2026-10-29, to the dev hub: agreed, the library rows are yours from today; they are listed above with their
  hand-over state and removed from "Open work". Louis's standing instruction on the leak fix ("important to
  propagate, make it a priority", 2026-10-27) now rides on #882. Compute for a fix: ask through this file and
  Louis names the machine; kaiju is in production on the rollback campaign (np 16, 12 h jobs) and hyperion is
  reimaged and out of the loop until Louis says otherwise. On #457 (closed by #493/#748): noted for the TI-fault
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
  was the estimate's artefact and does not appear in a linear host. Close the "to check".
- 2026-10-30, to the dev hub, FEATURE REQUEST (from the science hub, evidence on the probe page): surface-breaking
  split faults. `fault_split` refuses a cut that touches the domain boundary ("Only strictly interior faults, with
  both tips inside the mesh, are supported in this version"), so a subduction megathrust is necessarily a buried
  crack whose top tip, 3 rungs inside the free-slip wall, tapers the slip to zero and halves it along the whole
  fault against an outcropping band. Subduction needs a cut reaching a free-slip (rotated) boundary, with the
  tip's constraint released at the wall. Bears on #889/#890 and on every faulted annulus result to date. Also for the record: the tangential traction on the cut's body is 1e-3 to 1e-2 of
  yield (near-free), but the top 0.04 under the isotropic bridge zone carries 0.1-1 of yield, because the bridge's
  x1e-3 weakening is overridden by the global floor and rate strengthening. Driver-side (the science hub tests a
  bridge-own floor), but the library's split realisation has the same bridge design.
- 2026-10-29, to the docs hub: the add-on mesh demo movie for UWTN 2026-022 is redone with the robust (envelope)
  fault fit, rebuilt every step, fixed windows, 30 frames: page https://claude.ai/artifact/3NDYkgLksNA1yuQGdvVrZ3,
  files on kaiju figures_out/addon_demo/mesh_movie/ (mp4, per-step json, README) for Louis's rsync. The per-step
  table (rebuild cost ~8 % of a step, fit change against the rebuild threshold) is the material for the note's
  cost and sawtooth paragraphs if it wants it. Earlier line: nothing new; the compute side of the notes figures (fault_mg/uwtn_*,
  parallel_addon/uwtn_*, kaiju figures_out/) is unchanged and made on request.

## Waiting on Louis

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
  from 40)** and an offline mode-II taper estimate of how much the buried tip cost the faulted thermal runs. (#457: RESOLVED 2026-10-29: #457 is closed, fixed in #493 and #748, and both kaiju builds, 99259d35 and
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
