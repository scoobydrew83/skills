#!/usr/bin/env bash
# loop-creator harness test: the generated loop must actually EXECUTE.
#
# The package validator is all governance — prompts distinct, verdict parseable,
# ceiling present, evidence required. It once scored this harness 14/14 while the
# harness was structurally incapable of processing queue unit two. This dispatches
# the runtime smoke test that would have caught it.
#
# The real work lives in the skill so a generated package can run the same check
# on its own copy of the harness; this file only wires it into CI.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SMOKE="$SCRIPT_DIR/../plugins/coordinated-skills/skills/loop-creator/scripts/smoke_harness.sh"

if [[ ! -f "$SMOKE" ]]; then
  echo "  FAIL  smoke_harness.sh missing from the loop-creator skill"
  exit 1
fi

bash "$SMOKE"
