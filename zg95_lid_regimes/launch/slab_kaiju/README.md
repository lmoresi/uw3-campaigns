# The foundering-slab scan for kaiju

A prescribed lithosphere and slab in the annulus (half-space cooling referenced to an age line along the surface and down the slab, the slab profile diffused freely into the mantle for the time since subduction), at rest, with one fault at the trench on
the slab's upper surface, left to founder (after Zhong and Gurnis 1995): what makes it roll
back like a subduction zone rather than drip. The baseline is `common.sh`'s `BASE`; each
run changes one thing. The records carry, per fault, the tangential surface velocity of the
plate on each side of the trench (`plates`: -theta side, +theta side; the overriding plate is
the +theta side for a dip below 90) and the trench's own rate (`trench_rate`, positive toward
+theta). Roll-back is the trench moving toward the subducting plate faster than the
overriding plate advances. On the laptop the baseline's first steps gave slip 149, subducting
plate 102, overriding plate -58, trench -58.

| run | change |
|---|---|
| baseline | - |
| asth_none | no asthenosphere channel |
| asth_0.01 | channel viscosity x0.01 |
| tau_3.0 | tau1/Ra 3 (a stronger lid) |
| dip_60 | slab and fault at 60 degrees |
| slab_0.2 | a short slab (0.2 d) |
| slab_0.5 | a long slab (0.5 d) |
| plates_equal | overriding plate as old as the subducting one (age 0.0025, 0.1 d) |
| deta_1e5 | viscosity contrast 1e5 (a weaker interior under the same lid) |
| two_faults | up to two faults may form on the rate law |

Set `UW3_WORKTREE`, `UW3_CAMPAIGNS`, `ZG95_RUNS` and `NP` as for `suite_kaiju`. No checkpoint
is needed: the state is built by the driver (`-uw_init slab`). 1000 steps at dt 2-5e-5 reach
t 0.02-0.05, a slab sinking time or two; the base mesh is d/32 (refinement 4).
