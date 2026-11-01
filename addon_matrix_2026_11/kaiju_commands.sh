#!/bin/bash
# The add-on matrix rows 4 and 5, np 4 arms, for the kaiju dev runner. Every line is an
# independent job; run each from this directory with the underworld3 overlay built from
# bugfix/rotated-nullspace-from-mesh @ 964dc3ce (development 25d62812 + #906, whose
# changes do not reach these boxes). OMP_NUM_THREADS=1 for every rank.
set -u
cd "$(dirname "$0")"
mkdir -p records logs
export OMP_NUM_THREADS=1

# row 4: interface laws on the yielding-lid box, H0 against H1, the rotated loop's cap at 200
mpirun -np 4 python -u row4_interface_laws.py -uw_spacing 0.004 -uw_hier H0 -uw_law viscous -uw_max_it 200 -uw_out records/B_s0.004_H0_viscous_np4.json > logs/B_s0.004_H0_viscous_np4.log 2>&1
mpirun -np 4 python -u row4_interface_laws.py -uw_spacing 0.004 -uw_hier H1 -uw_law viscous -uw_max_it 200 -uw_out records/B_s0.004_H1_viscous_np4.json > logs/B_s0.004_H1_viscous_np4.log 2>&1
mpirun -np 4 python -u row4_interface_laws.py -uw_spacing 0.004 -uw_hier H0 -uw_law coulomb -uw_max_it 200 -uw_out records/B_s0.004_H0_coulomb_np4.json > logs/B_s0.004_H0_coulomb_np4.log 2>&1
mpirun -np 4 python -u row4_interface_laws.py -uw_spacing 0.004 -uw_hier H1 -uw_law coulomb -uw_max_it 200 -uw_out records/B_s0.004_H1_coulomb_np4.json > logs/B_s0.004_H1_coulomb_np4.log 2>&1
mpirun -np 4 python -u row4_interface_laws.py -uw_spacing 0.004 -uw_hier H0 -uw_law ratestate -uw_max_it 200 -uw_out records/B_s0.004_H0_ratestate_np4.json > logs/B_s0.004_H0_ratestate_np4.log 2>&1
mpirun -np 4 python -u row4_interface_laws.py -uw_spacing 0.004 -uw_hier H1 -uw_law ratestate -uw_max_it 200 -uw_out records/B_s0.004_H1_ratestate_np4.json > logs/B_s0.004_H1_ratestate_np4.log 2>&1
mpirun -np 4 python -u row4_interface_laws.py -uw_spacing 0.002 -uw_hier H0 -uw_law viscous -uw_max_it 200 -uw_out records/B_s0.002_H0_viscous_np4.json > logs/B_s0.002_H0_viscous_np4.log 2>&1
mpirun -np 4 python -u row4_interface_laws.py -uw_spacing 0.002 -uw_hier H1 -uw_law viscous -uw_max_it 200 -uw_out records/B_s0.002_H1_viscous_np4.json > logs/B_s0.002_H1_viscous_np4.log 2>&1
mpirun -np 4 python -u row4_interface_laws.py -uw_spacing 0.002 -uw_hier H0 -uw_law coulomb -uw_max_it 200 -uw_out records/B_s0.002_H0_coulomb_np4.json > logs/B_s0.002_H0_coulomb_np4.log 2>&1
mpirun -np 4 python -u row4_interface_laws.py -uw_spacing 0.002 -uw_hier H1 -uw_law coulomb -uw_max_it 200 -uw_out records/B_s0.002_H1_coulomb_np4.json > logs/B_s0.002_H1_coulomb_np4.log 2>&1
mpirun -np 4 python -u row4_interface_laws.py -uw_spacing 0.002 -uw_hier H0 -uw_law ratestate -uw_max_it 200 -uw_out records/B_s0.002_H0_ratestate_np4.json > logs/B_s0.002_H0_ratestate_np4.log 2>&1
mpirun -np 4 python -u row4_interface_laws.py -uw_spacing 0.002 -uw_hier H1 -uw_law ratestate -uw_max_it 200 -uw_out records/B_s0.002_H1_ratestate_np4.json > logs/B_s0.002_H1_ratestate_np4.log 2>&1

# row 5: fault networks at h_b/S = 24, H0 against H1; UW_FAC_COVER=1.01 forces the cover
# gate open, UW_FAC_STRUCTURAL=1 unions the structural rows into a fac_zone patch
env UW_FAC_STRUCTURAL=0 UW_FAC_COVER=0.75 mpirun -np 4 python -u row5_networks.py -uw_case junction -uw_hier H0 -uw_zone none -uw_gap 8 -uw_out records/junction_H0_zonenone_st0_cover0.75_gap8_np4.json > logs/junction_H0_zonenone_st0_cover0.75_gap8_np4.log 2>&1
env UW_FAC_STRUCTURAL=0 UW_FAC_COVER=0.75 mpirun -np 4 python -u row5_networks.py -uw_case junction -uw_hier H0 -uw_zone none -uw_gap 24 -uw_out records/junction_H0_zonenone_st0_cover0.75_gap24_np4.json > logs/junction_H0_zonenone_st0_cover0.75_gap24_np4.log 2>&1
env UW_FAC_STRUCTURAL=0 UW_FAC_COVER=0.75 mpirun -np 4 python -u row5_networks.py -uw_case junction -uw_hier H1 -uw_zone none -uw_gap 24 -uw_out records/junction_H1_zonenone_st0_cover0.75_gap24_np4.json > logs/junction_H1_zonenone_st0_cover0.75_gap24_np4.log 2>&1
env UW_FAC_STRUCTURAL=0 UW_FAC_COVER=0.75 mpirun -np 4 python -u row5_networks.py -uw_case pair -uw_hier H0 -uw_zone none -uw_gap 8 -uw_out records/pair_H0_zonenone_st0_cover0.75_gap8_np4.json > logs/pair_H0_zonenone_st0_cover0.75_gap8_np4.log 2>&1
env UW_FAC_STRUCTURAL=0 UW_FAC_COVER=1.01 mpirun -np 4 python -u row5_networks.py -uw_case pair -uw_hier H0 -uw_zone none -uw_gap 8 -uw_out records/pair_H0_zonenone_st0_cover1.01_gap8_np4.json > logs/pair_H0_zonenone_st0_cover1.01_gap8_np4.log 2>&1
env UW_FAC_STRUCTURAL=0 UW_FAC_COVER=0.75 mpirun -np 4 python -u row5_networks.py -uw_case pair -uw_hier H1 -uw_zone none -uw_gap 8 -uw_out records/pair_H1_zonenone_st0_cover0.75_gap8_np4.json > logs/pair_H1_zonenone_st0_cover0.75_gap8_np4.log 2>&1
env UW_FAC_STRUCTURAL=0 UW_FAC_COVER=0.75 mpirun -np 4 python -u row5_networks.py -uw_case ti -uw_hier H0 -uw_zone none -uw_gap 8 -uw_out records/ti_H0_zonenone_st0_cover0.75_gap8_np4.json > logs/ti_H0_zonenone_st0_cover0.75_gap8_np4.log 2>&1
env UW_FAC_STRUCTURAL=0 UW_FAC_COVER=1.01 mpirun -np 4 python -u row5_networks.py -uw_case ti -uw_hier H0 -uw_zone none -uw_gap 8 -uw_out records/ti_H0_zonenone_st0_cover1.01_gap8_np4.json > logs/ti_H0_zonenone_st0_cover1.01_gap8_np4.log 2>&1
env UW_FAC_STRUCTURAL=0 UW_FAC_COVER=0.75 mpirun -np 4 python -u row5_networks.py -uw_case ti -uw_hier H0 -uw_zone ti -uw_gap 8 -uw_out records/ti_H0_zoneti_st0_cover0.75_gap8_np4.json > logs/ti_H0_zoneti_st0_cover0.75_gap8_np4.log 2>&1
env UW_FAC_STRUCTURAL=1 UW_FAC_COVER=0.75 mpirun -np 4 python -u row5_networks.py -uw_case ti -uw_hier H0 -uw_zone ti -uw_gap 8 -uw_out records/ti_H0_zoneti_st1_cover0.75_gap8_np4.json > logs/ti_H0_zoneti_st1_cover0.75_gap8_np4.log 2>&1
timeout 900 env UW_FAC_STRUCTURAL=0 UW_FAC_COVER=0.75 mpirun -np 4 python -u row5_networks.py -uw_case ti -uw_hier H0 -uw_zone both -uw_gap 8 -uw_out records/ti_H0_zoneboth_st0_cover0.75_gap8_np4.json > logs/ti_H0_zoneboth_st0_cover0.75_gap8_np4.log 2>&1
env UW_FAC_STRUCTURAL=0 UW_FAC_COVER=0.75 mpirun -np 4 python -u row5_networks.py -uw_case ti -uw_hier H1 -uw_zone none -uw_gap 8 -uw_out records/ti_H1_zonenone_st0_cover0.75_gap8_np4.json > logs/ti_H1_zonenone_st0_cover0.75_gap8_np4.log 2>&1
