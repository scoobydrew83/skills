#!/usr/bin/env bash
# visual-plan tooling test: the plan lint must be MECHANICAL (exit code, not a
# banner), comment ids must never collide, and the plan-mode capture hook must
# never fail silently.
#
# Each case below is a regression: it fails if one of those three properties
# breaks. Everything runs against a throwaway repo in $TMPDIR.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VP="$REPO_ROOT/plugins/coordinated-skills/skills/visual-plan"

pass=0
fail=0
ok()   { echo "  PASS  $1"; pass=$((pass + 1)); }
bad()  { echo "  FAIL  $1"; fail=$((fail + 1)); }
check() { [[ "$2" == "$3" ]] && ok "$1" || bad "$1 (expected '$3', got '$2')"; }

if ! command -v node >/dev/null 2>&1; then
  echo "  SKIP  node not installed — visual-plan tools are node scripts"
  exit 0
fi

# Explicit XXXXXX template: portable across BSD and GNU mktemp. `mktemp -d -t
# vplan` works on macOS but GNU reads -t's argument as a template needing at
# least six X's, so it fails on CI runners — leaving $SB empty and every path
# below rooted at /.
SB=$(mktemp -d "${TMPDIR:-/tmp}/vplan.XXXXXX")
if [[ -z "${SB:-}" || ! -d "$SB" ]]; then
  echo "  FAIL  could not create a temp dir — refusing to run with paths rooted at /"
  exit 1
fi
trap 'rm -rf "$SB"' EXIT
mkdir -p "$SB/.harness/plan" "$SB/tools"
cp "$VP"/tools/*.mjs "$SB/tools/"

cat > "$SB/FEATURES.json" <<'EOF'
{ "project": "t", "phase": "t", "features": [
  { "id": "F-001", "category": "c", "description": "d", "passes": false } ] }
EOF

# A structurally clean plan: real feature ref, answered question, grounded code.
clean_plan() {
  cat > "$SB/.harness/plan/blocks.json" <<'EOF'
{ "blocks": [
  { "id": "b-1", "type": "note", "section": "S", "title": "t", "features": ["F-001"], "text": "x" },
  { "id": "b-2", "type": "question", "section": "S", "title": "q", "features": [], "text": "why?", "answer": "because" },
  { "id": "b-3", "type": "annotated-code", "section": "S", "title": "a", "features": [],
    "file": "FEATURES.json", "annotations": [ { "line": 2, "note": "n" } ] } ] }
EOF
}

# Replace the block list with one deliberately broken block.
broken_plan() { printf '{ "blocks": [ %s ] }\n' "$1" > "$SB/.harness/plan/blocks.json"; }

run_check() { (cd "$SB" && node tools/render-plan.mjs --repo . --check >/dev/null 2>&1); echo $?; }

echo "--- lint is mechanical (exit code, not a banner) ---"
clean_plan
check "clean plan passes --check" "$(run_check)" "0"
check "render without --check never fails" \
  "$( (cd "$SB" && node tools/render-plan.mjs --repo . >/dev/null 2>&1); echo $? )" "0"

broken_plan '{ "id": "b-x", "type": "note", "section": "S", "title": "t", "features": ["F-404"], "text": "x" }'
check "dangling feature ref fails" "$(run_check)" "1"

broken_plan '{ "id": "b-d", "type": "note", "section": "S", "title": "a", "features": [], "text": "x" },
             { "id": "b-d", "type": "note", "section": "S", "title": "b", "features": [], "text": "y" }'
check "duplicate block id fails" "$(run_check)" "1"

broken_plan '{ "id": "b-q", "type": "question", "section": "S", "title": "q", "features": [], "text": "unanswered?" }'
check "unanswered question fails" "$(run_check)" "1"

broken_plan '{ "id": "b-c", "type": "annotated-code", "section": "S", "title": "a", "features": [],
               "file": "FEATURES.json", "annotations": [ { "line": 9999, "note": "n" } ] }'
check "annotated-code past EOF fails" "$(run_check)" "1"

broken_plan '{ "id": "b-c", "type": "annotated-code", "section": "S", "title": "a", "features": [],
               "file": "nope.txt", "annotations": [ { "line": 1, "note": "n" } ] }'
check "annotated-code missing file fails" "$(run_check)" "1"

broken_plan '{ "id": "b-c", "type": "annotated-code", "section": "S", "title": "a", "features": [],
               "file": "FEATURES.json", "annotations": [] }'
check "annotated-code with no annotations fails" "$(run_check)" "1"

# An open comment is a NORMAL state of a plan under review — it must not fail lint.
clean_plan
(cd "$SB" && node tools/plan-comment.mjs --repo . --block b-1 "still thinking" >/dev/null 2>&1)
check "open comment does NOT fail lint" "$(run_check)" "0"

echo "--- comment ids never collide ---"
rm -f "$SB/.harness/plan/comments.jsonl"
(cd "$SB" && node tools/plan-comment.mjs --repo . --block b-1 "first"  >/dev/null 2>&1)
(cd "$SB" && node tools/plan-comment.mjs --repo . --block b-1 "second" >/dev/null 2>&1)
grep -v '"text":"first"' "$SB/.harness/plan/comments.jsonl" > "$SB/t" && mv "$SB/t" "$SB/.harness/plan/comments.jsonl"
(cd "$SB" && node tools/plan-comment.mjs --repo . --block b-1 "third" >/dev/null 2>&1)
ids=$(node -e '
  const fs = require("fs");
  const ids = fs.readFileSync(process.argv[1], "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l).id);
  console.log(new Set(ids).size === ids.length ? "unique" : "COLLISION");' "$SB/.harness/plan/comments.jsonl")
check "ids stay unique after a row is deleted" "$ids" "unique"

# A comment whose text equals a flag value must not be swallowed by arg parsing.
rm -f "$SB/.harness/plan/comments.jsonl"
(cd "$SB" && node tools/plan-comment.mjs --repo . --block b-1 "b-1" >/dev/null 2>&1)
check "comment text equal to the block id is kept" \
  "$(grep -c '"text":"b-1"' "$SB/.harness/plan/comments.jsonl")" "1"

echo "--- resolution requires an answer ---"
check "resolve without --answer is refused" \
  "$( (cd "$SB" && node tools/plan-comment.mjs --repo . --resolve c-001 >/dev/null 2>&1); echo $? )" "1"

# Legacy files can hold duplicate ids; resolving must clear ALL of them, or the
# survivor blocks its features with no way to clear it.
printf '%s\n%s\n' \
  '{"id":"c-9","block":"b-1","author":"x","text":"A","created":"2026-07-01","resolved":false}' \
  '{"id":"c-9","block":"b-1","author":"x","text":"B","created":"2026-07-02","resolved":false}' \
  > "$SB/.harness/plan/comments.jsonl"
(cd "$SB" && node tools/plan-comment.mjs --repo . --resolve c-9 --answer "done" >/dev/null 2>&1)
check "resolving a duplicated legacy id leaves none open" \
  "$( (cd "$SB" && node tools/plan-comment.mjs --repo . --list --open 2>/dev/null) | grep -c '●' )" "0"

echo "--- the capture hook never fails silently ---"
out=$(printf '{"tool_input":{"plan":"bad\ncontrol\nchars"},"cwd":"%s"}' "$SB" \
  | (cd "$SB" && node tools/capture-plan.mjs 2>&1); echo "rc=$?")
case "$out" in
  *FAILED*rc=0*) ok "malformed payload reports the error and still exits 0" ;;
  *rc=0*)        bad "malformed payload exited 0 but said nothing (silent no-op)" ;;
  *)             bad "malformed payload broke planning: $out" ;;
esac

rm -rf "$SB/.harness/plan/captured"
printf '{"tool_input":{"plan":"# Real plan"},"cwd":"%s"}' "$SB" \
  | (cd "$SB" && node tools/capture-plan.mjs >/dev/null 2>&1)
check "approved plan is captured to disk" \
  "$(ls "$SB/.harness/plan/captured" 2>/dev/null | grep -c '^plan-.*\.md$')" "1"

echo
echo "  $pass pass · $fail fail"
exit $fail
