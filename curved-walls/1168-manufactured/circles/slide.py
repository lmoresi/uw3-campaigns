"""Slide the annulus's nodes along their circles, as a mesh mover or adaptation would,
so that the wall chords are no longer of equal length. Radii are unchanged, so the
walls stay on their circles exactly (to rounding).

  "none"    the gmsh mesh as built (its wall chords are all of one length)
  "graded"  every node: theta -> theta + 0.1 sin 3 theta (monotone; chord lengths
            on each wall vary by +-30 % smoothly around it)
  "graded2" every node: theta -> theta + 0.1 sin 2 theta (grading aligned with the
            sin 2 theta slip: chord length squared then carries cos 2 theta)
  "graded3c" every node: theta -> theta + 0.1 cos 3 theta (grading aligned with the
            cos 3 theta slip's derivative)
  "jitter"  wall vertices only: each moved along its circle by a random fraction
            in [-1/4, 1/4] of its wall's mean chord (seeded, so the same mesh each run)
"""
import numpy as np
import underworld3 as uw
from underworld3.meshing.smoothing.graph import _pinned_mask


def slide(mesh, how, radii=(0.5, 1.0)):
    if how == "none":
        return
    xy = np.array(mesh.X.coords)
    r = np.hypot(xy[:, 0], xy[:, 1])
    th = np.arctan2(xy[:, 1], xy[:, 0])
    if how == "graded":
        th = th + 0.1 * np.sin(3 * th)
    elif how == "graded2":
        th = th + 0.1 * np.sin(2 * th)
    elif how == "graded3c":
        th = th + 0.1 * np.cos(3 * th)
    elif how == "jitter":
        rng = np.random.default_rng(1168)
        for wall in ("Upper", "Lower"):
            on = _pinned_mask(mesh.dm, (wall,))
            n = on.sum()
            th[on] = th[on] + rng.uniform(-0.25, 0.25, n) * (2 * np.pi / n)
    else:
        raise ValueError(how)
    new = np.stack([r * np.cos(th), r * np.sin(th)], axis=1)
    mesh._deform_mesh(new)
