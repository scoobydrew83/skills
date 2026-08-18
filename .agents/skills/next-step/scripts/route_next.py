#!/usr/bin/env python3
"""Read-only queue router used by next-step and conductor-router."""
import json
import re
import sys
from pathlib import Path

STATES = ("ORIENTING", "AWAITING_HUMAN", "PENDING", "IN_PROGRESS", "VERIFYING", "BLOCKED_HUMAN", "DONE")
NEXT = {
    "ORIENTING": "AWAITING_HUMAN or PENDING",
    "AWAITING_HUMAN": "Decision needed",
    "PENDING": "IN_PROGRESS",
    "IN_PROGRESS": "VERIFYING",
    "VERIFYING": "DONE or IN_PROGRESS",
    "BLOCKED_HUMAN": "Decision needed",
    "DONE": "No action"
}

def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    queue = root / "LOOP_QUEUE.md"
    policy = root / ".harness" / "loop-policy.json"
    result = {"root": str(root), "status": "BLOCKED", "next": "Decision needed: initialize LOOP_QUEUE.md", "item": None}
    if not queue.exists():
        print(json.dumps(result, indent=2)); return 0
    text = queue.read_text(encoding="utf-8")
    match = re.search(r"(?:- \[[ xX]\] )?(?:\[)?(" + "|".join(STATES) + r")(?:\])?\s*[:|\-]\s*(.+)", text)
    if not match:
        result["next"] = "Decision needed: add one queue item with a valid state"
        print(json.dumps(result, indent=2)); return 0
    state, item = match.groups()
    result.update({"item": item.strip(), "state": state, "status": "READY" if state in ("PENDING", "IN_PROGRESS", "VERIFYING") else "BLOCKED", "next": NEXT[state]})
    if state in ("AWAITING_HUMAN", "BLOCKED_HUMAN"):
        result["next"] = "Decision needed: record the human decision, then move this item to PENDING"
    if policy.exists():
        try: result["policy_version"] = json.loads(policy.read_text())["version"]
        except (ValueError, KeyError): result["status"] = "BLOCKED"; result["next"] = "Decision needed: repair .harness/loop-policy.json"
    print(json.dumps(result, indent=2)); return 0

if __name__ == "__main__":
    raise SystemExit(main())
