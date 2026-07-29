#!/usr/bin/env bash
# Cross-skill consistency: every hands_off_to: target resolves to a real skill.
#
# validate-skill.sh already catches this per-skill. This test runs at the
# library level and builds a fresh dangling-references report so a regression
# here is loud and obvious.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILLS_DIR="$REPO_ROOT/plugins/coordinated-skills/skills"

fail=0

# Build the set of known skill names (one dir per skill, each with a SKILL.md).
known_names=$(find "$SKILLS_DIR" -mindepth 1 -maxdepth 1 -type d \
  | while read -r d; do [[ -f "$d/SKILL.md" ]] && basename "$d"; done \
  | sort)
known_index=" $(echo "$known_names" | tr '\n' ' ')"

# Walk each skill and check its hands_off_to targets.
dangling=""
checked=0

for skill_dir in "$SKILLS_DIR"/*/; do
  [[ -d "$skill_dir" ]] || continue
  name=$(basename "$skill_dir")
  skill_md="$skill_dir/SKILL.md"
  if [[ ! -f "$skill_md" ]]; then
    echo "  FAIL  $name :: no SKILL.md"
    fail=$((fail + 1))
    continue
  fi
  checked=$((checked + 1))

  hot_line=$(awk '
    /^---[[:space:]]*$/ { count++; if (count == 1) { in_block = 1; next }; if (count == 2) exit }
    in_block && /^hands_off_to:/ { print; exit }
  ' "$skill_md")

  hot_inner=$(printf "%s" "$hot_line" | sed -E 's/^hands_off_to:[[:space:]]*\[(.*)\][[:space:]]*$/\1/')
  if [[ "$hot_inner" == "$hot_line" ]]; then
    # No brackets — already covered by validate-skill.sh as a format error.
    continue
  fi
  entries=$(printf "%s" "$hot_inner" | tr -d ' ' | tr ',' '\n' | grep -v '^$' || true)
  for target in $entries; do
    case "$known_index" in
      *" $target "*) ;;
      *) dangling="$dangling $name→$target" ;;
    esac
  done
done

if [[ -z "$dangling" ]]; then
  echo "  PASS  every hands_off_to target resolves ($checked skill(s) checked)"
else
  echo "  FAIL  dangling hands_off_to references:"
  for d in $dangling; do
    echo "         $d"
  done
  fail=$((fail + 1))
fi

exit $fail
