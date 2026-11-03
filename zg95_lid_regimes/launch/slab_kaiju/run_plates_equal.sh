#!/bin/bash
# plates_equal: the baseline with -uw_age_over 0.0025
source "$(dirname "$0")/common.sh"
launch plates_equal -uw_age_over 0.0025
