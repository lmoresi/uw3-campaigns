"""pytest plugin: put development's barycentric builder back (to show a test fails on it)."""
import os
import numpy as np
from underworld3.utilities import custom_mg
_ns = {"np": np, "_record": custom_mg._record}
exec(open(os.path.join(os.path.dirname(__file__), "old_bary.py")).read(), _ns)
custom_mg.barycentric_prolongation = _ns["_old_barycentric_prolongation"]
