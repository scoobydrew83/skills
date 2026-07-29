#!/usr/bin/env bash
# Structural tests for every .skill archive:
#   - unzip cleanly
#   - SKILL.md exists at the expected path
#   - frontmatter has all required keys
#   - phase value is valid
#   - **Next steps:** line is present
#
# Implementation strategy: this is exactly what tools/validate-skill.sh --all
# does, so we shell out to it and assert exit 0. Re-implementing the checks
# here would duplicate logic that already has one source of truth.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

fail=0
checks=0

check() {
  local label="$1"
  local rc="$2"
  checks=$((checks + 1))
  if [[ $rc -eq 0 ]]; then
    echo "  PASS  $label"
  else
    echo "  FAIL  $label"
    fail=$((fail + 1))
  fi
}

# Capture output so we can also count archives in the run.
output=$(bash "$REPO_ROOT/tools/validate-skill.sh" --all 2>&1)
rc=$?

archive_count=$(printf "%s\n" "$output" | grep -c '^skill: ')

check "validate-skill.sh --all exits 0" "$rc"

# Sanity: we expect at least the 12 surviving skills + 2 tombstones = 14.
# If the repo grows, that's fine — we only assert a floor.
if [[ $archive_count -ge 14 ]]; then
  check "at least 14 archives present (got $archive_count)" 0
else
  check "at least 14 archives present (got $archive_count)" 1
fi

# Re-emit the summary line so the runner shows it.
printf "%s\n" "$output" | tail -n1 | sed 's/^/  info  /'

echo
echo "  $checks checks · $fail fail"
exit $fail
