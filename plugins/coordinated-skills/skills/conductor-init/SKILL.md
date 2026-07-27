---
name: conductor-init
description: >-
  Initialize a repo for the Conductor Method loop: write init.sh, seed
  FEATURES.json from the spec, create CONTEXT.md and MEMORY_BANK.md, verify a
  one-command test and a one-command lint actually pass, and land the baseline
  commit `loop(0): baseline green + criteria defined`. Use whenever someone is
  standing up a builder/verifier loop on a repo that doesn't have one yet, or
  says "set up the conductor loop here", "initialize this repo for the loop",
  "do Phase 0", "get this repo loop-ready", "seed FEATURES.json", or asks why
  the verifier keeps returning BLOCKED on a fresh project (the answer is almost
  always missing acceptance criteria, which is what this skill installs). Also
  use on an existing repo to audit and repair a half-done Phase 0. Do NOT
  trigger to design the loop itself or write its prompts — that is
  `loop-creator`; this skill only prepares the ground the loop runs on.
phase: intake
hands_off_to: [loop-creator, agent-orchestration]
reads: [CONTEXT.md, MEMORY_BANK.md]
writes: [CONTEXT.md, MEMORY_BANK.md]
---

# Conductor Init

CONDUCTOR-LOOP-GUIDE Phase 0 as an agent instead of a human checklist. You run
once per repo, before any builder or verifier does, and you leave behind the
five artifacts every later phase assumes exist.

Everything downstream is graded against what you write here. A verifier with no
acceptance criteria returns `BLOCKED`; a loop with no green baseline can't tell
its own breakage from the code's. Get this wrong and every phase after it is
measuring nothing.

## The non-negotiables

1. **Criteria before code.** You produce checkable criteria, not a plan and not
   an implementation. If the spec is too vague to yield a runnable check, that's
   the finding — say so and stop. Do not invent criteria to fill the file.
2. **Green baseline or no baseline.** The commit is `loop(0): baseline green +
   criteria defined`. If test or lint doesn't pass, the baseline isn't green and
   you don't make that commit. Report what fails instead.
3. **One command each.** Test and lint must each be a single command a cold
   agent can run without reading the README. If they aren't, make them so
   (a script, an npm script, a Makefile target) — that IS part of the job.
4. **Evidence, not assertion.** Every criterion names a command and its
   observable outcome. "Works correctly" is not a criterion.
5. **You initialize; you don't build.** Nothing you write implements the
   project's features. Resist it.

## Workflow

### 1. Read the ground

Before writing anything, establish:

- **The spec** — whatever states what this project is supposed to do (a spec
  doc, a README, an issue, the conversation). This is what FEATURES.json is
  seeded *from*.
- **What already exists** — `ls` for CONTEXT.md, MEMORY_BANK.md, FEATURES.json,
  init.sh, `.claude/agents/`. Phase 0 is often half-done. Repair what's there;
  don't clobber a CONTEXT.md someone wrote by hand.
- **The test and lint commands** — `package.json` scripts, Makefile, `tox.ini`,
  `justfile`. Find the real ones. Do not guess.
- **Repo state** — clean tree, current branch. A dirty tree means stop and ask;
  you are about to make a commit.

If the spec is missing or too thin to yield checkable behavior, stop here and
say what's needed. That is a legitimate outcome, and a better one than a
FEATURES.json full of guesses.

### 2. Write `init.sh`

The one-command entry point for a cold agent or a fresh clone. Keep it boring
and idempotent — install deps, run the test command, run the lint command,
exit nonzero if either fails. It is the smoke test the builder's clean-state
exit contract re-runs at the start of every later session, so it must be fast
and it must be honest.

```bash
#!/usr/bin/env bash
set -euo pipefail
<install command>
<test command>
<lint command>
echo "init: OK"
```

Make it executable and verify it exits 0 by actually running it.

### 3. Seed `FEATURES.json` from the spec

The ground truth the verifier grades against — JSON on purpose, because models
mangle JSON less than prose. Seed it with the spec's user-visible behaviors,
one entry each, all starting `passes: false`.

```json
{
  "project": "<repo-name>",
  "phase": "<phase name/number matching CONTEXT.md>",
  "_contract": {
    "who_may_edit": {
      "builder": ["features[*].passes", "features[*].evidence"],
      "planner_or_human": ["everything else"]
    },
    "rules": [
      "It is unacceptable to remove or edit feature descriptions or steps; that hides missing or buggy functionality.",
      "passes flips to true only with evidence: a test name, command output, or file:line the verifier can re-check.",
      "The verifier grades against this file, not against CONTEXT.md prose. A phase with zero entries here is BLOCKED."
    ]
  },
  "features": [
    {
      "id": "F-001",
      "category": "functional",
      "description": "One-sentence, user-visible behavior.",
      "steps": ["Run <exact command>", "Assert <exact observable outcome>"],
      "passes": false,
      "evidence": null
    }
  ]
}
```

Rules for the seed:

- **`steps` are runnable.** A command plus an assertion about its output. If you
  can't write the command, the description is still too vague — fix the
  description, not the step.
- **Include at least one `regression` entry** — existing behavior that must not
  break. Loops break things sideways; nothing else catches it.
- **Everything starts false.** You are not permitted to flip `passes` — that's
  the builder's field, and only with evidence.
- **Categories** describe the kind of check (`functional`, `regression`,
  `contract`, `perf`), not its importance.

### 4. Create `CONTEXT.md` and `MEMORY_BANK.md`

`CONTEXT.md` — mission, current phase, and the phase's acceptance criteria. The
criteria section points at FEATURES.json rather than restating it; two copies of
the criteria drift within a week. Minimum viable shape:

```markdown
# CONTEXT

## Mission
<one paragraph: what this project is for>

## Current phase
Phase <N> — <name>

## Acceptance criteria
Graded from `FEATURES.json` (phase `<N>`). The verifier grades that file,
not this prose. Constraints that aren't feature-shaped go here:
- <architectural constraint>
- <out of scope for this phase>
```

`MEMORY_BANK.md` — the rolling log, seeded with its own format so later
appenders have an example to copy:

```markdown
# MEMORY BANK

Append-only in spirit. One line per settled decision, verdict, or lesson:
`- YYYY-MM-DD · <skill-or-agent> · <verdict-or-decision> · <one-line summary>`

- <today> · conductor-init · DECISION · baseline initialized, criteria seeded from <spec>
```

### 5. Verify the baseline

Actually run them. Not "should pass" — run them:

- `bash init.sh` exits 0.
- The test command passes.
- The lint command passes.
- `FEATURES.json` parses (`node -e "JSON.parse(...)"` or `jq . FEATURES.json`).

Any failure stops the sequence. Report the failing command and its output; do
not fix the project's code to make the baseline green. That's building, and it
isn't your job.

### 6. Commit the baseline

One commit, exactly this message:

```
loop(0): baseline green + criteria defined
```

Contents: `init.sh`, `FEATURES.json`, `CONTEXT.md`, `MEMORY_BANK.md`. Nothing
else. If you had to add an npm script or a Makefile target to make test/lint
one-command, that goes in too — it's part of the baseline.

## What you hand off

A repo where the next agent can run one command to know if it's broken, and
read one JSON file to know what "done" means. Report back: the four artifacts,
the test and lint commands you verified, the number of seeded features, and
anything the spec was too vague to make checkable.

**Next steps:** When the baseline commit lands, suggest `loop-creator` to design
the actual builder/verifier loop that will run against the criteria just seeded —
that's the normal path, and Phase 0 exists to feed it. Suggest
`agent-orchestration` instead when the work ahead is a multi-stage build the user
wants sequenced by hand rather than looped unattended. If you stopped short
because the spec couldn't yield checkable criteria, suggest neither — the user
needs to settle scope first, and `overwhelm-breakdown` or `task-decomposition` is
the better door.
