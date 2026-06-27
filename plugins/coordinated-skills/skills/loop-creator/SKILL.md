---
name: loop-creator
description: Design and generate autonomous/semi-autonomous AI work loops and the prompts that drive them — builder/verifier (maker/checker) loops, phased build loops, queue-driven multi-task loops, and nightly triage. Every loop it produces has explicit acceptance criteria, a verifier separated from the builder ("close is FAIL"), commit checkpoints, a hard max-iteration + human-escalation stop, and safe stopping conditions. Use whenever the user wants to build a loop, "create a loop", "make a loop creator", set up a self-correcting or maker/checker loop, write prompts for a loop, design an evaluator-optimizer or agentic loop, scaffold a LOOP_QUEUE, or wire a nightly triage workflow — even if they don't say the word "loop" but describe an iterate-until-it-passes process. When (and only when) the request says to look at a codebase or use Claude Code, it inspects the repo read-only and emits a headless Claude Code harness. Defaults to the Conductor Method conventions, all clearly overridable.
phase: execute
hands_off_to: [reality-check, drift-check, goal-builder]
reads: []
writes: []
---

# Loop Creator

Builds **work loops** — a builder step, a separate verifier step, and a controlled
iterate-until-it-passes cycle — plus all the prompts, queue, harness, and CI to run them.

The output is a **loop package**: a spec, the prompts, a queue, a runnable harness, and
(optionally) a GitHub Actions triage workflow. Everything it produces is then run through a
bundled validator so the loop can't ship without acceptance criteria, a real verifier,
checkpoints, and a stop condition.

## Why loops are built this way (the non-negotiables)

These come straight from Anthropic's agent guidance and how the Claude Code team runs loops.
They are the spine of every package this skill emits. See `references/loop-patterns.md` and
`references/claude-code-loops.md` for the grounding.

1. **The doer never grades its own work.** A loop is a *generator* (builder/maker) plus a
   *separate-context evaluator* (verifier/checker). The verifier's job is to try to *refute*
   success, not rubber-stamp it.
2. **"Close is FAIL."** Acceptance criteria are explicit and testable. Partial credit is how
   loops drift. A verifier that can't cleanly distinguish pass from fail makes the loop
   circular and useless — so criteria must be concrete (a command that exits 0, a test that
   passes, a string that appears).
3. **Verify by evidence, not assertion.** The builder must show the command it ran and what it
   returned (test output, lint result, diff). Reviewing evidence is faster and safer than
   trusting "done."
4. **Checkpoints are commits.** Each passed unit of work commits. Small, reviewable, one goal
   per change. This is the rollback point and the audit trail.
5. **Hard stop + human escalation.** Every loop has a max-iteration ceiling and a
   consecutive-FAIL threshold (default 3). On hitting it, the loop stops and escalates to a
   human — it never grinds forever and never "decides" to merge anyway.
6. **Never autonomously merge; prefer reversible actions; least privilege.** Loops leave work
   on a branch / open a PR for human approval. Destructive or irreversible steps are gated.
7. **Guard against comprehension debt.** Each checkpoint must include a plain-language summary
   of what changed and why, so a human can actually understand merged code instead of
   inheriting a black box.
8. **Start simple.** Reach for the smallest loop shape that fits. Add stages only when they
   demonstrably help. Over-engineered planning and monolithic agents are antipatterns.

If the user asks for a loop that violates 1, 2, or 5 (e.g. "no verifier, just let it run
forever and merge"), don't silently comply — explain the risk and offer the safe shape. They
can still override deliberately, but it should be a choice, not an accident.

## Workflow

### 1. Capture intent

Pin down, from the conversation first and the user second:
- **The goal** — what the loop is trying to accomplish, and what "done" looks like.
- **Acceptance criteria** — how a single unit of work is judged PASS/FAIL. Push for concrete,
  runnable checks. Vague criteria are the #1 failure mode; fix them here.
- **Codebase / Claude Code in scope?** Default **no**. Switch to codebase mode *only* if the
  request says to look at a repo or use Claude Code.
- **Risk surface** — does the loop touch real files, push commits, deploy? This sets how tight
  the safety gates are.

### 2. Decision checkpoint (interactive)

Before generating anything, surface the load-bearing choices and confirm them. Don't assume —
present them as a short checkpoint. The choices that actually change the output:

- **Loop shape** (see `references/loop-patterns.md` for selection):
  - *Builder + verifier* — single task, evaluator-optimizer. The default starting point.
  - *Phased build loop* — multi-phase feature with a gate per phase (Conductor Method).
  - *Queue-driven* — many tasks from a `LOOP_QUEUE.md`, one at a time.
  - *Nightly triage* — scheduled scan that **queues** work but never fixes autonomously.
- **Execution surface** — prompts-only (human drives) vs. headless Claude Code harness.
- **Conventions** — Conductor defaults (below) vs. overrides.
- **Escalation threshold** and **max iterations**.

### 3. Codebase mode (opt-in only)

Only if the request brought a repo into scope. Read before writing:
- Inventory read-only: `glob`/`grep`, `README`, `CLAUDE.md`, the build/test/lint commands,
  package manifests, CI config. Map the real subsystems.
- Derive acceptance criteria from **real commands** in that repo (the actual test runner, the
  actual linter), not invented ones.
- Then follow `references/claude-code-loops.md` to wire the headless harness (`claude -p`),
  plan mode for exploration, least-privilege tools, and stopping conditions.

### 4. Generate the loop package

Fill the templates in `assets/templates/` with the captured specifics. A full package is:

| File | Purpose |
|---|---|
| `LOOP_SPEC.md` | Goal, acceptance criteria, loop shape, limits, safety, conventions |
| `builder-prompt.md` | The maker prompt — does work, shows evidence, writes checkpoint summary |
| `verifier-prompt.md` | The checker prompt — fresh context, "close is FAIL", correctness-only |
| `LOOP_QUEUE.md` | The work queue (for queue-driven / triage shapes) |
| `run_loop.sh` | The harness that drives builder→verifier→commit with limits & escalation |
| `loop-triage.yml` | (triage only) GitHub Actions that scans and appends to the queue |

Apply Conductor defaults from `references/conductor-conventions.md`, and clearly mark each as
overridable in `LOOP_SPEC.md` so the user can dial it to their context.

For prompts-only output, emit `LOOP_SPEC.md` + the two prompts (+ queue if relevant) and skip
the harness/CI.

### 5. Self-validate (always)

Run the bundled validator on the generated package and fix anything it flags **before**
handing over:

```bash
python3 scripts/validate_loop_package.py <path-to-generated-package>
```

It checks the non-negotiables: acceptance criteria present and testable; verifier exists and is
separate from the builder; "close is FAIL" enforced; checkpoint/commit defined; max-iteration
ceiling and escalation threshold present; stopping + safety conditions present; evidence
requirement present; comprehension-debt summary required. Show the user the report.

### 6. Present

Hand over the package (the generated loop files). Point the user at `LOOP_SPEC.md` first, then
how to run `run_loop.sh`. Keep the wrap-up short.

## Conductor defaults (overridable)

Unless told otherwise, loops inherit: builder/verifier role split; `LOOP_QUEUE.md` as the work
queue; "close is FAIL"; commit checkpoint per passed unit; escalate to human after **3**
consecutive FAILs; nightly automation is **triage-only** (queues, never fixes); never auto-merge
to the default branch. Full detail and rationale in `references/conductor-conventions.md`.

## References

- `references/loop-patterns.md` — loop shapes, when to use each, antipatterns (grounded in
  Anthropic's "Building Effective Agents").
- `references/claude-code-loops.md` — headless `claude -p`, codebase exploration, GH Actions,
  the documented safeguards, evidence-based verification.
- `references/conductor-conventions.md` — the Conductor Method defaults and why they exist.

**Next steps:** After the loop package is generated and self-validated, suggest `reality-check` to
pressure-test the acceptance criteria and harness for fabricated commands or unverifiable claims
before anyone runs it, and `drift-check` if this loop joins several specs/prompts that could
contradict each other. If the user actually just needed a single Claude Code `/goal` line rather
than a whole package, point them to `goal-builder` instead. Skip the suggestion if they only
wanted a quick scaffold and are done.
