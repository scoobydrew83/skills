#!/usr/bin/env python3
"""Validate the portable Conductor loop-policy contract without dependencies."""
import json
import sys
from pathlib import Path

REQUIRED = {"version", "max_parallel_items", "max_consecutive_failures", "autonomous_actions", "human_gates", "evidence"}
GATES = {"scope_or_acceptance_change", "consequential_assumption", "secrets_or_spending", "external_communication", "destructive_action", "deployment_or_permission_expansion", "merge_or_release", "third_consecutive_failure"}

def main() -> int:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else ".harness/loop-policy.json")
    try: data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"FAIL policy unreadable: {error}"); return 1
    missing = REQUIRED - data.keys()
    errors = []
    if missing: errors.append("missing keys: " + ", ".join(sorted(missing)))
    if data.get("version") != 1: errors.append("version must be 1")
    if not isinstance(data.get("max_parallel_items"), int) or data.get("max_parallel_items", 0) < 1: errors.append("max_parallel_items must be a positive integer")
    if data.get("max_consecutive_failures") != 3: errors.append("max_consecutive_failures must be 3")
    if not GATES <= set(data.get("human_gates", [])): errors.append("human_gates must include all mandatory gates")
    if data.get("evidence", {}).get("require_for_pass") is not True: errors.append("evidence.require_for_pass must be true")
    if data.get("evidence", {}).get("redact_raw_prompts") is not True: errors.append("evidence.redact_raw_prompts must be true")
    if errors:
        for error in errors: print("FAIL " + error)
        return 1
    print("PASS loop policy is valid")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
