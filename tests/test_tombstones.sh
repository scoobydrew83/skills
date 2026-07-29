#!/usr/bin/env bash
# Tombstone test: the two skills that were merged in Phase 1 must still exist
# as DEPRECATED tombstones, with phase: meta and hands_off_to pointing at the
# survivor that absorbed them.
#
# Tombstones don't fail the build — they're tracked so we notice if one gets
# accidentally repurposed or if its redirect target drifts.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILLS_DIR="$REPO_ROOT/plugins/coordinated-skills/skills"

# Expected tombstone → survivor mapping (from COORDINATION-STATUS.md).
declare -A EXPECTED
EXPECTED[adaptive-communication]=neurodivergent-comms
EXPECTED[task-decomposition]=overwhelm-breakdown
EXPECTED[idea-validator]=hemlock

warn=0
fail=0

for tomb in "${!EXPECTED[@]}"; do
  survivor="${EXPECTED[$tomb]}"
  skill_md="$SKILLS_DIR/$tomb/SKILL.md"

  if [[ ! -f "$skill_md" ]]; then
    echo "  WARN  $tomb tombstone missing — was it cleanly deleted? Update this test if so."
    warn=$((warn + 1))
    continue
  fi

  if grep -qE 'DEPRECATED' "$skill_md"; then
    echo "  PASS  $tomb marked DEPRECATED"
  else
    echo "  FAIL  $tomb is no longer marked DEPRECATED — either undeprecate properly or update tests"
    fail=$((fail + 1))
  fi

  phase_value=$(awk '
    /^---[[:space:]]*$/ { count++; if (count == 1) { in_block = 1; next }; if (count == 2) exit }
    in_block && /^phase:/ { sub(/^phase:[[:space:]]*/, ""); print; exit }
  ' "$skill_md" | tr -d ' ')
  if [[ "$phase_value" == "meta" ]]; then
    echo "  PASS  $tomb phase: meta"
  else
    echo "  WARN  $tomb phase is '$phase_value', expected 'meta'"
    warn=$((warn + 1))
  fi

  hot_line=$(awk '
    /^---[[:space:]]*$/ { count++; if (count == 1) { in_block = 1; next }; if (count == 2) exit }
    in_block && /^hands_off_to:/ { print; exit }
  ' "$skill_md")
  if printf "%s" "$hot_line" | grep -qE "\\[$survivor\\]"; then
    echo "  PASS  $tomb → $survivor"
  else
    echo "  WARN  $tomb hands_off_to does not point cleanly at [$survivor]; line was: $hot_line"
    warn=$((warn + 1))
  fi
done

echo
echo "  $fail fail · $warn warn (tombstones don't fail the build)"
# Only hard-fail on missing SKILL.md or undeprecated tombstones.
exit $fail
