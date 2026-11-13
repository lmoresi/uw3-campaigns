"""Time the transfer with and without the one-coarse-cell bookkeeping, per pass.

Same process, same DMs, each timed twice and the smaller taken. The 'without'
function is the PR's text with the condition removed and the vertex-to-cell
table not built.
"""
import importlib.util, inspect, re, textwrap, time
import numpy as np
import underworld3 as uw
from underworld3.utilities import nvb
from underworld3.utilities._nvb_transform import refine

params = uw.Params(cell_size=0.3, passes=4, root=".")
spec = importlib.util.spec_from_file_location("t0449", f"{params.root}/tests/test_0449_nested_transfer_3d_rows.py")
t = importlib.util.module_from_spec(spec); spec.loader.exec_module(t)

source = textwrap.dedent(inspect.getsource(nvb._nested_prolongation_local))
without = source.replace(" and in_one_cell(p_, q_)", "")
start = without.index("        ccS, ccE = coarse_dm.getHeightStratum(0)")
stop = without.index("        nbr = [[] for _ in range(n_f)]")
without = (without[:start] + without[stop:]).replace("def _nested_prolongation_local", "def _without")
scope = dict(nvb.__dict__); exec(compile(without, "<without>", "exec"), scope)

def best(f, *a):
    out = []
    for _ in range(2):
        t0 = time.perf_counter(); r = f(*a); out.append(time.perf_counter() - t0)
    return min(out), r

mesh = uw.meshing.UnstructuredSimplexBox(minCoords=(0.0,)*3, maxCoords=(1.0,)*3,
                                         cellSize=params.cell_size, refinement=1)
coarse = mesh.dm.clone(); coarse.setCoordinatesLocal(mesh.dm.getCoordinatesLocal())
nvb.write_tagged_state_label(coarse)
print(f"cell_size={params.cell_size} passes={params.passes}")
for k in range(params.passes):
    t0 = time.perf_counter(); fine = refine(t._marked(coarse)); t_refine = time.perf_counter() - t0
    t_with, r1 = best(nvb._nested_prolongation_local, coarse, fine)
    t_without, r0 = best(scope["_without"], coarse, fine)
    cS, cE = coarse.getHeightStratum(0); vS, vE = fine.getDepthStratum(0)
    print(f"COST pass {k}: coarse cells {cE - cS}, fine vertices {vE - vS}; refine {t_refine:.2f} s; "
          f"transfer with the rule {t_with:.2f} s, without {t_without:.2f} s "
          f"(ratio {t_with / t_without:.2f})", flush=True)
    coarse = fine
