# Conductor conventions (the overridable defaults)

These are the defaults a generated loop inherits unless the user overrides them. Each is marked
overridable in `LOOP_SPEC.md`. They exist to keep loops honest, bounded, and human-authored at
the points that matter. None of them are arbitrary — the rationale is given so you can adapt
rather than copy.

## Roles: builder (maker) and verifier (checker)

Two separate roles, two separate contexts. The **builder** does the work and produces evidence.
The **verifier** judges that evidence against acceptance criteria and nothing else. The human
remains the authorization point at checkpoints — the verifier subagent doesn't replace the
human, it removes the "actor grading itself" gap so the human is reviewing a real second
opinion instead of a self-report.

## "Close is FAIL"

The verifier's hard rule. If the work *mostly* meets the criteria, that is a FAIL, not a pass
with notes. Partial credit is exactly how loops drift away from the goal one acceptable-looking
increment at a time. Acceptance criteria must be concrete enough that "close" is even decidable.

## Escalate to a human after 3 consecutive FAILs

The builder gets the verifier's feedback and retries. After **3** consecutive FAILs on the same
unit, stop and escalate — write the failure context to an escalation log (or open an issue) and
halt that unit. Three is a default: enough for the builder to recover from a bad first attempt,
few enough that it doesn't thrash. Override per task risk.

## Commit checkpoint per passed unit

Each unit that passes the verifier gets its own commit: small, one goal, reviewable, with a
message that captures what changed and why. This is the rollback point and the audit trail.

## Comprehension-debt guard

Loop-generated code that merges without anyone understanding it is a named risk. So every
checkpoint requires a **plain-language summary**: what changed, why, and anything the human
should know before relying on it. The verifier confirms the summary exists and is real before
PASS. The goal is that a human can read the checkpoint and actually understand the code, not
inherit a black box — especially important when deeply understanding the codebase is itself a
goal of the project.

## Nightly automation is triage-only

Scheduled jobs **queue** work; they never run the fixer loop. Autonomy on a timer compounds an
early mistake silently across a whole run before anyone is awake to catch it. Keep the unattended
part to scanning, annotating, and appending to `LOOP_QUEUE.md`; keep the fixing human-authorized.

## Never auto-merge to the default branch

Loops leave work on a branch and open a PR. A human merges. Reversible by default; irreversible
steps (merge, deploy, delete, schema migration) are explicit human decisions.

## LOOP_QUEUE.md as the work queue

A single human-readable Markdown queue is the source of truth for multi-task and triage loops.
It's editable by hand, diffable in git, and doesn't require a database. Each entry carries the
task, its acceptance criteria (or a pointer to them), status, and FAIL count.

## How to override

In `LOOP_SPEC.md`, every default sits under an **Overridable** column or note. To change one,
the user edits the spec and reruns the validator — the validator enforces that the
*non-negotiables* (a verifier exists, criteria are testable, a stop condition exists) survive any
override, while letting the tunable values (threshold count, which branch, triage vs. active)
change freely.
