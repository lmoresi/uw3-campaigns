"""#1142 re-check: a failed history transfer inside the SemiLagrangian DDt's on_remesh
hook (the ALE opt-out REMAP path) reaches the caller, on every rank, after the move.
Rank 1 fails once, after the evaluation's collectives, for a variable the hook owns."""
import sys, numpy as np, sympy, underworld3 as uw
from underworld3.discretisation import remesh

case = sys.argv[1] if len(sys.argv) > 1 else "fail"
mesh = uw.meshing.UnstructuredSimplexBox(minCoords=(0, 0), maxCoords=(1, 1), cellSize=1 / 12, qdegree=3)
T = uw.discretisation.MeshVariable("T", mesh, 1, degree=2)
V = uw.discretisation.MeshVariable("V", mesh, 2, degree=1)
adv = uw.systems.AdvDiffusionSLCN(mesh, u_Field=T, V_fn=V.sym, order=1)
adv.constitutive_model = uw.constitutive_models.DiffusionModel
adv.constitutive_model.Parameters.diffusivity = 1.0
tc = np.asarray(T.coords); T.data[:, 0] = tc[:, 0] + 2 * tc[:, 1]
owned = [v for v in mesh.vars.values() if getattr(v, "_remesh_managed_by", None) is not None]
for v in owned:
    vc = np.asarray(v.coords); d = np.array(v.data); d[:] = (vc[:, 0] - vc[:, 1])[:, None]; v.data[...] = d
before = {v.clean_name if hasattr(v, "clean_name") else v.name: np.asarray(v.data).copy() for v in owned}

orig = uw.function.global_evaluate
fired = []
def ge(*a, **k):
    val = orig(*a, **k)
    if case == "fail" and not fired and uw.mpi.rank == 1 and sys._getframe(1).f_code.co_name == "remap_var_set" \
            and sys._getframe(2).f_code.co_name == "on_remesh":
        fired.append(1); print("FORCED failure on rank 1 inside the DDt hook's remap", flush=True)
        raise RuntimeError("forced failure after the evaluation")
    return val
uw.function.global_evaluate = ge

c0 = np.asarray(mesh.X.coords).copy(); x, y = c0[:, 0], c0[:, 1]
inside = (x > 1e-9) & (x < 1 - 1e-9) & (y > 1e-9) & (y < 1 - 1e-9)
c1 = c0.copy(); c1[inside, 0] += 0.02 * np.sin(np.pi * x[inside]) * np.sin(np.pi * y[inside])

def do_move():
    mesh._remesh_pending_scratch["ale_opt_out"] = True     # a discrete jump: the hook REMAPs
    mesh._deform_mesh(c1)

try:
    remesh.remesh_with_field_transfer(mesh, do_move, dt=0.1)
    raised = "none"
except RuntimeError as e:
    raised = "#960" if "#960" in str(e) else f"other: {str(e)[:80]}"
at_new = bool(np.abs(np.asarray(mesh.X.coords) - c1).max(initial=0) < 1e-12)
kept = {v.name: bool(np.array_equal(np.asarray(v.data), before[v.clean_name if hasattr(v, "clean_name") else v.name])) for v in owned}
r = uw.mpi.comm.gather((raised, at_new, kept, len(owned), len(fired)), root=0)
if uw.mpi.rank == 0:
    print(f"RESULT case={case} np={uw.mpi.size} raised={[x[0] for x in r]} at_new={[x[1] for x in r]} "
          f"history_kept={[x[2] for x in r]} owned={r[0][3]} fired={[x[4] for x in r]}", flush=True)
