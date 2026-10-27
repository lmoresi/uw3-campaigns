# What the wiki holds, and where each piece goes

**Status**: inventory by the docs hub, 2026-10-27, from a clone of `underworld3.wiki`
at its head of 2026-10-18. Input to Phase 1 of `INFORMATION-FLOW-PROPOSAL.md`.

## The shape of it

Nineteen pages, about 30,000 words, 72 figures, all written since 2026-10-05, in 40
commits over ten days. It is the most alive channel the project has, which is the case
for keeping what it holds and against keeping it where it is.

Three things stand out before any page is read:

1. **The commit log is already the journal.** Forty messages of the form "Box fault: 60
   degree walk is left-lateral (slip sense corrected)" or "Fault multigrid: orphan
   injection retired", each dated, each one finding. The hand-kept History sections at the
   foot of the pages duplicate it, less completely. Migration is therefore mostly a
   mapping from commits to entries, not a rewrite.
2. **"What did not work, and why" is the content nothing else holds.** Nine pages carry
   such a section, about forty dead ends in all, each with the reason and usually a
   number: the per-cell fit that overshot 0.89, 1.29, 3.05 over three steps; three weeks
   of nonlinear remedies for a linear failure; the lagged stretch that blew up in all
   three forms. None of this is in `docs/`, and `docs/` has no genre for it.
3. **It has started to rot in the wiki's way.** `Fault multigrid` says its rulings "are
   written in the technical notes" and names `FAULT_MULTIGRID_HIERARCHIES.md`, which does
   not exist in `docs/developer/design/`; the two that do exist there carry no status
   line. `Viscoelastic steady shear benchmark` names `tests/test_1068_fene_p.py`; test
   1068 is now the Picard warm-up test. Three weeks is enough.

## Four genres, four destinations

| Genre | Pages | Words | What it is | Goes to |
|---|---|---|---|---|
| Topic page | Fault multigrid, Shear-band length scales, Solvers and multigrid, Viscoelastic constitutive models, Viscoelastic stretch at large steps, Transport histories, Particle-to-field projection | 19,600 | current understanding, equations, rulings, dead ends, open questions | split three ways: rulings and recipes to capability guides, equations to subsystem pages, findings and dead ends to journal entries; the page itself becomes a journal topic page holding the short conclusion and the entry list |
| Benchmark page | Benchmarks (index), steady shear, Waters-King, confined cylinder, creeping cylinder, cross-slot, Spiegelman notch | 2,900 | problem, references, our status, what we claim and do not, next target | `docs/advanced/benchmarks/`, which already holds the ve-square, ve-harmonic and vep-square pages in a different format; one format, one index, each page naming its test |
| Campaign page | Cylinder campaign 2026, Spiegelman notch campaign 2026, Box fault cyclic loading, Tidal faulted shell | 7,400 | what was run, in order; results that stand and results to discount; figures | journal entries, one per commit, plus one campaign summary entry when the campaign closes; the box-fault and tidal-shell pages are paper drafts in wiki clothing and go on toward a note or paper |
| Process | Home, How we plan | 900 | the lifecycle and the planning protocol | Home becomes the pointer to the journal; How we plan is superseded by the proposal |

## Page by page

| Page | Offers | Destination | Notes |
|---|---|---|---|
| **Fault multigrid** (7,345 w, 18 figs) | three rulings (base never cut or rebalanced; one hierarchy for split and TI; no bespoke meshes); the four hierarchies tried and why C won; the ladder measurements; seven dead ends; the parallel imbalance decomposed | rulings and "which hierarchy when" to a new capability guide `fault-multigrid.md` (families Stokes, Stokes_Constrained); the formulation to `docs/advanced/split-node-faults.md` and `multigrid-preconditioning.md`, which exist and do not say this; measurements and dead ends to entries | the only fault-multigrid guidance agents can read today; `docs/` mentions "split-level" or "add-on" in one file. The three design docs it cites need status lines or deletion in the same PR. |
| **Shear-band length scales** (4,701 w, 109 equations) | two regularisations with full weak forms; width independent of refinement through level 5; Cosserat against micromorphic at equal width; multigrid cost; nine dead ends including rate strengthening alone | the formulations to a subsystem page (`constitutive-models-theory.md` is 876 words and does not cover this); the choice of defaults to `plasticity-solvers.md`; results to entries; the whole thing is a technical note in waiting (the writing plan's viscoplastic cluster) | branch `feature/shear-band-length-scale` is not merged, so the subsystem page waits on the PR; the journal does not. |
| **Solvers and multigrid** (2,220 w) | standing rules, the yield law and soft-min equations, two linear failure modes, twelve dead ends | the standing rules are already in CLAUDE.md and the `nonlinear-solver` and `plasticity-solvers` guides; check the three agree and fold the rest into those guides; dead ends to entries | the page says itself that the recipes are the skills; it is the guides' annex. |
| **Viscoelastic constitutive models** (1,542 w, 20 equations) | the model library as three independent choices; the equations per model and per step; FENE-P stored as log(f c) and why; five dead ends | equations to `subsystems/stress-transport.md` (the page names it as "usage") or a sibling theory page; dead ends to entries | links Discussion #815 as "the argument", the one Discussion the wiki cites. |
| **Viscoelastic stretch at large steps** (2,882 w) | a complete investigation: Jacobian spectrum, seven approaches in a table with outcomes, the switching policy, the cost accounting, corrections from an adversarial review | one `finding` entry per History line (three), the approaches table as the body; the switching policy as a paragraph in the transport or constitutive guide | the model of what a journal entry should look like; it already has the three-part shape. |
| **Transport histories** (475 w) | four histories and the Eulerian path, what each is good at, four dead ends | `guides/transport-schemes.md` exists with the right families; fold "what each is good at" into it; dead ends to entries | smallest gap: the guide is there, the findings are not in it. |
| **Particle-to-field projection** (430 w) | what we do now and four dead ends with numbers; one open item | a paragraph in the swarm or interpolation subsystem page; dead ends to entries | the Barth-Jespersen limiter "stays in the code, off" is a `TODO(DESIGN)` the code should carry. |
| **Benchmarks** + six benchmark pages | an index by family; per benchmark the problem, references, status, claims, next target | `docs/advanced/benchmarks/`, merged with the three pages already there into one format; each names its test file | the index's "what we learned about benchmarking itself" (three rules) belongs in the Charter's test section, where two of the three already are. |
| **Cylinder campaign 2026**, **Spiegelman notch campaign 2026** | the run sequence, results that stand, results to discount, lessons pointed elsewhere | entries; the "results to discount" sections are dead-end entries | both already separate standing from discounted results, which is the verdict rule the proposal asks for. |
| **Box fault cyclic loading**, **Tidal faulted shell** (5,100 w, 20 figs) | problem statement, implementation as built, results sections with figures, references | entries per commit (fourteen and six); the pages as campaign summaries; the results toward a note with Mark Simons | no History and no dead-end section on either: written as papers, not as notes. The ETD expression-viscosity bug found here is PR #851. |
| **Home**, **How we plan** | the lifecycle rule and the planning protocol | Home becomes a pointer; How we plan is replaced by the proposal | the lifecycle rule ("graduates when it stops moving") was right; nothing enforced it. |

## What the migration produces

- about 40 `finding` and `measurement` entries from the commit log, dated as committed;
- about 40 `dead-end` entries from the nine "What did not work" sections, dated from the
  History lines where possible;
- 7 topic pages with a short conclusion each, which is the opening paragraph each wiki
  page already has;
- 6 benchmark pages in `docs/advanced/benchmarks/`, in one format with the three there;
- 4 capability-guide changes (fault multigrid new; nonlinear-solver, plasticity-solvers
  and transport-schemes extended) and 2 subsystem-page changes (stress-transport or a
  theory sibling; split-node-faults), each a PR on underworld3;
- 72 figures, moved with their entries; the scripts that made them are in uw3-campaigns
  and the entries link them;
- a frozen wiki whose Home says where everything went.

Effort: the entries are mechanical and the docs hub can do them in a day once the journal
exists; the guide and subsystem PRs are a week of careful writing, each reviewable on
its own, and the shear-band subsystem page waits on its branch merging.

## Two corrections the migration makes on the way

- The fault-multigrid rulings are stated in the wiki, partly in CLAUDE.md, and in two
  design docs with no status; after migration they are stated once, in the guide, and the
  design docs either fold into it or carry a status line pointing at it.
- Benchmarks are split between the wiki (viscoelastic transients, the notch) and
  `docs/advanced/benchmarks/` (viscoelastic squares and harmonics) in two formats with no
  cross-reference; after migration there is one index.
