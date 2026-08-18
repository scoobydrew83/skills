# Loop patterns and selection

Grounding: Anthropic, *Building Effective Agents*; the evaluator-optimizer pattern; the
Claude Code agentic loop. Pick the **smallest shape that fits** — complexity is only worth
adding when it demonstrably improves outcomes.

## The underlying loop

Every loop here is the agentic loop: **gather context → take action → verify → repeat**, with
a hard stop. The verification step is what separates a loop from a one-shot prompt, and it must
be done by something other than the actor.

## Shape 1 — Builder + verifier (evaluator-optimizer)

One step generates work; a second, separate-context step evaluates it against criteria and
returns PASS/FAIL with specific feedback. On FAIL the feedback feeds the next build attempt.

- **Use when:** a single, well-specified task with a clear, checkable definition of done, and
  where iteration measurably improves the result (the classic "draft → critique → revise").
- **Termination:** verifier returns PASS, or the iteration ceiling is hit.
- **This is the default.** Start here unless the task obviously needs more structure.

## Shape 2 — Phased build loop (Conductor Method)

A multi-phase feature broken into ordered phases, each with its own acceptance criteria and a
**gate** (the verifier) before the next phase starts. A commit checkpoint closes each phase.

- **Use when:** the work is too big for one build/verify cycle and has natural stages (design →
  scaffold → implement → test → wire-up), and you want the human to retain authorization at
  phase boundaries.
- **Termination:** all phases pass, or a phase fails its gate past the escalation threshold.

## Shape 3 — Queue-driven (multi-task)

A `LOOP_QUEUE.md` holds many independent tasks. The loop pulls one, runs builder+verifier,
commits on PASS, marks it done, and moves on.

- **Use when:** a backlog of similar, independent units (lint fixes, migrations across many
  files, batch refactors).
- **Termination:** queue empty, ceiling hit, or escalation.
- Generate the task list with a script when the units are mechanical (e.g. "every file that
  imports X") rather than hand-listing them.

## Shape 4 — Nightly triage (scan, don't fix)

A scheduled job scans a signal (failing tests, new issues, dependency alerts) and **appends**
candidate work to `LOOP_QUEUE.md` with context. It does **not** run the fixer loop. A human
reviews the queue and authorizes the actual loop.

- **Use when:** you want continuous awareness without unattended changes landing overnight.
- This is the safe default for anything scheduled — autonomy on a timer compounds early
  mistakes silently before anyone notices.

## The other workflow primitives (for composition)

Loops often sit inside larger flows. Keep these in your pocket but don't reach for them by
reflex:
- **Prompt chaining** — fixed sequence, each step's output feeds the next. Good when steps are
  deterministic and ordered.
- **Routing** — classify the input, send it to the right handler.
- **Parallelization** — fan out independent subtasks, then synthesize.
- **Orchestrator-worker** — a coordinator decomposes and delegates to workers.

A real system mixes these (a triage job may route; a phased loop may parallelize within a
phase). Start sequential; add a primitive only when the simpler version breaks.

## Antipatterns to refuse or flag

- **No verifier / self-grading.** The actor approving its own work defeats the loop.
- **Soft acceptance criteria.** If PASS/FAIL isn't cleanly decidable, the loop is circular.
- **No stop condition.** Infinite or unbounded loops burn tokens and compound errors.
- **Autonomous merge / irreversible actions unattended.** Leave it on a branch for a human.
- **Monolithic agent doing everything in one context.** Split roles; keep contexts focused.
- **Over-engineered planning.** Don't generate a 12-stage plan for a 2-step task.
- **Missing observability.** If you can't see what each step did (evidence, logs), you can't
  trust or debug the loop.

## When a loop is the wrong tool

If first-attempt quality already meets the bar, or the task is high-frequency and low-
complexity (deterministic code is cheaper and faster), or there's no clear evaluation
criterion, don't build a loop. Say so and offer the simpler path.
