# kaiju_tools: composes old-recipe | recipe v2 pair movies matched by step (pair movie jobs, 2026-11-04)
"""Side-by-side movies, old twin left and recipe v2 right, matched by step (the steps both runs checkpointed), each half
the left two panels of the velocity-ring frame (T with streamlines and marker outlines; log10 strain rate), labelled
with the run, step, model time, slab tip depth and the surface plate speeds from records.json. Writes
~/+Claude/kaiju/movies/out/<pair>.mp4 and a contact strip of four matched steps per pair (<pair>_strip.png).
Run in the container (PIL, h5py, imageio-ffmpeg) by pair_movies.sh."""
import glob
import json
import os
import re
import shutil
import subprocess
import tempfile

import h5py
import numpy as np
from PIL import Image, ImageDraw, ImageFont

M = "/home/louis/+Claude/kaiju/movies"
import sys
KIND = sys.argv[1] if len(sys.argv) > 1 else "frame"      # "frame": the whole annulus; "zoom": the window on the trench
FRAMES = {n: f"{M}/work/{n}/{'frames' if KIND == 'frame' else 'zoom'}" for n in ("TAf_env", "TAf_v2", "earth_run1", "earth_run2")}
SET = os.environ.get("PAIRSET", "")                  # "rr1": the corrected restarts (their own work dirs and outputs)
RUNS = {"TAf_env": "/home/louis/campaigns/zg95/runs/slab_thermal_fault_TAf_env",
        "TAf_v2": "/home/louis/+Claude/kaiju/runs/slab_thermal_fault_TAf_v2",
        "earth_run1": "/home/louis/campaigns/zg95/runs/slab_earth_run1",
        "earth_run2": "/home/louis/+Claude/kaiju/runs/slab_earth_run2"}
LABEL = {"TAf_env": "TAf_env (old recipe)", "TAf_v2": "TAf-v2 (recipe v2)",
         "earth_run1": "Earth run 1 (old recipe)", "earth_run2": "Earth run 2 (recipe v2)"}
PAIRS = [("TAf_pair", "TAf_env", "TAf_v2"), ("earth_pair", "earth_run1", "earth_run2")]
if SET == "rr1":           # the cancelled runs' movies stay as the record of the defect; these are separate files
    for n in ("TAf_v2", "earth_run2"):
        FRAMES[n] = f"{M}/work/{n}_rr1/{'frames' if KIND == 'frame' else 'zoom'}"
        RUNS[n] = f"{M}/work/{n}_rr1/ckpts"
    LABEL["TAf_v2"], LABEL["earth_run2"] = "TAf-v2 (recipe v2, corrected)", "Earth run 2 (recipe v2, corrected)"
    PAIRS = [("TAf_pair_rr1", "TAf_env", "TAf_v2"), ("earth_pair_rr1", "earth_run1", "earth_run2")]
if SET == "c":             # the step-0 reruns on the corrected driver (9e69c6b and later): their own work dirs and outputs
    for n in ("TAf_v2", "earth_run2"):
        FRAMES[n] = f"{M}/work/{n}_c/{'frames' if KIND == 'frame' else 'zoom'}"
        RUNS[n] = f"{M}/work/{n}_c/ckpts"
    LABEL["TAf_v2"], LABEL["earth_run2"] = "TAf-v2 (recipe v2, from step 0)", "Earth run 2 (recipe v2, from step 0)"
    PAIRS = [("TAf_pair_c", "TAf_env", "TAf_v2"), ("earth_pair_c", "earth_run1", "earth_run2")]
FONT = None
for path in ("/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
    if os.path.exists(path):
        FONT = ImageFont.truetype(path, 44)
        break
FONT = FONT or ImageFont.load_default()
os.makedirs(f"{M}/out", exist_ok=True)


def image_name(name):
    """the file prefix the renderer used in this directory (a zoom render may name its windows frame_N or zoom_N)"""
    for prefix in (KIND, "frame"):
        if glob.glob(os.path.join(FRAMES[name], f"{prefix}_*.png")):
            return prefix
    return KIND


def steps(name):
    p = image_name(name)
    return {int(re.search(rf"{p}_(\d+)\.png", f).group(1)) for f in glob.glob(os.path.join(FRAMES[name], f"{p}_*.png"))}


def tip(run, step):
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


def record(run, step):
    for r in json.load(open(os.path.join(run, "records.json"))):
        if r.get("step") == step and "vrms" in r:
            return r
    return {}


def half(name, step):
    im = Image.open(os.path.join(FRAMES[name], f"{image_name(name)}_{step:05d}.png")).convert("RGB")
    # the left two panels: T with streamlines and marker outlines; log10 strain rate (the zoom's last two are the
    # plastic strain and yield panels, nearly empty here)
    im = im.crop((0, 0, im.width // 2, im.height))
    t, d = tip(RUNS[name], step)
    rec = record(RUNS[name], step)
    plates = list((rec.get("plates") or {}).values())
    pl = f"   plates {plates[0][0]:.0f} / {plates[0][1]:.0f}" if plates else ""
    head = 150
    canvas = Image.new("RGB", (im.width, im.height + head), "white")
    canvas.paste(im, (0, head))
    draw = ImageDraw.Draw(canvas)
    draw.text((30, 12), LABEL[name], fill="black", font=FONT)
    draw.text((30, 80), f"step {step}   t {t:.5f}   tip {d:.3f}   vrms {rec.get('vrms', float('nan')):.0f}{pl}",
              fill="black", font=FONT)
    return canvas


for pair, left, right in PAIRS:
    common = sorted(steps(left) & steps(right))
    if not common:
        print(f"{pair}: no common steps")
        continue
    tmp = tempfile.mkdtemp(dir=f"{M}/out")
    frames = []
    for k, s in enumerate(common):
        a, b = half(left, s), half(right, s)
        canvas = Image.new("RGB", (a.width + b.width + 20, max(a.height, b.height)), "white")
        canvas.paste(a, (0, 0))
        canvas.paste(b, (a.width + 20, 0))
        scale = 1920 / canvas.width
        canvas = canvas.resize((1920, 2 * round(canvas.height * scale / 2)), Image.LANCZOS)
        canvas.save(os.path.join(tmp, f"m_{k:04d}.png"))
        frames.append(canvas)
    import imageio_ffmpeg
    pair = pair if KIND == "frame" else pair + "_zoom"
    out = f"{M}/out/{pair}.mp4"
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-framerate", "3",
                    "-i", os.path.join(tmp, "m_%04d.png"), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
                    "-movflags", "+faststart", out], check=True)
    pick = [frames[i] for i in np.unique(np.linspace(0, len(frames) - 1, 4).round().astype(int))]
    strip = Image.new("RGB", (pick[0].width, sum(p.height for p in pick)), "white")
    y = 0
    for p in pick:
        strip.paste(p, (0, y))
        y += p.height
    strip.resize((960, round(strip.height * 960 / strip.width))).save(f"{M}/out/{pair}_strip.png")
    shutil.rmtree(tmp)
    print(f"-> {out}: {len(common)} frames, steps {common[0]}-{common[-1]}")
