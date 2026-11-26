#!/usr/bin/env bash
# SubagentStop evidence hook: verifier verdicts become valid EVIDENCE.jsonl
# rows, other agents are ignored, and the hook never blocks (always exit 0).

set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOOK="$ROOT/tools/hooks/record-evidence.sh"
fail=0
pass() { echo "  PASS  $*"; }
bad() { echo "  FAIL  $*"; fail=1; }

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
ledger="$tmp/.harness/EVIDENCE.jsonl"

report='VERDICT: PASS
PHASE: phase-2-auth
CRITERIA:
  - [PASS] login returns 200 — tests/auth.test.js:14
  - [PASS] bad password returns 401 — tests/auth.test.js:22
TESTS: npm test (42 passed)
SCOPE FLAGS: none
NEXT: close phase-2-auth'

event() { # agent_type message
  python3 -c 'import json,sys; print(json.dumps({"hook_event_name":"SubagentStop","session_id":"s1","agent_id":"a1","agent_type":sys.argv[1],"last_assistant_message":sys.argv[2],"stop_hook_active":False}))' "$1" "$2"
}

event conductor-verifier "$report" | CLAUDE_PROJECT_DIR="$tmp" bash "$HOOK"
rc=$?
[[ $rc -eq 0 ]] && pass "hook exits 0 on a verdict" || bad "hook exits 0 on a verdict (got $rc)"
[[ -f "$ledger" && $(wc -l < "$ledger") -eq 1 ]] && pass "one row appended for a verifier verdict" || bad "one row appended for a verifier verdict"

python3 - "$ledger" <<'PY' && pass "row has the required keys and parsed fields" || bad "row has the required keys and parsed fields"
import json, sys
row = json.loads(open(sys.argv[1]).readline())
assert {"run_id", "item_id", "phase", "actor", "checks", "verdict", "next"} <= row.keys(), row
assert row["verdict"] == "PASS" and row["item_id"] == "phase-2-auth", row
assert row["run_id"] == "s1:a1" and row["phase"] == "verify", row
assert sum(1 for c in row["checks"] if c.get("result") == "PASS") == 2, row
assert row["next"] == "close phase-2-auth", row
PY

event coordinated-skills:conductor-verifier "$report" | CLAUDE_PROJECT_DIR="$tmp" bash "$HOOK"
[[ $(wc -l < "$ledger") -eq 2 ]] && pass "plugin-namespaced verifier is recorded" || bad "plugin-namespaced verifier is recorded"

event conductor-builder "$report" | CLAUDE_PROJECT_DIR="$tmp" bash "$HOOK"
event Explore "no verdict here" | CLAUDE_PROJECT_DIR="$tmp" bash "$HOOK"
[[ $(wc -l < "$ledger") -eq 2 ]] && pass "non-verifier agents are ignored" || bad "non-verifier agents are ignored"

transcript="$tmp/transcript.jsonl"
python3 -c 'import json,sys; print(json.dumps({"type":"assistant","message":{"content":[{"type":"text","text":sys.argv[1]}]}}))' "${report/PASS/FAIL}" > "$transcript"
python3 -c 'import json,sys; print(json.dumps({"hook_event_name":"SubagentStop","session_id":"s1","agent_id":"a2","agent_type":"conductor-verifier","agent_transcript_path":sys.argv[1],"last_assistant_message":"Handing back."}))' "$transcript" \
  | CLAUDE_PROJECT_DIR="$tmp" bash "$HOOK"
tail -1 "$ledger" | grep -q '"verdict": "FAIL"' && pass "falls back to the transcript when the closing text has no verdict" || bad "falls back to the transcript when the closing text has no verdict"

before=$(wc -l < "$ledger")
printf 'not json' | CLAUDE_PROJECT_DIR="$tmp" bash "$HOOK"
rc=$?
[[ $rc -eq 0 && $(wc -l < "$ledger") -eq $before ]] && pass "bad input exits 0 and writes nothing" || bad "bad input exits 0 and writes nothing"

# The doctor exits nonzero here (the temp root has no AGENTS.md etc.), so read
# its JSON report rather than its exit code.
doctor_out="$(python3 "$ROOT/.agents/skills/conductor-doctor/scripts/doctor.py" "$tmp" 2>/dev/null || true)"
printf '%s' "$doctor_out" \
  | python3 -c 'import json,sys; c=[x for x in json.load(sys.stdin)["checks"] if x["label"]=="evidence ledger"]; sys.exit(0 if c and c[0]["ok"] else 1)' \
  && pass "conductor-doctor accepts the ledger" || bad "conductor-doctor accepts the ledger"

grep -q 'record-evidence.sh' "$ROOT/.claude/settings.json" && pass "hook is wired in .claude/settings.json" || bad "hook is wired in .claude/settings.json"

exit "$fail"
