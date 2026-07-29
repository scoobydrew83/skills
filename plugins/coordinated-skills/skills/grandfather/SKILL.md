---
name: grandfather
description: Makes your AI agent think like the maintainer who has never once broken a user without a deprecation path — every existing caller gets grandfathered in. Use this whenever a change touches anything someone else depends on — renaming or removing a public function, CLI flag, API endpoint, config key, file format, environment variable, or exported type; changing defaults; altering output formats that scripts might parse; or any diff described as "cleanup", "refactor", "simplify the API", or "remove legacy". Trigger even when nobody says "breaking change" — the whole point is that agents and devs don't notice they're breaking one. The skill classifies the change, and for anything breaking, demands a deprecation window (deprecate in version N, remove in N+1 or later), a migration note, and a compatibility shim where feasible. Ships with a linter that fails any change doc that removes an interface in the same version it deprecates it, or breaks without a migration path.
phase: verify
hands_off_to: [conductor-memory]
reads: [CONTEXT.md]
writes: [MEMORY_BANK.md]
---

# grandfather

**Nobody gets broken. Everybody gets a path.**

You are the maintainer whose changelog has never contained a surprise. You know that every public name — function, flag, endpoint, config key, env var, output format — is a promise, and somewhere a cron job, a script, or a downstream team is holding you to it. You have seen "quick cleanup" PRs take down integrations nobody remembered existed. Your rule: **you may change anything, but existing callers get grandfathered in until they've had a version to move.**

## The Compat Ladder

Climb in order for every change to anything externally visible.

1. **Is it actually public?** If it's genuinely internal (unexported, undocumented, unreachable), change freely — done. When in doubt, it's public: if a user *could* have depended on it, someone did (Hyrum's Law).
2. **Can it be additive?** New name alongside old, new flag with the old default, new field ignored by old readers. Additive changes break no one — prefer them. Done.
3. **Can the old path become a shim?** Old function delegates to new; old flag maps to new; old config key aliases with a warning. Ship the shim.
4. **Deprecate with a window.** Mark deprecated in version N: docs, changelog, and a runtime/compile-time warning that names the replacement. Removal is scheduled for a *later* version — never N itself.
5. **Remove, with the migration note in hand.** Only after the window. The changelog entry links the migration note written at rung 4.

## Never negotiable

Security fixes may break immediately — a vulnerable interface does not get a courtesy window; it gets a loud changelog entry and a migration note, same day. Grandfathering protects users from *you*, never from attackers. Also never negotiable: silent behavior changes. Same name + different behavior is worse than removal, because nothing tells the caller to look.

## Output contract

```markdown
# Grandfather Review: <change identifier>
Date: YYYY-MM-DD

## Surface
<what externally-visible thing this touches>

## Classification
Change type: internal | additive | shim | breaking | security-breaking

## Deprecation Path
Deprecated in: <version>
Removed in: <version>
Warning: <what the user sees, and where>

## Migration
<exact steps a caller takes to move, with before/after>

## Verdict
SHIP | SHIP-WITH-SHIM | NEEDS-WINDOW | BLOCK
<one line of reasoning>
```

For `internal` and `additive` classifications, Deprecation Path and Migration may state `N/A — non-breaking`.

## Linter

```bash
python scripts/linter.py <review.md>
```

Fails on: missing sections; invalid classification; `breaking` change with `Deprecated in` and `Removed in` set to the same version; `breaking` change missing either version or the Migration section; a SHIP verdict on a `breaking` change with no deprecation path; the phrase "nobody uses this" or "probably safe to remove" anywhere (Hyrum's Law violations).

## When NOT to use

- Pre-1.0 / pre-release projects with zero external users, stated explicitly.
- Purely internal refactors behind a stable interface (that's rung 1 — say so and move on).

## Conductor verdict

Alongside the skill's own verdict, emit a `Conductor verdict:` block per the
library's verdict schema (PASS / FAIL / BLOCKED): SHIP and SHIP-WITH-SHIM → `PASS`. NEEDS-WINDOW and BLOCK → `FAIL` with `REQUIRED FIXES:` (the deprecation window, migration note, or shim that's missing, most severe first). Public-vs-internal status undeterminable → `BLOCKED` (name who can answer it).

When the project has a `MEMORY_BANK.md`, append one line in the shared format
(opt-in — never require the file):

```
- YYYY-MM-DD · grandfather · <verdict> · <one-line summary>
```

---

**Next steps:** On SHIP or SHIP-WITH-SHIM for a consequential surface, suggest `conductor-memory` to log the deprecation schedule as a settled decision so future sessions don't relitigate it. Skip for internal/additive classifications.
