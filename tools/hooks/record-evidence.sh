#!/usr/bin/env bash
# SubagentStop hook: persist every conductor-verifier verdict as one row in
# .harness/EVIDENCE.jsonl, so the Learn phase has data to mine.
#
# Wired in .claude/settings.json. Claude Code passes the event as JSON on stdin;
# SubagentStop input carries agent_type, agent_id, agent_transcript_path and
# last_assistant_message (hooks reference, "SubagentStop input").
#
# Row keys follow CONVENTIONS.md §4 and conductor-doctor's ledger check:
# run_id, item_id, phase, actor, checks, verdict, next. Only summaries are
# stored, never raw prompts or source.
#
# Telemetry never blocks work (CONVENTIONS.md "Skill telemetry"): this hook
# always exits 0, even when it cannot parse or write.
set -uo pipefail

input="$(cat)"
root="${CLAUDE_PROJECT_DIR:-$(pwd)}"

HOOK_INPUT="$input" EVIDENCE_ROOT="$root" python3 - <<'PY' || true
import json, os, re, sys, datetime

try:
    event = json.loads(os.environ.get("HOOK_INPUT") or "{}")
except json.JSONDecodeError:
    sys.exit(0)

agent = event.get("agent_type") or ""
if event.get("hook_event_name", "SubagentStop") != "SubagentStop":
    sys.exit(0)
if not agent.split(":")[-1] == "conductor-verifier":
    sys.exit(0)

VERDICT_RE = re.compile(r"^\s*(?:VERDICT|Conductor verdict):\s*(PASS|FAIL|BLOCKED)\b", re.M)

def find_report(text):
    """Return the text from the last VERDICT line onward, or None."""
    if not text:
        return None
    matches = list(VERDICT_RE.finditer(text))
    return text[matches[-1].start():] if matches else None

report = find_report(event.get("last_assistant_message") or "")
if report is None:
    # A subagent that hands back through SubagentHandback leaves only closing
    # text in last_assistant_message; fall back to its own transcript.
    # The transcript is JSONL; collect the text blocks of assistant messages.
    path = event.get("agent_transcript_path") or ""
    texts = []
    try:
        with open(os.path.expanduser(path), encoding="utf-8") as fh:
            for line in fh:
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(entry, dict):
                    continue
                message = entry.get("message") or {}
                # Only the verifier's own words count: a verdict quoted in its
                # prompt or a tool result must never become evidence.
                if entry.get("type") != "assistant" and message.get("role") != "assistant":
                    continue
                content = message.get("content")
                if isinstance(content, str):
                    texts.append(content)
                elif isinstance(content, list):
                    texts.extend(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text")
    except OSError:
        pass
    report = find_report("\n".join(texts))
if report is None:
    sys.exit(0)

def field(name):
    m = re.search(r"^\s*%s:\s*(.+)$" % name, report, re.M)
    return m.group(1).strip()[:200] if m else ""

verdict = VERDICT_RE.search(report).group(1)
criteria = re.findall(r"^\s*-\s*\[(PASS|FAIL)\]\s*(.+)$", report, re.M)
checks = [{"criterion": text.strip()[:200], "result": result} for result, text in criteria[:20]]
tests = field("TESTS")
if tests:
    checks.append({"command": tests})

row = {
    "run_id": "%s:%s" % (event.get("session_id", "unknown"), event.get("agent_id", "unknown")),
    # item_id must match the LOOP_QUEUE.md id that conductor-doctor checks, so
    # prefer the verifier's ITEM line and fall back to PHASE only without one.
    "item_id": (field("ITEM") if field("ITEM").lower() not in ("", "none") else "") or field("PHASE") or "unknown",
    "phase": "verify",
    "actor": agent,
    "checks": checks,
    "verdict": verdict,
    "next": field("NEXT"),
    "recorded_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "source": "tools/hooks/record-evidence.sh",
}

target = os.path.join(os.environ["EVIDENCE_ROOT"], ".harness", "EVIDENCE.jsonl")
try:
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
except OSError:
    pass
PY
exit 0
