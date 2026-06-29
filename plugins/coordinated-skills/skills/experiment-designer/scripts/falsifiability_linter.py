#!/usr/bin/env python3
"""
falsifiability_linter.py — checks a pre-registration for the properties that make
an experiment honest: a fixed numeric/binary threshold, an explicit FAIL/KILL branch,
a stated sample size, an empty Result (proving the bar predates the data), and
criteria that don't rest only on vague verbs.

stdlib-only. Usage: python falsifiability_linter.py <prereg.md>
Exit 0 = all checks pass, 1 = at least one FAIL.
"""
import re
import sys

VAGUE = ["better", "improve", "improves", "improved", "seems", "faster", "good",
         "nicer", "cleaner", "more robust", "works well", "should help"]

def check(text):
    low = text.lower()
    results = []  # (passed, label, detail)

    # 1. Explicit PASS branch
    has_pass = bool(re.search(r"\bpass\s+if\b", low))
    results.append((has_pass, "Has explicit PASS-if rule",
                    "" if has_pass else "no 'PASS if' branch found"))

    # 2. Explicit FAIL/KILL branch — the one most often missing
    has_kill = bool(re.search(r"\b(fail|kill|no-?go)\s*(/|,|\s|if)", low))
    results.append((has_kill, "Has explicit FAIL/KILL rule",
                    "" if has_kill else "no failure branch — an experiment with no way to fail isn't one"))

    # 3. A numeric/quantified threshold somewhere in the decision rule
    has_number = bool(re.search(r"(>=|<=|>|<|=|\b\d+(\.\d+)?\s?(%|x|ms|s|/|of)\b|\bn\s*=\s*\d+)", text))
    results.append((has_number, "Has a numeric/quantified threshold",
                    "" if has_number else "no number in the rule — 'better' is not a threshold"))

    # 4. Sample size / power stated
    has_n = bool(re.search(r"\b(n\s*=\s*\d+|sample size|trials?|seeds?|power|underpowered)\b", low))
    results.append((has_n, "States sample size / power",
                    "" if has_n else "no sample size or power statement"))

    # 5. Result section empty (proves bar predates data) — only enforced if doc is labeled pre-registered
    is_prereg = "pre-registered" in low or "pre-registration" in low or "prereg" in low
    result_empty = True
    m = re.search(r"##\s*result(.*?)(?=\n##|\Z)", text, re.IGNORECASE | re.DOTALL)
    if m:
        body = re.sub(r"[\s\-\u2190←]", "", re.sub(r"←.*", "", m.group(1)))
        # strip the "leave empty" hint line
        body = re.sub(r"leaveempty.*?done", "", body, flags=re.IGNORECASE)
        result_empty = len(body.strip()) == 0
    if is_prereg:
        results.append((result_empty, "Result section still empty (bar predates data)",
                        "" if result_empty else "doc is labeled pre-registration but Result is filled — threshold may be post-hoc"))

    # 6. Decision rule not resting ONLY on vague verbs
    rule = ""
    rm = re.search(r"(pass\s+if.*?)(?=##|\Z)", low, re.DOTALL)
    if rm:
        rule = rm.group(1)
    vague_only = (not has_number) and any(v in rule for v in VAGUE)
    results.append((not vague_only, "Decision rule isn't only vague verbs",
                    "" if not vague_only else "rule leans on vague language with no number"))

    return results

def main():
    if len(sys.argv) != 2:
        print("usage: python falsifiability_linter.py <prereg.md>")
        sys.exit(2)
    text = open(sys.argv[1], encoding="utf-8").read()
    results = check(text)
    failed = 0
    print(f"\nFalsifiability check — {sys.argv[1]}\n" + "-" * 48)
    for passed, label, detail in results:
        mark = "PASS" if passed else "FAIL"
        if not passed:
            failed += 1
        line = f"[{mark}] {label}"
        if detail and not passed:
            line += f"\n        → {detail}"
        print(line)
    print("-" * 48)
    print(f"{'ALL CHECKS PASSED' if failed == 0 else str(failed) + ' CHECK(S) FAILED'}\n")
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()
