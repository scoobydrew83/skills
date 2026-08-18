#!/usr/bin/env bash
# Integration test using the vault's Deterministic Logic-Puzzle Engine idea.
# It never builds the product or contacts agencies: the buyer-validation
# outreach remains a human-gated Phase 0 action.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/.harness"
cp "$ROOT/.harness/loop-policy.json" "$tmp/.harness/loop-policy.json"
printf '%s\n' '# Policy' > "$tmp/AGENTS.md"
printf '%s\n' '# Context' 'Phase 0 — buyer validation; no product build or outreach without an explicit human decision.' > "$tmp/CONTEXT.md"
printf '%s\n' '# Memory Bank' > "$tmp/MEMORY_BANK.md"
printf '%s\n' '- [ ] AWAITING_HUMAN | P0-buyer-signal | Authorize the five-agency logic-puzzle outreach test; no messages are sent by this harness.' > "$tmp/LOOP_QUEUE.md"
printf '%s\n' '{"features":[{"id":"F-P0","category":"validation","description":"Buyer-validation gate is recorded before any Phase 1 work.","steps":["Record explicit human authorization", "Record reproducible review evidence"],"passes":false,"evidence":null}]}' > "$tmp/FEATURES.json"

doctor="$ROOT/.agents/skills/conductor-doctor/scripts/doctor.py"
runner="$ROOT/.agents/skills/conductor-router/scripts/transition.py"

doctor_out="$(python3 "$doctor" "$tmp" || true)"
if grep -q '"verdict": "BLOCKED"' <<<"$doctor_out"; then
  echo '  PASS  Phase 0 is blocked pending human authorization'
else
  echo '  FAIL  Phase 0 did not stop at the human gate'; exit 1
fi
if python3 "$runner" "$tmp" P0-buyer-signal PENDING >/dev/null 2>&1; then
  echo '  FAIL  runner bypassed external-communication gate'; exit 1
else
  echo '  PASS  runner rejects gate bypass'
fi
python3 "$runner" "$tmp" P0-buyer-signal PENDING --human-decision 'Drew approved a no-send harness simulation only.' >/dev/null
python3 "$runner" "$tmp" P0-buyer-signal IN_PROGRESS >/dev/null
python3 "$runner" "$tmp" P0-buyer-signal VERIFYING >/dev/null
if python3 "$runner" "$tmp" P0-buyer-signal DONE --feature-id F-P0 >/dev/null 2>&1; then
  echo '  FAIL  runner allowed DONE without evidence'; exit 1
else
  echo '  PASS  runner requires verification evidence'
fi
python3 "$runner" "$tmp" P0-buyer-signal DONE --feature-id F-P0 --check 'spec-review|Phase 0 stays gated|PASS' >/dev/null
doctor_out="$(python3 "$doctor" "$tmp")"
if grep -q '"verdict": "PASS"' <<<"$doctor_out"; then
  echo '  PASS  doctor accepts the evidenced Phase 0 completion'
else
  echo '  FAIL  doctor rejected the evidenced Phase 0 completion'; exit 1
fi
grep -q '"item_id":"P0-buyer-signal"' "$tmp/.harness/EVIDENCE.jsonl" \
  && echo '  PASS  transition evidence persisted' \
  || { echo '  FAIL  transition evidence missing'; exit 1; }
