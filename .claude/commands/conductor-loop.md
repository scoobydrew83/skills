---
name: conductor-loop
description: Run the conductor-builder → conductor-verifier maker/checker pattern on a task.
argument-hint: <task description>
---

# /conductor-loop $ARGUMENTS

Fire the existing maker/checker pair against the task described in
`$ARGUMENTS`. This is glue, not new logic — the actual work lives in the
two agent definitions: `conductor-builder` and `conductor-verifier`. In the
Marketplace plugin, invoke their namespaced forms when Claude exposes them.

Steps:

1. Confirm the task in `$ARGUMENTS` has acceptance criteria. If not, ask the
   user to add them before invoking the loop (the verifier needs them to
   grade against).
2. Read the installed `loop-creator` and `next-step` skills for the
   portable protocol — especially worktree/branching rules and FAIL escalation.
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
7. Learn, once the loop stops (PASS, BLOCKED, or escalation):
   - Append one line to `MEMORY_BANK.md` in the CONVENTIONS.md §4 format:
     `- YYYY-MM-DD · conductor-loop · <verdict> · <one-line lesson>`. If the
     same lesson is already there, append it again with `(repeat)` at the end
     so `harness-improver` can count it. Skip the line only when the run
     taught nothing new and passed first time.
   - Check `.harness/EVIDENCE.jsonl` for a row from this run. The project's
     `SubagentStop` hook (`tools/hooks/record-evidence.sh`) writes one per
     verifier verdict. If no row is there (the hook isn't installed, as in
     the Marketplace plugin), append one yourself with the keys `run_id`,
     `item_id`, `phase`, `actor`, `checks`, `verdict`, `next`.
   - Never write rules into `AGENTS.md` from this step. Rule changes go
     through `harness-improver` as a reviewed PR.

Do not invent new loop semantics. If the protocol needs to change, edit
`CONDUCTOR-LOOP-GUIDE.md` first and rerun.
