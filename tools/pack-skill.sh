#!/usr/bin/env bash
# pack-skill.sh — build a distributable <skill-name>.skill archive from its
# source directory at plugins/coordinated-skills/skills/<skill-name>/.
#
# The source of truth is the unpacked directory; the .skill archive is a build
# artifact (gitignored) for the "drop a single skill into your skills folder"
# use case. Output goes to dist/<skill-name>.skill.
#
# Usage:
#   tools/pack-skill.sh <skill-name>
#   tools/pack-skill.sh --all
#   tools/pack-skill.sh --help
#
# Idempotent: replaces an existing archive in place.

set -euo pipefail

usage() {
  cat <<'EOF'
pack-skill.sh — build dist/<name>.skill from its source directory.

Usage:
  tools/pack-skill.sh <skill-name>
  tools/pack-skill.sh --all
  tools/pack-skill.sh --help

Arguments:
  skill-name   Bare skill name (no .skill extension). Source dir must exist at
               plugins/coordinated-skills/skills/<skill-name>/.
  --all        Pack every skill directory into dist/.

Example:
  tools/pack-skill.sh overwhelm-breakdown
    → builds dist/overwhelm-breakdown.skill from
      plugins/coordinated-skills/skills/overwhelm-breakdown/
EOF
}

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" || $# -eq 0 ]]; then
  usage
  exit 0
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SRC_BASE="$REPO_ROOT/plugins/coordinated-skills/skills"
DIST="$REPO_ROOT/dist"

if ! command -v zip >/dev/null 2>&1; then
  echo "error: 'zip' is required but not in PATH" >&2
  exit 1
fi

pack_one() {
  local skill="$1"
  local src="$SRC_BASE/$skill"
  local archive="$DIST/${skill}.skill"

  if [[ ! -d "$src" ]]; then
    echo "error: source dir not found: $src" >&2
    exit 1
  fi
  if [[ ! -f "$src/SKILL.md" ]]; then
    echo "error: $src/SKILL.md is missing — every skill must contain SKILL.md" >&2
    exit 1
  fi

  mkdir -p "$DIST"
  # Build into a tmp file then move into place: avoids zip's append-if-exists
  # behavior and is atomic on the same filesystem.
  local tmp_dir tmp_archive
  tmp_dir=$(mktemp -d)
  trap 'rm -rf "$tmp_dir"' RETURN
  tmp_archive="$tmp_dir/${skill}.skill"

  # zip from the parent of the skill dir so the archive contains <name>/... at
  # its top level (the layout a skills folder expects on install).
  (
    cd "$SRC_BASE"
    zip -q -r "$tmp_archive" "$skill"
  )
  mv -f "$tmp_archive" "$archive"
  echo "packed: $src → $archive"
}

if [[ "$1" == "--all" ]]; then
  for d in "$SRC_BASE"/*/; do
    [[ -f "$d/SKILL.md" ]] || continue
    pack_one "$(basename "$d")"
  done
else
  pack_one "$1"
fi
