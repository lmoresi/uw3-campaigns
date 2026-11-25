"""pytest plugin: swap in the k-fixed-at-9 mutant of the bounded repair."""
import os
import numpy as np
from underworld3.utilities import custom_mg
_ns = {"np": np, "_record": custom_mg._record}
exec(open(os.path.join(os.path.dirname(__file__), "mutant_k9.py")).read(), _ns)
custom_mg.barycentric_prolongation = _ns["_mutant"]
