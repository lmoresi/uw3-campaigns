"""H7: cluster names by code name (Louis's ruling, 2026-11-28, via C1). The RSES kaiju
platform, described once per document from hpc-cluster-setup.md's own facts; NCI's Gadi
at its first mention in a document. Identifiers stay: UW_CLUSTER values, script names,
container image tags. (file, line, old, new); nothing is written unless all match."""
import sys
K = "the RSES kaiju platform"
KD = "the RSES kaiju platform (a Slurm system of 8 compute nodes, each with 104 CPUs, Intel Xeon Gold 6230R)"
D = "docs/developer/"
E = [
# fault-split-multigrid.md
(D + "subsystems/fault-split-multigrid.md", 156, "add-on matrix's box (kaiju,", "add-on matrix's box (" + KD + ","),
(D + "subsystems/fault-split-multigrid.md", 168, "networks (kaiju, np 4 to 16, 2026-11)", "networks (the kaiju platform, np 4 to 16, 2026-11)"),
(D + "subsystems/fault-split-multigrid.md", 496, "rows in the block; kaiju, 2026-11)", "rows in the block; the kaiju platform, 2026-11)"),
# CONVERGENCE_REFERENCE_POLICY
(D + "design/CONVERGENCE_REFERENCE_POLICY_2026-11.md", 88, "(kaiju measured 28-57 % of Stokes time)", "(measured on " + KD + ": 28-57 % of Stokes time)"),
(D + "design/CONVERGENCE_REFERENCE_POLICY_2026-11.md", 102, "- the zg95 rotated drivers (kaiju);", "- the zg95 rotated drivers (the kaiju platform);"),
# faults-in-convection.md
(D + "guides/faults-in-convection.md", 73, "np 16 (kaiju, `development` 25d62812", "np 16 (" + KD + ", `development` 25d62812"),
(D + "guides/faults-in-convection.md", 81, "accepted on kaiju at np 16)", "accepted on the kaiju platform at np 16)"),
# fault-multigrid.md
(D + "guides/fault-multigrid.md", 124, "annulus at np 16 (kaiju,", "annulus at np 16 (" + KD + ","),
(D + "guides/fault-multigrid.md", 131, "kaiju at np 16; the drivers'", "the kaiju platform at np 16; the drivers'"),
(D + "guides/fault-multigrid.md", 287, "kaiju's budget)", "the kaiju platform's budget)"),
(D + "guides/fault-multigrid.md", 301, "kaiju (2026-11-01)", "the kaiju platform (2026-11-01)"),
# hpc_containers
(D + "hpc_containers/README.md", 14, "Gadi, Kaiju", "NCI's Gadi, RSES kaiju"),
(D + "hpc_containers/README.md", 26, "| Gadi | Rocky 8.10 |", "| NCI's Gadi | Rocky 8.10 |"),
(D + "hpc_containers/README.md", 27, "| Kaiju | same image as Gadi |", "| the RSES kaiju platform (Slurm, 8 compute nodes of 104 CPUs) | same image as Gadi |"),
(D + "hpc_containers/base.rocky-ompi", 2, "(NCI Gadi, ANU Kaiju).", "(NCI's Gadi, the RSES kaiju platform)."),
# hpc-cluster-setup.md (its Hardware table describes the system)
(D + "guides/hpc-cluster-setup.md", 25, "## Kaiju", "## The RSES kaiju platform"),
(D + "guides/hpc-cluster-setup.md", 79, "#### What PETSc builds on Kaiju", "#### What PETSc builds on the kaiju platform"),
(D + "guides/hpc-cluster-setup.md", 110, "is **required** on Kaiju (", "is **required** on the kaiju platform ("),
(D + "guides/hpc-cluster-setup.md", 134, "### Troubleshooting (Kaiju)", "### Troubleshooting (the kaiju platform)"),
(D + "guides/hpc-cluster-setup.md", 165, "## Gadi", "## NCI's Gadi"),
# Gadi, first mention per document
(D + "CHANGELOG.md", 895, "Gadi Singularity container build", "NCI's Gadi Singularity container build"),
(D + "subsystems/boundary-stress-and-projection-postprocessing.md", 25, "OOM-killed mid-sequence on Gadi.", "OOM-killed mid-sequence on NCI's Gadi."),
(D + "subsystems/solvers.md", 332, "Gadi at np=144", "NCI's Gadi at np=144"),
(D + "guides/release-process.md", 333, "(NCI Gadi or Pawsey Setonix)", "(NCI's Gadi or Pawsey Setonix)"),
(D + "design/petsc-dmplex-checkpoint-reload-plan.md", 196, "allocation on Gadi.", "allocation on NCI's Gadi."),
("docs/advanced/performance.md", 28, "In a controlled Gadi campaign", "In a controlled campaign on NCI's Gadi"),
("docs/advanced/troubleshooting.md", 73, "**Reported thresholds.** On Gadi (", "**Reported thresholds.** On NCI's Gadi ("),
("docs/reviews/2026-07/solver-wall-clock-guard-adversarial-review.md", 74, "\"at Gadi scale", "\"at NCI's Gadi scale"),
("docs/docstrings/inventory.json", 48128, "(e.g. Gadi),", "(e.g. NCI's Gadi),"),
("src/underworld3/utilities/_params.py", 161, "(e.g. Gadi),", "(e.g. NCI's Gadi),"),
("src/underworld3/utilities/_jitextension.py", 1990, "RTLD_Global, Gadi.", "RTLD_Global, NCI's Gadi."),
("src/underworld3/utilities/_petsc_tools.py", 38, "(Gadi being the case in #111)", "(NCI's Gadi being the case in #111)"),
("src/underworld3/cython/petsc_generic_snes_solvers.pyx", 5344, "# Gadi scale to push past", "# NCI's Gadi scale to push past"),
("tests/test_1063_constrained_traction.py", 34, "stalls on Gadi.", "stalls on NCI's Gadi."),
("tests/test_0821_params_cli_override.py", 4, "(e.g. Gadi)", "(e.g. NCI's Gadi)"),
("tests/test_1181_cylindrical_dirichlet.py", 302, "The Gadi MPI16 gate first", "The MPI16 gate on NCI's Gadi first"),
]
root = sys.argv[1]; bad = 0; files = {}
for f, ln, old, new in E:
    lines = files.setdefault(f, open(f"{root}/{f}").read().split("\n"))
    if lines[ln - 1].count(old) != 1:
        print(f"NO MATCH {f}:{ln}: {old!r}"); bad += 1; continue
    lines[ln - 1] = lines[ln - 1].replace(old, new)
if bad: sys.exit(f"{bad} edits did not match; nothing written")
for f, lines in files.items():
    open(f"{root}/{f}", "w").write("\n".join(lines))
print(f"{len(E)} edits in {len(files)} files")
