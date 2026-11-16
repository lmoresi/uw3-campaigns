# Rotation probe (H7, 2026-11-16)

`rotation_probe.py` imports `_carried_error` unchanged from `test_1102_port.py`, which is
`tests/test_1102_stress_history_moves_with_the_flow.py` on branch `bugfix/stress-snapshot-order-735`
(913694e8). It runs one serial case per `stress_transport` on whatever underworld3 is importable:

    python rotation_probe.py test_1102_port.py semi_lagrangian integration_point eulerian forward lagrangian none

`rotation_dev_fafbecb8.txt` is the output on development fafbecb8 (serial, a 96-thread Linux
workstation). Each line gives the relative error of the stored stress against the rotated stress
and against the stress where it was made.
