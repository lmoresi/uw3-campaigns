# kaiju_tools: composes the resolution movie (ref4 | production | coarse base) matched by tip depth
"""The resolution movie (Louis, 2026-11-04: "I'd like to see the evolution at this resolution to see how well resolved
it is"): TAf-v2 at refinement 4 | production (refinement 5) | the coarse base (cell 0.25, refinement 4, the same
resolution on another triangulation), side by side, the trench window (T with streamlines and marker outlines; log10
strain rate). Frames follow the production run's checkpoints; each other panel shows that run's checkpoint whose slab
tip is nearest in depth (dt differs between the runs, so steps do not correspond), or a blank panel once the tip has
gone deeper than that run reached. Each panel is labelled with run, step, model time, tip depth, vrms and both plate
speeds. Writes ~/+Claude/kaiju/movies/out/TAf_resolution.mp4 and a contact strip. Run in the container by
res_movies.sh.
"""
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
R = "/home/louis/+Claude/kaiju/runs"
RUNS = [("ref4", "TAf-v2, refinement 4 (h_b 0.031)", f"{R}/slab_thermal_fault_TAf_v2_ref4"),
        ("ref5", "TAf-v2, production (h_b 0.0156)", f"{R}/slab_thermal_fault_TAf_v2_c"),
        ("cell025", "TAf-v2, coarse base (h_b 0.0156, other mesh)", f"{R}/slab_thermal_fault_TAf_v2_cell025")]
FONT = None
for path in ("/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
    if os.path.exists(path):
        FONT = ImageFont.truetype(path, 40)
        break
FONT = FONT or ImageFont.load_default()


def tip(run, step):
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


def frames(key):
    d = f"{M}/work/res_{key}/zoom"
    out = {}
    for f in glob.glob(os.path.join(d, "*.png")):
        m = re.search(r"(?:zoom|frame)_(\d+)\.png", f)
        if m:
            out[int(m.group(1))] = f
    return out


records = {}
for key, _, run in RUNS:
    records[key] = {r["step"]: r for r in json.load(open(os.path.join(run, "records.json"))) if "vrms" in r}
avail = {key: frames(key) for key, _, _ in RUNS}
tips = {key: {s: tip(run, s) for s in sorted(avail[key])} for key, _, run in RUNS}
for key in tips:
    print(key, "checkpoints", sorted(tips[key]), flush=True)


def panel(key, label, step):
    if step is None:
        im = Image.open(next(iter(avail["ref5"].values()))).convert("RGB")
        im = im.crop((0, 0, im.width // 2, im.height))
        im = Image.new("RGB", im.size, "white")
        text = ["(tip deeper than this run reached)", ""]
    else:
        im = Image.open(avail[key][step]).convert("RGB")
        im = im.crop((0, 0, im.width // 2, im.height))
        t, d = tips[key][step]
        rec = records[key].get(step, {})
        pl = list((rec.get("plates") or {}).values())
        text = [f"step {step}   t {t:.5f}   tip {d:.3f}",
                f"vrms {rec.get('vrms', float('nan')):.0f}" + (f"   plates {pl[0][0]:.0f} / {pl[0][1]:.0f}" if pl else "")]
    head = 190
    canvas = Image.new("RGB", (im.width, im.height + head), "white")
    canvas.paste(im, (0, head))
    draw = ImageDraw.Draw(canvas)
    draw.text((20, 10), label, fill="black", font=FONT)
    draw.text((20, 70), text[0], fill="black", font=FONT)
    draw.text((20, 125), text[1], fill="black", font=FONT)
    return canvas


tmp = tempfile.mkdtemp(dir=f"{M}/out")
made = []
for k, s5 in enumerate(sorted(tips["ref5"])):
    target = tips["ref5"][s5][1]
    row = []
    for key, label, _ in RUNS:
        if key == "ref5":
            row.append(panel(key, label, s5))
            continue
        cand = [(abs(d - target), s) for s, (_, d) in tips[key].items() if np.isfinite(d)]
        reach = max((d for _, d in tips[key].values() if np.isfinite(d)), default=-1)
        pick = min(cand)[1] if cand and (target <= reach + 0.02) else None
        row.append(panel(key, label, pick))
    canvas = Image.new("RGB", (sum(p.width for p in row) + 40, max(p.height for p in row)), "white")
    x = 0
    for p in row:
        canvas.paste(p, (x, 0))
        x += p.width + 20
    canvas = canvas.resize((2400, 2 * round(canvas.height * 2400 / canvas.width / 2)), Image.LANCZOS)
    canvas.save(os.path.join(tmp, f"m_{k:04d}.png"))
    made.append(canvas)
import imageio_ffmpeg  # noqa: E402
out = f"{M}/out/TAf_resolution.mp4"
subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-framerate", "3",
                "-i", os.path.join(tmp, "m_%04d.png"), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
                "-movflags", "+faststart", out], check=True)
pick = [made[i] for i in np.unique(np.linspace(0, len(made) - 1, 4).round().astype(int))]
strip = Image.new("RGB", (pick[0].width, sum(p.height for p in pick)), "white")
y = 0
for p in pick:
    strip.paste(p, (0, y))
    y += p.height
strip.resize((1200, round(strip.height * 1200 / strip.width))).save(f"{M}/out/TAf_resolution_strip.png")
shutil.rmtree(tmp)
print(f"-> {out}: {len(made)} frames")
