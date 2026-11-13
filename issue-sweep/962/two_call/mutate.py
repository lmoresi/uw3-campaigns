"""Apply one named mutant to the two-call Jacobian routine in petsc_compat.h."""
import sys
from pathlib import Path

path, name = Path(sys.argv[1]), sys.argv[2]
s = path.read_text()

SET_ASIDE = '''        for (i = 0; i < n; ++i)
            for (k = 0; k < UW_NUM_JACOBIAN_TABLES; ++k) tables[i].wf->form[UW_WF_PRECONDITIONER[k]] = none;
'''
MOVE = '''            for (i = 0; i < n; ++i)
                for (k = 0; k < UW_NUM_JACOBIAN_TABLES; ++k) tables[i].wf->form[UW_WF_JACOBIAN[k]] = tables[i].preconditioner[k];
'''
RESTORE_J = '''                tables[i].wf->form[UW_WF_JACOBIAN[k]]       = tables[i].jacobian[k];
'''
RESTORE_P = '''                tables[i].wf->form[UW_WF_PRECONDITIONER[k]] = tables[i].preconditioner[k];
'''
BOUNDARY = "PetscCall(UW_PetscDSGetBoundaryWeakForm(ds, bd, &tables[i++].wf));"
REGISTER = "    PetscCall(DMSNESSetJacobianLocal(dm, UW_DMPlexSNESComputeJacobianFEM, NULL));\n"
for text in (SET_ASIDE, MOVE, RESTORE_J, RESTORE_P, BOUNDARY, REGISTER):
    assert s.count(text) == 1, text

if name == "first_call_on_the_whole_system":      # the tables are set aside only for call 2
    later = "".join("    " + line + "\n" for line in SET_ASIDE.splitlines())
    s = s.replace(SET_ASIDE, "").replace(MOVE, MOVE + later)
elif name == "second_call_keeps_the_jacobian_kernels":
    s = s.replace(MOVE, "")
elif name == "jacobian_tables_not_restored":
    s = s.replace(RESTORE_J, "")
elif name == "preconditioner_tables_not_restored":
    s = s.replace(RESTORE_P, "")
elif name == "boundary_tables_left_alone":
    s = s.replace(BOUNDARY, "PetscCall(PetscDSGetWeakForm(ds, &tables[i++].wf));")
elif name == "not_registered":
    s = s.replace(REGISTER, "")
else:
    raise SystemExit(f"unknown mutant {name}")
path.write_text(s)
