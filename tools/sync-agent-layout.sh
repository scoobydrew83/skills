#!/usr/bin/env bash
# sync-agent-layout.sh — guard the portable agent layout.

set -euo pipefail

usage() {
  cat <<'EOF'
sync-agent-layout.sh — verify or apply repository agent compatibility aliases.

Usage:
  tools/sync-agent-layout.sh --check
  tools/sync-agent-layout.sh --apply

AGENTS.md is canonical. CLAUDE.md and GEMINI.md must be relative symlinks to it.
--apply never overwrites a real file or an incorrect symlink.
EOF
}

[[ $# -eq 1 ]] || { usage >&2; exit 2; }
mode="$1"
[[ "$mode" == "--check" || "$mode" == "--apply" ]] || { usage >&2; exit 2; }

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
fail=0

check_alias() {
  local name="$1" path="$REPO_ROOT/$1"
  if [[ -L "$path" && "$(readlink "$path")" == "AGENTS.md" ]]; then
    echo "PASS $name -> AGENTS.md"
    return 0
  fi
  if [[ "$mode" == "--apply" && ! -e "$path" && ! -L "$path" ]]; then
    ln -s AGENTS.md "$path"
    echo "CREATED $name -> AGENTS.md"
    return 0
  fi
  echo "FAIL $name must be a relative symlink to AGENTS.md" >&2
  fail=1
}

[[ -f "$REPO_ROOT/AGENTS.md" ]] || { echo "FAIL AGENTS.md is missing" >&2; exit 1; }
check_alias CLAUDE.md
check_alias GEMINI.md

if [[ "$mode" == "--apply" && $fail -eq 0 ]]; then
  bash "$SCRIPT_DIR/build-plugin.sh"
elif [[ "$mode" == "--check" ]]; then
  bash "$SCRIPT_DIR/build-plugin.sh" --check || fail=1
fi

exit "$fail"
