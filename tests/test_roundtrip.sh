#!/usr/bin/env bash
# Pack-fidelity test: building a .skill archive from a skill's source directory
# and extracting it back yields byte-identical files. This catches regressions
# in pack-skill.sh (the à-la-carte distribution path) without touching the repo
# — we extract into a tmpdir and diff against the source.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILLS_DIR="$REPO_ROOT/plugins/coordinated-skills/skills"

# Pick a small, stable skill with references/scripts so the test exercises a
# multi-file tree, not just SKILL.md.
SKILL="session-continuity"
SRC="$SKILLS_DIR/$SKILL"

if [[ ! -d "$SRC" ]]; then
  echo "  FAIL  source dir missing: $SRC"
  exit 1
fi

TEST_DIR=$(mktemp -d)
trap 'rm -rf "$TEST_DIR"' EXIT

fail=0

# Build the archive (pack-skill writes to the gitignored dist/).
ARCHIVE="$REPO_ROOT/dist/${SKILL}.skill"
if bash "$REPO_ROOT/tools/pack-skill.sh" "$SKILL" >/dev/null 2>&1 && [[ -f "$ARCHIVE" ]]; then
  echo "  PASS  pack produces archive"
else
  echo "  FAIL  pack failed or archive not produced"
  exit 1
fi

# Extract and diff against the source tree.
unzip -q -o "$ARCHIVE" -d "$TEST_DIR/extract"
if diff -r "$SRC" "$TEST_DIR/extract/$SKILL" >/dev/null 2>&1; then
  echo "  PASS  extracted archive matches source"
else
  echo "  FAIL  extracted archive differs from source:"
  diff -r "$SRC" "$TEST_DIR/extract/$SKILL" 2>&1 | sed 's/^/         /'
  fail=$((fail + 1))
fi

exit $fail
