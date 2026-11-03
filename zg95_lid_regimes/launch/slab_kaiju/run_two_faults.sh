#!/bin/bash
# two_faults: the baseline with -uw_max_faults 2 -uw_fault_separation 6
source "$(dirname "$0")/common.sh"
launch two_faults -uw_max_faults 2 -uw_fault_separation 6
