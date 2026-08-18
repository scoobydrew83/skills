#!/usr/bin/env python3
"""Read-only deterministic audit for the portable Conductor harness."""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

STATES = {"ORIENTING", "AWAITING_HUMAN", "PENDING", "IN_PROGRESS", "VERIFYING", "BLOCKED_HUMAN", "DONE"}
REQUIRED_POLICY = {"version", "max_parallel_items", "max_consecutive_failures", "autonomous_actions", "human_gates", "evidence"}

def check(ok, label, detail, checks):
    checks.append({"ok": ok, "label": label, "detail": detail})

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", nargs="?", default=".")
    parser.add_argument("--library-root", help="optional skills-library root for alias/package checks")
    args = parser.parse_args()
    root = Path(args.repo).resolve()
    checks = []
    for name in ("AGENTS.md", "CONTEXT.md", "MEMORY_BANK.md", "LOOP_QUEUE.md", "FEATURES.json"):
        check((root / name).is_file(), name, "present" if (root / name).is_file() else "missing", checks)
    policy_path = root / ".harness" / "loop-policy.json"
    policy = None
    try:
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        check(REQUIRED_POLICY <= policy.keys(), "loop policy", "valid required keys" if REQUIRED_POLICY <= policy.keys() else "missing required keys", checks)
        check(policy.get("max_consecutive_failures") == 3, "retry ceiling", "three failures require human escalation", checks)
    except (OSError, json.JSONDecodeError):
        check(False, "loop policy", "missing or invalid .harness/loop-policy.json", checks)
    features_path = root / "FEATURES.json"
    try:
        features = json.loads(features_path.read_text(encoding="utf-8"))
        entries = features.get("features", [])
        check(bool(entries), "acceptance criteria", "non-empty" if entries else "no feature criteria", checks)
        no_evidence_pass = [x.get("id", "?") for x in entries if x.get("passes") is True and not x.get("evidence")]
        check(not no_evidence_pass, "pass evidence", "all passing criteria have evidence" if not no_evidence_pass else "missing evidence: " + ", ".join(no_evidence_pass), checks)
    except (OSError, json.JSONDecodeError):
        check(False, "acceptance criteria", "missing or invalid FEATURES.json", checks)
    queue_path = root / "LOOP_QUEUE.md"
    done_ids = []
    gated_ids = []
    if queue_path.exists():
        unknown = []
        for line in queue_path.read_text(encoding="utf-8").splitlines():
            match = re.search(r"\b([A-Z_]+)\b\s*[:|\-]", line)
            if match and match.group(1) not in STATES:
                unknown.append(match.group(1))
            done = re.match(r"^- \[[xX]\] DONE \| ([^|]+) \|", line)
            if done:
                done_ids.append(done.group(1).strip())
            gated = re.match(r"^- \[ \] (?:AWAITING_HUMAN|BLOCKED_HUMAN) \| ([^|]+) \|", line)
            if gated:
                gated_ids.append(gated.group(1).strip())
        check(not unknown, "queue states", "valid" if not unknown else "unknown: " + ", ".join(sorted(set(unknown)),), checks)
        check(not gated_ids, "queue gate", "no human decision pending" if not gated_ids else "Decision needed for: " + ", ".join(gated_ids), checks)
    evidence = root / ".harness" / "EVIDENCE.jsonl"
    if evidence.exists():
        bad = []
        for number, line in enumerate(evidence.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip(): continue
            try:
                row = json.loads(line)
                if not {"run_id", "item_id", "phase", "actor", "checks", "verdict", "next"} <= row.keys(): bad.append(str(number))
            except json.JSONDecodeError: bad.append(str(number))
        check(not bad, "evidence ledger", "valid JSONL" if not bad else "invalid rows: " + ", ".join(bad), checks)
        if not bad:
            rows = [json.loads(line) for line in evidence.read_text(encoding="utf-8").splitlines() if line.strip()]
            unproven = [item for item in done_ids if not any(row.get("item_id") == item and row.get("verdict") == "PASS" and row.get("checks") for row in rows)]
            check(not unproven, "done-item evidence", "all DONE items have reproducible PASS evidence" if not unproven else "missing PASS evidence: " + ", ".join(unproven), checks)
    else:
        check(True, "evidence ledger", "not yet created; required before a PASS run", checks)
    if args.library_root:
        library = Path(args.library_root).resolve()
        check((library / "AGENTS.md").is_file(), "library AGENTS.md", "present" if (library / "AGENTS.md").is_file() else "missing", checks)
        aliases_ok = all((library / alias).is_symlink() and (library / alias).readlink() == Path("AGENTS.md") for alias in ("CLAUDE.md", "GEMINI.md"))
        check(aliases_ok, "library instruction aliases", "both aliases point at AGENTS.md" if aliases_ok else "CLAUDE.md/GEMINI.md must alias AGENTS.md", checks)
        sync = library / "tools" / "sync-agent-layout.sh"
        if sync.is_file():
            result = subprocess.run(["bash", str(sync), "--check"], cwd=library, text=True, capture_output=True)
            check(result.returncode == 0, "library generated package", "matches canonical source" if result.returncode == 0 else result.stdout.strip() or result.stderr.strip(), checks)
        else:
            check(False, "library generated package", "missing tools/sync-agent-layout.sh", checks)
    failed = [c for c in checks if not c["ok"]]
    verdict = "PASS" if not failed else ("BLOCKED" if any(c["label"] in {"loop policy", "acceptance criteria", "LOOP_QUEUE.md", "queue gate"} for c in failed) else "FAIL")
    result = {"verdict": verdict, "root": str(root), "checks": checks,
              "next": "Run conductor-router on the top PENDING item" if verdict == "PASS" else "Repair the first failed check, then rerun conductor-doctor"}
    print(json.dumps(result, indent=2))
    return 0 if verdict == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())
