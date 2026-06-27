# Conductor Loop System — Full Build Guide

Goal: extend the Conductor Method from a human-gated phase workflow into a
closed-loop build system: **scheduled discovery → isolated build → independent
verification → gated merge → persisted state**, with the human reviewing
pre-graded diffs instead of raw output.

Each phase below has explicit acceptance criteria and a commit checkpoint.
Run phases in order. The system is resumable — state lives in files, so any
phase can be picked up cold.

---

## Phase 0 — Prerequisites (15 min)

**Do:**

1. Pick ONE repo as the testbed. Recommended: `@sfdt/cli` (it already has CI
   and tests, which the loop needs as its ground truth).
2. Confirm the repo has: a one-command test suite, a one-command lint, and a
   CONTEXT.md + MEMORY_BANK.md per Conductor Method. If CONTEXT.md lacks
   per-phase acceptance criteria, fix that first — the verifier returns
   BLOCKED without them.
3. Confirm Claude Code is current: `claude --version`, then `claude update`
   if needed.

**Acceptance criteria:** `npm test` (or equivalent) passes on main;
CONTEXT.md has at least one phase with 3+ concrete, checkable criteria.

**Checkpoint:** commit `loop(0): baseline green + criteria defined`.

---

## Phase 1 — Install the maker/checker pair (30 min)

This is the single highest-value change. Everything else builds on it.

**Do:**

1. Copy `conductor-verifier.md` and `conductor-builder.md` into
   `.claude/agents/` in the repo. Commit them — project-scoped agents are
   shared infrastructure, not personal config.
2. Add a gating rule to the repo's CLAUDE.md:

   ```
   ## Phase gates
   - No phase commit closes without a `VERDICT: PASS` from the
     conductor-verifier subagent recorded in the phase log.
   - On FAIL, the conductor-builder addresses REQUIRED FIXES only.
   - After 3 consecutive FAILs on one phase, stop and escalate to the maintainer.
   ```

3. Dry-run the pair on something trivial: ask the main session to
   "Use the conductor-builder subagent to implement <small real item>, then
   use the conductor-verifier subagent to grade it." Watch one full
   build → verify → PASS cycle end to end.

**Acceptance criteria:** one complete cycle observed; verifier produced the
structured verdict format; a deliberately broken criterion produces FAIL
(test this — a verifier that can't fail is decoration).

**Checkpoint:** commit `loop(1): maker/checker pair installed and exercised`.

---

## Phase 2 — Close the loop locally (45 min)

A loop = decision logic that reads state and chooses the next action, with a
verifiable stopping condition. You build that as a work queue + a goal-driven
session.

**Do:**

1. Create `LOOP_QUEUE.md` in the repo root:

   ```markdown
   # Loop Queue
   ## Pending
   - [ ] <work item> | criteria: <ref to CONTEXT.md phase or inline>
   ## In progress
   ## Done (verifier-passed)
   ```

2. Add loop semantics to CLAUDE.md:

   ```
   ## Loop protocol
   1. Read LOOP_QUEUE.md. Take the TOP pending item only.
   2. Move it to "In progress" with branch name and timestamp.
   3. Create an isolated worktree:
      git worktree add ../wt-<item-slug> -b loop/<item-slug>
   4. Delegate the build to conductor-builder in that worktree.
   5. Delegate grading to conductor-verifier.
   6. On PASS: open a PR (never merge), move item to Done with the
      verdict summary, append lessons to MEMORY_BANK.md.
   7. On 3rd FAIL: move item back to Pending tagged BLOCKED-HUMAN, stop.
   8. Stopping condition: queue empty, item blocked, or budget reached.
   ```

3. Run it goal-driven: `claude "Run the loop protocol until the queue is
   empty or a stopping condition is hit"` with 2–3 small real items queued.
   (If your Claude Code version exposes `/goal` or `/loop`, use it with the
   same stopping condition; the protocol file makes the behavior identical
   either way — that's what keeps it portable across tools.)

**Acceptance criteria:** loop processed ≥2 queue items unattended; each
produced a PR with a verifier PASS in the description; queue file accurately
reflects final state; no commits landed on main.

**Checkpoint:** commit `loop(2): local closed loop operational`.

---

## Phase 3 — Parallel worktrees (30 min)

**Do:**

1. Queue two items that touch disjoint parts of the codebase.
2. Instruct the main session to dispatch both to conductor-builder subagents
   in parallel, each in its own worktree, then verify each independently.
3. Hard limit: **2 parallel tracks**. Multi-agent runs cost roughly 4–7x the
   tokens of a single session, and every parallel track is comprehension
   debt you haven't paid yet. Scale only after Phase 5 guardrails exist.

**Acceptance criteria:** two PRs from two worktrees, both verifier-passed,
zero cross-contamination (each diff touches only its item's files), main
untouched.

**Checkpoint:** commit `loop(3): parallel tracks validated at n=2`.

---

## Phase 4 — Scheduled discovery (1 hr)

This is the "automation" primitive: the loop finds its own work.

**Do:**

1. Add `.github/workflows/nightly-triage.yml`:

   ```yaml
   name: Nightly Triage
   on:
     schedule:
       - cron: "0 11 * * 1-5"   # 06:00 Central, weekdays
     workflow_dispatch: {}
   permissions:
     contents: write
     pull-requests: write
     issues: read
     actions: read
   jobs:
     triage:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
           with: { fetch-depth: 0 }
         - uses: anthropics/claude-code-action@v1
           with:
             anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
             prompt: |
               Triage only — do not fix anything in this run.
               1. Inspect CI runs from the last 24h (gh run list / gh run
                  view) and open issues labeled "loop-eligible".
               2. For each actionable failure, append a queue item to
                  LOOP_QUEUE.md Pending with inline acceptance criteria
                  (max 3 new items per night).
               3. Open a single PR titled "loop: nightly triage <date>"
                  containing only the LOOP_QUEUE.md change, with a one-line
                  rationale per item in the PR body.
   ```

   (Verify the action's current input names against its README before first
   run — `anthropics/claude-code-action` has evolved.)

2. Morning routine: you review the triage PR (this is your decision point —
   merging it is what authorizes the work), then kick the Phase 2 loop, or
   wire a second scheduled job that runs the loop protocol on queue items
   after the triage PR merges.

**Acceptance criteria:** triage runs on schedule for 3 consecutive weekdays;
items it queues are real (no hallucinated failures); it never modifies
anything except LOOP_QUEUE.md.

**Checkpoint:** commit `loop(4): scheduled discovery live`.

---

## Phase 5 — Guardrails (45 min, non-optional)

The article's warning, made enforceable:

**Do — add to CLAUDE.md and enforce via branch protection:**

1. **Comprehension gate.** Nothing merges to main unread. The verifier
   reduces review burden; it never replaces review. Branch-protect main:
   require 1 human review + green CI on every loop PR.
2. **Budget gate.** Cap loop sessions (max turns / spend per run; max 3 new
   queue items per night; 2 parallel tracks). A loop running unattended is
   also a loop making mistakes unattended — caps bound the blast radius.
3. **Memory hygiene.** Every verifier-passed item appends one "lesson" line
   to MEMORY_BANK.md. Your update-rules skill already does this for
   mistakes; this extends it to the loop's successes so tomorrow's run is
   smarter than today's.
4. **Kill switch.** Document the disable path: pause the GitHub Action
   (`gh workflow disable nightly-triage`) and tag all queue items
   BLOCKED-HUMAN. One command, written down, tested once.

**Acceptance criteria:** branch protection active; kill switch tested; caps
written in CLAUDE.md where the loop reads them.

**Checkpoint:** commit `loop(5): guardrails enforced` — system is live.

---

## Operating rhythm once live

- **Morning (5 min):** review triage PR → merge or edit queue → loop runs.
- **Midday:** review verifier-passed PRs. Read the diffs. Merge what you
  understand; queue questions on what you don't.
- **Weekly:** prune MEMORY_BANK.md lessons into CLAUDE.md rules (your
  update-rules skill is the natural home for this).

## Rollout order across your repos

1. `@sfdt/cli` — proves the system (has tests + CI today).
2. Inspector clone — run phases of the 7-phase roadmap as queue items;
   independent feature modules are the parallel-track candidates.
3. WorthSync — only after the pattern is boring and reliable.
