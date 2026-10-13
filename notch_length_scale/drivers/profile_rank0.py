"""Run a driver under cProfile on rank 0 only: profile_rank0.py <out.prof> <driver> [args]."""
import cProfile
import runpy
import sys

from mpi4py import MPI

out, driver = sys.argv[1], sys.argv[2]
sys.argv = [driver] + sys.argv[3:]
if MPI.COMM_WORLD.rank == 0:
    cProfile.run(f"runpy.run_path({driver!r}, run_name='__main__')", out)
else:
    runpy.run_path(driver, run_name="__main__")
