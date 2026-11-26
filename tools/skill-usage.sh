#!/usr/bin/env bash
# skill-usage.sh — count how often each canonical skill shows up in real
# project state, to help decide which skills to keep.
#
# Usage:
#   tools/skill-usage.sh [<project-root> ...]
#   tools/skill-usage.sh --help
#
# For each skill in .agents/skills/ it counts, across the project roots given
# (default: this repository):
#   - MEMORY_BANK.md lines whose skill field names it (CONVENTIONS.md §4)
#   - .harness/EVIDENCE.jsonl rows that mention it
# Skills seen zero times are flagged NEVER-SEEN. This is one input to the
# trim in docs/SKILL-TRIM.md, not a verdict: a skill can be used without
# writing a MEMORY_BANK line. Read-only; it changes nothing.

set -euo pipefail

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  sed -n '2,15p' "$0" | sed 's/^# \{0,1\}//'
  exit 0
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILLS_DIR="$REPO_ROOT/.agents/skills"

roots=("$@")
[[ ${#roots[@]} -eq 0 ]] && roots=("$REPO_ROOT")

for root in "${roots[@]}"; do
  [[ -d "$root" ]] || { echo "error: not a directory: $root" >&2; exit 2; }
done

printf '%-28s %8s %8s  %s\n' SKILL MEMORY EVIDENCE STATUS
never=0
total=0
for dir in "$SKILLS_DIR"/*/; do
  skill="$(basename "$dir")"
  [[ -f "$dir/SKILL.md" ]] || continue
  total=$((total + 1))
  mem=0
  ev=0
  for root in "${roots[@]}"; do
    if [[ -f "$root/MEMORY_BANK.md" ]]; then
      n=$(grep -cE "^- [0-9]{4}-[0-9]{2}-[0-9]{2} · ${skill} · " "$root/MEMORY_BANK.md" || true)
      mem=$((mem + n))
    fi
    if [[ -f "$root/.harness/EVIDENCE.jsonl" ]]; then
      n=$(grep -cF "$skill" "$root/.harness/EVIDENCE.jsonl" || true)
      ev=$((ev + n))
    fi
  done
  status=seen
  if [[ $mem -eq 0 && $ev -eq 0 ]]; then
    status=NEVER-SEEN
    never=$((never + 1))
  fi
  printf '%-28s %8d %8d  %s\n' "$skill" "$mem" "$ev" "$status"
done
echo
echo "$never of $total skills never seen in ${#roots[@]} project root(s)."
