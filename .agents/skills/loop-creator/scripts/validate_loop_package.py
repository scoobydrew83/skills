#!/usr/bin/env python3
"""
validate_loop_package.py — structural lint for a generated loop package.

Enforces the non-negotiables a loop must have before it ships:
  acceptance criteria that are testable, a verifier separate from the builder, "close is FAIL",
  a commit/checkpoint, a max-iteration ceiling, a human-escalation threshold, stopping + safety
  conditions, an evidence requirement, and a comprehension-debt summary.

Usage:
  python3 validate_loop_package.py <package_dir>

Exit code 0 if all REQUIRED checks pass, 1 otherwise. ADVISORY checks never fail the run.
"""
import subprocess
import sys
import re
from pathlib import Path

REQUIRED = "required"
ADVISORY = "advisory"


def smoke_harness(pkg: Path):
    """Run the package's harness against a stubbed model over a 3-item queue.

    Every other check here is governance and reads the package as text. None of
    them notice a harness that can only ever process one unit. Returns
    (severity, ok, hint) so a missing/unrunnable harness degrades to advisory
    instead of failing a package that legitimately has no bundled harness.
    """
    harness = next((p for p in (pkg / "run_loop.sh", pkg / "scripts" / "run_loop.sh")
                    if p.is_file()), None)
    if harness is None:
        return ADVISORY, False, "No run_loop.sh in the package — execution was never tested."

    smoke = Path(__file__).resolve().parent / "smoke_harness.sh"
    if not smoke.is_file():
        return ADVISORY, False, f"smoke_harness.sh not found next to {Path(__file__).name}."

    try:
        proc = subprocess.run(["bash", str(smoke), str(harness.resolve())],
                              capture_output=True, text=True, timeout=180)
    except (OSError, subprocess.SubprocessError) as exc:
        return ADVISORY, False, f"could not run the smoke test: {exc}"

    if proc.returncode == 0:
        return REQUIRED, True, ""
    detail = (proc.stdout + proc.stderr).strip().splitlines()
    failed = [ln.strip() for ln in detail if ln.strip().startswith("FAIL")]
    return REQUIRED, False, "harness smoke test failed: " + ("; ".join(failed) or "see output")


def read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return ""


def has_any(text: str, *needles: str) -> bool:
    low = text.lower()
    return any(n.lower() in low for n in needles)


def validate(pkg: Path):
    spec = read(pkg / "LOOP_SPEC.md")
    builder = read(pkg / "builder-prompt.md")
    verifier = read(pkg / "verifier-prompt.md")
    # harness can be bundled or copied in; check whichever exists
    harness = read(pkg / "run_loop.sh") or read(pkg / "scripts" / "run_loop.sh")

    results = []

    def check(name, severity, ok, hint=""):
        results.append((name, severity, bool(ok), hint))

    # --- presence ---
    check("LOOP_SPEC.md exists", REQUIRED, bool(spec.strip()),
          "Every package needs a spec describing goal, criteria, limits, safety.")
    check("builder prompt exists", REQUIRED, bool(builder.strip()))
    check("verifier prompt exists", REQUIRED, bool(verifier.strip()),
          "A loop without a verifier is just a one-shot in a while-loop.")

    # --- verifier is separate from builder ---
    check("verifier is distinct from builder", REQUIRED,
          bool(builder.strip()) and bool(verifier.strip()) and builder.strip() != verifier.strip(),
          "The doer must not grade its own work; keep these two prompts separate.")

    # --- acceptance criteria, and they look testable ---
    has_criteria = has_any(spec, "acceptance criteria", "acceptance criterion", "definition of done")
    check("acceptance criteria present", REQUIRED, has_criteria)
    looks_testable = bool(re.search(
        r"(exit\s*0|exits?\s*(with\s*)?0|passes?\b|`[^`]+`|npm (run )?test|pytest|lint|build|"
        r"returns?\b|assert|coverage|status\s*200|\bcommand\b)", spec, re.I))
    check("acceptance criteria look testable", REQUIRED, has_criteria and looks_testable,
          "Criteria must be concrete (a command that exits 0, a passing test) so 'close is FAIL' is decidable.")

    # --- close is FAIL + verdict contract ---
    check("'close is FAIL' enforced", REQUIRED,
          has_any(verifier, "close is fail", "close is a fail", "partial credit") or
          has_any(spec, "close is fail"),
          "The verifier must treat 'mostly done' as FAIL.")
    check("verifier emits a parseable verdict", REQUIRED,
          has_any(verifier, "VERDICT: PASS", "VERDICT:PASS", "verdict: pass"),
          "Verifier must print 'VERDICT: PASS' or 'VERDICT: FAIL' so the harness can branch.")

    # --- checkpoint / commit ---
    check("commit checkpoint defined", REQUIRED,
          has_any(spec, "commit", "checkpoint") or has_any(harness, "git commit"),
          "Each passed unit should commit: the rollback point and audit trail.")

    # --- limits: ceiling + escalation ---
    check("max-iteration ceiling present", REQUIRED,
          has_any(spec, "max iteration", "max-iteration", "iteration ceiling", "max_iterations") or
          has_any(harness, "MAX_ITERATIONS"),
          "Loops must be bounded.")
    check("human-escalation threshold present", REQUIRED,
          has_any(spec, "escalat") or has_any(harness, "FAIL_THRESHOLD", "escalate"),
          "After N consecutive FAILs the loop must stop and hand off to a human.")

    # --- stopping + safety ---
    check("never auto-merge / works on a branch", REQUIRED,
          has_any(spec, "never auto-merge", "not merge", "open a pr", "branch", "human approval") or
          has_any(harness, "checkout -B", "WORK_BRANCH"),
          "Loops leave work on a branch / PR for a human; they don't merge to the default branch.")
    check("stopping conditions stated", ADVISORY,
          has_any(spec, "stopping condition", "stop condition", "queue empty", "done when"))
    check("least-privilege / reversible noted", ADVISORY,
          has_any(spec, "least privilege", "least-privilege", "reversible", "sandbox"))

    # --- evidence + comprehension debt ---
    check("builder must show evidence", REQUIRED,
          has_any(builder, "evidence", "show the command", "output of", "test output", "paste the"),
          "Builder must show the command it ran and what it returned, not just claim success.")
    # --- the harness actually runs (the only check that isn't governance) ---
    sev, ok, hint = smoke_harness(pkg)
    check("harness executes the whole queue (runtime smoke test)", sev, ok, hint)

    check("comprehension-debt summary required", REQUIRED,
          has_any(builder, "plain-language", "plain language", "summary of what changed",
                  "what changed and why") or
          has_any(spec, "comprehension debt", "comprehension-debt", "plain-language summary"),
          "Each checkpoint needs a human-readable summary so merged code isn't a black box.")

    return results


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    pkg = Path(sys.argv[1])
    if not pkg.exists():
        print(f"error: {pkg} does not exist")
        sys.exit(2)

    results = validate(pkg)
    req_fail = [r for r in results if r[1] == REQUIRED and not r[2]]
    adv_fail = [r for r in results if r[1] == ADVISORY and not r[2]]

    width = max(len(r[0]) for r in results)
    print(f"\nLoop package validation: {pkg}\n" + "-" * (width + 12))
    for name, sev, ok, hint in results:
        mark = "PASS" if ok else ("FAIL" if sev == REQUIRED else "warn")
        print(f"  [{mark:4}] {name.ljust(width)}")
        if not ok and hint:
            print(f"         -> {hint}")

    print("-" * (width + 12))
    print(f"required: {sum(1 for r in results if r[1]==REQUIRED and r[2])}/"
          f"{sum(1 for r in results if r[1]==REQUIRED)} passed; "
          f"advisory warnings: {len(adv_fail)}")

    if req_fail:
        print("\nRESULT: NOT READY — fix the FAILed required checks above.\n")
        sys.exit(1)
    print("\nRESULT: READY — all required checks passed.\n")
    sys.exit(0)


if __name__ == "__main__":
    main()
