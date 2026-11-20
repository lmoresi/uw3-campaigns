# #1166: is the answer the same across rank counts?

`p_1166_answer_across_ranks.py` judges #1166 by Louis's 2026-11-14 rule: the
same answer to an answerable question, not the same bits. One mover step
(`node_redistribution` on `metric_density_from_gradient`'s front-following
density, defaults) on #1166's mesh and front. On the moved mesh it reports the
interpolation error of T, a Poisson answer (integral and L2 norm, solved to
1e-10), the total area and the extreme cell areas: none depends on the
partition's numbering.

    mpirun -n {1,2,4} python p_1166_answer_across_ranks.py
    # and np 8 with an empty rank, and with a random partition

**np 1** (W1, macOS 12-core Apple M4, development 2026-11-21):

    RES np 1: interp L2 error 6.8092659358e-03  poisson int 1.596744289623e-02  L2 1.999555703206e-02  area 1.000000000000e+00  cell area min 7.675567e-04 max 3.511443e-03

**Reading.** If the interpolation error and the Poisson answers agree across
rank counts to about the solve's tolerance (or far below the effect of the
adaptation itself), #1166 takes a comment with the numbers and no fix. If they
move beyond that, the fix is #1166's option 2 (a floor below which the flat
region is not ranked) or a tolerance-aware projection.
