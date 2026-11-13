# #1164 review by H5 (head c0bbd822)

**Verdict: NOT READY.** One more reachable segfault of the same class (F1) should be in this PR; F2 is a one-line fix of the same kind; M1 is the behaviour question.

Checked on hyperion (96-thread Linux workstation, MPICH), development-based build; the sites below are unchanged by the PR.

## Fact checked

`dm.getLabel(missing)` returns a label with a null handle, never `None`: `is None` is False, `bool(label)` is False, `handle == 0`. So the `if not label` / `if label:` sites are correct (`petsc_discretisation.pyx:260`, `discretisation_mesh.py:1546` and `:11641`), and only `is None` tests are dead.

## F1 (fix here): `rotated_bc._wall_vertex_rows` — reachable segfault from the user API

`rotated_bc.py:3823` tests `label is None`, then calls `label.getValueIS()` on the null handle. On the PR's own fixture (`Annulus(radiusInner=0)`), serially:

    s.add_rotated_freeslip_bc("Upper"); s.add_rotated_freeslip_bc("Lower"); s.solve()

segfaults at `rotated_bc.py:3829` via `_declared_mode_flags` (3897) <- `_rotated_nullspace` (3401) <- `solve_rotated_freeslip` (1924). A direct `_wall_vertex_rows(dm, "Lower")` segfaults too; `"Upper"` gives 32 rows.

Fix: `if not dm.hasLabel(name)`. Decide what a rotated free-slip condition on a wall the mesh does not hold should do: empty rows (consistent with the rest of the PR), or a refusal naming the wall at `add_rotated_freeslip_bc`. A constraint asked for on a wall that does not exist is more likely a user error than a pin list entry is. `hasLabel` is a property of the distributed DM, so either answer is the same on every rank. Add the case to the test file.

## F2 (low, one line): the inactive-region label check never fires

`petsc_generic_snes_solvers.pyx:12342`: `if bc_label is None: raise ValueError("DM label ... not found")` is dead, so a misnamed inactive-region label goes on to `c_label = bc_label` and a null DMLabel, not to the intended error. Use `hasLabel`.

## Dead `is None` tests that are harmless (no change needed; optional tidy)

- `adaptivity.py:587` — `_dm_unstack_bcs` creates every boundary label a few lines earlier.
- `discretisation_mesh.py:2488` — names enumerated from the DM's own labels.
- `create_dmplex_from_medit.py:77` — the next call is the DM-level `dm.getStratumIS(name, value)`, which handles a missing label.
- `discretisation_mesh.py:3698` and `systems/ddt.py:5719` already go through `hasLabel`.

## M1: the behaviour change should warn in one case

`_auto_pinned_labels` now drops names the DM does not hold. For the solid disc that is right and should stay silent. But a mesh whose DM has lost its per-boundary labels (a rebuilt or reloaded DM) now gets an empty tuple, and `smooth_mesh_interior` / `boundary_slip` run with nothing pinned: the boundary vertices are free to move off the domain, silently, where before the run crashed. Suggest:

- auto list empty while `mesh.boundaries` names geometric walls: warn, naming them;
- an explicit `pinned_labels` name the DM does not hold (a typo): warn, naming it;
- the auto list dropping some names (the solid disc): silent.

Every rank answers `hasLabel` the same, so the warning is collective-safe.

## Tests

Not rerun here; the PR reports 6 of 8 segfault on development and 8 pass at np 1 to 4. F1 needs a case in the same file.
