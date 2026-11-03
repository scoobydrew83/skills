#!/usr/bin/env bash
# Retired-skills test: skills that were merged or deleted stay gone.
#
# A retired skill is deleted outright (no DEPRECATED stub), because a stub still
# loads its description into every session and can still be picked. This test
# fails if a retired name comes back as a directory, or if any canonical skill,
# command, agent, or top-level doc still points at it.
#
# Add a line to RETIRED when you retire a skill: name=survivor (or name=- if it
# was dropped with no successor).

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

RETIRED=(
  "adaptive-communication=neurodivergent-comms"
  "task-decomposition=overwhelm-breakdown"
  "idea-validator=hemlock"
  "session-continuity=session-bookend"
  "experiment-designer=derisk-sequencer"
  "conductor-router=next-step"
  "agent-workspace-compatibility=skill-librarian"
)

SEARCH_PATHS=(.agents/skills .claude/commands agents skills.sh.json README.md HOW-TO-USE.md CONVENTIONS.md CONDUCTOR-LOOP-GUIDE.md AGENTS.md)

fail=0
for entry in "${RETIRED[@]}"; do
  name="${entry%%=*}"
  survivor="${entry#*=}"

  if [[ -e ".agents/skills/$name" ]]; then
    echo "  FAIL  retired skill '$name' exists again at .agents/skills/$name"
    fail=$((fail + 1))
    continue
  fi

  hits=$(grep -rnw --include='*' -e "$name" "${SEARCH_PATHS[@]}" 2>/dev/null || true)
  if [[ -n "$hits" ]]; then
    echo "  FAIL  '$name' is retired (use '$survivor') but is still referenced:"
    printf '%s\n' "$hits" | sed 's/^/          /'
    fail=$((fail + 1))
  else
    echo "  PASS  $name retired → $survivor"
  fi

  if [[ "$survivor" != "-" && ! -f ".agents/skills/$survivor/SKILL.md" ]]; then
    echo "  FAIL  survivor '$survivor' for '$name' does not exist"
    fail=$((fail + 1))
  fi
done

echo
echo "  $fail fail"
exit $fail
