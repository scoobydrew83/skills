#!/usr/bin/env python3
"""Persist one legal Conductor queue transition and its redacted evidence."""
import argparse
import datetime as dt
import json
import re
import sys
import uuid
from pathlib import Path

LEGAL = {
    "ORIENTING": {"PENDING", "AWAITING_HUMAN"},
    "PENDING": {"IN_PROGRESS"},
    "IN_PROGRESS": {"VERIFYING"},
    "VERIFYING": {"DONE", "IN_PROGRESS", "BLOCKED_HUMAN"},
    "AWAITING_HUMAN": {"PENDING"},
    "BLOCKED_HUMAN": {"PENDING"},
    "DONE": set(),
}
QUEUE_RE = re.compile(r"^(?P<prefix>- \[[ xX]\] )(?P<state>[A-Z_]+) \| (?P<id>[^|]+) \| (?P<summary>.+)$")

def fail(message: str) -> int:
    print(f"FAIL {message}", file=sys.stderr)
    return 1

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo")
    parser.add_argument("item_id")
    parser.add_argument("to_state", choices=LEGAL)
    parser.add_argument("--human-decision", help="recorded human decision required to leave a gate")
    parser.add_argument("--feature-id", help="criterion verified when transitioning to DONE")
    parser.add_argument("--check", action="append", default=[], metavar="COMMAND|EXPECTED|ACTUAL")
    parser.add_argument("--actor", default="conductor-router")
    args = parser.parse_args()
    root = Path(args.repo).resolve()
    queue_path = root / "LOOP_QUEUE.md"
    policy_path = root / ".harness" / "loop-policy.json"
    evidence_path = root / ".harness" / "EVIDENCE.jsonl"
    features_path = root / "FEATURES.json"
    try:
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        if policy.get("max_consecutive_failures") != 3:
            return fail("invalid loop policy")
    except (OSError, json.JSONDecodeError):
        return fail("missing or invalid loop policy")
    try:
        lines = queue_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return fail("missing LOOP_QUEUE.md")
    selected = None
    for index, line in enumerate(lines):
        match = QUEUE_RE.match(line)
        if match and match.group("id").strip() == args.item_id:
            selected = (index, match)
            break
    if not selected:
        return fail(f"queue item not found: {args.item_id}")
    index, match = selected
    current = match.group("state")
    if args.to_state not in LEGAL.get(current, set()):
        return fail(f"illegal transition: {current} -> {args.to_state}")
    if current in {"AWAITING_HUMAN", "BLOCKED_HUMAN"} and not args.human_decision:
        return fail("Decision needed: a recorded human decision is required")
    if args.to_state == "DONE" and not args.check:
        return fail("verification evidence is required before DONE")
    checks = []
    for raw in args.check:
        parts = raw.split("|", 2)
        if len(parts) != 3:
            return fail("--check must be COMMAND|EXPECTED|ACTUAL")
        checks.append({"command": parts[0], "expected": parts[1], "actual": parts[2]})
    evidence_ref = None
    if args.to_state == "DONE":
        if not args.feature_id:
            return fail("--feature-id is required before DONE")
        try:
            features = json.loads(features_path.read_text(encoding="utf-8"))
            feature = next(item for item in features.get("features", []) if item.get("id") == args.feature_id)
        except (OSError, json.JSONDecodeError, StopIteration):
            return fail("verified feature is missing from FEATURES.json")
        existing_rows = evidence_path.read_text(encoding="utf-8").splitlines() if evidence_path.exists() else []
        evidence_ref = f"EVIDENCE.jsonl:{len(existing_rows) + 1}"
        feature["passes"] = True
        feature["evidence"] = evidence_ref
        features_path.write_text(json.dumps(features, indent=2) + "\n", encoding="utf-8")
    prefix = "- [x] " if args.to_state == "DONE" else "- [ ] "
    lines[index] = f"{prefix}{args.to_state} | {args.item_id} | {match.group('summary')}"
    queue_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "run_id": str(uuid.uuid4()), "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
        "item_id": args.item_id, "phase": args.to_state.lower(), "actor": args.actor,
        "checks": checks, "verdict": "PASS" if args.to_state == "DONE" else args.to_state,
        "gate": "human_decision" if args.human_decision else "none",
        "decision": args.human_decision, "feature_id": args.feature_id,
        "next": "No action" if args.to_state == "DONE" else f"Advance {args.item_id} from {args.to_state}",
    }
    with evidence_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, separators=(",", ":")) + "\n")
    print(json.dumps({"ok": True, "from": current, "to": args.to_state, "item_id": args.item_id, "evidence": evidence_ref}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
