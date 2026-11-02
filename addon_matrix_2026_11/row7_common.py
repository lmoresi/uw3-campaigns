"""What the add-on matrix row 7 drivers share (dev hub, 2026-11-01): the corridor
refinement of the base, the slip profile in fixed physical coordinates, the FAC patch's
blocks timed, and the level smoothers as installed.

Row 7 asks whether a finer ladder does physical work, and whether refining the base
under the fault corridor is the route to slip resolution instead (Louis, 2026-11-01:
the ladder works best when it and the base mesh have similar resolution; S is a mesh
parameter, not a physical length).
"""
import time

import numpy as np
import underworld3 as uw
from underworld3.utilities import custom_mg
from underworld3.utilities.fault_contact import fault_pair_jumps


def distance_to_polyline(points, polyline):
    """The distance from each point to the polyline (segments, end caps round)."""
    c = np.asarray(points)[:, :2]
    P = np.asarray(polyline, dtype=float)
    d = np.full(len(c), np.inf)
    for a, b in zip(P[:-1], P[1:]):
        ab = b - a
        s = np.clip(((c - a) @ ab) / (ab @ ab), 0.0, 1.0)
        d = np.minimum(d, np.linalg.norm(c - (a + s[:, None] * ab), axis=1))
    return d


def corridor_child(base, polyline, h_b, rings, depth):
    """The base refined ``depth`` times inside the corridor of half-width ``rings * h_b``
    around ``polyline`` (nested NVB, ``mesh.adapt``), or the base itself at depth 0.

    The metric asks for less than h_b / 2**depth inside the corridor and for 2 h_b
    outside it, so ``max_levels`` sets the depth and nothing outside is marked (NVB's
    conforming closure adds a graded ring). The child carries the welded tail: the
    base levels, then one level per doubling."""
    if int(depth) <= 0:
        return base
    h_in = 0.5 * h_b / 2 ** int(depth)

    def metric(centroids):
        near = distance_to_polyline(centroids, polyline) < float(rings) * h_b
        return np.where(near, 1.0 / h_in ** 2, 0.25 / h_b ** 2)

    return base.adapt(metric, max_levels=int(depth))


def cell_sizes_near(mesh, polyline, radius):
    """Median and range of sqrt(2 area) over the owned cells whose centroid lies within
    ``radius`` of the polyline, all ranks (the corridor's realised cell size)."""
    dm = mesh.dm
    c0, c1 = dm.getHeightStratum(0)
    owned = mesh.dm.getCellNumbering().getIndices() >= 0
    sizes, cents = [], []
    for k, c in enumerate(range(c0, c1)):
        if not owned[k]:
            continue
        vol, cen, _ = dm.computeCellGeometryFVM(c)
        sizes.append(np.sqrt(2.0 * abs(vol)))
        cents.append(cen[:2])
    sizes = np.asarray(sizes)
    near = (distance_to_polyline(np.asarray(cents).reshape(-1, 2), polyline) < radius
            if len(cents) else np.zeros(0, dtype=bool))
    allv = np.concatenate(uw.mpi.comm.allgather(sizes[near]))
    if not len(allv):
        return None
    return {"median": float(np.median(allv)), "min": float(allv.min()),
            "max": float(allv.max()), "cells": int(len(allv))}


def tip_topology(mesh, boundary, surface_point, t_hat, n_fault, h_element, surface_y=1.0, max_steps=8):
    """The split fault's upper tip in the placed mesh, against the surface y = surface_y.

    The tip is the unpaired vertex of the fault's Plus facets nearest the surface (the
    split stops there, so the vertex is not duplicated). Measured at the tip: its depth,
    its distance down dip from ``surface_point`` (where the fault meets the surface),
    the lengths of its edges (the local element size), and its distance to the surface
    in edges. Measured on the pairs: the topmost pair point, and how many pair points
    lie on the surface (the rotated assembly refuses a node that carries both a wall
    block and a pair block). The pairs are rank-local (the split keeps a fault
    rank-interior); the result is gathered so every rank holds it."""
    dm = mesh.dm
    dim = mesh.dim
    csec = dm.getCoordinateSection()
    cvec = np.asarray(dm.getCoordinatesLocal().array)
    v0, v1 = dm.getDepthStratum(0)
    t_hat = np.asarray(t_hat, dtype=float)
    surface_point = np.asarray(surface_point, dtype=float)

    def x_of(q):
        if v0 <= q < v1:
            off = csec.getOffset(q)
            return cvec[off:off + dim]
        return np.mean([x_of(int(c)) for c in dm.getTransitiveClosure(q)[0] if v0 <= c < v1], axis=0)

    pairs = mesh._fault_point_pairs.get(boundary, {})
    paired = {int(k) for k in pairs} | {int(v) for v in pairs.values()}
    plus = f"{boundary}Plus"
    closure, facets = set(), []
    if dm.hasLabel(plus) and dm.getLabel(plus).getStratumSize(mesh.boundaries[plus].value) > 0:
        fS, fE = dm.getHeightStratum(1)
        for f in dm.getLabel(plus).getStratumIS(mesh.boundaries[plus].value).getIndices():
            if fS <= int(f) < fE:
                facets.append(int(f))
                closure.update(int(c) for c in dm.getTransitiveClosure(int(f))[0] if v0 <= c < v1)
    ends = [q for q in closure if q not in paired]

    local = None
    if ends:
        tip = max(ends, key=lambda q: x_of(q)[1])
        xt = np.array(x_of(tip), dtype=float)
        edges = [int(e) for e in dm.getSupport(tip)]
        lengths = [float(np.linalg.norm(x_of(int(a)) - x_of(int(b))))
                   for a, b in (dm.getCone(e) for e in edges)]
        # breadth-first over edges from the tip until a vertex lies on the surface
        steps, seen, front = None, {tip}, [tip]
        for k in range(1, max_steps + 1):
            nxt = []
            for q in front:
                for e in dm.getSupport(q):
                    for w in (int(c) for c in dm.getCone(e)):
                        if w not in seen:
                            seen.add(w)
                            nxt.append(w)
            if any(x_of(w)[1] >= surface_y - 1e-9 for w in nxt):
                steps = k
                break
            front = nxt
        local = {"x": [float(c) for c in xt], "depth": float(surface_y - xt[1]),
                 "down_dip": float((xt - surface_point) @ t_hat),
                 "edge_lengths": lengths, "edges_to_surface": steps}

    plus_points = [int(q) for q in pairs.values()]
    pair_y = [float(x_of(q)[1]) for q in plus_points]
    top_y = max(pair_y) if pair_y else -np.inf
    on_surface = sum(y >= surface_y - 1e-9 for y in pair_y)
    frame_dot = None
    if plus_points:
        top = plus_points[int(np.argmax(pair_y))]
        acc = np.zeros(dim)
        for f in facets:
            if top in (int(c) for c in dm.getTransitiveClosure(f)[0]):
                a, b = (x_of(int(c)) for c in dm.getCone(f))
                acc += np.array([-(b - a)[1], (b - a)[0]])     # |f| times the unit normal
        frame_dot = float(abs(acc @ np.asarray(n_fault, dtype=float)) / (np.linalg.norm(acc) + 1e-30))

    gathered = uw.mpi.comm.allgather((local, top_y, on_surface, frame_dot))
    tips = [g[0] for g in gathered if g[0] is not None]
    tip = max(tips, key=lambda t: -t["depth"]) if tips else None
    top_rank = int(np.argmax([g[1] for g in gathered]))
    out = {"pair_points_on_surface": int(sum(g[2] for g in gathered)),
           "top_pair_depth": float(surface_y - gathered[top_rank][1]),
           "top_pair_frame_dot": gathered[top_rank][3], "h_element": float(h_element)}
    if tip is not None:
        L = tip["edge_lengths"]
        out.update({"tip_x": tip["x"], "tip_depth": tip["depth"], "tip_down_dip": tip["down_dip"],
                    "inset_elements": tip["down_dip"] / h_element,
                    "inset_elements_depth": tip["depth"] / h_element,
                    "tip_edge_min_mean_max": [min(L), float(np.mean(L)), max(L)] if L else None,
                    "tip_edges_to_surface": tip["edges_to_surface"]})
    return out


def top_pairs(stokes, boundary, info, origin, t_hat, n_fault, count=4):
    """The ``count`` pairs nearest ``origin`` along ``t_hat`` (the tip's end of the
    fault): their distance s, the slip V and the leak (oriented as in
    ``slip_profile``), and |n . n_fault|, the pair's frame normal against the fault's."""
    coords, jumps, normals = fault_pair_jumps(stokes, boundary, info, gather=True)
    if not len(coords):
        return []
    t_hat = np.asarray(t_hat, dtype=float)
    n_hat = np.array([-t_hat[1], t_hat[0]])
    N = np.asarray(normals)[:, :2]
    J = np.asarray(jumps)[:, :2] * np.sign(N @ n_hat)[:, None]
    s = (np.asarray(coords)[:, :2] - np.asarray(origin)) @ t_hat
    _, first = np.unique(np.round(s, 9), return_index=True)
    first = first[np.argsort(s[first])][:count]
    return [{"s": float(s[i]), "x": [float(c) for c in np.asarray(coords)[i, :2]],
             "V": float(J[i] @ t_hat), "leak": float(J[i] @ n_hat),
             "frame_dot": float(abs(N[i] @ np.asarray(n_fault, dtype=float)))} for i in first]


def slip_profile(stokes, boundary, info, origin, t_hat):
    """The slip along the fault in fixed physical coordinates, all ranks, sorted: s the
    distance from ``origin`` along ``t_hat``, V the tangential jump oriented to the
    normal n = t_hat rotated by +90 degrees (so the sign is the same on every mesh),
    and the largest normal jump (the leak)."""
    coords, jumps, normals = fault_pair_jumps(stokes, boundary, info, gather=True)
    t_hat = np.asarray(t_hat, dtype=float)
    n_hat = np.array([-t_hat[1], t_hat[0]])
    if not len(coords):
        return {"s": [], "V": [], "leak_max": 0.0}
    side = np.sign(np.asarray(normals)[:, :2] @ n_hat)
    J = np.asarray(jumps)[:, :2] * side[:, None]
    s = (np.asarray(coords)[:, :2] - np.asarray(origin)) @ t_hat
    V = J @ t_hat
    leak = J @ n_hat
    s_key, first = np.unique(np.round(s, 9), return_index=True)
    return {"s": [float(x) for x in s[first]], "V": [float(x) for x in V[first]],
            "leak_max": float(np.abs(leak).max())}


class FacBlockTimer:
    """The FAC patch's blocks on the finest patch level, timed through every rotated
    solve: ``custom_mg._set_up_fac_smoothers`` is wrapped so that, once it has put the
    block solver on the live block KSPs, each block is set up there (its LU
    factorisation, otherwise done at its first application) and timed. On every later
    block solve a pre-solve hook (KSPSolve calls it before KSPSetUp) and the monitor's
    first call bracket the set-up, which refactors the block whenever its operator
    has changed (a new Newton Jacobian), and the monitor times the block solve.

    A monitored preonly solve computes one residual after the block solve (a block
    MatMult), so the application time includes it; ``t_mult_s_per_application`` is
    that MatMult timed on the last set-up's blocks, and ``t_apply_net_s`` subtracts it.
    """

    def __init__(self):
        self.setups = 0
        self.t_factor = 0.0
        self.applications = 0
        self.t_apply = 0.0
        self.refactors = 0
        self.t_refactor = 0.0
        self.blocks = []
        self._start = [0.0]
        self._pre = [0.0]
        self._states = {}
        self._orig = custom_mg._set_up_fac_smoothers
        custom_mg._set_up_fac_smoothers = self._wrapped

    def reset(self):
        """Zero the counters, keeping the blocks and their monitors (a second solve on
        the cached operators sets nothing up again)."""
        self.setups = 0
        self.t_factor = 0.0
        self.applications = 0
        self.t_apply = 0.0
        self.refactors = 0
        self.t_refactor = 0.0

    def _presolve(self, ksp, _b, _x):
        self._pre[0] = time.perf_counter()
        state = ksp.getOperators()[0].stateGet()
        if self._states.get(id(ksp), state) != state:
            self.refactors += 1
        self._states[id(ksp)] = state

    def _monitor(self, _ksp, its, _rnorm):
        if its == 0:
            now = time.perf_counter()
            self.t_refactor += now - self._pre[0]
            self._start[0] = now
        elif its == 1:
            self.t_apply += time.perf_counter() - self._start[0]
            self.applications += 1

    def _wrapped(self, pc, fac_keys):
        self._orig(pc, fac_keys)
        if not fac_keys:
            return
        finest = [l for l in range(1, pc.getMGLevels())
                  if any(k.startswith(f"mg_levels_{l}_") for k in fac_keys)]
        if not finest:
            return
        level_pc = pc.getMGSmoother(finest[-1]).getPC()
        asm = (level_pc.getCompositePC(1) if level_pc.getType() == "composite"
               else level_pc)
        blocks = list(asm.getASMSubKSP())
        wall = time.perf_counter()
        for block in blocks:
            block.setUp()
        self.t_factor += time.perf_counter() - wall
        for block in blocks:
            block.setMonitor(self._monitor)
            block.setPreSolve(self._presolve)
            self._states[id(block)] = block.getOperators()[0].stateGet()
        self.blocks = blocks
        self.setups += 1

    def record(self):
        """The counters, summed and maxed over the ranks."""
        sizes = [int(k.getOperators()[0].getSize()[0]) for k in self.blocks]
        t_mult = 0.0
        for k in self.blocks:
            A = k.getOperators()[0]
            x, y = A.createVecs()
            x.setRandom()
            wall = time.perf_counter()
            for _ in range(3):
                A.mult(x, y)
            t_mult += (time.perf_counter() - wall) / 3
            x.destroy()
            y.destroy()
        n_blocks = len(self.blocks)
        per_app = t_mult / n_blocks if n_blocks else 0.0
        net = self.t_apply - self.applications * per_app
        comm = uw.mpi.comm
        # t_refactor: KSPSetUp inside each block solve, which refactors after an operator
        # change and is near zero otherwise; t_factor: the set-ups at installation
        mine = {"t_factor_s": self.t_factor, "t_refactor_s": self.t_refactor,
                "t_apply_s": self.t_apply, "t_apply_net_s": net,
                "t_block_total_s": self.t_factor + self.t_refactor + self.t_apply}
        out = {
            "setups_rank0": self.setups,
            "blocks": int(comm.allreduce(n_blocks)),
            "block_rows": sorted(r for part in comm.allgather(sizes) for r in part),
            "block_pc": sorted(set().union(*comm.allgather(
                {k.getPC().getType() for k in self.blocks}))),
            "applications": int(comm.allreduce(self.applications)),
            "refactors": int(comm.allreduce(self.refactors)),
            "t_mult_s_per_application_rank_max": float(comm.allreduce(per_app, op=max)),
        }
        for key, val in mine.items():
            out[key + "_sum"] = round(float(comm.allreduce(val)), 4)
            out[key + "_rank_max"] = round(float(comm.allreduce(val, op=max)), 4)
        return out


def level_smoothers(velpc):
    """The smoother each velocity multigrid level runs, as installed: KSP and PC type;
    for a FAC patch level (custom_mg, #629: PC composite = whole-level SOR, then ASM
    over the band blocks) the ASM blocks and their rows summed over the ranks, the
    largest block's rows, and the block solver. Level 0 is the coarse solve."""
    out = []
    for lev in range(velpc.getMGLevels()):
        ksp = velpc.getMGSmoother(lev)
        pc = ksp.getPC()
        entry = {"level": lev, "ksp": ksp.getType(), "pc": pc.getType()}
        asm = None
        if pc.getType() == "composite":
            subs = [pc.getCompositePC(i) for i in range(2)]     # custom_mg adds sor, asm
            entry["composite"] = [s.getType() for s in subs]
            asm = next((s for s in subs if s.getType() == "asm"), None)
        elif pc.getType() == "asm":
            asm = pc
        if asm is not None:
            sub_ksps = asm.getASMSubKSP()
            rows = sum(k.getOperators()[0].getSize()[0] for k in sub_ksps)
            entry["asm_blocks"] = int(uw.mpi.comm.allreduce(len(sub_ksps)))
            entry["asm_rows"] = int(uw.mpi.comm.allreduce(rows))
            entry["asm_block_rows_max"] = max(uw.mpi.comm.allgather(
                max((k.getOperators()[0].getSize()[0] for k in sub_ksps), default=0)))
            entry["asm_sub_pc"] = sorted(set().union(*uw.mpi.comm.allgather(
                {k.getPC().getType() for k in sub_ksps})))
        out.append(entry)
    return out


def level_operators(velpc):
    """Rows and nonzeros per row of each velocity level operator."""
    from petsc4py import PETSc
    ops = []
    for lev in range(velpc.getMGLevels()):
        Amat = velpc.getMGSmoother(lev).getOperators()[0]
        rows = Amat.getSize()[0]
        nz = Amat.getInfo(PETSc.Mat.InfoType.GLOBAL_SUM)["nz_used"]
        ops.append({"rows": int(rows), "nnz_per_row": round(nz / max(rows, 1), 1)})
    return ops


def n_cells(m):
    """Cells owned across the ranks (the plex numbering marks the others negative)."""
    n_own = int(np.count_nonzero(m.dm.getCellNumbering().getIndices() >= 0))
    return int(uw.mpi.comm.allreduce(n_own))

