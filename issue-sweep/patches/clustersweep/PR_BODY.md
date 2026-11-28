## docs, src, tests: name clusters by their code names, described as systems

**Why.** This applies the platform-naming ruling: a system is named by its code name and described as a system, never by a hostname, IP, login node, username or filesystem path.
- Kaiju becomes **the RSES kaiju platform**. Each document describes it once, near its first mention, using only the facts in `hpc-cluster-setup.md`: "a Slurm system of 8 compute nodes, each with 104 logical CPUs (two Intel Xeon Gold 6230R)" (or "... from two Intel Xeon Gold 6230R processors" where a parenthesis would nest or follow another). The container README's table row says the same, with its base image (Rocky 8.10, the image built for Gadi). That guide states no interconnect, so none is given.
- Gadi becomes **NCI's Gadi** at its first mention in a document; later mentions stay "Gadi".

There are 36 edits on 36 lines in 23 files (docs, plus Gadi comments in 4 source and 3 test files).

**Left as they are.**
- **Identifiers:** the `UW_CLUSTER=kaiju|gadi` values (`hpc-cluster-setup.md:21`), the install and job-script names (`kaiju_install_user.sh`, `kaiju_slurm_job.sh`, `gadi_pbs_job.sh`, ...), and the container image tags (`petsc-gadi`, `underworld3-gadi`).
- **The quickstart's link:** it already names "GADI, at the National Computational Infrastructure".
- **Kaiju in src/ and tests/:** those lines are reworded to "a Linux cluster" by the separate session-code and host-name sweeps of those directories, which this merges with cleanly.

**For the maintainer's decision (not changed):** `hpc-cluster-setup.md` gives two filesystem paths users need.
- The shared Gadi install, `source /g/data/m18/software/uw3-pixi/gadi_install_shared.sh` (line 259), which names a project code.
- The kaiju shared storage, `/opt/cluster` (its Hardware table).

The ruling's "never a filesystem path" would replace them with placeholders, but users of the shared install need the real location.

**Text only.**
- For the 7 Python and Cython files, the token streams with comment and string contents blanked are identical. For the 6 Python files, the ASTs with docstrings and strings stripped are identical too.
- The one JSON file (`docs/docstrings/inventory.json`, which mirrors `_params.py`'s comment) still parses.
- The rest is Markdown and comments. A review document quotes the `petsc_generic_snes_solvers.pyx` comment, so the two change together.

**Docs build.** `sphinx -b html docs` on development and on this branch: 89 warnings each, identical once paths are normalised (the edited tables included).

**Base.** development fbef72fa. One commit, as a `git format-patch` file. It merges cleanly with the tests/, src/, docs/ and local-paths sweeps. Not pushed (GitHub pause).

Underworld development team with AI support from Claude Code
