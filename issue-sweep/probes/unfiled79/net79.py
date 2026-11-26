import time, threading
t0 = time.perf_counter()
import underworld3 as uw
t1 = time.perf_counter()
times = []
for h in (0.2, 0.1, 0.05):
    a = time.perf_counter()
    uw.meshing.UnstructuredSimplexBox(minCoords=(0, 0), maxCoords=(1, 1), cellSize=h)
    times.append(time.perf_counter() - a)
alive = [t.name for t in threading.enumerate() if t is not threading.main_thread()]
print(f"NET import {t1 - t0:.2f} s, meshes {[round(x, 2) for x in times]} s, threads alive {alive}", flush=True)
