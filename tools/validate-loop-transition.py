#!/usr/bin/env python3
"""Validate one proposed Conductor state transition without mutating state."""
import argparse
import json

LEGAL = {
    "ORIENTING": {"PENDING", "AWAITING_HUMAN"},
    "PENDING": {"IN_PROGRESS"},
    "IN_PROGRESS": {"VERIFYING"},
    "VERIFYING": {"DONE", "IN_PROGRESS", "BLOCKED_HUMAN"},
    "AWAITING_HUMAN": {"PENDING"},
    "BLOCKED_HUMAN": {"PENDING"},
    "DONE": set(),
}

parser = argparse.ArgumentParser()
parser.add_argument("from_state", choices=LEGAL)
parser.add_argument("to_state", choices=LEGAL)
parser.add_argument("--human-decision", action="store_true")
parser.add_argument("--consecutive-failures", type=int, default=0)
args = parser.parse_args()

ok, reason = args.to_state in LEGAL[args.from_state], "transition is not allowed"
if ok and args.from_state in {"AWAITING_HUMAN", "BLOCKED_HUMAN"} and not args.human_decision:
    ok, reason = False, "human decision is required before leaving a human gate"
if ok and args.consecutive_failures >= 3 and args.to_state != "BLOCKED_HUMAN":
    ok, reason = False, "third consecutive failure must transition to BLOCKED_HUMAN"
if ok:
    reason = "legal transition"
print(json.dumps({"ok": ok, "from": args.from_state, "to": args.to_state, "reason": reason}))
raise SystemExit(0 if ok else 1)
