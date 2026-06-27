#!/usr/bin/env bash
# validate-skill.sh — check one or all skills against CONVENTIONS.md.
#
# Usage:
#   tools/validate-skill.sh <skill-name>
#   tools/validate-skill.sh --all
#   tools/validate-skill.sh --help
#
# Checks for each skill:
#   - SKILL.md exists in the skill's source directory
#   - Frontmatter has name, description, phase, hands_off_to, reads, writes
#   - phase value is one of intake/plan/execute/verify/communicate/bookend/meta
#   - Every hands_off_to entry names a real skill in this repo
#   - Body contains a "**Next steps:**" line
#
# Output is one line per check. Tombstones (description starts with DEPRECATED)
# are validated but their hands_off_to may legitimately point only at survivors —
# that's fine, the check is identical.
#
# Exit code: nonzero if any FAIL was reported.

set -uo pipefail

usage() {
  cat <<'EOF'
validate-skill.sh — check one or all skills against CONVENTIONS.md.

Usage:
  tools/validate-skill.sh <skill-name>
  tools/validate-skill.sh --all
  tools/validate-skill.sh --help

Exit code: nonzero if any FAIL was reported.
EOF
}

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" || $# -eq 0 ]]; then
  usage
  exit 0
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILLS_DIR="$REPO_ROOT/plugins/coordinated-skills/skills"
ALLOWED_PHASES="intake plan execute verify communicate bookend meta"

# ---------------------------------------------------------------------------
# Discover the set of known skill names — one directory per skill under
# SKILLS_DIR, each containing a SKILL.md. This directory is the source of truth.
# ---------------------------------------------------------------------------
list_all_skill_names() {
  find "$SKILLS_DIR" -mindepth 1 -maxdepth 1 -type d \
    | while read -r d; do [[ -f "$d/SKILL.md" ]] && basename "$d"; done \
    | sort
}

ALL_NAMES=$(list_all_skill_names)

# Build a space-padded lookup string so we can grep for " <name> ".
NAMES_INDEX=" $(echo "$ALL_NAMES" | tr '\n' ' ')"

# ---------------------------------------------------------------------------
# Extract <archive> into a tmp dir and run checks against its SKILL.md.
# Echoes "PASS|FAIL <check> :: <message>" lines and returns nonzero on FAIL.
# ---------------------------------------------------------------------------
fail_count=0
pass_count=0
check_count=0
warn_count=0

record_pass() {
  pass_count=$((pass_count + 1))
  check_count=$((check_count + 1))
  printf "  PASS  %s\n" "$1"
}

record_fail() {
  fail_count=$((fail_count + 1))
  check_count=$((check_count + 1))
  printf "  FAIL  %s :: %s\n" "$1" "$2"
}

record_warn() {
  warn_count=$((warn_count + 1))
  printf "  WARN  %s :: %s\n" "$1" "$2"
}

validate_one() {
  local skill="$1"
  local skill_dir="$SKILLS_DIR/$skill"

  printf "\n%s\n" "skill: $skill"

  if [[ ! -d "$skill_dir" ]]; then
    record_fail "skill-dir-present" "no directory at $skill_dir"
    return
  fi
  record_pass "skill-dir-present"

  local skill_md="$skill_dir/SKILL.md"
  if [[ ! -f "$skill_md" ]]; then
    record_fail "skill-md-present" "missing $skill/SKILL.md"
    return
  fi
  record_pass "skill-md-present"

  # ----- Frontmatter extraction -----
  # Frontmatter is the block between the first two "---" lines.
  local frontmatter
  frontmatter=$(awk '
    /^---[[:space:]]*$/ {
      count++
      if (count == 1) { in_block = 1; next }
      if (count == 2) { exit }
    }
    in_block { print }
  ' "$skill_md")

  if [[ -z "$frontmatter" ]]; then
    record_fail "frontmatter-present" "no YAML frontmatter block found"
    return
  fi
  record_pass "frontmatter-present"

  # ----- Required keys -----
  local key
  for key in name description phase hands_off_to reads writes; do
    if printf "%s\n" "$frontmatter" | grep -qE "^${key}:"; then
      record_pass "key-${key}"
    else
      record_fail "key-${key}" "missing '$key:' in frontmatter (see CONVENTIONS.md §1)"
    fi
  done

  # ----- phase value -----
  local phase_value
  phase_value=$(printf "%s\n" "$frontmatter" | sed -nE 's/^phase:[[:space:]]*([A-Za-z_-]+).*/\1/p' | head -n1)
  if [[ -z "$phase_value" ]]; then
    record_fail "phase-value-set" "phase: key has no value"
  else
    local found=0
    for p in $ALLOWED_PHASES; do
      if [[ "$p" == "$phase_value" ]]; then
        found=1
        break
      fi
    done
    if [[ $found -eq 1 ]]; then
      record_pass "phase-value-valid ($phase_value)"
    else
      record_fail "phase-value-valid" "phase '$phase_value' not in {$ALLOWED_PHASES} (CONVENTIONS.md §3)"
    fi
  fi

  # ----- hands_off_to entries are real skills -----
  # Accept inline list "[a, b, c]" or "[]". Multi-line YAML lists are out of
  # scope here — the convention uses inline form.
  local hot_line
  hot_line=$(printf "%s\n" "$frontmatter" | grep -E "^hands_off_to:" | head -n1)
  if [[ -n "$hot_line" ]]; then
    local hot_inner
    hot_inner=$(printf "%s" "$hot_line" | sed -E 's/^hands_off_to:[[:space:]]*\[(.*)\][[:space:]]*$/\1/')
    # If the line had no brackets, hot_inner will equal hot_line — treat as empty/skip.
    if [[ "$hot_inner" == "$hot_line" ]]; then
      record_fail "hands_off_to-format" "expected inline list 'hands_off_to: [a, b]' (CONVENTIONS.md §1)"
    else
      # Strip whitespace and split on commas.
      local entries
      entries=$(printf "%s" "$hot_inner" | tr -d ' ' | tr ',' '\n' | grep -v '^$' || true)
      if [[ -z "$entries" ]]; then
        record_pass "hands_off_to-targets (empty list — overlay/terminal)"
      else
        local bad=""
        for target in $entries; do
          # Look for " target " in the names index.
          case "$NAMES_INDEX" in
            *" $target "*) ;;
            *) bad="$bad $target" ;;
          esac
        done
        if [[ -z "$bad" ]]; then
          record_pass "hands_off_to-targets ($(printf "%s" "$entries" | tr '\n' ',' | sed 's/,$//'))"
        else
          record_fail "hands_off_to-targets" "unknown skill(s):$bad — must name real skills in this repo"
        fi
      fi
    fi
  fi

  # ----- Next steps line -----
  if grep -qE '^\*\*Next steps:\*\*' "$skill_md"; then
    record_pass "next-steps-line"
  else
    record_fail "next-steps-line" "body has no line starting with '**Next steps:**' (CONVENTIONS.md §2)"
  fi

  # ----- Tombstone advisory -----
  if printf "%s\n" "$frontmatter" | grep -qE '^[[:space:]]*DEPRECATED' \
     || grep -qE 'DEPRECATED — this skill' "$skill_md"; then
    record_warn "tombstone" "marked DEPRECATED — non-blocking, see CONVENTIONS.md for tombstone policy"
  fi
}

# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------
if [[ "$1" == "--all" ]]; then
  for s in $ALL_NAMES; do
    validate_one "$s"
  done
else
  validate_one "$1"
fi

printf "\nsummary: %d checks · %d pass · %d fail · %d warn\n" \
  "$check_count" "$pass_count" "$fail_count" "$warn_count"

if [[ $fail_count -gt 0 ]]; then
  exit 1
fi
