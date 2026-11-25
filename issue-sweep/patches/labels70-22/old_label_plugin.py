"""pytest plugin: development's _label_cut_edges (the midpoint rule), to show a test fails on it."""
import os
from underworld3.utilities import line_cut as lc
ns = dict(lc.__dict__)
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "old_label.py")).read(), ns)
lc._label_cut_edges = ns["_old_label_cut_edges"]
