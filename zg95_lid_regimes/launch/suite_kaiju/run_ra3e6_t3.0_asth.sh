#!/bin/bash
# ra3e6_t3.0_asth: Ra 2.73375e+06, tau1 8.20125e+06 (tau1/Ra 3), refinement 4 (d/32), asthenosphere top 0.3
source "$(dirname "$0")/common.sh"
launch ra3e6_t3.0_asth -uw_ra 2.73375e+06 -uw_tau1 8.20125e+06 -uw_refinement 4 -uw_asth_top 0.3
