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
