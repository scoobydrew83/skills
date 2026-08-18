#!/usr/bin/env bash
# Every active skill must explicitly opt into the universal delivery contract.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
missing=()
while IFS= read -r skill; do
  grep -q '^response_contract: universal$' "$skill" || missing+=("${skill#$ROOT/}")
done < <(find "$ROOT/.agents/skills" -name SKILL.md -type f | sort)

if [[ ${#missing[@]} -gt 0 ]]; then
  printf '  FAIL  missing universal response contract: %s\n' "${missing[*]}"
  exit 1
fi
echo "  PASS  all skills declare the universal response contract"
