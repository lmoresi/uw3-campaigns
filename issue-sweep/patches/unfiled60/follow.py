"""Follow the messages: from the refused ribbon (top 0.9, width 0.1) and sheet (z 0.87), apply
each message's first suggestion until the placement succeeds; print each step."""
import re, numpy as np, underworld3 as uw
from underworld3.utilities.place_surface import place_fault_ribbon_2d, place_sheet
m = uw.meshing.Annulus(radiusOuter=1.0, radiusInner=0.5, cellSize=0.1, refinement=1, qdegree=2)
th, dip = np.radians(80.0), np.radians(35.0)
inward = -np.array([np.cos(th - dip), np.sin(th - dip)])
def ribbon(top_r, wdt):
    top = top_r * np.array([np.cos(th), np.sin(th)])
    place_fault_ribbon_2d(m, [("Fault", top + (0.05 * np.arange(7))[:, None] * inward)], wdt,
                          margin_rings=1, clearance=0.7, split=False, mesher="ladder")
for plan in ("move", "narrow-then-move"):
    r, wdt = 0.9, 0.1
    for step in range(5):
        try:
            ribbon(r, wdt); print(f"FOLLOW ribbon {plan} step {step}: top {r:.4f} width {wdt:.4f} placed"); break
        except RuntimeError as e:
            msg = str(e)
            mv = float(re.search(r"at least about ([0-9.e-]+) further", msg).group(1))
            nw = re.search(r"down to a width of about ([0-9.e-]+)", msg)
            if plan == "narrow-then-move" and nw and step == 0:
                wdt = float(nw.group(1)); act = f"narrow to {wdt:.4f}"
            else:
                r -= mv; act = f"move {mv:.4f} (top {r:.4f})"
            print(f"FOLLOW ribbon {plan} step {step}: refused -> {act}; reach/wall " + " ".join(re.findall(r"(?:reaches|is) ([0-9.]+) from", msg)))
s = np.linspace(-0.2, 0.2, 5)
tris = np.array([t for i in range(4) for j in range(4) for t in ((5*i+j, 5*i+j+1, 5*(i+1)+j+1), (5*i+j, 5*(i+1)+j+1, 5*(i+1)+j))], dtype=np.int64)
box = uw.meshing.UnstructuredSimplexBox(minCoords=(0, 0, 0), maxCoords=(1, 1, 1), cellSize=0.11, regular=False, qdegree=2)
z = 0.87
for step in range(5):
    try:
        place_sheet(box.dm, np.array([(0.5 + a, 0.5 + b, z) for a in s for b in s]), tris, label="Fault")
        print(f"FOLLOW sheet step {step}: z {z:.4f} placed"); break
    except RuntimeError as e:
        mv = float(re.search(r"at least about ([0-9.e-]+) further", str(e)).group(1)); z -= mv
        print(f"FOLLOW sheet step {step}: refused -> move {mv:.4f} (z {z:.4f})")
