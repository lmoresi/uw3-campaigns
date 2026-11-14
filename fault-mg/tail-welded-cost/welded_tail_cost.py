"""One rank: what a welded add-on level under a split finest costs the velocity
multigrid.

Fixture: tests/parallel/fault_fixtures.py (unit box, add-on of k levels toward a
straight interior trace, frictionless fault, simple shear on the walls). The
replay of the cut onto the add-on levels (fault_mg.split_tail_levels) runs from
the finest add-on level down and stops at the first level it cannot cut; here it
is made to stop after `kept` levels, as a refusal would.

    python welded_tail_cost.py <directory holding fault_fixtures.py>
"""
import sys
import warnings

import numpy as np
import underworld3 as uw
from underworld3.utilities import fault_split

sys.path.insert(0, sys.argv[1])
import fault_fixtures as ff  # noqa: E402

original = fault_split.add_fault
state = {"kept": None, "replays": 0}


def add_fault(mesh, *args, **kwargs):
    if kwargs.get("partition", True) is False:          # a replay onto a level
        if state["kept"] is not None and state["replays"] >= state["kept"]:
            raise RuntimeError("probe: this level is refused")
        state["replays"] += 1
    return original(mesh, *args, **kwargs)


fault_split.add_fault = add_fault

for k in (1, 2, 3, 4):
    for kept in [None] + list(range(k - 1, -1, -1)):
        state.update(kept=kept, replays=0)
        print(f"START k={k} kept={kept}", file=sys.stderr, flush=True)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            mesh = ff.faulted_2d(k)
            tail = mesh._custom_mg_coarse_meshes
            split = [bool(getattr(m, "_fault_point_pairs", None)) for m in tail]
            stokes, info, slip = ff.shear_fault_solve(mesh)
        said = [str(w.message)[:90] for w in caught if "fault_mg" in str(w.message)]
        print(f"k={k} add-on levels split {sum(split)} of {k} (tail {len(tail)} levels, split flags {split}); "
              f"pc {info.get('velocity_pc')}; converged {info.get('converged')}; "
              f"velocity its per outer {info.get('vel_its_last')}; outer {info.get('ksp_its', info.get('outer_its'))}; "
              f"peak slip {slip:.6f}; warned {bool(said)}", flush=True)
print("info keys:", sorted(info.keys()))
print("done")
