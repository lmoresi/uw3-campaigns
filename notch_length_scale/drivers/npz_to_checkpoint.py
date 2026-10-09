"""One-off migration: the early runs saved their fields as npz (serial, rank-local
arrays); write each as a checkpoint (``write_timestep``) beside them, so every later
script reads one parallel-safe format. Run serially, once - the npz files are serial
by construction. Skips runs that already have a checkpoint.
"""
import glob
import os
import re
import sys

import numpy as np
import underworld3 as uw

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)
import coupled_notch as cn   # noqa: E402

NAME = re.compile(r"fields_(micro|cosserat)_ref(\d)_xi([\d.]+)_.*\.npz")
COUPLED = dict(micro=("chi", 1), cosserat=("omega", None))
for model_dir in ("micromorphic", "cosserat"):
    out = os.path.join(_here, "..", "results", model_dir)
    for path in sorted(glob.glob(os.path.join(out, "fields_*.npz"))):
        match = NAME.match(os.path.basename(path))
        if match is None:
            continue
        kind, ref, xi = match.group(1), int(match.group(2)), float(match.group(3))
        name = os.path.basename(path)[len("fields_"):-len(".npz")]
        if os.path.exists(os.path.join(out, "checkpoints", f"{name}.mesh.U.00000.h5")):
            continue
        saved = np.load(path)
        S = cn.build_notch(ref, xi, seed=False)
        key, degree = COUPLED[kind]
        degree = degree or (2 if "_P2" in name else 1)
        coupled = uw.discretisation.MeshVariable(key, S["mesh"], 1, degree=degree, units="1/s")
        fields = dict(v=S["v"], p=S["p"], **{key: coupled})
        for k, var in fields.items():
            if not np.allclose(np.asarray(var.coords), saved[f"{k}_coords"]):
                raise ValueError(f"{path}: {k} nodes do not match the rebuilt mesh")
            values = saved[k].reshape(var.array.shape)
            if var.units is not None:
                values = uw.utilities.UnitAwareArray(values, units=var.units)
            var.array[...] = values
        os.makedirs(os.path.join(out, "checkpoints"), exist_ok=True)
        S["mesh"].write_timestep(name, 0, outputPath=os.path.join(out, "checkpoints"),
                                 meshVars=list(fields.values()), create_xdmf=False)
        uw.pprint(f"checkpoint written: {name}")
        del S
