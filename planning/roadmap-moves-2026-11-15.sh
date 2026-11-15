#!/bin/bash
# Move five roadmap-type issues to draft items on the Underworld roadmap project
# (org underworldcode, project 10). Louis approved the move on 2026-11-15.
# Run on a machine where gh has the project scope (gh auth login -s project,read:project).
# New drafts land in Status Inbox; the planning orchestrator routes them.
# After this runs, C1 closes each issue as "not planned" with a comment naming the draft.
set -euo pipefail
P="--owner underworldcode"
R=underworldcode/underworld3

mk() {  # $1 issue number, $2 draft title
  local body
  body="$(gh issue view "$1" --repo "$R" --json body,url --jq '"Moved from issue " + .url + " (closed there as tracked on the roadmap, 2026-11-15).\n\n" + .body')"
  gh project item-create 10 $P --title "$2" --body "$body" --format json --jq '.id'
  echo "  <- #$1"
}

mk 320 "Compare free-slip methods on the Kramer annulus and spherical benchmarks (Mac, then Gadi)"
mk 508 "A high-level model-building API for UW3 (the UWGeodynamics equivalent)"
mk 554 "Thin viscous sheet (plane stress) solver, with the Barr and Houseman 1996 analytic benchmark"
mk 635 "Document Gadi MPI rank placement for MatMult-dominated Stokes solves"
mk 831 "Explicit get_min_radius() method selection, for reproducing earlier results"
