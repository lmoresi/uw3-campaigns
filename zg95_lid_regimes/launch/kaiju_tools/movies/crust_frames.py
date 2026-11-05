# kaiju_tools: composes the crust-test comparison movies matched by model time (jobs 4035, 4050)
"""The crust-test comparison movies (Louis, 2026-11-05: "how the evolution looks"): per case (TAf, Earth), three columns
- the production crust (one base cell, weak; the control), the half-element crust and the passive crust - matched by
model time: for each control checkpoint, each other arm's checkpoint nearest in time (blank once an arm has not reached
it). Each column is the whole annulus's temperature panel above the trench window's, from the render_v2 renders
(particles, no contours), labelled with the arm, step, model time, slab tip depth, vrms and plate speeds.
Writes ~/+Claude/kaiju/movies/out/crust_<case>.mp4 and a contact strip. Run in the container by crust_movies.sh."""
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
CASES = {"TAf": "TAf-v2", "earth": "Earth run 2"}
ARMS = [("c1", "production crust (1 cell, weak)"), ("c05", "half-element crust"), ("passive", "passive crust (no weakening)")]
FONT = None
for path in ("/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
    if os.path.exists(path):
        FONT = ImageFont.truetype(path, 30)
        BIG = ImageFont.truetype(path, 40)
        break
FONT = FONT or ImageFont.load_default()
BIG = BIG if FONT is not ImageFont.load_default() else FONT


def work(case, arm):
    return f"{M}/work/crust_{case}_{arm}"


def steps(case, arm):
    w = work(case, arm)
    a = {int(re.search(r"frame_(\d+)", f).group(1)) for f in glob.glob(f"{w}/frames/frame_*.png")}
    b = {int(re.search(r"zoom_(\d+)", f).group(1)) for f in glob.glob(f"{w}/zoom/zoom_*.png")}
    return sorted(a & b)


def state(case, arm, s):
    return json.load(open(f"{work(case, arm)}/ckpts/state_{s:05d}.json"))


def tip(case, arm, s):
    st = state(case, arm, s)
    with h5py.File(f"{work(case, arm)}/ckpts/annulus.mesh.T.{s:05d}.h5", "r") as h:
        xy = h["fields/coordinates"][:]
        T = h["fields/T"][:].ravel()
    r = np.hypot(xy[:, 0], xy[:, 1])
    depth = r.max() - r
    dth = (np.arctan2(xy[:, 1], xy[:, 0]) - float(st["params"]["uw_theta_trench"]) + np.pi) % (2 * np.pi) - np.pi
    cold = (T < 0.5) & (depth > 0.14) & (np.abs(dth) < np.pi / 2)
    return st["t"], float(depth[cold].max()) if cold.any() else float("nan")


RECS = {}


def record(case, arm, s):
    key = (case, arm)
    if key not in RECS:
        RECS[key] = {r.get("step"): r for r in json.load(open(f"{work(case, arm)}/ckpts/records.json")) if "vrms" in r}
    return RECS[key].get(s, {})


def quarter(path):
    im = Image.open(path).convert("RGB")
    return im.crop((0, 0, im.width // 4, im.height))          # the temperature panel


def column(case, arm, label, s, t_ref):
    w = work(case, arm)
    a = quarter(f"{w}/frames/frame_{s:05d}.png")
    b = quarter(f"{w}/zoom/zoom_{s:05d}.png")
    b = b.resize((a.width, round(b.height * a.width / b.width)))
    head = 150
    col = Image.new("RGB", (a.width, head + a.height + b.height), "white")
    col.paste(a, (0, head))
    col.paste(b, (0, head + a.height))
    t, d = tip(case, arm, s)
    rec = record(case, arm, s)
    pl = list((rec.get("plates") or {}).values())
    d_ = ImageDraw.Draw(col)
    d_.text((14, 6), label, fill="black", font=FONT)
    d_.text((14, 44), f"step {s}  t {t:.2e}  tip {d:.3f}", fill="black", font=FONT)
    d_.text((14, 82), f"vrms {rec.get('vrms', float('nan')):.0f}" + (f"  plates {pl[0][0]:.0f} / {pl[0][1]:.0f}" if pl else ""),
            fill="black", font=FONT)
    return col


def blank(like, label):
    col = Image.new("RGB", like.size, "white")
    ImageDraw.Draw(col).text((14, 6), label + ": not there yet", fill="#888888", font=FONT)
    return col


def ended(like, label, t_end):
    col = Image.new("RGB", like.size, "white")
    ImageDraw.Draw(col).text((14, 6), f"{label}:\nrun ended at t {t_end:.2e}\n(at or past the base)", fill="#888888", font=FONT)
    return col


for case, title in CASES.items():
    ctl = steps(case, "c1")
    if not ctl:
        print(f"{case}: no control frames")
        continue
    times = {arm: {s: state(case, arm, s)["t"] for s in steps(case, arm)} for arm, _ in ARMS}
    tmp = tempfile.mkdtemp(dir=f"{M}/out")
    frames = []
    # the frame times: every control checkpoint, then any later checkpoints of the other arms (they run ahead in time)
    t_list = sorted(set(times["c1"].values()))
    t_max = max(max(v.values()) for v in times.values() if v)
    extra = sorted(t for arm in ("c05", "passive") for t in times[arm].values() if t > max(t_list) + 1e-12)
    t_list += [t for k, t in enumerate(extra) if k == 0 or t - extra[k - 1] > 0.5 * np.median(np.diff(t_list))]
    for k, t_ref in enumerate(t_list):
        cols = []
        half_gap = 0.6 * np.median(np.diff(sorted(times["c1"].values())))
        for arm, label in ARMS:
            got = times[arm]
            if got and max(got.values()) < t_ref - half_gap:
                cols.append(("ended", max(got.values())))
                continue
            if not got or min(got.values()) > t_ref + half_gap:
                cols.append(None)
                continue
            s = min(got, key=lambda x: abs(got[x] - t_ref))
            cols.append(column(case, arm, label, s, t_ref))
        like = next(c for c in cols if c is not None and not isinstance(c, tuple))
        cols = [blank(like, ARMS[i][1]) if c is None else
                ended(like, ARMS[i][1], c[1]) if isinstance(c, tuple) else c for i, c in enumerate(cols)]
        canvas = Image.new("RGB", (sum(c.width for c in cols) + 20 * (len(cols) - 1), like.height + 70), "white")
        ImageDraw.Draw(canvas).text((14, 10), f"{title}: the crust test, matched by model time (t ~ {t_ref:.2e})",
                                    fill="black", font=BIG)
        x = 0
        for c in cols:
            canvas.paste(c, (x, 70))
            x += c.width + 20
        canvas = canvas.resize((1920, 2 * round(canvas.height * 1920 / canvas.width / 2)), Image.LANCZOS)
        canvas.save(os.path.join(tmp, f"m_{k:04d}.png"))
        frames.append(canvas)
    import imageio_ffmpeg
    out = f"{M}/out/crust_{case}.mp4"
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-framerate", "3",
                    "-i", os.path.join(tmp, "m_%04d.png"), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
                    "-movflags", "+faststart", out], check=True)
    pick = [frames[i] for i in np.unique(np.linspace(0, len(frames) - 1, 4).round().astype(int))]
    strip = Image.new("RGB", (pick[0].width, sum(p.height for p in pick)), "white")
    y = 0
    for p in pick:
        strip.paste(p, (0, y))
        y += p.height
    strip.resize((1200, round(strip.height * 1200 / strip.width))).save(f"{M}/out/crust_{case}_strip.png")
    shutil.rmtree(tmp)
    print(f"-> {out}: {len(frames)} frames, t {t_list[0]:.2e}-{t_list[-1]:.2e}")
