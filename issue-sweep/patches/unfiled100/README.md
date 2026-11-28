# UNFILED 100: the pressure sub-solve cap

One commit on development fbef72fa. PR text: PR_BODY.md.
Bit-identity evidence: baseline.py (before.txt = after2.txt); histories.py with hist-*.txt. fix1 equals the first development run byte for byte. rotfs3 and rotfs20 alternate between two values across sessions on both builds.
Left open, a line for row 100: strategy still rewrites the sub-solves rtol and ksp_type.
Owed: H1 np 2 of the rotated case.

## C1: no caveat: 0002
The cap is read before every rotated saddle solve (_set_absolute_target, key in ctx), so a cap set after the first solve reaches the cached KSP. Probe byte-identical (after4.txt); histories differ from development only in rotfs3/rotfs20 (hist-fix4.txt). test_0908: 4 passed.
