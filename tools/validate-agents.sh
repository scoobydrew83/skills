#!/usr/bin/env bash
# validate-agents.sh — check the Conductor agent definitions against the contract.
#
# Usage:
#   tools/validate-agents.sh
#   tools/validate-agents.sh --help
#
# Checks:
#   1. conductor-builder.md and conductor-verifier.md each carry the required
#      frontmatter keys: name, description, tools, phase, hands_off_to.
#   2. The VERDICT block in conductor-verifier.md uses exactly the verdict
#      vocabulary defined in CONVENTIONS.md §5 — extracted from both and diffed,
#      fails on any mismatch (so the verifier's output schema can't drift from
#      the documented contract).
#
# Output is one line per check. Exit code: nonzero if any FAIL was reported.

set -uo pipefail

usage() {
  cat <<'EOF'
validate-agents.sh — check the Conductor agent definitions against the contract.

Usage:
  tools/validate-agents.sh
  tools/validate-agents.sh --help

Exit code: nonzero if any FAIL was reported.
EOF
}

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  usage
  exit 0
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

AGENTS="conductor-builder.md conductor-verifier.md"
REQUIRED_KEYS="name description tools phase hands_off_to"
VERIFIER="$REPO_ROOT/conductor-verifier.md"
CONVENTIONS="$REPO_ROOT/CONVENTIONS.md"

fail=0
pass() { echo "PASS  $*"; }
bad()  { echo "FAIL  $*"; fail=1; }

# --- 1. frontmatter keys -----------------------------------------------------
# Frontmatter is the YAML block between the first two '---' lines.
frontmatter() { awk 'NR==1 && $0=="---"{f=1; next} f && $0=="---"{exit} f'; }

for name in $AGENTS; do
  file="$REPO_ROOT/$name"
  if [[ ! -f "$file" ]]; then
    bad "$name — file missing"
    continue
  fi
  fm="$(frontmatter <"$file")"
  for key in $REQUIRED_KEYS; do
    if grep -qE "^${key}:" <<<"$fm"; then
      pass "$name — frontmatter has '${key}:'"
    else
      bad "$name — frontmatter missing '${key}:' (add it to the YAML frontmatter)"
    fi
  done
done

# --- 2. VERDICT vocabulary parity vs CONVENTIONS.md §5 -----------------------
# Extract the ordered, de-duplicated verdict tokens from each source and diff.
tokens() { grep -oE '\b(PASS|FAIL|BLOCKED)\b' | awk '!seen[$0]++' | tr '\n' ' '; }

schema_tokens="$(awk '/^## 5\./{s=1; next} /^## 6\./{s=0} s' "$CONVENTIONS" | tokens)"
block_tokens="$(awk '/^VERDICT:/{print}' "$VERIFIER" | tokens)"

if [[ -z "$block_tokens" ]]; then
  bad "conductor-verifier.md — no 'VERDICT:' block found"
elif [[ "$schema_tokens" == "$block_tokens" ]]; then
  pass "conductor-verifier.md — VERDICT vocabulary matches CONVENTIONS.md §5 [$block_tokens]"
else
  bad "conductor-verifier.md — VERDICT vocabulary [$block_tokens] != CONVENTIONS.md §5 [$schema_tokens]"
fi

echo
if [[ $fail -eq 0 ]]; then
  echo "validate-agents: OK"
else
  echo "validate-agents: FAILED — fix the items above"
fi
exit $fail
