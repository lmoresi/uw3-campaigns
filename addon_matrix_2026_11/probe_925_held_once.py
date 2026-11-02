"""#925 probe 2: does holding each patch row in one block only restore convergence?

probe_925_block_multiplicity.py found that at np 2 and 4 a few hundred rows of
the finest level's FAC patch sit in blocks on two ranks (none in serial), so
basic ASM adds two corrections there. This probe runs row5_networks.py
unchanged, with custom_mg._configure_pcmg wrapped: before the patch is handed
to PCASM, a row held by blocks on two or more ranks stays only on its owner, if
the owner holds it, otherwise on the lowest such rank. Nothing else changes.
If the solve now converges at np 4 where 2328b4ca does not, the double
correction is the cause and the library fix is the same rule inside build().

    mpirun -np 4 python probe_925_held_once.py <row5_networks.py arguments>
"""
import inspect
import os
import runpy
import sys

import numpy as np
from mpi4py import MPI

HERE = os.path.dirname(os.path.abspath(__file__))
sys.argv[0] = os.path.join(HERE, "row5_networks.py")

from underworld3.utilities import custom_mg  # noqa: E402

_configure = custom_mg._configure_pcmg
_signature = inspect.signature(_configure)


def _held_once(pairs, r0, r1, comm):
    """This rank's blocks with every row another rank also holds removed,
    unless this rank keeps it (owner first, else the lowest holder)."""
    mine = np.unique(np.concatenate([np.asarray(s, dtype=np.int64) for _o, s in pairs])
                     if pairs else np.zeros(0, np.int64))
    everyone = comm.allgather((r0, r1, mine))
    holders = {}
    for rank, (_a, _b, rows) in enumerate(everyone):
        for row in rows.tolist():
            holders.setdefault(row, []).append(rank)
    starts = np.array([e[0] for e in everyone])
    drop = set()
    for row in mine.tolist():
        ranks = holders[row]
        if len(ranks) < 2:
            continue
        owner = int(np.searchsorted(starts, row, side="right") - 1)
        keeper = owner if owner in ranks else min(ranks)
        if keeper != comm.rank:
            drop.add(row)
    kept = []
    for own, sub in pairs:
        sub = np.asarray(sub, dtype=np.int64)
        own = np.asarray(own, dtype=np.int64)
        kept.append((own[~np.isin(own, list(drop))] if drop else own,
                     sub[~np.isin(sub, list(drop))] if drop else sub))
    return kept, len(drop)


def _probe(pc, Ps, *args, **kwargs):
    bound = _signature.bind(pc, Ps, *args, **kwargs)
    patch_rows = bound.arguments.get("patch_rows")
    if patch_rows and any(e is not None for e in patch_rows):
        comm = MPI.COMM_WORLD
        patch_rows = list(patch_rows)
        for level, entry in enumerate(patch_rows):
            if entry is None or level == 0:
                continue
            pairs = entry if isinstance(entry, list) else [entry]
            r0, r1 = Ps[level - 1].getOwnershipRange()
            kept, dropped = _held_once(pairs, r0, r1, comm)
            total = comm.allreduce(dropped)
            if comm.rank == 0:
                print(f"PROBE925B level {level}: {total} duplicate row entries dropped",
                      flush=True)
            patch_rows[level] = kept if isinstance(entry, list) else kept[0]
        bound.arguments["patch_rows"] = patch_rows
    return _configure(*bound.args, **bound.kwargs)


custom_mg._configure_pcmg = _probe
runpy.run_path(sys.argv[0], run_name="__main__")
