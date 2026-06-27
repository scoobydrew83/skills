# /goal mechanics (grounded in Claude Code's official docs)

Source of truth: Claude Code docs, "Keep Claude working toward a goal" (code.claude.com/docs/en/goal).
This file is the factual backbone; don't contradict it.

## What /goal does

Setting `/goal <condition>` gives Claude Code a completion condition and it keeps working across
turns until the condition is met — you don't prompt each step. Normally Claude stops when it
*judges* itself done; `/goal` adds a **separate evaluator** that checks your condition after every
turn, so completion is decided by a fresh model rather than the one doing the work. Under the
hood it's a session-scoped, prompt-based Stop hook; the evaluator is a small fast model (Haiku by
default).

Why the separation matters: if the worker graded its own work it could quietly find a shortcut
that satisfies the letter of the task while missing the intent. A separate evaluator removes that
conflict of interest.

## The evaluator only sees the transcript

This is the fact that decides whether a goal works. The evaluator **judges the condition against
what Claude has surfaced in the conversation. It does not run commands or read files on its own.**
So the condition must be provable by Claude's own printed output:
- "All tests in `test/auth` pass" works — Claude runs them and the result lands in the transcript.
- The consequence: if Claude writes "fixed" but never runs the check, the evaluator can't confirm,
  and the turn continues. The check's output has to actually be printed.

## Anatomy of a condition that holds up

1. **One measurable end state** — a test result, a build exit code, a file count, an empty queue.
2. **A stated check** — how Claude proves it: "`npm test` exits 0", "`git status` is clean".
3. **Constraints that matter** — what must not change on the way there: "no other test file is
   modified". Constraints also close cheat paths (hardcoding outputs, deleting the failing test).

Limits and bounding:
- The condition can be up to **4,000 characters**.
- There is **no built-in token budget** — it runs until the condition is met or you stop it
  (Ctrl+C or `/goal clear`). Bound it by putting a **turn or time clause in the condition**, e.g.
  "or stop after 20 turns".
- **Compound objectives overwhelm the evaluator.** Split big work ("redesign auth, add OAuth,
  write tests, update docs") into sequential goals, each with its own verifiable end state.

## Commands and lifecycle

- `/goal <condition>` — set or replace the active goal; it **starts a turn immediately** (no
  separate prompt needed). One goal active per session; a new one replaces the old.
- `/goal` — show status: condition, turns, tokens, the evaluator's most recent reason.
- `/goal clear` — remove the active goal. Aliases: `stop`, `off`, `reset`, `none`, `cancel`.
  Running `/clear` (new conversation) also drops the active goal.
- `--resume` / `--continue` restores an active goal; the condition carries over but turn count,
  timer, and token baseline reset. Achieved or cleared goals are not restored.

## Where it runs

Interactive, the desktop app, Remote Control, and non-interactive mode:
`claude -p "/goal <condition>"` runs the loop to completion headlessly (Ctrl+C to stop).
Pairs well with auto mode: auto mode removes per-tool prompts within a turn, `/goal` removes the
per-turn "keep going" — together each turn runs unattended until the condition holds.

Availability: `/goal` needs the workspace trust dialog accepted (the evaluator is part of the
hooks system). It's unavailable when `disableAllHooks` is set at any level, or when
`allowManagedHooksOnly` is set in managed settings — the command tells you why rather than
silently doing nothing.

## /goal vs /loop vs Stop hooks

- **/goal** — re-runs the moment a turn finishes; stops when the evaluator confirms a condition.
  Best for a defined end state: migrations, refactors, getting a suite green, draining a queue.
- **/loop** — re-runs a prompt on a time interval (every N minutes). Best for polling/periodic
  work (watch a deploy, summarize new comments). Not for "finish this refactor."
- **Stop hook** — deterministic, permanent, lives in settings and applies to every session in
  scope. Use when you want a fixed rule after every turn (e.g. always run `tsc --noEmit`).

## Reliability tips

- A `CLAUDE.md` at the project root (build/test/lint commands, conventions) makes goal runs more
  reliable, since every turn inherits that context.
- Make sure the condition names a check whose **output Claude will print** — phrase it around
  observable output, not internal state.
- Add the cheat-closing constraints up front; don't wait for the model to find the shortcut.
