# Underworld3 run sizes for the ANUMAS 2027 SU budget (from C1, the dev hub)

Prepared 2026-11-16 for `2027-ANUMAS/run-sizes-C1.md` in underworldcode/NCMAS-proposal. C1 could not push it there:
its permission check refused attaching that repository. Every figure below is from a recorded run unless it is
marked **estimated**. SU are at 2 SU per core-hour, as asked. The groups and projects named in the request are not
the projects these runs came from; each row says which project it is the closest analogue for.

## 2-D runs

| Run (source) | Closest analogue | Where, cores | Size | Time | Core-hours, SU | Status |
|---|---|---|---|---|---|---|
| Barr-Houseman rectangular-fault benchmark: 2-D nonlinear Stokes, P2/P1, cell 0.01, power law n = 3, viscosity contrast 1e5, 4 SNES / 24 KSP solves (underworld3 issue #635) | Gollapalli, 2-D fault benchmarks | Gadi `normal`, 8 ranks | one mesh, same for every run | 1:23:34 PBS wall time | 11.1 core-h, **22 SU** | measured |
| same | same | Gadi `normal`, 12 ranks | same | 0:56:02 | 11.2 core-h, **22 SU** | measured |
| same | same | Gadi `normal`, 4 ranks | same | 2:30:48 | 10.1 core-h, **20 SU** | measured |
| same | same | Gadi `normalsr`, 8 ranks | same | 1:07:43 | 9.0 core-h, **18 SU** | measured |
| 2-D annulus subduction with a placed fault, production resolution (zg95 campaign; Annulus refinement 5, 126,976 cells, about 511k P2 velocity and 64k pressure dofs) | Lu (subduction), Mittal (lithospheric stress) | Kaiju, 16 ranks, one node | about 100 time steps to the slab reaching the base | 177 to 260 s per step; 5 to 8 h per run | 80 to 130 core-h per run | measured per step; run length from the step count |
| same, long overturn run (480 steps) | same | Kaiju, 16 ranks | 480 steps | about 29 h | about 470 core-h | per-step cost measured, total **estimated** from it |
| same at refinement 6 (about 4x the cells) | same, high resolution | Kaiju, 32 ranks | about 100 steps | 780 s per step; about 35 h projected | about 1,100 core-h | per-step cost measured, total **estimated** |
| 2-D annulus subduction with an MMPDE moving mesh and a graded base (H2 trial) | Lu, Mittal | Linux workstation, 4 ranks | 280 steps | 12.1 h | 48 core-h | measured |

On Gadi at 2 SU per core-hour, a 100-step production subduction run (16 ranks, 5 to 8 h) is about **160 to 260 SU**;
the refinement-6 version is about **2,200 SU** (**estimated**, from the Kaiju per-step cost; Gadi's per-core speed
differs, see the next section).

Memory: production subduction runs use 17 to 22 GB at 16 ranks. The Gadi benchmark peaks at 7 to 10 GB.

## Throughput and scaling (Kaiju, measured, same subduction case, seconds per Newton iteration for one node)

| ranks on one node | s per Newton iteration |
|---|---|
| 16 | 40.6 |
| 32 | 29.7 |
| 52 | 32.1 |
| two 26-rank runs, one per socket | 25 (for the node) |

So for budgeting, two 26-rank runs per Kaiju node is the efficient packing (about 1.2x one run). Rank count also
changes the 2-D Gadi benchmark's MatMult rate by a factor of 2.6 between 4 and 12 ranks (#635), with Sapphire
Rapids (`normalsr`) about 20 % faster than Cascade Lake at 8 ranks.

## Not covered

- **3-D production runs:** C1 has no measured full-run timing. The 3-D evidence it holds is component timing only
  (for example, one Jacobian assembly on a 153,472-cell spherical shell takes 108 s on one laptop core), which is
  not a basis for an SU figure.
- **Graciosa's, Salam's and Sajeev's projects, and release scaling campaigns on Gadi:** no data here. C2 (the
  science hub) may have them.
