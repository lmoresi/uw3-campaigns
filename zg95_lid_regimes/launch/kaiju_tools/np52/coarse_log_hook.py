# kaiju_tools: run_driver.py's monitoring hook: per-solve log stages and the FAC_PATCH report; solvers held by WEAK reference since 2026-11-06 (#948: the strong list leaked 180-260 MB per rank per rebuild in every job run through run_driver.py; fix verified by job 4098)
import weakref
from petsc4py import PETSc
import underworld3 as uw
from underworld3.utilities import custom_mg
# (weak ref to the solver, boundary) from add_fault_bc, for the per-rank fault-node count. Held WEAKLY (2026-11-06,
# underworld3 #948): a strong list kept every rebuilt solver alive with its faulted mesh, coarse levels and FMG
# hierarchy, 180-260 MB per rank per rebuild (found by the dev runner's gc referrer dump, job 4094)
_faults = []
_add_fault_bc = uw.systems.Stokes.add_fault_bc
def _recorded(self, conds=0, boundary=None, **kw):
    _faults[:] = [(r, b) for r, b in _faults if r() is not None]
    _faults.append((weakref.ref(self), boundary))
    return _add_fault_bc(self, conds, boundary=boundary, **kw)
uw.systems.Stokes.add_fault_bc = _recorded

# kaiju (2026-11-01, Louis's time-budget question): every Stokes solve in its own PETSc log stage ("solve_<n>"), so
# -log_view splits per solve (one per step, two with a cold retry); UW_FORCE_COLD_FIRST=1 makes the first solve start
# from rest (zero velocity and pressure) whatever the driver asked
import os
_n_solve = [0]
_solve = uw.systems.Stokes.solve
def _staged(self, *a, **kw):
    n = _n_solve[0]; _n_solve[0] += 1
    if n == 0 and os.environ.get("UW_FORCE_COLD_FIRST"):
        kw["zero_init_guess"] = True
        uw.pprint("COLD_FIRST: the first solve forced to start from rest")
    stage = PETSc.Log.Stage(f"solve_{n}")
    stage.push()
    try:
        return _solve(self, *a, **kw)
    finally:
        stage.pop()
uw.systems.Stokes.solve = _staged
_configure = custom_mg._configure_pcmg
_seen = set()
def _logged(pc, Ps, **kw):
    PETSc.Options()[(pc.getOptionsPrefix() or "") + "pc_mg_log"] = True
    # kaiju addition (2026-11-01): the FAC patch rows per level and rank (owned, subdomain), printed once per layout
    rows = kw.get("patch_rows")
    comm = pc.getComm().tompi4py()
    try:                                   # local only, so every rank still reaches the collective gather
        mine = tuple(None if r is None else (len(r[0]), len(r[1])) for r in (rows or ()))
    except Exception as err:
        mine = (f"unreadable: {type(err).__name__}",)
    every = comm.gather(mine, root=0)
    try:                                   # the split's coincident node pairs this rank owns (rank-local)
        from underworld3.utilities.fault_contact import _fault_pair_nodes
        live = [(r(), b) for r, b in _faults if r() is not None]
        solver = live[-1][0] if live else None
        cut = sum(len(_fault_pair_nodes(sv, b)) for sv, b in live if sv is solver) if solver else 0
    except Exception as err:
        cut = f"unreadable: {type(err).__name__}"
    cuts = comm.gather(cut, root=0)
    if comm.rank == 0:
        try:
            key = (len(Ps), tuple(every))
            if key not in _seen:
                _seen.add(key)
                lv = sorted({l for e in every for l, r in enumerate(e) if isinstance(r, tuple)})
                print(f"FAC_PATCH levels {len(Ps) + 1}: patched levels {lv}; per rank (owned, subdomain) rows on "
                      f"those levels: {[[e[l] if l < len(e) else None for l in lv] for e in every]}; fault node pairs "
                      f"per rank: {cuts}", flush=True)
        except Exception as err:
            print(f"FAC_PATCH report failed: {err!r}", flush=True)
    out = _configure(pc, Ps, **kw)
    try:                                   # the coarse level's size and the coarse solver the options DB asks for
        pre = pc.getOptionsPrefix() or ""
        o = PETSc.Options()
        nc = Ps[0].getSize()[1] if Ps else None
        if comm.rank == 0 and (len(Ps), nc) not in _seen:
            _seen.add((len(Ps), nc))
            keys = ("mg_coarse_pc_type", "mg_coarse_redundant_pc_type", "mg_coarse_ksp_type", "pc_mg_type")
            print(f"COARSE prefix {pre!r}: coarse dofs {nc}; coarse kw {kw.get('coarse')!r}; "
                  + "; ".join(f"{k}={o.getString(pre + k, '-') if o.hasName(pre + k) else '-'}" for k in keys), flush=True)
    except Exception as err:
        if comm.rank == 0:
            print(f"COARSE report failed: {err!r}", flush=True)
    return out
custom_mg._configure_pcmg = _logged
