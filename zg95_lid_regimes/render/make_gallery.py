"""One image of every box run's final state (T over log10 eta_eff), labelled, for comparing regimes."""
import os
from PIL import Image, ImageDraw, ImageFont
Z = os.path.expanduser("~/+Simulations/zg95")
rows = [
    ("box_regimes/runs/mobile_ref_H1.42", 1975, "No fault, tau1/Ra 1, standard start: STAGNANT (M 0.03)"),
    ("box_regimes/runs/tau1x0.75_H1.42", 6625, "No fault, tau1/Ra 0.75: mobile (M 0.85)"),
    ("box_regimes/runs/tau1x0.50_H1.42", 2150, "No fault, tau1/Ra 0.5: mobile (M 0.92)"),
    ("box_regimes/runs/tau1x1.00_from_mobile_H1.42", 5675, "No fault, tau1/Ra 1 from a mobile start: MOBILE (bistable, M 0.78)"),
    ("box_faults/runs/stagnant_tau1x1.00_fault_x2.0_dip45_chain", 4000, "Fixed fault through the stagnant lid, t 0.405: fault became a spreading centre (M 0.74)"),
    ("box_faults/runs/stagnant_tau1x1.00_fault_x2.0_dip45_moving_chain", 2619, "Moving-trench fault, t 0.282: spreading, fault carried with the plate (M 0.75)"),
    ("box_regimes/runs/unfaulted_from_fault_4000", 6075, "Fixed-fault final state with the fault REMOVED, dt 0.18 later: stays mobile (M 0.69)"),
]
tiles = []
for run, idx, label in rows:
    im = Image.open(os.path.join(Z, run, "renders", f"frame_{idx:05d}.png")).convert("RGB")
    w, h = im.size
    im = im.crop((0, 0, w, int(h * 2 / 3)))
    band = Image.new("RGB", (w, 56), "white")
    ImageDraw.Draw(band).text((20, 10), label, fill=(0, 0, 0), font=ImageFont.load_default(size=34))
    tile = Image.new("RGB", (w, im.size[1] + 56), "white")
    tile.paste(band, (0, 0)); tile.paste(im, (0, 56))
    tiles.append(tile)
W, H = tiles[0].size
sheet = Image.new("RGB", (W, H * len(tiles)), "white")
for k, t in enumerate(tiles):
    sheet.paste(t, (0, k * H))
    ImageDraw.Draw(sheet).line([(0, k * H), (W, k * H)], fill=(120, 120, 120), width=3)
scale = 3000 / sheet.size[1]
sheet = sheet.resize((int(W * scale), 3000), Image.LANCZOS)
out = os.path.join(Z, "movies", "00_regime_gallery.png")
sheet.save(out); print(out)
