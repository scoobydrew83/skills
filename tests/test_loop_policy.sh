#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail=0
pass() { echo "  PASS  $*"; }
bad() { echo "  FAIL  $*"; fail=1; }

if python3 "$ROOT/tools/validate-loop-policy.py" "$ROOT/.harness/loop-policy.json"; then
  pass "repository loop policy validates"
else
  bad "repository loop policy validates"
fi

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/.harness"
cp "$ROOT/.harness/loop-policy.json" "$tmp/.harness/loop-policy.json"
printf '# Queue\n- [ ] PENDING: safe task\n' > "$tmp/LOOP_QUEUE.md"
route="$(python3 "$ROOT/.agents/skills/next-step/scripts/route_next.py" "$tmp")"
grep -q '"next": "IN_PROGRESS"' <<<"$route" && pass "router advances pending item" || bad "router advances pending item"
printf '# Queue\n- [ ] AWAITING_HUMAN: choose provider\n' > "$tmp/LOOP_QUEUE.md"
route="$(python3 "$ROOT/.agents/skills/next-step/scripts/route_next.py" "$tmp")"
grep -q 'Decision needed' <<<"$route" && pass "router stops at human gate" || bad "router stops at human gate"

python3 "$ROOT/tools/validate-loop-transition.py" PENDING IN_PROGRESS >/dev/null \
  && pass "legal queue transition accepted" \
  || bad "legal queue transition accepted"
if python3 "$ROOT/tools/validate-loop-transition.py" PENDING DONE >/dev/null 2>&1; then
  bad "illegal queue transition rejected"
else
  pass "illegal queue transition rejected"
fi
if python3 "$ROOT/tools/validate-loop-transition.py" AWAITING_HUMAN PENDING >/dev/null 2>&1; then
  bad "human gate bypass rejected"
else
  pass "human gate bypass rejected"
fi
python3 "$ROOT/tools/validate-loop-transition.py" AWAITING_HUMAN PENDING --human-decision >/dev/null \
  && pass "recorded human decision unblocks work" \
  || bad "recorded human decision unblocks work"

for f in AGENTS.md CONVENTIONS.md agents/conductor-builder.md agents/conductor-verifier.md; do
  grep -qi 'response baseline\|Decision needed\|neurodivergent-comms' "$ROOT/$f" \
    && pass "response contract declared in $f" \
    || bad "response contract missing from $f"
done

exit "$fail"
