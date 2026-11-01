# Iterative FAC patch probes (dev hub, 2026-11-01)

Louis's questions:
1. Can the add-on patch be an iterative solve that scales?
2. Does it need LU accuracy at all?
3. What are the known strategies for a fault broken into patches plus a coarse problem?

## Setup

**Fixtures:**
- UWTN 2026-022 problem A, under H0 (the welded base, then the split S level with the FAC patch), at h_b/S = 24, 48 and 97 (320, 640 and 1280 rungs), np 1;
- the yielding-lid box (problem B, frictionless) at S = 0.004, np 4.

The cover gate is forced open (`UW_FAC_COVER=1.01`, see #918).

**Reference:** one LU block, the defaults: 66-67 velocity iterations on problem A.

**Build:** underworld3 branch `probe/iterative-patch`, not for merge. It is `feature/fault-slip-coarse-space` with development 25d62812 merged in, plus one knob, `UW_FAC_STRIP_WIDTH`, which cuts the structural patch into strips along strike.

**Files:**
- `patch_probe.py`: the patch spec (block solver, cutting, slip coarse space) and the record helpers;
- `iterative_patch_linear.py`, `iterative_patch_box.py`: the two drivers;
- `kaiju_commands.sh`: 164 jobs plus an HPDDM check, one independent job per line;
- `kaiju_commands_hypre.sh`: experiment 1's hypre BoomerAMG arms, 40 jobs.

## Experiment 1: inexact block solves

Each block's `preonly` + LU is replaced by FGMRES with one of four preconditioners: ILU(1), ILU(2), GAMG or hypre BoomerAMG. It runs either to a block rtol of 1e-1, 1e-2 or 1e-3 (cap 200), or for exactly 5 or 10 steps (convergence test `skip`). The same arms run on one structural block (cut 0) and on pieces of 2000 rows (cut 1).

No library code changes. The block KSPs read their options when the ASM sets up, inside `_set_up_fac_smoothers`, under the per-solve prefix `rotfs<N>_fieldsplit_vel_mg_levels_<l>_sub_1_sub_`. `patch_probe.configure_patch` writes those keys for the next few solve counts. `UW_FAC_SUB_PC` picks the block PC.

The BoomerAMG arms run on kaiju only, because wombat's PETSc has no hypre.

Two cautions for reading the results:
- An FGMRES block solve is a nonlinear function of its right-hand side, so the level smoother changes between applications. The outer velocity KSP is FGMRES and tolerates that.
- The level's own GMRES smoother does not tolerate it, so a stall can come from there rather than from the block's accuracy.

## Experiment 2: rung-line blocks plus the slip coarse space

The structural patch is cut into strips 1, 2, 4 or 8 rung spacings long (`UW_FAC_STRIP_WIDTH`, LU blocks), each with and without the slip coarse space. The comparisons are pieces of 2000 rows with the coarse space (the earlier 79-85), and one LU block.

The slip coarse space has one column per piece that carries slip. So m = 1 makes its dimension the rung count: 320-1280 here, and in 3-D the number of rung columns on the sheet. This is the cost to weigh against the tiny local solves.

## Experiment 3: PCHPDDM (GenEO), ruled out

Louis ruled on 2026-11-01: "I prefer strategies that use the basic conda forge petsc. Adding packages adds a large technical overhead." So this experiment is not run.

- **Why it needed a build.** PCHPDDM needs HPDDM and SLEPc, and neither PETSc we have carries them:
  - wombat: PETSc 3.25.0, custom build;
  - kaiju's image: PETSc 3.25.0, with `hasExternalPackage("hpddm")` False, `PC.setType("hpddm")` raising, and no SLEPc. It carries an unmatched slepc4py 3.24.3, plus MUMPS, superlu_dist, hypre, mmg and parmmg.
- **What a build would take.**
  - PETSc reconfigured with `--download-slepc --download-hpddm`. That needs C++11 and LAPACK, then a full rebuild: about 30-60 min on a Xeon Gold 6230R node, plus petsc4py.
  - The probe itself: a python PC member wrapping KSP + PCHPDDM on the patch submatrix, about a day of work. PCHPDDM makes one subdomain per MPI rank, and the add-on gathers each fault's patch onto one rank, so the patch would also have to be spread across ranks, with seams `conform` or by redistributing it. With no Neumann matrices it would use `-pc_hpddm_harmonic_overlap`.
- **The standing rule.** Every solver strategy runs on conda-forge PETSc as shipped:
  - in: MUMPS, superlu_dist, hypre, and anything in PETSc proper;
  - out: HPDDM, SLEPc and anything needing a rebuild;
  - also out: PCBDDC, which needs MATIS (unassembled subdomain matrices) that our assembled, rotated, Galerkin patch block does not have.
- **The consequence.** The hand-built slip coarse space is our coarse space. Re-propose GenEO only with new information, such as conda-forge shipping HPDDM.

## Known strategies

1. **Two-level overlapping Schwarz** (additive, restricted, multiplicative): local solves on the pieces plus a coarse problem that carries what the pieces cannot. The coarse space is the design choice:
   - **Nicolaides:** one constant per piece. Our "indicator per piece" arm measured 90/117/152, because a slip step is a dislocation.
   - **Partition of unity plus energy-minimising extension** (GDSW and RGDSW, as in FROSch; MS-GFEM): coarse functions on the interface, here the slip rows, extended harmonically into the pieces. The slip coarse space on `feature/fault-slip-coarse-space` is of this family.
   - **Spectral (GenEO, as in PCHPDDM; SHEM; ACMS):** local generalised eigenproblems choose the modes the local solves miss. This is robust against coefficient jumps, at the cost of the eigen-solves and of the local Neumann matrices, or the algebraic variant.
2. **Non-overlapping substructuring (BDDC, FETI-DP):** primal constraints on the interface. For a fault the slip is the natural primal variable. PETSc's PCBDDC needs MATIS, that is, unassembled local matrices. It scales in 3-D.
3. **Inexact local solves:** AMG or ILU in place of LU. Two-level theory keeps the method optimal if the local solver is spectrally equivalent to the block. AMG can be; ILU on our blocks, with their rotated constraint rows and near-zero pivots, was fragile (#892: ILU(0) took 344 iterations against 67).
4. **Line and plane relaxation:** on a structured band, the across-band rung lines are the classic block-line smoother for an anisotropic direction. In 3-D these become rung columns, or planes.
5. **Fault-specific practice:** PyLith treats fault slip with Lagrange multipliers and a field split, with the fault block preconditioned by an approximate Schur complement (Aagaard, Knepley and Williams 2013). In our split-node form the corresponding object is a Schur complement onto the slip rows: a 1-D problem along strike in 2-D, a 2-D sheet in 3-D. The slip coarse space with m = 1 approaches it.
6. **Deflation or augmented Krylov with the slip modes:** the coarse correction applied in the outer Krylov instead of the smoother.
