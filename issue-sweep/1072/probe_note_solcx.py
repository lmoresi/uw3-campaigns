"""#1072: the SolCx test of UWTN 2026-016 with Nitsche on the top wall.

The note's own `examples/solcx.py` (copied unchanged to `note_016/`) is
imported and its `measure` is run for the Nitsche column, which the note
leaves out because the solve did not converge. We print the SNES reason and
the iteration counts with the note's metrics, whether the solve converged or
not, and the component Dirichlet column beside it as the reference.

Parts (`-uw_part`):
  sweep     elements 16, 32, 64 at a viscosity contrast of 1e6
  contrast  contrast 1e1 to 1e6 at 32 elements
  gamma     gamma 1, 10, 12.5, 100, 1000 at 32 elements, contrast 1e6

Serial.
"""
import pathlib
import sys

import underworld3 as uw

sys.path.insert(0, str(pathlib.Path(__file__).parent / "note_016"))
import solcx  # noqa: E402

params = uw.Params(part="sweep")
part = str(params.part)
print(f"part={part}", flush=True)

solved = {}
build = solcx.build


def build_and_keep(mode, **kwargs):
    made = build(mode, **kwargs)
    solved["stokes"] = made[1]
    return made


solcx.build = build_and_keep
solcx.converged = lambda stokes: True


def row(label, mode, **kwargs):
    got = solcx.measure(mode, **kwargs)
    snes = solved["stokes"].snes
    print(
        f"| {label} | {mode} | {snes.getConvergedReason()} | {snes.getIterationNumber()} "
        f"| {snes.getLinearSolveIterations()} | {got['soft']:.2e} | {got['stiff']:.2e} "
        f"| {got['velocity']:.2e} | {got['recovered']:.2e} | {got['trimmed']:.2e} |",
        flush=True,
    )


print("| case | wall | reason | newton | linear | leak soft | leak stiff | velocity | stress | stress trimmed |")
print("|---|---|---|---|---|---|---|---|---|---|")
if part == "sweep":
    for res in (16, 32, 64):
        for mode in ("dirichlet", "nitsche"):
            row(f"res {res}", mode, res=res)
elif part == "contrast":
    for ratio in (1.0e1, 1.0e2, 1.0e3, 1.0e4, 1.0e6):
        for mode in ("dirichlet", "nitsche"):
            row(f"contrast {ratio:.0e}", mode, eta_B=ratio)
elif part == "gamma":
    for gamma in (1.0, 10.0, 12.5, 100.0, 1000.0):
        row(f"gamma {gamma:g}", "nitsche", gamma=gamma)
else:
    raise ValueError(part)
