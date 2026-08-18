#!/usr/bin/env python3
"""Validate provider-neutral outcome-evaluation fixtures; never calls a model."""
import json
import sys
from pathlib import Path

root = Path(sys.argv[1] if len(sys.argv) > 1 else "tests/outcome-evals/fixtures")
bad = []
for path in sorted(root.glob("*.json")):
    try:
        row = json.loads(path.read_text())
        if not {"id", "input", "expected"} <= row.keys(): bad.append(path.name)
    except (OSError, json.JSONDecodeError): bad.append(path.name)
if bad:
    print("FAIL invalid outcome fixtures: " + ", ".join(bad)); raise SystemExit(1)
print(f"PASS outcome fixtures valid ({len(list(root.glob('*.json')))})")
