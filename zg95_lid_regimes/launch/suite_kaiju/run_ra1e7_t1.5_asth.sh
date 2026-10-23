#!/bin/bash
# ra1e7_t1.5_asth: Ra 9.1125e+06, tau1 1.36688e+07 (tau1/Ra 1.5), refinement 5 (d/64), asthenosphere top 0.25
source "$(dirname "$0")/common.sh"
launch ra1e7_t1.5_asth -uw_ra 9.1125e+06 -uw_tau1 1.36688e+07 -uw_refinement 5 -uw_asth_top 0.25
