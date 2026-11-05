# kaiju_tools: composes the Earth overturn movie, whole annulus and trench window (jobs 3984, 3992)
"""The Earth overturn movie (Earth run 2_c, recipe v2 from step 0, continued past the base): each frame is the whole
annulus (left) and the trench window (right), the left two panels of each render (T with streamlines and marker
outlines; log10 strain rate), labelled with step, model time, slab tip depth, vrms and the surface plate speeds from
records.json. Writes ~/+Claude/kaiju/movies/out/earth_overturn.mp4 and a contact strip of six steps.
Run in the container (PIL, h5py, imageio-ffmpeg) by overturn_movie.sh."""
import glob
import os
import re
import shutil
import subprocess
import tempfile

import json
import types

import h5py
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# tip(), record() and the font as in pair_frames.py (not imported: its module-level loop would rebuild the pair movies)
pf = types.SimpleNamespace(FONT=None)
for path in ("/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
    if os.path.exists(path):
        pf.FONT = ImageFont.truetype(path, 44)
        break
pf.FONT = pf.FONT or ImageFont.load_default()


def _tip(run, step):
    """slab tip depth (tip_depth.py's definition: T < 0.5 below 0.14, within 90 deg of the trench angle)"""
    with open(os.path.join(run, f"state_{step:05d}.json")) as f:
        s = json.load(f)
    with h5py.File(os.path.join(run, f"annulus.mesh.T.{step:05d}.h5"), "r") as h:
        xy = h["fields/coordinates"][:]
        T = h["fields/T"][:].ravel()
    r = np.hypot(xy[:, 0], xy[:, 1])
    depth = r.max() - r
    dth = (np.arctan2(xy[:, 1], xy[:, 0]) - float(s["params"]["uw_theta_trench"]) + np.pi) % (2 * np.pi) - np.pi
    cold = (T < 0.5) & (depth > 0.14) & (np.abs(dth) < np.pi / 2)
    return s["t"], float(depth[cold].max()) if cold.any() else float("nan")


RECORDS = None


def _record(run, step):
    global RECORDS
    if RECORDS is None:
        RECORDS = {r.get("step"): r for r in json.load(open(os.path.join(run, "records.json"))) if "vrms" in r}
    return RECORDS.get(step, {})


pf.tip, pf.record = _tip, _record

M = "/home/louis/+Claude/kaiju/movies"
import sys
TAG = f"_{sys.argv[1]}" if len(sys.argv) > 1 else ""   # "v2": the restyled render (particles, no contours)
W = f"{M}/work/earth_overturn{TAG}"
RUN = f"{W}/ckpts"


def steps(d, prefix):
    return {int(re.search(rf"{prefix}_(\d+)\.png", f).group(1)) for f in glob.glob(f"{d}/{prefix}_*.png")}


def left_half(path):
    im = Image.open(path).convert("RGB")
    return im.crop((0, 0, im.width // 2, im.height))


zp = "zoom" if glob.glob(f"{W}/zoom/zoom_*.png") else "frame"
common = sorted(steps(f"{W}/frames", "frame") & steps(f"{W}/zoom", zp))
tmp = tempfile.mkdtemp(dir=f"{M}/out")
frames = []
for k, s in enumerate(common):
    a = left_half(f"{W}/frames/frame_{s:05d}.png")
    b = left_half(f"{W}/zoom/{zp}_{s:05d}.png")
    b = b.resize((round(b.width * a.height / b.height), a.height), Image.LANCZOS)
    t, d = pf.tip(RUN, s)
    rec = pf.record(RUN, s)
    plates = list((rec.get("plates") or {}).values())
    pl = f"   plates {plates[0][0]:.0f} / {plates[0][1]:.0f}" if plates else ""
    head = 150
    canvas = Image.new("RGB", (a.width + b.width + 20, a.height + head), "white")
    canvas.paste(a, (0, head))
    canvas.paste(b, (a.width + 20, head))
    draw = ImageDraw.Draw(canvas)
    draw.text((30, 12), "Earth run 2 (recipe v2, from step 0): the overturn", fill="black", font=pf.FONT)
    draw.text((30, 80), f"step {s}   t {t:.5f}   tip {d:.3f}   vrms {rec.get('vrms', float('nan')):.0f}{pl}",
              fill="black", font=pf.FONT)
    canvas = canvas.resize((1920, 2 * round(canvas.height * 1920 / canvas.width / 2)), Image.LANCZOS)
    canvas.save(os.path.join(tmp, f"m_{k:04d}.png"))
    frames.append(canvas)
import imageio_ffmpeg
out = f"{M}/out/earth_overturn{TAG}.mp4"
subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-framerate", "8",
                "-i", os.path.join(tmp, "m_%04d.png"), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
                "-movflags", "+faststart", out], check=True)
pick = [frames[i] for i in np.unique(np.linspace(0, len(frames) - 1, 6).round().astype(int))]
strip = Image.new("RGB", (pick[0].width, sum(p.height for p in pick)), "white")
y = 0
for p in pick:
    strip.paste(p, (0, y))
    y += p.height
strip.resize((960, round(strip.height * 960 / strip.width))).save(f"{M}/out/earth_overturn{TAG}_strip.png")
frames[-1].save(f"{M}/out/earth_overturn{TAG}_last.png")
shutil.rmtree(tmp)
print(f"-> {out}: {len(common)} frames, steps {common[0]}-{common[-1]}")
