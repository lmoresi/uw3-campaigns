import warnings, numpy as np, underworld3 as uw
warnings.simplefilter("ignore")
mesh = uw.meshing.UnstructuredSimplexBox(minCoords=(0, 0), maxCoords=(1, 1), cellSize=1 / 12, regular=False)
h = 1 / 12
for ds in (2.0, 1.0, 0.7, 0.5, 0.3):
    for ang in (0.3, 1.1):
        n = int(round(6 / ds))
        s = np.linspace(0, 6 * h, n + 1)
        Q = np.array([0.5, 0.5]) + np.outer(s - 3 * h, [np.cos(ang), np.sin(ang)])
        try:
            m2 = mesh.add_fault(("F", Q))
            b = [bb for bb in m2.boundaries if bb.name == "F"][0]
            lab = m2.dm.getLabel("F")
            print(f"STRAIGHT ds {ds} ang {ang}: ok, facets {lab.getStratumSize(b.value)}", flush=True)
        except Exception as e:
            print(f"STRAIGHT ds {ds} ang {ang}: raised {str(e)[:70]}", flush=True)
