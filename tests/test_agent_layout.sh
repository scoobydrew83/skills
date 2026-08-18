#!/usr/bin/env bash
# Canonical-source, generated-package, and instruction-alias contract.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
fail=0

check() {
  local label="$1"
  shift
  if "$@"; then
    echo "  PASS  $label"
  else
    echo "  FAIL  $label"
    fail=1
  fi
}

check "canonical skills directory exists" test -d "$REPO_ROOT/.agents/skills"
check "Claude alias targets AGENTS.md" test "$(readlink "$REPO_ROOT/CLAUDE.md")" = AGENTS.md
check "Gemini alias targets AGENTS.md" test "$(readlink "$REPO_ROOT/GEMINI.md")" = AGENTS.md
check "generated plugin has no skill symlinks" sh -c '! find "$1" -type l -print -quit | grep -q .' sh "$REPO_ROOT/plugins/coordinated-skills/skills"
check "generated plugin includes Claude Conductor commands" sh -c 'test -f "$1/commands/conductor-loop.md" && test -f "$1/commands/conductor-route.md" && test -f "$1/commands/conductor-doctor.md"' sh "$REPO_ROOT/plugins/coordinated-skills"
check "generated route command resolves plugin root" grep -q '\${CLAUDE_PLUGIN_ROOT:' "$REPO_ROOT/plugins/coordinated-skills/commands/conductor-route.md"
check "generated plugin includes maker/checker agents" sh -c 'test -f "$1/agents/conductor-builder.md" && test -f "$1/agents/conductor-verifier.md"' sh "$REPO_ROOT/plugins/coordinated-skills"
check "canonical skills contain no Python caches" sh -c '! find "$1" -type d -name __pycache__ -print -quit | grep -q .' sh "$REPO_ROOT/.agents/skills"
check "generated package contains no Python caches" sh -c '! find "$1" -type d -name __pycache__ -print -quit | grep -q .' sh "$REPO_ROOT/plugins/coordinated-skills/skills"
check "sync check passes" bash "$REPO_ROOT/tools/sync-agent-layout.sh" --check

exit "$fail"
