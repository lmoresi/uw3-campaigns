"""Review r2 probe (serial): the one-rank values behind the parallel test's constants,
and whether each fixture's flow is resolved or a guaranteed number."""
import importlib.util
import sys
from pathlib import Path

import numpy as np

import underworld3 as uw

worktree = Path(sys.argv[1])
sys.path.insert(0, str(worktree / "tests/parallel"))
spec = importlib.util.spec_from_file_location(
    "p0786", worktree / "tests/parallel/test_0786_stokes_rank_without_cells_parallel.py")
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)
import empty_rank_fixtures as erf


def run(name, mesh, walls, recorded):
    stokes, v = p._stokes(mesh, walls)
    stokes.solve()
    speed = float(np.linalg.norm(np.asarray(v.array)[:, 0, :], axis=1).max())
    its = stokes.snes.getIterationNumber()
    ksp_its = stokes.snes.getLinearSolveIterations()
    rel = abs(speed - recorded) / recorded
    print(f"{name}: cells {erf.cells_per_rank(mesh)}, reason {stokes.snes.getConvergedReason()}, "
          f"snes its {its}, ksp its {ksp_its}, speed {speed:.7e}, recorded {recorded:.7e}, "
          f"rel diff {rel:.2e}, moving nodes {(np.linalg.norm(np.asarray(v.array)[:, 0, :], axis=1) > 1e-12).sum()}"
          f" of {np.asarray(v.array).shape[0]}", flush=True)


mesh, walls, rec = p._box_of_two_cells()
run("box", mesh, walls, rec)
for n in (4, 8):
    dm = erf.right_triangle_of_cells(n, 1)
    dm.createLabel("All_Boundaries")
    dm.markBoundaryFaces("All_Boundaries", erf.ALL_BOUNDARIES_VALUE)
    run(f"triangle n={n}", uw.discretisation.Mesh(dm, qdegree=3), {"All_Boundaries": p.NO_SLIP},
        p.SPEED_TRIANGLE[n])
mesh, walls, rec = p._region_held_by_rank_0()
run("region", mesh, walls, rec)
