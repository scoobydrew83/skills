#!/usr/bin/env python3
"""
sequence_linter.py — checks a de-risk sequence table for the ordering discipline:
every build step must be unlocked by a prior test, success-problems (governance/
breadth/optimization) must not precede their gate, and every step needs a kill-if.

Expects a markdown table with columns: # | Step | Type | Unlocked-by | Kill-if
stdlib-only. Usage: python sequence_linter.py <sequence.md>
Exit 0 = clean, 1 = at least one violation.
"""
import re
import sys

DEFER_WORDS = ["governance", "protocol", "conformance", "foundation", "multi-platform",
               "multi-language", "breadth", "optimize", "optimization", "performance",
               "scale", "scaling"]

def parse_rows(text):
    rows = []
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 5:
            continue
        if cells[0].lower() in ("#", "") or set(cells[0]) <= set("-: "):
            continue
        if not re.match(r"^\d+", cells[0]):
            continue
        rows.append({
            "num": cells[0], "step": cells[1], "type": cells[2].lower(),
            "unlocked": cells[3], "kill": cells[4],
        })
    return rows

def check(rows):
    issues = []
    seen_tests = set()
    pmv_gate_passed = False  # once any test mentions pmv/demand/validation milestone

    for r in rows:
        num = r["num"]
        if r["type"] == "test":
            seen_tests.add(num)
            if re.search(r"pmv|product-market|demand|differentiat|incumbent", r["step"], re.I):
                pmv_gate_passed = True

        # 1. build steps must reference a prior test in unlocked-by
        if r["type"] == "build":
            ref = re.findall(r"\d+", r["unlocked"])
            if not ref:
                issues.append(f"step {num}: BUILD with no unlocking test (unlocked-by is '{r['unlocked'] or 'empty'}') — building on an unchecked assumption")
            else:
                if not any(x in seen_tests for x in ref):
                    issues.append(f"step {num}: BUILD unlocked by step(s) {ref} that are not prior tests — test must come first")

        # 2. success-problems must be deferred, not early
        if any(w in r["step"].lower() for w in DEFER_WORDS):
            if r["type"] != "defer":
                issues.append(f"step {num}: '{r['step'][:40]}' looks like a success-problem (governance/breadth/optimization) but isn't typed 'defer' — schedule it behind its gate")

        # 3. every step needs a kill-if (or an explicit em-dash for un-killable defers)
        if not r["kill"] or r["kill"] in ("", " "):
            issues.append(f"step {num}: no kill-if condition")

    return issues

def main():
    if len(sys.argv) != 2:
        print("usage: python sequence_linter.py <sequence.md>")
        sys.exit(2)
    text = open(sys.argv[1], encoding="utf-8").read()
    rows = parse_rows(text)
    print(f"\nDe-risk sequence check — {sys.argv[1]}\n" + "-" * 48)
    if not rows:
        print("[FAIL] no sequence table found (expected | # | Step | Type | Unlocked-by | Kill-if |)")
        sys.exit(1)
    print(f"parsed {len(rows)} step(s)")
    issues = check(rows)
    if not issues:
        print("[PASS] sequence is risk-ordered: no build precedes its test, success-problems deferred")
        print("-" * 48 + "\nALL CHECKS PASSED\n")
        sys.exit(0)
    for i in issues:
        print(f"[FAIL] {i}")
    print("-" * 48 + f"\n{len(issues)} VIOLATION(S)\n")
    sys.exit(1)

if __name__ == "__main__":
    main()
