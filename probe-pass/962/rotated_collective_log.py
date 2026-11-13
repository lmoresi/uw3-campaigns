"""Per-rank log of PETSc's collective-call counters at each line of the rotated solve (#962).

Run under MPI in place of pytest:

    UW_LINE_LOG_DIR=<empty dir> mpirun -n 8 python rotated_collective_log.py --with-mpi -x <test id>

Each rank writes ``lines_rank<r>.log``: one entry per executed line of
``rotated_bc.py`` with PETSc's running counts of reductions (R: MPI_Allreduce,
MPI_Bcast and the all-to-all family, as PETSc's log counts them) and gathers
(G: MPI_Allgather(v)), read before the line runs. The difference between two
consecutive entries is what the earlier line did. ``events_rank<r>.log`` holds
the per-event reduction counts each time a Jacobian or a PtAP line is reached.
Summarise with ``collective_table.py <dir>``.
"""
import ctypes
import linecache
import os
import sys

import pytest
from petsc4py import PETSc

WATCH = ("rotated_bc.py",)
EVENT_LINES = ("computeJacobian", ".ptap(")
EVENTS = (
    "SNESJacobianEval", "SNESFunctionEval", "DMPlexJacobianFE", "DMPlexResidualFE",
    "MatAssemblyBegin", "MatAssemblyEnd", "MatZeroEntries", "MatSetValues",
    "VecAssemblyBegin", "VecAssemblyEnd", "MatPtAP", "MatPtAPSymbolic", "MatPtAPNumeric",
    "MatTranspose", "MatMatMultSym", "MatMatMultNum", "MatGetBrwoOfAcols",
    "SFSetGraph", "SFSetUp", "SFBcastBegin", "SFReduceBegin", "DMGlobalToLocal",
    "DMLocalToGlobal", "VecNorm", "VecDot", "VecScatterBegin", "MatMult",
    "PCSetUp", "KSPSolve",
)


def _petsc_library():
    """The libpetsc this process already has, as a ctypes handle."""
    try:
        lib = ctypes.CDLL(None)
        ctypes.c_double.in_dll(lib, "petsc_allreduce_ct")
        return lib
    except (ValueError, OSError):
        pass
    with open("/proc/self/maps") as maps:
        for row in maps:
            path = row.split()[-1]
            if "libpetsc" in os.path.basename(path):
                return ctypes.CDLL(path)
    raise RuntimeError("libpetsc is not loaded in this process")


PETSc.Log.begin()
RANK = PETSc.COMM_WORLD.getRank()
OUT = os.environ.get("UW_LINE_LOG_DIR", ".")
LIB = _petsc_library()
REDUCTIONS = ctypes.c_double.in_dll(LIB, "petsc_allreduce_ct")
GATHERS = ctypes.c_double.in_dll(LIB, "petsc_gather_ct")
LOG = open(os.path.join(OUT, f"lines_rank{RANK}.log"), "w", buffering=1)
EVLOG = open(os.path.join(OUT, f"events_rank{RANK}.log"), "w", buffering=1)
_last = None


def _local(frame, event, arg):
    global _last
    if event == "line":
        here = (frame.f_code.co_filename, frame.f_lineno)
        if here != _last:
            _last = here
            LOG.write(f"{os.path.basename(here[0])}:{here[1]} {frame.f_code.co_name} "
                      f"R={int(REDUCTIONS.value)} G={int(GATHERS.value)}\n")
            text = linecache.getline(*here)
            if any(mark in text for mark in EVENT_LINES):
                counts = " ".join(
                    f"{name}={int(PETSc.Log.Event(name).getPerfInfo()['numReductions'])}"
                    for name in EVENTS)
                EVLOG.write(f"before {os.path.basename(here[0])}:{here[1]} {counts}\n")
    return _local


def _global(frame, event, arg):
    if frame.f_code.co_filename.endswith(WATCH):
        return _local
    return None


if __name__ == "__main__":
    sys.settrace(_global)
    code = pytest.main(sys.argv[1:])
    sys.settrace(None)
    LOG.write(f"end R={int(REDUCTIONS.value)} G={int(GATHERS.value)}\n")
    LOG.write(f"pytest exit {int(code)}\n")
    LOG.close()
    EVLOG.close()
    sys.exit(int(code))
