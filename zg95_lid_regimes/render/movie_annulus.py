"""A movie of an annulus run's rendered checkpoints: the full annulus over the zoom on
the trench, each frame labelled with its frame number, step and time.

    python movie_annulus.py -uw_run <run dir> -uw_out <movie.mp4> -uw_fps 3
"""
import glob
import json
import os
import re
import shutil
import subprocess
import tempfile

import underworld3 as uw
from PIL import Image, ImageDraw, ImageFont

params = uw.Params(
    uw_run="~/+Simulations/zg95/annulus_faults/runs/tau1x1.50_fault_th0_dip45_fn_sw_reg10",
    uw_out="",                  # default: <run>/renders/movie.mp4
    uw_fps=3,
    uw_width=1920,              # output width in pixels
    uw_renders="renders",       # the renders directory under the run (renders_strain for the strain panels)
)
run = os.path.expanduser(params.uw_run)
renders = os.path.join(run, params.uw_renders)
out = os.path.expanduser(params.uw_out) if params.uw_out else os.path.join(renders, "movie.mp4")

steps = sorted(int(re.search(r"frame_(\d+)\.png", f).group(1))
               for f in glob.glob(os.path.join(renders, "frame_*.png")))
steps = [s for s in steps if os.path.exists(os.path.join(renders, f"zoom_{s:05d}.png"))]
font = None
for path in ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/System/Library/Fonts/Helvetica.ttc"):
    if os.path.exists(path):
        font = ImageFont.truetype(path, 56)
        break
font = font or ImageFont.load_default()

tmp = tempfile.mkdtemp(dir=renders)
for k, step in enumerate(steps):
    full = Image.open(os.path.join(renders, f"frame_{step:05d}.png")).convert("RGB")
    zoom = Image.open(os.path.join(renders, f"zoom_{step:05d}.png")).convert("RGB")
    header = 110                # the label sits in its own strip, clear of the panels
    canvas = Image.new("RGB", (max(full.width, zoom.width), header + full.height + zoom.height), "white")
    canvas.paste(full, (0, header))
    canvas.paste(zoom, (0, header + full.height))
    with open(os.path.join(run, f"state_{step:05d}.json")) as f:
        t = json.load(f)["t"]
    label = f"frame {k:3d}   step {step}   t = {t:.4f}"
    draw = ImageDraw.Draw(canvas)
    draw.text((40, 25), label, fill="black", font=font)
    scale = params.uw_width / canvas.width
    canvas = canvas.resize((params.uw_width, 2 * round(canvas.height * scale / 2)), Image.LANCZOS)
    canvas.save(os.path.join(tmp, f"m_{k:04d}.png"))

subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(params.uw_fps),
                "-i", os.path.join(tmp, "m_%04d.png"), "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-crf", "18", out], check=True)
shutil.rmtree(tmp)
print(f"-> {out}: {len(steps)} frames, steps {steps[0]}-{steps[-1]}")
