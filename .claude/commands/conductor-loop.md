---
name: conductor-loop
description: Run the conductor-builder → conductor-verifier maker/checker pattern on a task.
argument-hint: <task description>
---

# /conductor-loop $ARGUMENTS

Fire the existing maker/checker pair against the task described in
`$ARGUMENTS`. This is glue, not new logic — the actual work lives in the
two agent definitions at the repo root: `conductor-builder.md` and
`conductor-verifier.md`.

Steps:

1. Confirm the task in `$ARGUMENTS` has acceptance criteria. If not, ask the
   user to add them before invoking the loop (the verifier needs them to
   grade against).
2. Read `CONDUCTOR-LOOP-GUIDE.md` for the current loop protocol —
   especially the worktree/branching rules and the FAIL escalation policy.
3. Invoke `conductor-builder` (as a subagent) with:
   - The task description
   - The acceptance criteria
   - A pointer to `CONTEXT.md` and `MEMORY_BANK.md`
4. When the builder reports completion, invoke `conductor-verifier` (as a
   subagent) with the same context plus the builder's handoff block.
5. On `Conductor verdict: PASS`, surface the verdict and stop. On `FAIL`,
   route the REQUIRED FIXES list back to `conductor-builder` for another
   pass. On `BLOCKED`, surface what would unblock it and stop — don't loop.
6. After 3 consecutive FAILs on the same task, STOP and escalate to the
   human with both the latest builder handoff and the verifier report.

Do not invent new loop semantics. If the protocol needs to change, edit
`CONDUCTOR-LOOP-GUIDE.md` first and rerun.
