"""Replay a captured _gmsh_fill_2d call with extra gmsh options: python replay_fill.py <pkl> [Name=value ...]"""
import pickle, sys, time
import numpy as np
import gmsh
import underworld3.utilities.place_surface as ps
d = pickle.load(open(sys.argv[1], "rb"))
extra = [a.split("=") for a in sys.argv[2:]]
real_gen = gmsh.model.mesh.generate
def gen(dim):
    for k, v in extra:
        gmsh.option.setNumber(k, float(v))
    return real_gen(dim)
gmsh.model.mesh.generate = gen
t0 = time.time()
try:
    out = ps._gmsh_fill_2d(d["Xall"], d["ring"], d["chain"], holes=d["holes"], size_of=d["size_of"])
    print(f"RESULT finished {time.time()-t0:.1f}s, {len(out[1]) if isinstance(out, tuple) else '?'} triangles")
except Exception as e:
    print(f"RESULT raised {type(e).__name__}: {str(e)[:150]} after {time.time()-t0:.1f}s")
