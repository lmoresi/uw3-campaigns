# UNFILED 62 handoff: bounded orphan-repair query (W1 to H1)

Base: underworld3 development fbef72fa. Two commits, as `git format-patch` files.

```bash
git worktree add ../uw3-unfiled62 fbef72fa && cd ../uw3-unfiled62
git switch -c bugfix/orphan-repair-bounded-query
git am /path/to/issue-sweep/patches/unfiled62/000*.patch
./uw build
pytest tests/test_0893_custom_mg_orphan_repair_memory.py
```

Review record: `REVIEW_unfiled62.md`. Probes (each run from this directory):
- `ab_plugin.py`: a pytest plugin (`PYTHONPATH=. pytest -p ab_plugin ...`). It runs development's
  builder (`old_bary.py`) next to the new one on every call, asserts the CSR matrices are equal,
  and logs each call to `ab_calls.jsonl`.
- `old_plugin.py`: puts development's builder back in, to show that test_0893 fails on it.
- `probe_eq.py`: the forced-orphan grids and the 40 random clouds. `probe_mem.py <n> old|new`
  measures the peak with tracemalloc.
- `probe_ties.py` and `probe_ties99.py`: exact-tie grids, testing the patched build (e2aa7be6)
  and 99cfea1e (`b99.py`) against development.

Still to do: test_0885 in parallel on the branch, which uses the public default.
