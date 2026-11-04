---
name: skill-librarian
description: >-
  Audits, refreshes, and maintains a library of skills so it stays lean,
  non-duplicated, portable across agents, and aligned with Anthropic's skill
  authoring guidance. Use when someone wants to review, clean up, consolidate,
  merge, dedupe, refresh, or "update all my skills", asks whether two skills
  overlap or which skill owns a piece of guidance, asks why an installed skill
  behaves differently from the repo, is about to add a skill to a library that
  already has many, or is setting up or migrating a portable layout
  (.agents/skills as source, AGENTS.md as canonical instructions, generated
  Claude, Codex, Gemini, or skills.sh packages). Not for auditing project
  documents (drift-check), writing one new skill's body from scratch, or
  verifying an AI-generated plan (reality-check).
response_contract: universal
phase: meta
hands_off_to: [drift-check, conductor-doctor]
reads: [MEMORY_BANK.md, AGENTS.md, CONVENTIONS.md]
writes: [MEMORY_BANK.md]
---

# Skill Librarian

Keeps the library as a whole healthy: which skills should exist, where each
piece of guidance lives, whether each skill is written for the model that reads
it, and whether every installed copy matches the source. Structural rules for
this repository (coordination header, Next-steps line, phases) live in
`CONVENTIONS.md` and `CONTRIBUTING.md`; follow them rather than restating them.
For drafting and evaluating one skill in depth, Anthropic's skill-creator skill
is the companion tool.

Done means: an inventory, a decision for every overlap, drafted edits for skills
the user owns, passing repository checks, and a trigger test for each change.

## Audit workflow

Copy this checklist and tick it off:

```
- [ ] 1. Inventory: every skill's phase, description, owner (repo / vendor / Anthropic)
- [ ] 2. Compare installed copies against the source tree; flag stale or doubled installs
- [ ] 3. Group overlaps (same user situation, shared procedures or examples)
- [ ] 4. Decide each group: merge, anti-trigger, keep as link, disable vendor copy, reinstall
- [ ] 5. Check each owned skill against the authoring checklist below
- [ ] 6. Draft changes; keep the more specific name, absorb unique material
- [ ] 7. Validate, fix, re-run until clean (commands below)
- [ ] 8. Record one MEMORY_BANK line in the library's format
```

In this repository, step 7 is:

```bash
bash tools/validate-skill.sh --all      # conventions + Anthropic limits
bash tools/sync-agent-layout.sh --check # aliases and generated package
bash tests/run-all.sh                   # full suite
```

Fix every FAIL and re-run. After changing canonical skills, regenerate with
`bash tools/build-plugin.sh` and `bash tools/skill-graph.sh`, and update the
routing fixtures in `tests/triggering-evals/prompts/`.

## Authoring checklist (Anthropic guidance)

| Check | Rule |
|---|---|
| Description | Third person, says what the skill does and when to use it, ≤ 1,024 characters. It is always loaded, so every word costs context in every session |
| Name | Lowercase letters, digits, hyphens; ≤ 64 characters; no "anthropic" or "claude" |
| SKILL.md size | Under 500 lines; lead with the workflow in the first screen, not backstory |
| Progressive disclosure | Detail goes in files linked directly from SKILL.md (one level deep). Reference files over 100 lines open with a Contents list |
| Degrees of freedom | Exact scripts for fragile, repeatable, high-stakes steps; templates for the common case; goals and context for exploratory work |
| Feedback loops | Where output can be checked, give a validate → fix → re-run loop and a copyable checklist |
| Hard rules | Rules that must never break belong in hooks, scripts, or tests, not only prose |
| Time-sensitive text | No "as of" dates or changelog notes in the body; history lives in git |
| Testing | Trigger and outcome checks on every model the skill will run on (Haiku needs more explicit steps than Opus) |

`tools/validate-skill.sh` enforces the description, name, and size limits and
warns on non-third-person descriptions and long references without a Contents
list.

## Principles

### 1. One home per piece of information

Each fact, rule, or procedure lives in one skill; anything else that needs it
links by name. A duplicated rule drifts, and the model then sees two conflicting
instructions. Say each rule once within a skill, too. A thin skill or command
that only routes to a fuller one is a link, not a duplicate.

### 2. Write for the model's intelligence

State the goal, the context needed for good decisions, and what done looks like.
Add a rigid rule only with evidence (a real failure, a real risk, a repeated
correction), and say why it exists. Habits like "think step by step" and
capitalized ALWAYS/NEVER compensated for weaker models and can now narrow
judgment. Periodically remove a rule and retest; if output holds, it was dead
weight.

**Exception: safety and irreversibility.** Guardrails against data loss,
destructive actions, security exposure, human-gate bypass, or spending stay
unless the user decides otherwise. Their evidence is the risk itself.

### 3. Look around before acting on an outside system

A skill that touches an external system (repo, Drive, Notion, Salesforce org)
should explore its structure before changing anything. For a complex system
used often, map it once as its own skill and link to it.

## Library rules

- **Check source against installed copies** before diagnosing an overlap; a
  duplicate in a stale install is fixed by reinstalling, not editing.
- **Resolve trigger collisions** by giving each skill an anti-trigger naming
  the other.
- **Don't restate the platform.** Add only what the environment lacks.
- **Don't edit skills you don't own.** Vendor plugins are overwritten on
  update; recommend disabling one of two overlapping copies instead.
- **Retire by deleting.** Move unique material into the survivor, update every
  reference to the old name (the repository tests catch dangling ones), and
  note the redirect in the commit message. Deprecated stubs still load their
  description into every session and can still be picked.

## Portable layout (setup or migration)

1. Inspect the canonical skills directory, provider package outputs,
   instruction aliases, and the build/check commands before changing anything.
2. Keep one authored tree under `.agents/skills/`. Provider packages that
   disallow external symlinks are generated as physical copies (here:
   `bash tools/build-plugin.sh` → `plugins/coordinated-skills/`).
3. Make `AGENTS.md` the canonical always-on instruction file, with relative
   aliases (`CLAUDE.md`, `GEMINI.md`). Never overwrite a real instruction file
   without explicit approval; `tools/sync-agent-layout.sh --apply` only creates
   missing aliases.
4. Keep the build deterministic with a check mode that detects generated-output
   drift (`tools/sync-agent-layout.sh --check`). Test clean setup, stale output,
   broken links, and repeated runs.
5. Use skills.sh for cross-agent installation, in copy mode where symlinks are
   unavailable.

**Next steps:** When the library's own docs (README, CONVENTIONS, skill graph)
disagree with each other or with the skills, suggest `drift-check`. When a
target repository's Conductor harness, aliases, or generated package need a
read-only health check, suggest `conductor-doctor`. Skip if the user clearly
wants to stop.
