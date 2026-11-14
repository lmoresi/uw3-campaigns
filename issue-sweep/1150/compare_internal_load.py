"""#1150: compare the load of two runs of internal_load_by_face.py, node by node.

    python compare_internal_load.py internal_load_np1.npz internal_load_np8.npz

A node is identified between the two runs by the exact bytes of its
coordinates: the two runs read one mesh file, and no number is shared between
two partitions of it. No tolerance is used for that match; nodes of one run
with no partner in the other are counted and reported (a mesh whose coordinates
depend on the rank count would itself be a finding). Each node's load is the
sum of the rows every rank holds for it.

ROUND_OFF (1e-12, relative to the largest nodal load) separates a difference
from round-off. ON_FACE (1e-9, in barycentric coordinates, dimensionless)
decides whether a node lies on a face of `Internal`.
"""
import sys

import numpy as np

ROUND_OFF = 1.0e-12
ON_FACE = 1.0e-9


def assembled(path):
    data = np.load(path)
    total = {}
    for xyz, load in zip(data["node_xyz"], data["node_load"]):
        key = np.ascontiguousarray(xyz).tobytes()
        total[key] = total.get(key, 0.0) + load
    return data, total


def faces_holding(point, face_xyz):
    """Indices of the faces the point lies on."""
    a, b, c = face_xyz[:, 0], face_xyz[:, 1], face_xyz[:, 2]
    e1, e2, d = b - a, c - a, point - a
    normal = np.cross(e1, e2)
    area2 = (normal * normal).sum(axis=1)
    l1 = (np.cross(d, e2) * normal).sum(axis=1) / area2
    l2 = (np.cross(e1, d) * normal).sum(axis=1) / area2
    off = np.abs((d * normal).sum(axis=1)) / area2 ** 0.75
    inside = (l1 > -ON_FACE) & (l2 > -ON_FACE) & (l1 + l2 < 1.0 + ON_FACE) & (off < ON_FACE)
    return np.flatnonzero(inside)


first, load_a = assembled(sys.argv[1])
second, load_b = assembled(sys.argv[2])
only_a, only_b = set(load_a) - set(load_b), set(load_b) - set(load_a)
print(f"nodes: {len(load_a)} and {len(load_b)}; without a partner: {len(only_a)} and {len(only_b)}")

common = sorted(set(load_a) & set(load_b))
xyz = np.array([np.frombuffer(k, dtype=float) for k in common])
a = np.array([load_a[k] for k in common])
b = np.array([load_b[k] for k in common])
scale = max(np.abs(a).max(), np.abs(b).max())
diff = np.abs(b - a).max(axis=1)
differing = np.flatnonzero(diff > ROUND_OFF * scale)
print(f"largest nodal load {scale:.6e}; nodes that differ by more than {ROUND_OFF:g} of it: "
      f"{len(differing)} of {len(common)}; sum of the differences {(b - a).sum(axis=0)}")

# the faces of the SECOND run (the one with more ranks) say which are shared
face_xyz, face_ranks = second["face_xyz"], second["face_ranks"]
print(f"faces of Internal in the second file: {len(face_xyz)}; held by more than one rank: "
      f"{int((face_ranks > 1).sum())}")
on_shared = on_single = off_surface = 0
touched = set()
for i in sorted(differing, key=lambda j: -diff[j]):
    faces = faces_holding(xyz[i], face_xyz)
    shared = [int(f) for f in faces if face_ranks[f] > 1]
    touched.update(shared)
    if len(faces) == 0:
        off_surface += 1
    elif shared:
        on_shared += 1
    else:
        on_single += 1
print(f"differing nodes: {on_shared} on a face held by more than one rank, {on_single} only on faces "
      f"held by one rank, {off_surface} not on Internal")
print(f"faces held by more than one rank that carry a differing node: {len(touched)} of "
      f"{int((face_ranks > 1).sum())}")
for i in sorted(differing, key=lambda j: -diff[j])[:12]:
    faces = faces_holding(xyz[i], face_xyz)
    print(f"  node at radius {np.linalg.norm(xyz[i]):.6f}: difference {b[i] - a[i]} "
          f"(load {a[i]}); faces {len(faces)}, ranks holding them {face_ranks[faces].tolist()}, "
          f"owners {second['face_owner'][faces].tolist()}")
