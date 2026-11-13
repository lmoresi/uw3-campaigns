"""Does MatPtAP hang when some ranks own no rows? A standalone check for issue #962.

No underworld3: petsc4py only. Written by the dev hub and NOT run before it was sent
(the hub's container has no petsc4py), so treat a Python error as the script's fault.

    timeout 120 mpirun -n 8 python ptap_empty_rank.py <variant> <empty ranks ...>

variant:
    plain       P is assembled directly
    transpose   P is the transpose of an assembled matrix (MatTranspose), as a rotation
                built as Q and used as Qt would be
    rect        P is rectangular (fewer columns than rows on every non-empty rank)
empty ranks: the ranks that own no rows, e.g. "0 4"; give "none" for the control.

Exit 0 and a line "ptap done" on every variant means MatPtAP copes with empty ranks
on this PETSc; a hang (exit 124 from timeout) or an MPI abort reproduces #962 without
any of our code.
"""
import sys

from petsc4py import PETSc

comm = PETSc.COMM_WORLD
rank = comm.getRank()

variant = sys.argv[1] if len(sys.argv) > 1 else "plain"
names = sys.argv[2:] if len(sys.argv) > 2 else ["0", "4"]
empty = set() if names == ["none"] else {int(a) for a in names}

ROWS = 12                                  # local rows on a rank that owns any
n_row = 0 if rank in empty else ROWS


def banded(n_local_rows, n_local_cols):
    """An MPIAIJ matrix with a diagonal and two off-diagonals that reach other ranks."""
    M = PETSc.Mat().create(comm=comm)
    M.setSizes(((n_local_rows, PETSc.DETERMINE), (n_local_cols, PETSc.DETERMINE)))
    M.setType(PETSc.Mat.Type.AIJ)
    M.setPreallocationNNZ((3, 3))
    M.setOption(PETSc.Mat.Option.NEW_NONZERO_ALLOCATION_ERR, False)
    n_rows_global, n_cols_global = M.getSize()
    r0, r1 = M.getOwnershipRange()
    for i in range(r0, r1):
        j = min(i, n_cols_global - 1) if n_cols_global else 0
        if n_cols_global:
            M.setValue(i, j, 2.0)
            M.setValue(i, (j + ROWS) % n_cols_global, -1.0)     # a column another rank owns
            M.setValue(i, (j - ROWS) % n_cols_global, -1.0)
    M.assemble()
    return M


A = banded(n_row, n_row)
if variant == "plain":
    P = banded(n_row, n_row)
elif variant == "transpose":
    P = banded(n_row, n_row).transpose()
elif variant == "rect":
    P = banded(n_row, 0 if rank in empty else ROWS // 2)
else:
    raise SystemExit(f"unknown variant {variant!r}")

PETSc.Sys.Print(f"variant {variant}, empty ranks {sorted(empty)}: "
                f"A {A.getSizes()} P {P.getSizes()} (rank 0's view); entering ptap")
C = A.ptap(P)
PETSc.Sys.Print(f"ptap done: C {C.getSize()}, norm {C.norm():.6e}")
