#!/usr/bin/env python3
"""
postmortem_linter.py — fails the markers of a vanity retrospective: no evidence
citations, a single blended grade instead of a multi-dimension scorecard, and
missing root-cause / transferable-lessons / what-survives sections.

stdlib-only. Usage: python postmortem_linter.py <postmortem.md>
Exit 0 = clean, 1 = at least one FAIL.
"""
import re
import sys

def check(text):
    low = text.lower()
    results = []

    # 1. Evidence citations: commit-hash-like tokens, PR refs, or doc-dated refs
    hashes = re.findall(r"\b[0-9a-f]{7,40}\b", text)
    # filter out pure-decimal (years etc.) — require at least one a-f letter to look like a hash
    hashes = [h for h in hashes if re.search(r"[a-f]", h)]
    prs = re.findall(r"\b(pr|#)\s?\d+", low)
    cited = len(hashes) + len(prs)
    ok = cited >= 3
    results.append((ok, "Has >=3 evidence citations (commit hashes / PR refs)",
                    "" if ok else f"only {cited} citation-like anchors found — a memory-based retro, not evidence-based"))

    # 2. Scorecard with multiple distinct graded dimensions (a table with >=3 grade rows)
    grade_rows = re.findall(r"\|[^|\n]+\|\s*([A-DF][+\-]?)\s*\|", text)
    multi = len(grade_rows) >= 3
    results.append((multi, "Scorecard grades >=3 dimensions separately",
                    "" if multi else f"found {len(grade_rows)} graded rows — a blended/single grade hides the dimension that killed it"))

    # 3. Required sections
    for name, pats in [
        ("Root cause", [r"root[\s-]?cause"]),
        ("Transferable lessons", [r"transferable lesson", r"lessons (learned|&|and)", r"## .*lessons"]),
        ("What survives", [r"what survives", r"survives", r"salvage"]),
    ]:
        present = any(re.search(p, low) for p in pats)
        results.append((present, f"Has '{name}' section",
                        "" if present else f"missing — {name} is core to a useful post-mortem"))

    # 4. Evidence-not-memory posture stated or implied
    grounded = bool(re.search(r"git (history|log)|not (from )?memory|decision docs|commit", low))
    results.append((grounded, "Grounds itself in evidence, not memory",
                    "" if grounded else "no signal the retro is evidence-grounded"))

    return results

def main():
    if len(sys.argv) != 2:
        print("usage: python postmortem_linter.py <postmortem.md>")
        sys.exit(2)
    text = open(sys.argv[1], encoding="utf-8").read()
    results = check(text)
    failed = 0
    print(f"\nPost-mortem check — {sys.argv[1]}\n" + "-" * 48)
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
