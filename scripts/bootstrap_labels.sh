#!/usr/bin/env bash
set -euo pipefail
# Run with a GitHub CLI login that can manage labels in the current repository.
gh label create "agent:triage" --color "7957d5" --description "Maintainer-approved AI issue triage" --force
gh label create "agent:review" --color "1d76db" --description "Maintainer-approved AI static PR review" --force
gh label create "type:bug" --color "d73a4a" --description "Defect report" --force
gh label create "type:feature" --color "a2eeef" --description "Feature request" --force
gh label create "status:blocked" --color "e4e669" --description "Needs human decision or external dependency" --force
gh label create "agent:approved" --color "0e8a16" --description "Maintainer-approved issue eligible for controller dispatch" --force
gh label create "agent:blocked" --color "b60205" --description "Not eligible for autonomous implementation" --force
echo "Labels are ready."
