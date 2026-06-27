#!/usr/bin/env bash
#
# run_loop.sh — generic builder/verifier loop harness.
#
# Drives: builder turn -> verifier turn -> (PASS: commit & advance | FAIL: feed back & retry),
# with a hard iteration ceiling and human escalation after N consecutive FAILs.
#
# This harness carries all state between turns (queue, counters, feedback). Each model turn is a
# fresh, non-interactive `claude -p` invocation — the builder and verifier are deliberately
# separate contexts so the verifier is a real second opinion, not the actor grading itself.
#
# Usage:
#   ./run_loop.sh path/to/loop.config.sh
#
# The config file defines the variables documented in loop.config.sh.template. Anything not set
# falls back to the Conductor defaults below.

set -euo pipefail

CONFIG="${1:?Usage: run_loop.sh <loop.config.sh>}"
# shellcheck source=/dev/null
source "$CONFIG"

# ---- Conductor defaults (overridable in the config) ------------------------------------------
: "${MAX_ITERATIONS:=25}"          # hard ceiling on total builder turns across the whole run
: "${FAIL_THRESHOLD:=3}"           # consecutive FAILs on one unit before escalating to a human
: "${WORK_BRANCH:=loop/work}"      # loops never touch the default branch directly
: "${QUEUE_FILE:=LOOP_QUEUE.md}"   # source of truth for queue-driven loops
: "${ESCALATION_LOG:=LOOP_ESCALATION.md}"
: "${COMMIT_ON_PASS:=true}"
: "${CLAUDE_BIN:=claude}"          # override (e.g. a mock) for testing
: "${BUILDER_PROMPT_FILE:=builder-prompt.md}"
: "${VERIFIER_PROMPT_FILE:=verifier-prompt.md}"
: "${ACCEPTANCE_COMMAND:=}"        # optional: a command that must exit 0 (ground-truth gate)

# SINGLE_TASK mode (Shape 1/2) vs queue mode (Shape 3). If TASK is set, run one unit.
: "${TASK:=}"

log() { printf '[loop] %s\n' "$*" >&2; }

escalate() {
  local unit="$1" reason="$2"
  {
    echo "## Escalation $(date -u +%FT%TZ)"
    echo "- Unit: $unit"
    echo "- Reason: $reason"
    echo "- Consecutive FAILs: $FAIL_THRESHOLD"
    echo "- Last verifier feedback:"
    echo '```'
    cat "$FEEDBACK_FILE" 2>/dev/null || echo "(none)"
    echo '```'
    echo
  } >> "$ESCALATION_LOG"
  log "ESCALATED unit '$unit' -> $ESCALATION_LOG. Halting this unit for human review."
}

run_claude() {
  # $1 = prompt file, $2 = extra context appended to the prompt
  local prompt_file="$1" ctx="${2:-}"
  local prompt; prompt="$(cat "$prompt_file")"
  if [[ -n "$ctx" ]]; then prompt="$prompt"$'\n\n'"$ctx"; fi
  "$CLAUDE_BIN" -p "$prompt" --output-format stream-json
}

# Verifier contract: it MUST print a line matching exactly 'VERDICT: PASS' or 'VERDICT: FAIL'.
# "Close is FAIL" — anything that isn't a clean PASS is treated as FAIL.
parse_verdict() {
  if grep -qE '^VERDICT:[[:space:]]*PASS[[:space:]]*$' "$1"; then echo PASS; else echo FAIL; fi
}

process_unit() {
  local unit="$1"
  local fails=0
  FEEDBACK_FILE="$(mktemp)"
  : > "$FEEDBACK_FILE"

  while (( fails < FAIL_THRESHOLD )); do
    (( TOTAL_ITERS++ )) || true
    if (( TOTAL_ITERS > MAX_ITERATIONS )); then
      log "Max iterations ($MAX_ITERATIONS) reached. Stopping run."
      escalate "$unit" "max-iterations ceiling reached"
      return 2
    fi

    log "Unit '$unit' — builder turn (iteration $TOTAL_ITERS, fails $fails)"
    local build_ctx="TASK: $unit"
    if [[ -s "$FEEDBACK_FILE" ]]; then
      build_ctx+=$'\n\nPREVIOUS VERIFIER FEEDBACK (address all of it):\n'"$(cat "$FEEDBACK_FILE")"
    fi
    run_claude "$BUILDER_PROMPT_FILE" "$build_ctx" || { log "builder turn failed to execute"; (( fails++ )); continue; }

    # Optional ground-truth gate: a real command that must pass before the verifier even looks.
    if [[ -n "$ACCEPTANCE_COMMAND" ]]; then
      log "Running acceptance command: $ACCEPTANCE_COMMAND"
      if ! eval "$ACCEPTANCE_COMMAND" > "$FEEDBACK_FILE" 2>&1; then
        log "Acceptance command failed -> FAIL"
        (( fails++ )); continue
      fi
    fi

    log "Unit '$unit' — verifier turn"
    local vout; vout="$(mktemp)"
    run_claude "$VERIFIER_PROMPT_FILE" "TASK: $unit"$'\n\nReview the latest changes (git diff) and the builder evidence against the acceptance criteria.' > "$vout" || true

    local verdict; verdict="$(parse_verdict "$vout")"
    if [[ "$verdict" == PASS ]]; then
      log "Unit '$unit' — VERDICT: PASS"
      if [[ "$COMMIT_ON_PASS" == true ]]; then
        git add -A
        git commit -m "loop: $unit" -m "$(sed -n '1,40p' "$vout")" || log "nothing to commit"
      fi
      rm -f "$vout" "$FEEDBACK_FILE"
      return 0
    fi

    log "Unit '$unit' — VERDICT: FAIL"
    cp "$vout" "$FEEDBACK_FILE"
    rm -f "$vout"
    (( fails++ ))
  done

  escalate "$unit" "$FAIL_THRESHOLD consecutive FAILs"
  return 1
}

# ---- main ------------------------------------------------------------------------------------
TOTAL_ITERS=0

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { log "not a git repo; refusing to run"; exit 1; }
git checkout -B "$WORK_BRANCH"
log "Working on branch '$WORK_BRANCH'. This loop will NOT merge to the default branch."

if [[ -n "$TASK" ]]; then
  process_unit "$TASK" || true
  log "Single-task run complete. Review branch '$WORK_BRANCH' and open a PR if satisfied."
  exit 0
fi

# Queue mode: process unchecked '- [ ]' items from the queue, top to bottom.
[[ -f "$QUEUE_FILE" ]] || { log "no $QUEUE_FILE and no TASK set; nothing to do"; exit 1; }
while IFS= read -r line; do
  case "$line" in
    "- [ ] "*)
      unit="${line#- [ ] }"
      if process_unit "$unit"; then
        # mark done
        sed -i "s|- \[ \] ${unit//|/\\|}|- [x] ${unit//|/\\|}|" "$QUEUE_FILE"
        git add "$QUEUE_FILE" && git commit -m "loop: mark done — $unit" || true
      else
        log "Stopping queue: unit '$unit' escalated. Resolve it before resuming."
        break
      fi
      ;;
  esac
done < "$QUEUE_FILE"

log "Queue run complete. Review branch '$WORK_BRANCH' and open a PR for human approval."
