# Register row 30 (proposed): hold a fault's jump along both arms' normals at a turn vertex

From UNFILED 84. The fault constraint holds a pair's jump to zero along ONE normal, the
measure-weighted average of the adjacent facet normals. At a turn vertex that normal matches
neither arm, and the apex opens against both.

The probe-side patch (`row30.py`) wraps `rotated_bc.build_rotation`. It adds the jump-TANGENT row
of each pair at a turn vertex to the constrained set. In 2-D, both arms' normals span the plane,
so this holds the whole jump at the apex to zero.

## Measured (labels70-22 0008; sheared box, frictionless fault; 12 cells per side against 48)
Kinks with two 2.5-cell arms, sampled half a cell apart; "angle" is the turn. There were 8
orientations per angle and box; the counts are the kinks added at both resolutions with both
constraints.

| Turn | n | Largest-slip error, base (median/max) | Pinned (median/max) | `normal="trace"` (median/max) | Base apex slip at 12 / at 48 | Pinning moves the 48-cell answer (median/max) |
|---|---|---|---|---|---|---|
| 60 | 8 | 14.6 / 35.6 % | 6.3 / 12.4 % | 26.2 / 91.5 % | 0.066 / 0.035 | 3.7 / 15.7 % |
| 90 | 9 | 7.6 / 13.0 % | 4.5 / 10.7 % | 7.6 / 250 % | 0.028 / 0.011 | 0.6 / 3.1 % |
| 120 | 9 | 3.7 / 10.1 % | 4.0 / 9.1 % | 3.1 / 11.0 % | 0.039 / 0.029 | 0.8 / 2.1 % |

**150 and 160 degrees:** no random kink was added at both 12 and 48 (refused at one or both), so
the grid's characterised hairpin (kink150_3, sampled 0.3 cells apart) was run directly:

| | Apex jump at 12 | Largest slip at 12 | At 48 (base / pinned) | Error at 12 |
|---|---|---|---|---|
| box_reg, base | 0.134 | 0.134 | 0.0856 / 0.0856 | +57 % |
| box_reg, pinned | 0 | 0.0744 | | −13 % |
| box_irr, base | 0.139 | 0.139 | 0.0866 / 0.0866 | +60 % |
| box_irr, pinned | 0 | 0.075 | | −13 % |

- **Iterations:** unchanged. The velocity sub-solve's last count is equal or 1-2 fewer with the
  pin, the outer count is 1 either way, and every pinned solve converged with one row pinned.
- **The apex opens at every turn, not only at hairpins.** On the 48-cell mesh the base apex jump
  is still 0.035 at a 60-degree turn and 0.029 at 120. Pinning moves the converged slip by up to
  16 % at 60 degrees (3.7 % median) and under 3 % at 90-120. In the continuum a no-opening jump
  that is tangent to both arms is zero at the corner, so the pinned result is the consistent one.
  That should be confirmed at 96 cells per side, which was not run.
- **The default normal (`normal=None`, #1168's territory)** opens the apex at every turn.
  `normal="trace"` is worse at 60 and 90 degrees (medians 26 % and 7.6 %, outliers up to 250 %).
  On the 150-degree hairpin it gave the same numbers as the pin to four digits; why was not
  traced.
- **3-D (not measured):** a pair's normal is built the same way, from the facet-measure-weighted
  average of the adjacent facet normals, with one jump-normal row. Every node on a crease line
  between two fault facets that meet at an angle has the same structure and can open against both
  sheets. The analogue of the fix holds the jump along both sheets' normals, leaving slip free
  only along the crease. That is the 3-D form of row 30; whether it matters at realistic crease
  angles is not measured here.
- **The place for the change** is the pair-block loop of `rotated_bc.build_rotation` (the
  `normal_rows.append(gm[0])` line). A turn vertex would add its jump-tangent row in 2-D, or the
  row along the second sheet's normal in 3-D. That is a solver change, Louis's under "solver
  stability is paramount", with #1168.

## Convergence to 96 cells per side (hub's check; `conv30.py`, `hpconv.py`)
Largest slip at 12 / 24 / 48 / 96 cells per side, base against pinned:

| Kink | Base | Pinned | Base apex jump |
|---|---|---|---|
| 60 deg, box_irr trial 1 | 0.0993 / 0.1032 / 0.0947 / 0.0905 | 0.0891 / 0.0877 / 0.0865 / 0.0864 | 0.069 / 0.094 / 0.068 / 0.046 |
| 60 deg, trial 5 | 0.0918 / 0.0914 / 0.0906 / 0.0893 | 0.0854 / 0.0876 / 0.0883 / 0.0879 | 0.040 / 0.028 / 0.023 / 0.018 |
| 60 deg, trial 6 | 0.1146 / 0.1072 / 0.1011 / 0.0988 | 0.1031 / 0.0964 / 0.0963 / 0.0965 | 0.063 / 0.067 / 0.046 / 0.030 |
| 90 deg (5 kinks, both boxes) | 24-96 within 0.5 % of pinned | the same | 0.010-0.017 at 96, NOT decaying |
| 150-degree hairpin, box_irr, resampled at half a cell of each mesh | 0.1305 / 0.1099 / 0.0952 / refused | 0.0736 / 0.0843 / 0.0863 / refused | 0.130 / 0.110 / 0.093 |

- **Same limit, and the pin gets there first.** At 60 degrees the pinned slip has settled by 48
  cells (to within 0.5 %), while the base is still falling towards it at 96, 2-5 % above. The
  slip one cell from the apex drifts the same way; trial 1, the arm whose 12-cell slip was 0.047,
  reads 0.047 / 0.046 / 0.038 / 0.033 base against 0.027 / 0.029 / 0.029 / 0.029 pinned.
- **The base apex jump decays slowly at 60 degrees, and not at all at 90** (0.010-0.017 at 96 cells
  per side). At 90 degrees the largest slip is away from the apex, so it converges anyway.
- **The hairpin** follows the 60-degree pattern on the irregular box: base 0.130 to 0.095 and still
  falling, pinned 0.074 to 0.086 and levelling near 0.087. That limit agrees with the 48-cell value
  from the 0.3 sampling. The regular box refuses it at every resolution (the snap inverts cells
  with every sample pulled), and 96 is refused on both boxes.
- **Iterations:** the velocity sub-solve's last count is equal, or 1-10 fewer pinned, at every
  resolution (e.g. 29/33/72/127 base against 28/33/70/116 pinned).

## `normal="trace"` at the apex (`tracefirst.py`)
- **Not a probe artefact.** In a fresh process, whatever runs before it, the trace normal gives an
  apex jump of 6.7e-10 and the pinned largest slip (0.09149) for box_irr 90 trial 0.
- **How the normal is built:** the trace normal interpolates the tangent ANGLE along the polyline
  (`_trace_normal_fn`). At the apex it is the bisector (30/30 degrees from the arms at 60, 45/45
  at 90), and it rotates smoothly over the neighbouring P2 nodes. At 90 degrees four of the five
  apex jumps were ~1e-10.
- **It does not pin reliably.** At 60 degrees its apex jump is LARGER than the default's (0.128,
  0.041, 0.073 against 0.069, 0.040, 0.063). In the one 90-degree case where the default normal is
  also 45/45, the two give the same nonzero jump (0.018).
- **Why it gives zero at some 90-degree apexes is not established.**

## 3-D: a creased sheet (`crease.py`, add_fault's 3-D path with a triangulated sheet)
**Set-up:** two planar facets 0.25 wide meeting along a crease parallel to x (half-length 0.25),
turned by 60, 90 or 120 degrees. The sheet is triangulated at 0.03, with each quad's diagonal
chosen to leave no all-rim triangle. The box is sheared in y-z, so the slip crosses the crease;
the fault is frictionless.

**The probe patch:** at each crease pair the pair block is rewritten in the frame (averaged
normal, w = averaged normal × crease direction, crease direction), and the jump along w is
constrained too. That holds the jump along both sheets' normals and leaves slip free along the
crease.

| Turn | Cell size (cells) | Opening at the crease, default / pinned | Largest slip, default / pinned | Slip along the crease, default / pinned | Velocity its, default / pinned |
|---|---|---|---|---|---|
| 60 | 0.06 (24k) | 0.0246 / 0 | 0.1203 / 0.1145 | 0.049 / 0.009 | 81 / 77 |
| 60 | 0.045 (56k) | 0.0252 / 0 | 0.1212 / 0.1151 | 0.051 / 0.014 | 76 / 74 |
| 60 | 0.034 (123k) | 0.0255 / 0 | 0.1219 / 0.1158 | 0.051 / 0.017 | 75 / 74 |
| 90 | 0.06 / 0.045 / 0.034 | 0.0053 / 0.0039 / 0.0030 against 0 | 0.1056 / 0.1064 / 0.1070, the same pinned to 0.03 % | 0.015-0.024, the same | 82 / 76, 78 / 75, 72 / 68 |
| 120 | 0.06 / 0.045 / 0.034 | 0.012 / 0.010 / 0.010 against 0 | 0.1188 / 0.1192 / 0.1200, the same pinned to 0.05 % | 0.017-0.025, the same | 82 / 81, 80 / 80, 75 / 74 |

- **The crease opens under the default constraint, as the 2-D apex does.** At a 60-degree turn it
  opens by 0.025 at every level (about 21 % of the slip), and the opening feeds a false slip along
  the crease (0.05 against 0.01-0.02 pinned). At 90 degrees it decays; at 120 it does not.
- **The largest slip** is unaffected at 90 and 120 degrees. At 60 the default is 5 % above the
  pinned value at every level.
- **The limit of this measurement:** the crease has 33 pairs at every level. The placement
  conforms the mesh to the sheet's own triangulation (0.03), so refining the box does not refine
  the fault surface, and the constant 5 % gap at 60 degrees cannot be resolved into a common limit
  or two different ones. That needs the sheet refined with the box; at 123k cells a solve takes
  about 10 minutes on the laptop. Not run.
- **The two-dimensional conclusions carry over:** opening at the turn, no iteration cost, and the
  pinned frame is consistent. Convergence in 3-D is unshown.

### 3-D at 60 degrees with the sheet refined along with the box (`crease_ref.py`)
Sheet spacing half the cell size (0.03 / 0.0225 / 0.017):

| Cell size (cells) | Crease pairs | Default largest slip | Pinned | Gap | Default opening | Slip along the crease, default / pinned |
|---|---|---|---|---|---|---|
| 0.06 (24k) | 33 | 0.12029 | 0.11446 | 5.1 % | 0.0246 | 0.049 / 0.009 |
| 0.045 (58k) | 43 | 0.11929 | 0.11463 | 4.1 % | 0.0219 | 0.044 / 0.014 |
| 0.034 (126k) | 57 | 0.11851 | 0.11497 | 3.1 % | 0.0192 | 0.039 / 0.015 |

- **The gap closes in proportion to the cell size** (0.0058, 0.0047, 0.0035, about 0.1 h) and
  extrapolates to zero, so default and pinned converge to the SAME limit.
- **The pinned value is much closer to it at each level:** it moves 0.15-0.3 % per level, against
  0.65-0.8 % for the default, which comes down towards it.
- **The opening of the default decays slowly** (0.0246 to 0.0192); the pinned crease does not open.
- **Iterations:** pinned equal or 3-5 fewer (81/77, 92/87, 113/110).
- **So row 30's 3-D form has the same evidence as 2-D.** The earlier constant gap came from
  refining the box without the sheet.
