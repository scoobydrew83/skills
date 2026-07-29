#!/usr/bin/env bash
# CONVENTIONS.md presence and content sanity:
#   - File exists at the repo root
#   - References the four shared-state files: CONTEXT.md, MEMORY_BANK.md,
#     LOOP_QUEUE.md, CLAUDE.md
#   - References the verdict schema (PASS / FAIL / BLOCKED)
#   - Documents the seven phases

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CONV="$REPO_ROOT/CONVENTIONS.md"

fail=0

if [[ -f "$CONV" ]]; then
  echo "  PASS  CONVENTIONS.md exists at repo root"
else
  echo "  FAIL  CONVENTIONS.md missing at $CONV"
  exit 1
fi

# Required references.
for ref in CONTEXT.md MEMORY_BANK.md LOOP_QUEUE.md CLAUDE.md; do
  if grep -qF "$ref" "$CONV"; then
    echo "  PASS  references $ref"
  else
    echo "  FAIL  CONVENTIONS.md does not reference $ref"
    fail=$((fail + 1))
  fi
done

# Verdict schema.
missing_verdict=()
for verdict in PASS FAIL BLOCKED; do
  if ! grep -qE "\\b$verdict\\b" "$CONV"; then
    missing_verdict+=("$verdict")
  fi
done
if [[ ${#missing_verdict[@]} -eq 0 ]]; then
  echo "  PASS  verdict schema (PASS / FAIL / BLOCKED) documented"
else
  echo "  FAIL  verdict schema missing terms: ${missing_verdict[*]}"
  fail=$((fail + 1))
fi

# Phase vocabulary.
missing_phases=()
for phase in intake plan execute verify communicate bookend meta; do
  if ! grep -qE "\\b$phase\\b" "$CONV"; then
    missing_phases+=("$phase")
  fi
done
if [[ ${#missing_phases[@]} -eq 0 ]]; then
  echo "  PASS  phase vocabulary (7 phases) documented"
else
  echo "  FAIL  phase vocabulary missing: ${missing_phases[*]}"
  fail=$((fail + 1))
fi

exit $fail
