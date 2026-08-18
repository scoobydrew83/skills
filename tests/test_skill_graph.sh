#!/usr/bin/env bash
# Generated documentation must be deterministic AND committed in sync: a
# timestamp creates permanent dirty diffs, and a stale committed graph hides
# real routing changes. Generates to a temp path so the test never dirties the
# tracked tree.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
graph="$ROOT/skill-graph.md"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

SKILL_GRAPH_OUT="$tmp/first.md" bash "$ROOT/tools/skill-graph.sh" >/dev/null
SKILL_GRAPH_OUT="$tmp/second.md" bash "$ROOT/tools/skill-graph.sh" >/dev/null

if cmp -s "$tmp/first.md" "$tmp/second.md"; then
  echo "  PASS  graph generation is deterministic"
else
  echo "  FAIL  graph generation changes without source changes"
  exit 1
fi

if cmp -s "$tmp/first.md" "$graph"; then
  echo "  PASS  committed graph matches the skill directories"
else
  echo "  FAIL  skill-graph.md is stale — regenerate with tools/skill-graph.sh"
  diff "$graph" "$tmp/first.md" | head -20
  exit 1
fi

for skill in next-step assumption-grill conductor-router conductor-doctor; do
  if grep -q "\`$skill\`" "$graph"; then
    echo "  PASS  graph includes $skill"
  else
    echo "  FAIL  graph missing $skill"
    exit 1
  fi
done
