# zg95 compositional slab with a crust fault (kaiju)

Recipe: `launch/stage_a/run_stage_b_comp.sh` BASE plus, for the faulted runs, FAULT = `-uw_fault_law crust -uw_max_faults 1 -uw_fault_depth_max 0.15 -uw_detect_start 0 -uw_detect_every 5` (rebuild_rungs and chain at their defaults), 300 steps, checkpoints every 10, np 16 (one exclusive node per segment). Driver zg95-annulus-for-kaiju 0fb51f9 (crust fault law 3463bbd + the checkpoint-traces fix); underworld3 feature/box-faults-warm 99259d35. The faulted runs leak ~7 GB/node per faulted-mesh rebuild (handed to hyperion), so they ran as restart segments; records are continuous and every segment's first step restored the faulted mesh at match distance 0 (segments below). Frames: the left two panels of the zoom on the initial trench at steps 20, 60, 120, 200 and 299; `solver_record.jpg`; `trench_retreat.png` with the fault-free control B1 as reference. `peak rss/node` is the largest `Peak memory` line among a run's segment logs; a segment cancelled before its end logs none (B1_crust0.1_fault's segment 1 was stopped at a measured 164 GB, see Segments), and B1_crust1_fault's 183 GB is the segment the OOM handler killed.

| case | change from B1 | segments | steps | t end | wall (h) | s/step | peak rss/node (GB) | KSP-cap hits | what it shows |
|---|---|---|---|---|---|---|---|---|---|
| [fault_B1_crust0.1_nofault](fault_B1_crust0.1_nofault/) | `-uw_crust_weak 0.1` | 1 | 300 | 0.0032 | 2.17 | 26 | 27.1 | none | Crust x0.1 (vs B1's x0.001), no fault: slightly slower than B1 (0.175 d at t 0.0005, tip at the base t 0.0010), 0.62 d of retreat by t 0.0032. The fault-free reference for the faulted B1 runs. |
| [fault_B1_crust0.1_fault](fault_B1_crust0.1_fault/) | `-uw_crust_weak 0.1 + FAULT` | 3 | 300 | 0.0031 | 2.31 | 28 | 66.2 | none | Crust x0.1 + crust fault: the fault forms at the trench at step 0 and tracks it (F0 at -15.4 deg at the end, 27 rebuilds), slips heavily (median slip 484), yet the trench history is IDENTICAL to the no-fault run (0.62 d by t 0.0031): with a weak crust the fault is redundant for the plate-scale motion. |
| [fault_B1_crust1_fault](fault_B1_crust1_fault/) | `-uw_crust_weak 1 + FAULT` | 3 | 300 | 0.0046 | 2.35 | 28 | 183.1 | none | No weak crust (x1) + crust fault: the fault does the decoupling and retreat DOUBLES, 1.16 d by t 0.0046 (the trench moves 29 deg); the slab flattens to 53 deg. The fault is rebuilt at almost every detection (47 rebuilds, every ~5 steps) to follow the trench, and its slip falls from 434 at the start to a steady 15-50 for most of the run. Over the 46 rebuilds that replaced an existing fault the slip at the rebuild step is 1.55x the step before in median (0.20-3.52): the first 8 rebuilds cut it (median 0.43) while the slip falls from its early peak, the last 24 carry the slip peak (1.5-2x) with decay between rebuilds. |
| [fault_C1_crust0.1_fault](fault_C1_crust0.1_fault/) | `-uw_over_eta 100 -uw_over_gap 0.15 -uw_crust_weak 0.1 + FAULT` | 3 | 300 | 0.0053 | 3.36 | 40 | 95.7 | none | Overriding plate x100 at 0.15 d + crust x0.1 + crust fault: 0.76 d by t 0.0053, against 0.56 d by t 0.0045 for C1 (crust x0.001, no fault); the fault at the plate contact helps the trench move (35 rebuilds, F0 at -18.3 deg). |
| [B1](B1/) | `the fault-free control (crust x0.001, no fault)` | 1 | 300 | 0.0022 | 2.55 | 31 | 27.2 | none | The fault-free control (crust x0.001, no fault), for reference: 0.56 d by t 0.0022. |

## Segments

The faulted runs leak ~0.4 GB/rank per faulted-mesh rebuild (see the hub's leak task), so each run is
a chain of segments: a restart (`-uw_init checkpoint -uw_restart N`, driver 0fb51f9) from the run's own
last checkpoint before a node fills. Records are continuous (a restart keeps records <= N and appends).
Every segment's first step restores the faulted mesh from the checkpoint; the line
"restart: V, P from the faulted-mesh checkpoint (same mesh, largest match distance ...)" is quoted.

| run | segment | job | steps | node | restored at | match distance | end |
|---|---|---|---|---|---|---|---|
| B1_crust1_fault | 1 | 2193 | 0-136 | n8 | (init) | - | OOM-killed at 136 (last ckpt 130) |
| B1_crust1_fault | 2 | 2195 | 131-230 | n8 | 130 | 0.00e+00 | done, exit 0, no KSP-cap hits; 19 meshes built; peak rss 134.5 GB/node |
| B1_crust1_fault | 3 | 2200 | 231-299 | n3 | 230 | 0.00e+00 | done, exit 0, no KSP-cap hits; 10 meshes built; peak rss 73.7 GB/node. RUN COMPLETE: records 0-299 continuous, all with record["solver"] |
| B1_crust0.1_fault | 1 | 2192 | 0-141 | n7 | (init) | - | cancelled at 141 (164 GB of 187), last ckpt 140 |
| B1_crust0.1_fault | 2 | 2197 | 141-240 | n7 | 140 | 0.00e+00 | done, exit 0, no KSP-cap hits; 8 meshes built; peak rss 67.8 GB/node |
| B1_crust0.1_fault | 3 | 2198 | 241-299 | n7 | 240 | 0.00e+00 | done, exit 0, no KSP-cap hits; 3 meshes built; peak rss 30.9 GB/node. RUN COMPLETE: records 0-299 continuous, all with record["solver"] |
| C1_crust0.1_fault | 1 | 2194 | 0-170 | n3 (bigmem) | (init) | - | stopped at the complete ckpt 170 (188.7 GB, 23 meshes built) |
| C1_crust0.1_fault | 2 | 2199 | 171-270 | n8 | 170 | 0.00e+00 | done, exit 0, no KSP-cap hits; 11 meshes built; peak rss 95.7 GB/node |
| C1_crust0.1_fault | 3 | 2201 | 271-299 | n3 | 270 | 0.00e+00 | done, exit 0, no KSP-cap hits; 4 meshes built; peak rss 33.7 GB/node. RUN COMPLETE: records 0-299 continuous, all with record["solver"] |
| B1_crust0.1_nofault | 1 | 2190 | 0-299 | n6 | (init) | - | done, exit 0, no KSP-cap hits (no fault, no leak). RUN COMPLETE |
Failed first attempts on dd8efcb (checkpoint KeyError at step 0): runs/slab_fault_<case>_failed_dd8efcb (jobs 2187-2189).
