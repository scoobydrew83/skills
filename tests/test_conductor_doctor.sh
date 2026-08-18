#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/.harness"
for f in AGENTS.md CONTEXT.md MEMORY_BANK.md LOOP_QUEUE.md; do printf '# %s\n' "$f" > "$tmp/$f"; done
printf '%s\n' '- [ ] PENDING: test doctor' > "$tmp/LOOP_QUEUE.md"
cp "$ROOT/.harness/loop-policy.json" "$tmp/.harness/loop-policy.json"
printf '%s\n' '{"features":[{"id":"F-1","passes":false,"evidence":null}]}' > "$tmp/FEATURES.json"
printf '%s\n' '{"run_id":"r1","item_id":"i1","phase":"verify","actor":"test","checks":[],"verdict":"PASS","next":"done"}' > "$tmp/.harness/EVIDENCE.jsonl"
if python3 "$ROOT/.agents/skills/conductor-doctor/scripts/doctor.py" "$tmp" | grep -q '"verdict": "PASS"'; then
  echo '  PASS  doctor accepts valid harness'
else
  echo '  FAIL  doctor accepts valid harness'; exit 1
fi
if python3 "$ROOT/.agents/skills/conductor-doctor/scripts/doctor.py" "$tmp" --library-root "$ROOT" | grep -q '"library generated package"'; then
  echo '  PASS  doctor audits aliases and generated package when requested'
else
  echo '  FAIL  doctor audits aliases and generated package when requested'; exit 1
fi
rm "$tmp/.harness/loop-policy.json"
if python3 "$ROOT/.agents/skills/conductor-doctor/scripts/doctor.py" "$tmp" >/dev/null 2>&1; then
  echo '  FAIL  doctor blocks missing policy'; exit 1
else
  echo '  PASS  doctor blocks missing policy'
fi
