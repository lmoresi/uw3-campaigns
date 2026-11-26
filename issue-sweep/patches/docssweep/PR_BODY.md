## docs: describe the review or the machine, not session codes or host names

**Why.** Developer notes and review records under `docs/` named the review sessions that took a measurement, by their internal codes, or the workstation it was taken on, by its host name. Each one now says what matters:
- "review, M2", or "the review's fixture";
- "a 96-thread Linux workstation", or "a workstation", where the machine matters.

There are 15 edits on 12 lines in 6 files:
- `CONVERGENCE_REFERENCE_POLICY_2026-11.md`
- `CHANGELOG.md`
- `rotated-freeslip.md`
- `parallel-addon-distribution-2026-10.md`
- `fault-multigrid.md`
- `docs/reviews/2026-10/stress-snapshot-order-adversarial-review.md`

**Left as they are, deliberately.**
- **Cluster and platform names.** Kaiju and Gadi, including where a measurement was made on a cluster (26 lines, `cluster_mentions_left.txt`). Whether a cluster may be named as a supported platform is a maintainer decision, still open. The HPC set-up guides depend on these names.
- **Local paths.** `/Users/...` paths in examples, review records and a tutorial's saved PETSc traceback (18 files, `local_paths_left.txt`). These are outside this change.
- **False positives.**
  - the C1/C2 test categories and review item labels;
  - matplotlib's `color='C1'`;
  - the H1-H5 metric variables and K1 matrices in examples;
  - the W1-W5b example names;
  - "C1-continuous";
  - the container paths `/home/jovyan` and `/home/mambauser`.

**Text only.** Every change is Markdown prose, and no code, notebook or configuration file changes.

**Base.** development fbef72fa. One commit, as a `git format-patch` file. Not pushed (GitHub pause).

Underworld development team with AI support from Claude Code
