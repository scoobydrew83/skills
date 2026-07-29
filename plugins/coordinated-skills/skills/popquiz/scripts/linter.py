#!/usr/bin/env python3
"""popquiz linter — no APPROVE without a completed quiz.

Exit 0 = PASS, 1 = FAIL, 2 = usage error.
"""
import re
import sys

REQUIRED_SECTIONS = [
    "## One-Sentence Summary",
    "## Riskiest Line",
    "## Blast Radius",
    "## Quiz",
    "## Verdict",
]

RUBBER_STAMPS = ["lgtm", "looks good to me", "seems fine", "trust the tests", "nothing risky here"]
FILE_LINE_RE = re.compile(r"\S+\.\w+:\d+")
Q_RE = re.compile(r"^Q\d+:\s*(\S.*)$", re.MULTILINE)
A_RE = re.compile(r"^A\d+:\s*(.*)$", re.MULTILINE)
VERDICT_RE = re.compile(r"^\s*(APPROVE|EXPLAIN-FIRST|REJECT)\b", re.MULTILINE)


def section(text: str, header: str) -> str:
    m = re.search(re.escape(header) + r"\s*\n(.*?)(?=\n## |\Z)", text, re.DOTALL)
    return m.group(1) if m else ""


def lint(text: str) -> list[str]:
    v: list[str] = []
    low = text.lower()

    for h in REQUIRED_SECTIONS:
        if h not in text:
            v.append(f"MISSING SECTION: {h}")

    for s in RUBBER_STAMPS:
        if s in low:
            v.append(f"RUBBER STAMP: '{s}' — do the review, don't wave at it")

    rl = section(text, "## Riskiest Line")
    if "## Riskiest Line" in text and not FILE_LINE_RE.search(rl):
        v.append("RISKIEST LINE UNCITED: needs a file:line reference")

    quiz = section(text, "## Quiz")
    questions = Q_RE.findall(quiz)
    answers = [a.strip() for a in A_RE.findall(quiz)]
    real_answers = [a for a in answers if len(a) >= 10]

    if "## Quiz" in text and len(questions) < 3:
        v.append(f"QUIZ TOO SHORT: {len(questions)} question(s), need >=3")
    if len(real_answers) < len(questions):
        v.append(
            f"UNANSWERED/HOLLOW QUESTIONS: {len(questions)} Q vs {len(real_answers)} real A "
            "(answers must be present and substantive)"
        )

    vd = section(text, "## Verdict")
    m = VERDICT_RE.search(vd)
    if "## Verdict" in text and not m:
        v.append("INVALID VERDICT: must be APPROVE, EXPLAIN-FIRST, or REJECT")
    if m and m.group(1) == "APPROVE":
        if len(questions) < 3 or len(real_answers) < len(questions) or len(questions) == 0:
            v.append("APPROVE WITHOUT COMPLETED QUIZ: understanding is a merge requirement")

    return v


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: linter.py <review.md>", file=sys.stderr)
        return 2
    try:
        text = open(sys.argv[1], encoding="utf-8").read()
    except OSError as e:
        print(f"cannot read file: {e}", file=sys.stderr)
        return 2
    violations = lint(text)
    if violations:
        print(f"FAIL — {len(violations)} violation(s):")
        for x in violations:
            print(f"  - {x}")
        return 1
    print("PASS — merge is understood")
    return 0


if __name__ == "__main__":
    sys.exit(main())
