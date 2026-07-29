#!/usr/bin/env python3
"""tinfoil linter — no PASS without enumerated inputs, handlings, and defeated attacks.

Exit 0 = PASS, 1 = FAIL, 2 = usage error.
"""
import re
import sys

REQUIRED_SECTIONS = ["## Trust Boundaries", "## Inputs", "## Gaps", "## Verdict"]

REASSURANCE = [
    "should be fine",
    "internal only so it's safe",
    "users would never",
    "unlikely to be attacked",
    "trusted input",
]
INPUT_LINE = re.compile(r"^Input:\s*(.+)$", re.MULTILINE)
NO_INPUTS = re.compile(r"No external inputs:\s*\S+")
VERDICT_RE = re.compile(r"^\s*(PASS|FLAG|BLOCK)\b", re.MULTILINE)
SANITIZED_VAGUE = re.compile(r"\bsanitized\b(?!.*(escape|allowlist|schema|paramet|encod))", re.IGNORECASE)


def section(text: str, header: str) -> str:
    m = re.search(re.escape(header) + r"\s*\n(.*?)(?=\n## |\Z)", text, re.DOTALL)
    return m.group(1) if m else ""


def lint(text: str) -> list[str]:
    v: list[str] = []
    low = text.lower()

    for h in REQUIRED_SECTIONS:
        if h not in text:
            v.append(f"MISSING SECTION: {h}")

    for w in REASSURANCE:
        if w in low:
            v.append(f"REASSURANCE AS EVIDENCE: '{w}' — that's attack surface, not mitigation")

    boundaries = section(text, "## Trust Boundaries")
    if "## Trust Boundaries" in text and not re.search(r"^\s*-\s*\S", boundaries, re.MULTILINE):
        v.append("NO BOUNDARIES DRAWN: list at least one, or prove there are none")

    inputs_sec = section(text, "## Inputs")
    input_lines = INPUT_LINE.findall(inputs_sec)
    if "## Inputs" in text and not input_lines and not NO_INPUTS.search(inputs_sec):
        v.append("INPUTS UNENUMERATED: list 'Input:' lines or a justified 'No external inputs:' proof")
    for i, line in enumerate(input_lines, 1):
        if "Handling:" not in line:
            v.append(f"INPUT #{i} WITHOUT HANDLING: name the mechanism (validate/escape/parameterize/...)")
        if "Attack defeated:" not in line:
            v.append(f"INPUT #{i} WITHOUT DEFEATED ATTACK: if you can't write the attack, you don't understand the handling")
        if SANITIZED_VAGUE.search(line):
            v.append(f"INPUT #{i} VAGUE 'SANITIZED': say how — escaping for which context, which allowlist")

    gaps = section(text, "## Gaps").strip()
    vd = section(text, "## Verdict")
    m = VERDICT_RE.search(vd)
    if "## Verdict" in text and not m:
        v.append("INVALID VERDICT: must be PASS, FLAG, or BLOCK")
    if m and m.group(1) == "PASS":
        if gaps and "none found" not in gaps.lower():
            v.append("PASS WITH OPEN GAPS: verdict must be FLAG or BLOCK until gaps close")
        if not input_lines and not NO_INPUTS.search(inputs_sec):
            v.append("PASS WITHOUT INPUT ENUMERATION: nothing was actually reviewed")

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
    print("PASS — hostile inputs accounted for")
    return 0


if __name__ == "__main__":
    sys.exit(main())
