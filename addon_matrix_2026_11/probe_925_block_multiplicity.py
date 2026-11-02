"""#925 probe: how many FAC patch blocks hold each row of the finest level.

Runs row5_networks.py unchanged (same arguments), with custom_mg._configure_pcmg
wrapped. At the first configuration that carries a patch it gathers every rank's
blocks (global rows, before PCASM's overlap layer), prints the multiplicity of
each row over all blocks of all ranks, and exits on every rank before the solve.

Basic ASM sums the corrections of every block that holds a row. In serial the
zone pieces are disjoint and the structural block excludes the zone's rows, so
every row should be held once. The question is whether at np > 1 rows are held
by two or more blocks (the zone's seam halo, or a structural block holding rows
another rank's zone block holds), which would make the smoother over-correct.

    mpirun -np 4 python probe_925_block_multiplicity.py <row5_networks.py arguments>
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


def _report(level, blocks_by_rank, ranges, n_rows):
    held = np.concatenate([np.concatenate(bl) if bl else np.zeros(0, np.int64)
                           for bl in blocks_by_rank])
    rows, count = np.unique(held, return_counts=True)
    print(f"PROBE925 level {level}: {n_rows} rows, {rows.size} in some block, "
          f"{held.size} block entries", flush=True)
    hist = {k: int(np.sum(count == k)) for k in (1, 2, 3)}
    hist["4+"] = int(np.sum(count >= 4))
    print(f"PROBE925 rows by number of blocks holding them: {hist}", flush=True)
    per_rank = [np.unique(np.concatenate(bl)) if bl else np.zeros(0, np.int64)
                for bl in blocks_by_rank]
    _r, nranks = np.unique(np.concatenate(per_rank), return_counts=True)
    print(f"PROBE925 rows held by blocks on 2+ ranks: {int(np.sum(nranks >= 2))}",
          flush=True)
    for r, bl in enumerate(blocks_by_rank):
        r0, r1 = ranges[r]
        sizes = [b.size for b in bl]
        allr = np.concatenate(bl) if bl else np.zeros(0, np.int64)
        off = int(np.sum((allr < r0) | (allr >= r1)))
        within = (int(np.sum(np.unique(allr, return_counts=True)[1] >= 2))
                  if allr.size else 0)
        others = (np.concatenate([np.concatenate(b) for q, b in enumerate(blocks_by_rank)
                                  if q != r and b]) if len(blocks_by_rank) > 1
                  else np.zeros(0, np.int64))
        last = bl[-1] if bl else np.zeros(0, np.int64)
        last_shared = int(np.isin(last, others).sum()) if others.size else 0
        print(f"PROBE925 rank {r}: owns [{r0},{r1}) {r1 - r0} rows; {len(bl)} blocks, "
              f"sizes max {max(sizes, default=0)} sum {sum(sizes)}; off-rank entries "
              f"{off}; rows in 2+ of its own blocks {within}; last block {last.size} "
              f"rows, {last_shared} of them held by another rank's blocks", flush=True)


def _probe(pc, Ps, *args, **kwargs):
    out = _configure(pc, Ps, *args, **kwargs)
    bound = _signature.bind(pc, Ps, *args, **kwargs)
    patch_rows = bound.arguments.get("patch_rows")
    if not patch_rows or all(e is None for e in patch_rows):
        return out
    comm = MPI.COMM_WORLD
    for level, entry in enumerate(patch_rows):
        if entry is None or level == 0:
            continue
        pairs = entry if isinstance(entry, list) else [entry]
        mine = [np.asarray(sub, dtype=np.int64) for _own, sub in pairs]
        r0, r1 = Ps[level - 1].getOwnershipRange()
        n_rows = Ps[level - 1].getSize()[0]
        gathered = comm.gather(((r0, r1), mine), root=0)
        if comm.rank == 0:
            _report(level, [g[1] for g in gathered], [g[0] for g in gathered], n_rows)
    comm.Barrier()
    raise SystemExit(0)


custom_mg._configure_pcmg = _probe
runpy.run_path(sys.argv[0], run_name="__main__")
