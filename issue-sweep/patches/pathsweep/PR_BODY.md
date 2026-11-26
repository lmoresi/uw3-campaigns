## docs: a developer's home-directory paths become placeholders

**Why.** Examples, design notes and review records under `docs/` carried absolute paths in two developers' home directories: checkpoint directories, simulation output, worktrees, and a downloaded reference. Each is now a placeholder, `~/path/to/...`, that keeps the part naming what the path is. There are 44 lines in 17 files.

| was | now |
|---|---|
| `<home>/+Simulations/...` | `~/path/to/simulations/...` |
| `<home>/+Underworld/underworld3-pixi/.claude/worktrees/...` | `~/path/to/worktrees/...` |
| `<home>/+Underworld/underworld3-pixi/`, `.../underworld-pixi-2/underworld3`, `.../underworld3/` | `~/path/to/underworld3...` |
| `<home>/+Underworld/underworld-pixi-2/petsc/` | `~/path/to/petsc/` |
| `<home>/Downloads/`, a second developer's `Documents/codes/` | `~/path/to/` |

An example's `checkpoint_dir`, or a script's `FIG`, now reads as a placeholder to set. The original path also had to be set on any other machine.

**Left as they are.**
- The saved PETSc traceback in the stderr output of cell 11 of `docs/beginner/tutorials/17-Richards-Transient-Wetting-Front.ipynb` (5 lines). It is quoted output.
- A path inside a binary spreadsheet, `docs/examples/WIP/Geographical/Structures/InferredFaults_Depths_20250401.numbers`.

**Text only.**
- In the 8 Python files, only comments and string constants change: the AST with docstrings dropped and strings replaced by a placeholder is identical (`astdiff.txt`).
- The other 9 files are Markdown.
- It merges cleanly with the `tests/`, `src/` and `docs/` session-code sweeps.

**Base.** development fbef72fa. One commit, as a `git format-patch` file. Not pushed (GitHub pause).

Underworld development team with AI support from Claude Code
