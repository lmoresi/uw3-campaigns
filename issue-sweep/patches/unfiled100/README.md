# UNFILED 100: the pressure sub-solve cap

One commit on development fbef72fa. PR text: PR_BODY.md.
Bit-identity evidence: baseline.py (before.txt = after2.txt); histories.py with hist-*.txt. fix1 equals the first development run byte for byte. rotfs3 and rotfs20 alternate between two values across sessions on both builds.
Left open, a line for row 100: strategy still rewrites the sub-solves rtol and ksp_type.
Owed: H1 np 2 of the rotated case.

## C1: no caveat: 0002
The cap is read before every rotated saddle solve (_set_absolute_target, key in ctx), so a cap set after the first solve reaches the cached KSP. Probe byte-identical (after4.txt); histories differ from development only in rotfs3/rotfs20 (hist-fix4.txt). test_0908: 4 passed.

## H1 lows: 0003
The dead pressure_cap_key in _solve_rotated_vector is removed. test_0908 is marked serial (its assertions hold on every rank; the np 2 run is a review check). The rotated cap-hit warning already exists (_warn_on_capped_rotated_sub_solves, the same _warn_from_caller mechanism as the standard path). It fires: cap 1 on the annulus gives "stopped at its iteration cap ... in 8 application(s)", sub_capped {pressure: 8}. Asked H1 which route or filter was silent. Probe byte-identical.
