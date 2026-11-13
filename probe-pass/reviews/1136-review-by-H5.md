# Review of #1136 at 52e544f4, by H5

H5: fault, multigrid and restart fixes, with parallel runs on a 96-thread Linux workstation (single system image; Intel Xeon Gold 6240R, AVX-512; MPICH). Run on development a7297194 with the PR's test files (it changes tests and a design note only).

**Verdict: READY.** All three checks hold; there is one low note.

## (a) The swapped references, by an independent serial run

ptest_0863's two solves (split, and weak plane), run on one rank: the same code path, with no rank-specific branch.
- **Development's references** (Cross_1 0.00335, TI Cross_1 0.15717): both tests fail. The serial run gives Cross_1 0.0029 and TI Cross_1 0.1386.
- **The PR's references** (Cross_1 0.00295 and 0.13863, Cross_2 0.00335 and 0.15717): both pass serially, in 350 s.

So the swap is right by a serial run, not only by np 2.

## (b) np 3, with the skip removed

ptest_0864 and ptest_0865, development's versions (no skip), at np 3: **4 failed, 2 passed.**
- test_the_band_meshed_through_the_seam_gives_the_gathered_answer;
- test_the_ligament_placement_is_gated_and_rank_local;
- test_the_network_split_through_the_seams_matches_the_gathered_peaks;
- test_the_split_through_the_seam_is_the_gathered_split.

The errors come from the placement: "the seam crossings do not pair up on this rank: 2 span end(s) for 4 skin run end(s)", "a skin edge is not an edge of the sewn mesh", and "Main was not split on any rank".

So np 3 fails. The skip threshold is right (above np 2), and `scripts/test.sh`'s comment ("These fail at np 3 and np 4") was right. The design note's old "np=2 and np=3" was the wrong one, and the PR corrects it.

The PR's versions: 6 passed at np 2, 6 skipped at np 3. Both files import `MPI` for the `skipif`.

## (c) The note says what the skip says

The design note's three edits ("pins ... at np=2 (it fails at np=3 and np=4 ...)") match the skip reasons and `test.sh`'s `PTEST_NP2_ONLY` comment.

## Low

- **The 900 s advice is not enforced.** The new ptest_0863 note says "Give a supervisor at least 900 s of silence for this file". `scripts/test.sh` runs the ptests under `PARALLEL_SILENCE` (default 300), including ptest_0863 in the full-parallel pass at np 3 and 4. The 330 s test can still be stopped there. Either raise the silence for that file in `test.sh`, or say in the note that the CI default is 300 s.
- **The np 3 skip also skips two cases that pass at np 3.** That is an acceptable loss for a whole-file skip; noted only.
