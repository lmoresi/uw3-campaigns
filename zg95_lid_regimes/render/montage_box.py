"""Tile the rendered frames of a box run into one image, one row per frame, so a
sequence of steps can be read at a glance.

Each frame from render_box.py stacks temperature, log10 eta_eff and eta_eff/eta(T);
``-uw_panels 1`` keeps the temperature panel only, ``2`` adds the viscosity, ``3``
keeps all three. Frames are taken every ``uw_every`` checkpoints from ``uw_first``.

    python montage_box.py -uw_run <dir> -uw_first 2000 -uw_every 2 -uw_count 8
"""
import glob
import os
import re

import numpy as np
import underworld3 as uw
from PIL import Image, ImageDraw

params = uw.Params(
    uw_run="~/+Simulations/zg95/box_faults/runs/stagnant_tau1x1.00_fault_x2.0_dip45_chain",
    uw_first=0,
    uw_every=1,
    uw_count=8,
    uw_panels=2,
    uw_out="",                  # default: <run>/renders/montage_<first>_<last>.png
)
run = os.path.expanduser(params.uw_run)
frames = sorted(glob.glob(os.path.join(run, "renders", "frame_*.png")),
                key=lambda f: int(re.search(r"frame_(\d+)", f).group(1)))
frames = [f for f in frames if int(re.search(r"frame_(\d+)", f).group(1)) >= params.uw_first]
frames = frames[::params.uw_every][:params.uw_count]
if not frames:
    raise SystemExit(f"no frames in {run}/renders from {params.uw_first}")

tiles = []
for f in frames:
    im = Image.open(f).convert("RGB")
    w, h = im.size
    tiles.append(im.crop((0, 0, w, int(h * params.uw_panels / 3))))
tw, th = tiles[0].size
sheet = Image.new("RGB", (tw, th * len(tiles)), "white")
for k, tile in enumerate(tiles):
    sheet.paste(tile, (0, k * th))
    ImageDraw.Draw(sheet).line([(0, k * th), (tw, k * th)], fill=(160, 160, 160), width=2)
first = re.search(r"frame_(\d+)", frames[0]).group(1)
last = re.search(r"frame_(\d+)", frames[-1]).group(1)
out = params.uw_out or os.path.join(run, "renders", f"montage_{first}_{last}.png")
scale = min(1.0, 2400 / sheet.size[1])
sheet = sheet.resize((int(sheet.size[0] * scale), int(sheet.size[1] * scale)), Image.LANCZOS)
sheet.save(out)
print(out)
