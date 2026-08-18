#!/usr/bin/env python3
"""
validate_memory.py - Objectively verify a memory pack before integrating it.

Checks that every expected file is present, the machine-readable files parse and
carry their required keys, and that the synthesized files were actually filled in
(no leftover TODO placeholders, enough substance to be useful). Prints a checklist
and exits non-zero if anything fails, so it can gate integration in a script.

Usage:
    python validate_memory.py --dir <pack_dir> [--project conductor]
"""

import argparse
import json
import sys
from pathlib import Path

try:
    import yaml  # optional; YAML checks degrade gracefully if absent
    HAVE_YAML = True
except Exception:
    HAVE_YAML = False

MIN_CHARS = 200  # a synthesized file shorter than this is almost certainly a stub


def detect_project(pack: Path, override):
    if override:
        return override
    for f in pack.glob("*_memory_seed_data.json"):
        return f.name[: -len("_memory_seed_data.json")]
    for f in pack.glob("*_memory_conversation_summary.md"):
        return f.name[: -len("_memory_conversation_summary.md")]
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--project", default=None)
    args = ap.parse_args()

    pack = Path(args.dir).expanduser()
    results = []  # (label, passed, detail)

    def check(label, passed, detail=""):
        results.append((label, bool(passed), detail))

    if not pack.is_dir():
        print(f"FAIL: pack directory not found: {pack}")
        sys.exit(1)

    p = detect_project(pack, args.project)
    if not p:
        print("FAIL: could not detect project name (no *_memory_seed_data.json or summary). Pass --project.")
        sys.exit(1)

    expected = [
        "MEMORY_INDEX.md",
        f"{p}_memory_conversation_summary.md",
        f"{p}_memory_artifacts_index.md",
        f"{p}_memory_communication_style.md",
        f"{p}_memory_project_context.md",
        f"{p}_memory_seed_data.json",
        f"{p}_memory_personality.yaml",
        f"{p}_memory_verification.md",
        f"{p}_memory_maintenance.md",
        "integration.py",
    ]
    for name in expected:
        check(f"file present: {name}", (pack / name).exists())

    # Synthesized prose files: filled in, not stubs.
    prose = [
        "MEMORY_INDEX.md",
        f"{p}_memory_conversation_summary.md",
        f"{p}_memory_artifacts_index.md",
        f"{p}_memory_communication_style.md",
        f"{p}_memory_project_context.md",
    ]
    for name in prose:
        f = pack / name
        if not f.exists():
            continue
        text = f.read_text()
        check(f"substantive: {name}", len(text) >= MIN_CHARS, f"{len(text)} chars")
        check(f"no TODO left: {name}", "_TODO" not in text and "TODO:" not in text)

    # seed_data.json: parses + required keys.
    seed_path = pack / f"{p}_memory_seed_data.json"
    if seed_path.exists():
        try:
            seed = json.loads(seed_path.read_text())
            check("seed_data.json parses", True)
            check("seed has 'conversations' (list)", isinstance(seed.get("conversations"), list) and len(seed["conversations"]) > 0)
            check("seed has 'user_profile'", isinstance(seed.get("user_profile"), dict))
            check("seed has 'project_state'", isinstance(seed.get("project_state"), dict))
            ps = seed.get("project_state", {})
            check("project_state has 'next_tasks'", "next_tasks" in ps)
        except json.JSONDecodeError as e:
            check("seed_data.json parses", False, str(e))

    # personality.yaml: parses + has top-level 'personality'.
    pers_path = pack / f"{p}_memory_personality.yaml"
    if pers_path.exists():
        if HAVE_YAML:
            try:
                pers = yaml.safe_load(pers_path.read_text())
                check("personality.yaml parses", isinstance(pers, dict))
                check("personality.yaml has 'personality'", isinstance(pers, dict) and "personality" in pers)
            except yaml.YAMLError as e:
                check("personality.yaml parses", False, str(e))
        else:
            txt = pers_path.read_text()
            check("personality.yaml has 'personality'", "personality:" in txt, "(pyyaml not installed - text check only)")

    # Report
    width = max(len(l) for l, _, _ in results)
    passed_all = True
    print(f"\nMemory pack validation: {pack.name}\n")
    for label, ok, detail in results:
        mark = "PASS" if ok else "FAIL"
        passed_all = passed_all and ok
        extra = f"  ({detail})" if detail else ""
        print(f"  [{mark}] {label.ljust(width)}{extra}")
    n_pass = sum(1 for _, ok, _ in results if ok)
    print(f"\n{n_pass}/{len(results)} checks passed.")
    if passed_all:
        print("Pack is valid and ready to integrate.")
        sys.exit(0)
    print("Fix the FAIL items above before integrating.")
    sys.exit(1)


if __name__ == "__main__":
    main()
