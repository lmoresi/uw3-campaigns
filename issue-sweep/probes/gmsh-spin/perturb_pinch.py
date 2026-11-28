import pickle, sys, numpy as np
d = pickle.load(open(sys.argv[1], "rb")); vi, ei = int(sys.argv[2]), int(sys.argv[3]); rel, sign = float(sys.argv[4]), float(sys.argv[5])
X = np.array(d["Xall"], dtype=float); ring = list(d["ring"])
A, B = X[ring[ei]], X[ring[(ei + 1) % len(ring)]]; e = B - A; nrm = np.array([-e[1], e[0]]) / np.linalg.norm(e)
X[ring[vi]] = X[ring[vi]] + sign * rel * np.linalg.norm(e) * nrm
d["Xall"] = X
pickle.dump(d, open(sys.argv[6], "wb"))
