"""Pickle each _gmsh_fill_2d call's arguments before it runs; the last file is the spinning one."""
import faulthandler, pickle, sys, runpy
import underworld3.utilities.place_surface as ps
faulthandler.dump_traceback_later(60, exit=True)
real = ps._gmsh_fill_2d
n = [0]
def wrapped(Xall, ring, chain, holes=(), size_of=None):
    n[0] += 1
    with open(f"fill_call_{sys.argv[1]}_{sys.argv[2]}.pkl", "wb") as f:
        pickle.dump(dict(Xall=Xall, ring=ring, chain=chain, holes=holes, size_of=size_of, call=n[0]), f)
    return real(Xall, ring, chain, holes=holes, size_of=size_of)
ps._gmsh_fill_2d = wrapped
sys.argv = ["residual.py"] + sys.argv[1:]
runpy.run_path("residual.py", run_name="__main__")
