#!/usr/bin/env python3
"""
check_goal.py — lint a candidate Claude Code /goal condition.

A /goal is evaluated by a separate model that ONLY reads the transcript, so the condition has to
be provable by Claude's printed output. This linter checks for the properties Anthropic's docs and
the field reports say make a goal actually terminate correctly.

Usage:
  python3 check_goal.py "<goal condition text>"
  python3 check_goal.py --file goal.txt

Exit 0 if all REQUIRED checks pass, 1 otherwise. Advisory checks never fail the run.
"""
import sys
import re

MAX_LEN = 4000

# Adjectives/states a transcript-reading evaluator can't resolve to yes/no.
VAGUE = [
    "clean", "cleaner", "cleaned up", "production-ready", "production ready", "better", "nicer",
    "nice", "robust", "properly", "proper", "readable", "maintainable", "user-friendly",
    "user friendly", "modern", "elegant", "well-organized", "well organized", "makes sense",
    "looks right", "looks good", "high quality", "high-quality", "polished", "improve readability",
    "feels", "good enough", "tidy", "sensible",
]

# Signals that the condition names something observable / a command whose output prints.
CHECK_SIGNALS = [
    r"exits?\s*0", r"exit\s*code\s*0", r"exits?\s*non-?zero", r"\bpass(es|ed|ing)?\b",
    r"\bfails?\b", r"0\s*errors?", r"0\s*warnings?", r"zero\s*(errors?|warnings?|matches)",
    r"no\s*matches", r"`[^`]+`", r"git\s+status", r"wc\s*-l", r"\bgrep\b", r"\brg\b",
    r"\bnpm\b", r"\bnpx\b", r"\bpytest\b", r"\bcargo\b", r"\bgo\s+test\b", r"\bmake\b",
    r"\bjavac?\b", r"\btsc\b", r"\beslint\b", r"\bbuild\b", r"\bprints?\b", r"\boutputs?\b",
    r"status\s*200", r"\breturns?\b", r"exits?\s*with", r"is\s*empty", r"empty\s*queue",
    r"file\s*count", r"==", r"\bcoverage\b", r"\bbenchmark\b",
]

CONSTRAINT_SIGNALS = [
    r"\bwithout\b", r"\bdo not\b", r"\bdon't\b", r"\bmust not\b", r"\bno other\b",
    r"\bnot? (modify|change|edit|touch)\b", r"no test is", r"\bnever\b", r"\bonly\b",
    r"without hardcoding", r"without (modifying|editing|touching|deleting)",
]

CAP_SIGNALS = [
    r"stop after\s*\d+\s*turn", r"after\s*\d+\s*turns?", r"within\s*\d+\s*(min|minute|second|sec)",
    r"\bor stop\b", r"max(imum)?\s*\d+\s*turns?", r"\d+\s*turn (cap|limit)",
]

# crude compound detector: many distinct task verbs as separate clauses
TASK_VERBS = ["add", "write", "update", "redesign", "refactor", "implement", "create", "build",
              "migrate", "document", "rewrite", "design"]


def find(text, patterns):
    return [p for p in patterns if re.search(p, text, re.I)]


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(2)
    if args[0] == "--file":
        goal = open(args[1], encoding="utf-8").read().strip()
    else:
        goal = " ".join(args).strip()

    # strip a leading "/goal "
    goal = re.sub(r"^/goal\s+", "", goal).strip()
    low = goal.lower()

    results = []

    def check(name, severity, ok, hint=""):
        results.append((name, severity, bool(ok), hint))

    check("non-empty", "required", bool(goal))
    check(f"under {MAX_LEN} characters", "required", len(goal) <= MAX_LEN,
          f"condition is {len(goal)} chars; trim it.")

    check_hits = find(low, CHECK_SIGNALS)
    check("has a checkable signal", "required", bool(check_hits),
          "Name a command or observable output the evaluator can read from the transcript "
          "(e.g. `npm test` exits 0, `git status` is clean).")

    vague_hits = [v for v in VAGUE if v in low]
    # Vague language is a hard fail only when there's no concrete check to anchor on.
    check("no unverifiable language (or it's anchored to a check)", "required",
          not vague_hits or bool(check_hits),
          f"vague terms with no check: {', '.join(vague_hits)} — an evaluator can't resolve these "
          "to yes/no. Replace with an observable end state.")

    constraint_hits = find(low, CONSTRAINT_SIGNALS)
    check("has cheat-closing constraints", "advisory", bool(constraint_hits),
          "Add what must NOT change (e.g. 'without modifying the test file', 'no test disabled') "
          "so the model can't game the check.")

    cap_hits = find(low, CAP_SIGNALS)
    check("has a turn/time cap", "advisory", bool(cap_hits),
          "There's no built-in token budget; add 'or stop after N turns' so it can't run away.")

    verb_hits = [v for v in TASK_VERBS if re.search(rf"\b{v}\b", low)]
    looks_compound = len(set(verb_hits)) >= 3 or " and then " in low
    check("single end state (not compound)", "advisory", not looks_compound,
          f"looks compound ({', '.join(sorted(set(verb_hits)))}); split into sequential goals, "
          "one verifiable end state each.")

    if vague_hits and check_hits:
        check("vague terms present alongside check", "advisory", False,
              f"'{', '.join(vague_hits)}' may confuse the evaluator even with a check — consider "
              "dropping them and letting the check define done.")

    # report
    width = max(len(r[0]) for r in results)
    print(f"\n/goal condition lint\n  {goal}\n" + "-" * (width + 12))
    for name, sev, ok, hint in results:
        mark = "PASS" if ok else ("FAIL" if sev == "required" else "warn")
        print(f"  [{mark:4}] {name.ljust(width)}")
        if not ok and hint:
            print(f"         -> {hint}")
    print("-" * (width + 12))

    req_fail = [r for r in results if r[1] == "required" and not r[2]]
    adv_fail = [r for r in results if r[1] == "advisory" and not r[2]]
    print(f"required: {sum(1 for r in results if r[1]=='required' and r[2])}/"
          f"{sum(1 for r in results if r[1]=='required')} passed; advisory warnings: {len(adv_fail)}")
    if req_fail:
        print("\nRESULT: NOT A VALID GOAL — fix the FAILs (it's still a prompt, not a condition).\n")
        sys.exit(1)
    print("\nRESULT: VALID GOAL — checkable from the transcript.\n")
    sys.exit(0)


if __name__ == "__main__":
    main()
