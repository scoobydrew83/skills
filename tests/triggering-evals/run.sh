#!/usr/bin/env bash
# tests/triggering-evals/run.sh — description-driven triggering eval harness.
#
# For each skill we have a prompts/<skill>.json with should_trigger and
# should_not_trigger arrays. We feed every prompt to a matcher (static keyword
# overlap, or — if ANTHROPIC_API_KEY is set and --mode llm is requested —
# Claude haiku) and record precision/recall per skill against the expected
# label. score.py prints the table and returns the right exit code.
#
# Usage:
#   tests/triggering-evals/run.sh                       # all skills, static
#   tests/triggering-evals/run.sh --skill overwhelm-breakdown
#   tests/triggering-evals/run.sh --mode llm            # needs ANTHROPIC_API_KEY
#   tests/triggering-evals/run.sh --help
#
# Env vars:
#   ANTHROPIC_API_KEY        required for --mode llm
#   TRIGGER_RECALL_MIN       default 0.8
#   TRIGGER_PRECISION_MIN    default 0.8
#   STATIC_MATCH_MIN         default 0.05 (static-mode trigger threshold)
#   TRIGGER_LLM_MODEL        default claude-haiku-4-5
#
# Exit codes:
#   0   every skill meets recall/precision thresholds
#   1   at least one skill below threshold
#   2   harness error (missing inputs, malformed JSON, etc.)

set -uo pipefail

usage() {
  sed -n '2,28p' "$0" | sed 's/^# \{0,1\}//'
}

MODE="static"
SKILL=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h) usage; exit 0 ;;
    --mode)    MODE="${2:-}"; shift 2 ;;
    --mode=*)  MODE="${1#--mode=}"; shift ;;
    --skill)   SKILL="${2:-}"; shift 2 ;;
    --skill=*) SKILL="${1#--skill=}"; shift ;;
    *) echo "run.sh: unknown arg: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ "$MODE" != "static" && "$MODE" != "llm" ]]; then
  echo "run.sh: --mode must be 'static' or 'llm' (got '$MODE')" >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SKILLS_DIR="$REPO_ROOT/plugins/coordinated-skills/skills"
PROMPTS_DIR="$SCRIPT_DIR/prompts"
RESULTS_DIR="$SCRIPT_DIR/.results"

if ! command -v python3 >/dev/null 2>&1; then
  echo "run.sh: python3 not on PATH" >&2
  exit 2
fi

if [[ ! -d "$PROMPTS_DIR" ]]; then
  echo "run.sh: missing prompts dir at $PROMPTS_DIR" >&2
  exit 2
fi

# Warn (don't fail) on skills that have no prompt file yet.
shopt -s nullglob
missing=()
for skill_dir in "$SKILLS_DIR"/*/; do
  name="$(basename "$skill_dir")"
  [[ -f "$skill_dir/SKILL.md" ]] || continue
  case "$name" in
    adaptive-communication|task-decomposition) continue ;;  # tombstones
  esac
  [[ -f "$PROMPTS_DIR/$name.json" ]] || missing+=("$name")
done
if [[ ${#missing[@]} -gt 0 ]]; then
  echo "run.sh: note — no prompt file for: ${missing[*]}" >&2
fi

mkdir -p "$RESULTS_DIR"
ts="$(date +%Y%m%d-%H%M%S)"
out_json="$RESULTS_DIR/results-${MODE}-${ts}.json"

echo "==> running triggering eval (mode=$MODE${SKILL:+, skill=$SKILL})"
echo "    prompts dir : $PROMPTS_DIR"
echo "    skills root : $SKILLS_DIR"
echo "    results out : $out_json"
echo

match_args=(--mode "$MODE" --prompts-dir "$PROMPTS_DIR" --skills-root "$SKILLS_DIR" --out "$out_json")
[[ -n "$SKILL" ]] && match_args+=(--skill "$SKILL")

if ! python3 "$SCRIPT_DIR/_match.py" "${match_args[@]}"; then
  echo "run.sh: matcher failed" >&2
  exit 2
fi

python3 "$SCRIPT_DIR/score.py" "$out_json"
rc=$?

echo
echo "results JSON: $out_json"
exit $rc
