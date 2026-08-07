#!/usr/bin/env bash
#
# smoke_harness.sh — does the loop harness actually EXECUTE?
#
# Every other check on a loop package is governance: prompts distinct, verdict
# parseable, ceiling present, evidence required. None of them notice a harness
# that is structurally incapable of running unit two. This one runs it.
#
# Stubs CLAUDE_BIN with a counter script, drives a 3-item queue, and asserts the
# model was invoked once per turn per unit and that the queue file — the source
# of truth, not the harness's own log line — ends fully checked off.
#
# Usage:  ./smoke_harness.sh [path/to/run_loop.sh]
# Exit 0 if the harness executes correctly, 1 otherwise. No network, no API key.

set -uo pipefail

HARNESS="${1:-$(cd "$(dirname "$0")" && pwd)/run_loop.sh}"
[[ -f "$HARNESS" ]] || { echo "  FAIL  no harness at $HARNESS"; exit 1; }
HARNESS="$(cd "$(dirname "$HARNESS")" && pwd)/$(basename "$HARNESS")"

command -v git >/dev/null 2>&1 || { echo "  SKIP  git not installed"; exit 0; }

pass=0
fail=0
ok()  { echo "  PASS  $1"; pass=$((pass + 1)); }
bad() { echo "  FAIL  $1"; fail=$((fail + 1)); }
check() { [[ "$2" == "$3" ]] && ok "$1" || bad "$1 (expected '$3', got '$2')"; }

# Explicit XXXXXX template: BSD and GNU mktemp disagree about bare -t.
SB="$(mktemp -d "${TMPDIR:-/tmp}/loopsmoke.XXXXXX")"
[[ -n "${SB:-}" && -d "$SB" ]] || { echo "  FAIL  could not create temp dir"; exit 1; }
trap 'rm -rf "$SB"' EXIT

# A throwaway repo the harness can branch and commit in.
setup_repo() {
  local verdict="$1"
  rm -rf "$SB/repo"
  mkdir -p "$SB/repo"
  cd "$SB/repo" || exit 1
  git init -q .
  git config user.email loop@test.local
  git config user.name "loop smoke"

  printf '%s\n' '- [ ] unit one' '- [ ] unit two' '- [ ] unit three' > LOOP_QUEUE.md
  echo "builder: do the thing, show evidence" > builder-prompt.md
  echo "verifier: close is FAIL, print VERDICT: PASS or VERDICT: FAIL" > verifier-prompt.md
  git add -A && git commit -qm "baseline"

  # The stub: one line appended per invocation, then a fixed verdict. It reads
  # nothing from stdin, exactly like `claude -p` does not need to — but the real
  # binary DRAINS stdin, which is why the harness must not be fed from a live
  # `while read` over the queue.
  cat > stub_claude.sh <<EOF
#!/usr/bin/env bash
printf 'CALL %s\n' "\$(printf '%s ' "\$@" | tr '\n' ' ')" >> "$SB/calls.txt"
echo "VERDICT: $verdict"
EOF
  chmod +x stub_claude.sh

  cat > loop.config.sh <<EOF
CLAUDE_BIN="$SB/repo/stub_claude.sh"
QUEUE_FILE="LOOP_QUEUE.md"
BUILDER_PROMPT_FILE="builder-prompt.md"
VERIFIER_PROMPT_FILE="verifier-prompt.md"
WORK_BRANCH="loop/smoke"
MAX_ITERATIONS=25
FAIL_THRESHOLD=3
EOF
  : > "$SB/calls.txt"
}

# grep -c already prints 0 on no-match; `|| true` only swallows its exit status.
count_calls()  { grep -c '^CALL ' "$SB/calls.txt" 2>/dev/null || true; }
count_open()   { grep -c '^- \[ \] ' "$SB/repo/LOOP_QUEUE.md" 2>/dev/null || true; }
count_closed() { grep -c '^- \[x\] ' "$SB/repo/LOOP_QUEUE.md" 2>/dev/null || true; }

echo "--- the harness processes EVERY queue unit, not just the first ---"
setup_repo PASS
bash "$HARNESS" loop.config.sh > "$SB/run.log" 2>&1
rc=$?
check "all-PASS run exits 0" "$rc" "0"
# 3 units x (builder + verifier) = 6. A stdin-drained loop stops at 2.
check "model invoked once per turn per unit" "$(count_calls)" "6"
check "every unit marked done in the queue file" "$(count_closed)" "3"
check "no unit left unchecked" "$(count_open)" "0"
# The checkbox prefix must be stripped before the task reaches the model.
check "task text is the unit, not the raw checklist line" \
  "$(grep -c 'TASK: unit two' "$SB/calls.txt" 2>/dev/null || true)" "2"
check "checkbox markup never reaches the prompt" \
  "$(grep -c 'TASK: - \[ \]' "$SB/calls.txt" 2>/dev/null || true)" "0"

echo "--- a FAILing unit escalates instead of killing the run ---"
setup_repo FAIL
bash "$HARNESS" loop.config.sh > "$SB/run.log" 2>&1
rc=$?
[[ "$rc" -ne 0 ]] && ok "all-FAIL run exits nonzero" || bad "all-FAIL run exited 0 — it reported success on a failed queue"
# FAIL_THRESHOLD=3 retries on unit one, each a builder+verifier pair.
check "unit retried up to the FAIL threshold" "$(count_calls)" "6"
[[ -s "$SB/repo/LOOP_ESCALATION.md" ]] && ok "escalation log written for the human" || bad "no escalation log"
check "failed unit is NOT marked done" "$(count_closed)" "0"

echo
echo "  $pass pass · $fail fail"
[[ $fail -eq 0 ]] || exit 1
