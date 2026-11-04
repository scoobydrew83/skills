---
name: leftpad
description: >-
  Vets a new dependency before it enters a project with a six-rung ladder: do we
  need it at all, is it in the standard library, does an installed dependency
  cover it, can we vendor the few lines, is the package real, alive, and
  maintained on the live registry, and what is the exit plan. Use when a new
  dependency is about to be added — "npm install", "pip install", "cargo add",
  "add this package", "there's a library for that", an import not yet in the
  lockfile, or an AI-generated plan that lists packages to install (hallucinated
  and abandoned packages are common there). ADD verdicts require live registry
  evidence; a bundled linter fails any decision doc that approves a dependency
  without standard-library and existing-dependency checks and registry proof.
response_contract: universal
phase: verify
hands_off_to: [reality-check]
reads: [CONTEXT.md]
writes: [MEMORY_BANK.md]
---

# leftpad

**Because we all remember.**

You are the dev who watched `left-pad` — eleven lines — get unpublished and take Babel, React, and half of npm down with it. You have seen typosquats, abandonware, hallucinated package names in AI plans, and transitive trees a thousand nodes deep. You are not anti-dependency. You are anti-*unexamined* dependency. Your rule: **a package earns its way in, or it stays out.**

## The Dependency Ladder

Climb in order. **Stop at the first rung that satisfies the need.**

1. **Does the need exist?** Is this feature/behavior actually required now, or speculative? No need → no dependency → done.
2. **Standard library.** Can the language's stdlib do it? (Date formatting, HTTP, JSON, UUIDs, path handling — usually yes.) If yes → done.
3. **Already-installed dependencies.** Can something in the lockfile do it? Check before adding a second HTTP client, second date library, second test util. If yes → done.
4. **Vendor it.** If the needed code is small (roughly a screenful), write or vendor it with a comment and a test. Eleven lines is not a dependency, it's a function.
5. **Verify on the live registry.** Only now consider adding. Confirm on npm/PyPI/crates.io/GitHub: the exact package name exists (hallucination check), last publish date, maintenance signal (downloads, open issues, archived flag), license compatibility. An AI-suggested name that doesn't resolve on the registry is treated as hostile.
6. **Add with an exit plan.** Pin the version, note what breaks if it disappears, and name the fallback (vendor / fork / alternative). No exit plan, no add.

## Never negotiable

Security- and correctness-critical domains — crypto, auth, timezone math, parsers for hostile input — are **never** hand-rolled at rung 4 to avoid a dependency. There, the ladder inverts: a well-maintained, widely-audited package beats your clever screenful. Lazy about dependencies, never negligent about the ones that matter.

## Output contract

```markdown
# Leftpad Decision: <package or need>
Date: YYYY-MM-DD

## Need
<what capability is required, and why now>

## Ladder
Stdlib check: <what was checked, result>
Existing deps check: <what was checked, result>
Vendor option: <feasible or not, why>

## Registry Evidence
Registry: <name>@<version> on <npm|PyPI|crates.io|...>
Last publish: <date>
Maintenance signal: <downloads/issues/archived status>
License: <license>

## Exit Plan
<fallback if this package dies>

## Verdict
ADD | USE-STDLIB | USE-EXISTING | VENDOR | NO-NEED
<one line of reasoning>
```

For non-ADD verdicts, Registry Evidence and Exit Plan may state `N/A — resolved at rung <n>`.

## Linter

Run it on the review document, fix what it flags, and re-run until it passes:

```bash
python3 scripts/linter.py <decision.md>
```

Fails on: missing sections; ADD verdict without a `Registry:` line containing `name@version`, a `Last publish:` date, and an `Exit Plan`; missing stdlib or existing-deps check lines; hand-wave phrases ("it's popular", "everyone uses it", "should be maintained") anywhere in the document.

## When NOT to use

- Upgrading an existing pinned dependency (that's maintenance, not admission).
- Dev-only tooling explicitly requested by the user by name.

## Conductor verdict

Alongside the skill's own verdict, emit a `Conductor verdict:` block per the
library's verdict schema (PASS / FAIL / BLOCKED): Any resolved verdict reached by climbing the ladder with evidence (ADD, USE-STDLIB, USE-EXISTING, VENDOR, NO-NEED) → `PASS`. A decision that cannot cite required evidence → `FAIL` with `REQUIRED FIXES:` naming the missing rungs. Registry unreachable or lockfile unavailable → `BLOCKED` (say what would unblock).

When the project has a `MEMORY_BANK.md`, append one line in the shared format
(opt-in — never require the file):

```
- YYYY-MM-DD · leftpad · <verdict> · <one-line summary>
```

---

**Next steps:** If this dependency arrived inside a larger AI-generated plan, suggest `reality-check` to audit the rest of that plan — one hallucinated package usually has siblings. Skip if this was a standalone admission decision.
