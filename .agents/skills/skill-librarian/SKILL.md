---
name: skill-librarian
description: >-
  Audit, refresh, and maintain a library of existing skills so it stays lean,
  non-duplicated, and written for current models. Use whenever the user wants to
  review, clean up, consolidate, merge, dedupe, refresh, or "update all my
  skills", asks whether two skills overlap, wants to know which skill owns a
  piece of guidance, asks why an installed skill behaves differently from the
  repo, or is about to add a new skill to a library that already has many. Also
  use before creating a new skill, to check that its job isn't already owned.
  Do NOT trigger for auditing project documents (use drift-check), for writing
  one brand-new skill's body from scratch, or for verifying an AI-generated
  plan (use reality-check).
response_contract: universal
phase: meta
hands_off_to: [drift-check]
reads: [MEMORY_BANK.md]
writes: [MEMORY_BANK.md]
---

# Skill Librarian

This skill is about the library as a whole: which skills should exist, where
each piece of guidance lives, and whether each skill is still written for the
model that reads it. Structural rules for this repository (coordination header,
Next-steps line, phases, renames, tombstones) live in `CONVENTIONS.md` and
`CONTRIBUTING.md`; follow them rather than restating them here. For drafting
and evaluating a single skill in depth, Anthropic's skill-creator skill is the
companion tool.

## The goal

A library where every piece of guidance has exactly one home, every skill has
a job no other skill claims, installed copies match the source, and
instructions are as light as the current model allows. Done means: an
inventory, a decision for every overlap, drafted edits for skills the user
owns, passing repository tests, and a short trigger test for each change.

## Principles

### 1. One home per piece of information

Each fact, rule, or procedure lives in one skill. Anything else that needs it
links to that skill by name instead of repeating it.

Why: a duplicated rule drifts. When one copy is updated and the other isn't,
the model sees two conflicting instructions and has to guess which is current.

- **Across skills.** Before adding guidance, ask whether it warrants its own
  skill or belongs inside an existing one. If another skill needs it, link.
- **Within a skill.** Say each rule once, where it matters most, not in the
  description, the body, and an example.
- A thin skill or command that only routes to a fuller one is a link, not a
  duplicate. Leave it.

### 2. Write for the model's intelligence

State the goal, give the context needed for good decisions, and say what done
looks like so the model knows when to stop and when to keep going. Prefer that
over rigid step lists.

- Add a rigid rule only when there is evidence it is needed: a real failure, a
  real risk, or a correction the user kept repeating.
- After each rule, say why it exists, so the model can apply its intent in
  cases the rule didn't anticipate.
- Skills written months ago or for an earlier model are candidates for a
  lighter rewrite. Habits like "think step by step", "double-check your work",
  and capitalized ALWAYS/NEVER compensated for weaker models and can now narrow
  judgment instead of guiding it.
- Encourage periodically removing a rule and retesting. If output holds up
  without it, the rule was dead weight.

**Exception: safety and irreversibility.** Guardrails that prevent data loss,
destructive actions, security exposure, human-gate bypass, or spending money
stay unless the user explicitly decides otherwise. Their evidence is the risk
itself, not a past failure. The loop policy and human gates in this library are
examples.

### 3. Look around before acting on an outside system

When a skill has the model touch an external system (a repo, a Drive, a Notion
workspace, a Salesforce org), it should explore how that system is organized
before changing anything.

Why: acting on an assumed structure is the most common way agents create
duplicates, write to the wrong place, or redo work that already exists.

For a simple system, a one-line "look around first" is enough. For a complex
system used often, map it once, store the map as its own skill (it then has
one home), and link to it. Apply this to the library itself: read the source
tree and conventions before proposing any change.

## Library rules

- **Check source against installed copies.** Installed plugins can lag the
  repository. Before diagnosing an overlap, confirm the source still has it;
  a duplicate that exists only in a stale install is fixed by reinstalling,
  not by editing.
- **Resolve trigger collisions.** Two skills whose descriptions fire on the
  same phrases compete. Give each an anti-trigger naming the other.
- **Don't restate the platform.** If the environment already does something
  natively, a skill should add only what the platform lacks: a format, a
  standard, a boundary.
- **Don't edit skills you don't own.** Vendor and marketplace plugins are
  overwritten on update. Recommend disabling one of two overlapping vendor
  skills instead.
- **Retire with a tombstone**, following the library's existing pattern, and
  update every reference to the retired name. The repository tests catch
  dangling references.

## Audit workflow

1. **Inventory.** List every skill with its phase, description, and owner
   (this repo, vendor, or Anthropic). Compare the installed set against the
   source tree and flag anything stale or installed twice.
2. **Find overlaps.** Group skills whose descriptions target the same user
   situation or whose bodies share procedures or examples.
3. **Decide each group:** merge, add anti-triggers, keep as a link, disable a
   vendor copy, or reinstall from source. One sentence of reasoning each.
4. **Draft changes** for skills this repo owns, keeping the more specific name
   and absorbing unique material from the retired skill.
5. **Validate.** Run the repository's validation and test scripts, update the
   routing fixtures, and regenerate the skill graph and plugin copy.
6. **Record the result** as one MEMORY_BANK line in the library's format.

**Next steps:** When an audit finds that the library's own docs (README,
CONVENTIONS, skill graph) disagree with each other or with the skills, suggest
`drift-check` to audit that document set. Skip if the user clearly wants to
stop.
