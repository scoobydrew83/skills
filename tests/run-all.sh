#!/usr/bin/env bash
# run-all.sh — the structural test suite for the skill library.
#
# Real, deterministic checks over the committed tree. No network, no API keys.
# It aggregates the two enforcement validators and a handful of repo-shape
# invariants so a green run means the library still satisfies its own contract.
#
# Usage:  bash tests/run-all.sh
# Exit code: nonzero if any check FAILs. WARNs (tombstones) do not fail the run.

set -uo pipefail
cd "$(cd "$(dirname "$0")/.." && pwd)"

fail=0
checks=0
ok() { checks=$((checks + 1)); echo "ok   - $*"; }
no() { checks=$((checks + 1)); fail=1; echo "FAIL - $*"; }

# 1. Every skill validates against CONVENTIONS.md §1–§3.
if out="$(bash tools/validate-skill.sh --all 2>&1)"; then
  ok "validate-skill.sh --all ($(grep -oE '[0-9]+ pass' <<<"$out" | head -1))"
else
  no "validate-skill.sh --all"; echo "$out"
fi

# 2. Agent definitions satisfy the frontmatter + verdict-schema contract.
if out="$(bash tools/validate-agents.sh 2>&1)"; then
  ok "validate-agents.sh"
else
  no "validate-agents.sh"; echo "$out"
fi

# 3. Every skill directory carries a SKILL.md.
for d in plugins/coordinated-skills/skills/*/; do
  name="$(basename "$d")"
  [[ -f "${d}SKILL.md" ]] && ok "SKILL.md present :: $name" || no "SKILL.md missing :: $name"
done

# 4. The generated phase × handoffs map exists and is non-empty.
[[ -s skill-graph.md ]] && ok "skill-graph.md present" || no "skill-graph.md missing or empty"

# 5. CONVENTIONS.md keeps its load-bearing sections.
for h in '## 1.' '## 4.' '## 5.'; do
  grep -qF "$h" CONVENTIONS.md && ok "CONVENTIONS.md has $h" || no "CONVENTIONS.md missing $h"
done

echo
echo "run-all: $checks checks · $([[ $fail -eq 0 ]] && echo PASS || echo FAIL)"
exit $fail
