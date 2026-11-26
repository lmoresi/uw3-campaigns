## docs: a developer's home-directory paths become placeholders

**Why.** Examples, design notes and review records under `docs/` carried absolute paths in two developers' home directories: checkpoint directories, simulation output, worktrees, and a downloaded reference. Each is now a placeholder that keeps the part naming what the path is: `~/path/to/...` in prose and shell comments, and `path/to/...` inside Python strings, where a `~` is never expanded. There are 44 lines in 17 files.

| was | now |
|---|---|
| `<home>/+Simulations/...` | `~/path/to/simulations/...` (`path/to/simulations/...` in a Python string) |
| `<home>/+Underworld/underworld3-pixi/.claude/worktrees/...` | `~/path/to/worktrees/...` |
| `<home>/+Underworld/underworld3-pixi/`, `.../underworld-pixi-2/underworld3`, `.../underworld3/` | `~/path/to/underworld3...` |
| `<home>/+Underworld/underworld-pixi-2/petsc/` | `~/path/to/petsc/` |
| `<home>/Downloads/`, a second developer's `Documents/codes/` | `~/path/to/` |

No code change; seven example path values (a `checkpoint_dir`, `outdir` or `FIG`) become placeholders to set, as the original paths were on any other machine. Two commented-out lines that joined two paths by mistake keep the second, and a quoted shell path loses its quotes so that its `~` expands.

**Left as they are.**
- The saved PETSc traceback in the stderr output of cell 11 of `docs/beginner/tutorials/17-Richards-Transient-Wetting-Front.ipynb` (5 lines). It is quoted output.
- The owner column of an `ls -l` listing in a WIP notebook (out of scope).
- A path inside a binary spreadsheet, `docs/examples/WIP/Geographical/Structures/InferredFaults_Depths_20250401.numbers`.

**Text only.**
- In the 8 Python files, only comments and string constants change: the AST with docstrings dropped and strings replaced by a placeholder is identical (`astdiff.txt`).
- The other 9 files are Markdown.
- It merges cleanly with the `tests/`, `src/` and `docs/` session-code sweeps.

**Base.** development fbef72fa. One commit, as a `git format-patch` file. Not pushed (GitHub pause).

Underworld development team with AI support from Claude Code
