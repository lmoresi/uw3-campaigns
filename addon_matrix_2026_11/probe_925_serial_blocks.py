"""#925 probe 3: do the serial blocks, rebuilt at any rank count, restore the
serial velocity convergence?

probe_925_held_once.py removed the rows that two ranks' blocks both held (232 at
np 2, 224 at np 4). The outer solve then converged, but every velocity solve still
ran to its 200-iteration cap where serial takes 5. With every row held once, what
still differs from serial is how the rows are cut into blocks: each rank segments
its own part of the TI band (with the ghost rows of its masked cells), and the
structural rows outside the band form one block per rank, so rank boundaries cut
both. This probe rebuilds, at any rank count, the blocks the serial branch builds:
the band's rows gathered from every rank and segmented along strike at
fac_block_rows, and the structural rows outside the band as one block
(PROBE925_EXTRA=global) or as each rank's own rows (PROBE925_EXTRA=local). Each
gathered block goes whole to the rank that owns most of its rows. Nothing else
changes.

If np 2 and 4 then converge in a few velocity iterations per solve, the rank cuts
are the cause, and the library fix is to build the union's blocks from the
gathered rows.

    PROBE925_EXTRA=global mpirun -np 4 python probe_925_serial_blocks.py <row5 args>
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

MODE = os.environ.get("PROBE925_EXTRA", "global")
if MODE not in ("global", "local"):
    raise ValueError(f"PROBE925_EXTRA={MODE}: expected global or local")
STASH = {}

_build = custom_mg.CustomMGHierarchy.build


def _build_probe(self, solver):
    STASH.update(h=self, solver=solver, splits=[])
    return _build(self, solver)


def _recording(split):
    """``split`` (the serial or the parallel structural split), recording what it
    returns against the size of its fine level's node table."""
    def wrapped(P, coords_c, coords_f, *args, **kwargs):
        out = split(P, coords_c, coords_f, *args, **kwargs)
        STASH.setdefault("splits", []).append((np.asarray(coords_f).shape[0], out))
        return out
    return wrapped


def _zone_rows(lay, coords, nc):
    """This rank's zone rows (ghost rows included) and their node coordinates,
    built as the library's parallel branch builds them."""
    h = STASH["h"]
    cn = h.level_meshes[-1]._cell_node_indices(2, True)
    if cn.size and cn.max() >= coords.shape[0]:
        raise RuntimeError("cell nodes do not index the level coordinates")
    rows, xy = [], []
    for mk in h.fac_zone:
        nodes = np.unique(cn[np.asarray(mk, dtype=bool)])
        full = (nodes[:, None] * nc + np.arange(nc)[None, :]).ravel()
        g = lay.l2g[full]
        keep = g >= 0
        rows.append(g[keep])
        xy.append(coords[full[keep] // nc])
    if not rows:
        return np.zeros(0, np.int64), np.zeros((0, coords.shape[1]))
    return np.concatenate(rows).astype(np.int64), np.vstack(xy)


def _majority_rank(block, starts, size):
    owner = np.searchsorted(starts, block, side="right") - 1
    return int(np.bincount(owner, minlength=size).argmax())


def _serial_blocks(comm, r0, library_pairs):
    h, solver = STASH["h"], STASH["solver"]
    lay = custom_mg._level_dof_layout(solver.dm, h.field_id)
    if lay.rstart != r0:
        raise RuntimeError(f"finest layout starts at {lay.rstart}, the PCMG level at {r0}")
    coords = np.asarray(h.level_meshes[-1]._get_coords_for_basis(2, True))
    nc = coords.shape[1]
    zr, zx = _zone_rows(lay, coords, nc)
    finest = [out for n, out in STASH.get("splits", []) if n == coords.shape[0]]
    split = finest[-1] if finest else None
    sub = (np.asarray(split[1], dtype=np.int64) if split is not None
           else np.zeros(0, np.int64))
    lib = (np.unique(np.concatenate([np.asarray(s, dtype=np.int64)
                                     for _o, s in library_pairs]))
           if library_pairs else np.zeros(0, np.int64))
    everyone = comm.allgather((r0, zr, zx, sub, lib))
    starts = np.array([e[0] for e in everyone])
    Z, first = np.unique(np.concatenate([e[1] for e in everyone]), return_index=True)
    ZX = np.vstack([e[2] for e in everyone])[first]
    # a node's components stay in one piece: nodes keyed by coordinate (the TI
    # band is placed, not cut, so no two of its nodes share a position)
    node_xy, node = np.unique(np.round(ZX, 12), axis=0, return_inverse=True)
    cap = int(os.environ.get("UW_FAC_BLOCK_ROWS", STASH["h"].fac_block_rows))
    blocks = [np.unique(p).astype(np.int64)
              for p in custom_mg._segment_block(Z, node.ravel(), node_xy, cap) if p.size]
    S_all = np.unique(np.concatenate([e[3] for e in everyone]))
    if MODE == "global":
        extra = S_all[~np.isin(S_all, Z)]
        if extra.size:
            blocks.append(extra)
    mine = [b for b in blocks if _majority_rank(b, starts, comm.size) == comm.rank]
    if MODE == "local":
        extra = sub[~np.isin(sub, Z)]
        if extra.size:
            mine.append(extra)
    if comm.rank == 0:
        L = np.unique(np.concatenate([e[4] for e in everyone]))
        U = np.union1d(Z, S_all)
        print(f"PROBE925C mode {MODE}: zone rows {Z.size}, structural rows {S_all.size}, "
              f"union {U.size}; library blocks held {L.size} rows, "
              f"{np.setdiff1d(L, U).size} outside the union, "
              f"{np.setdiff1d(U, L).size} of the union not held", flush=True)
        print(f"PROBE925C gathered blocks: {[int(b.size) for b in blocks]} "
              f"to ranks {[_majority_rank(b, starts, comm.size) for b in blocks]}",
              flush=True)
    held = comm.allgather(np.concatenate(mine) if mine else np.zeros(0, np.int64))
    sizes = comm.allgather([int(b.size) for b in mine])
    _r, count = np.unique(np.concatenate(held), return_counts=True)
    if comm.rank == 0:
        print(f"PROBE925C rows held: {_r.size}, held more than once: "
              f"{int(np.sum(count > 1))}; block sizes per rank {sizes}", flush=True)
    return mine


def _probe(pc, Ps, *args, **kwargs):
    bound = _signature.bind(pc, Ps, *args, **kwargs)
    patch_rows = bound.arguments.get("patch_rows")
    if patch_rows and any(e is not None for e in patch_rows) and "h" in STASH:
        comm = MPI.COMM_WORLD
        patch_rows = list(patch_rows)
        for level, entry in enumerate(patch_rows):
            if entry is None or level == 0:
                continue
            pairs = entry if isinstance(entry, list) else [entry]
            r0, _r1 = Ps[level - 1].getOwnershipRange()
            mine = _serial_blocks(comm, r0, pairs)
            new = [(b, b) for b in mine]
            patch_rows[level] = (new if len(new) > 1 else new[0] if new
                                 else (np.zeros(0, np.int64), np.zeros(0, np.int64)))
        bound.arguments["patch_rows"] = patch_rows
    return _configure(*bound.args, **bound.kwargs)


_configure = custom_mg._configure_pcmg
_signature = inspect.signature(_configure)
custom_mg.CustomMGHierarchy.build = _build_probe
custom_mg._fac_patch_split_parallel = _recording(custom_mg._fac_patch_split_parallel)
custom_mg._fac_patch_split = _recording(custom_mg._fac_patch_split)
custom_mg._configure_pcmg = _probe
runpy.run_path(sys.argv[0], run_name="__main__")
