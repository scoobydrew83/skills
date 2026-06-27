---
name: goal-builder
description: Turn a vague intent into a correct, transcript-verifiable Claude Code /goal condition through a short question-and-answer interview, then (when the pattern recurs) crystallize it into a reusable .claude/commands/ slash command. Use whenever the user wants to write, fix, or improve a /goal command, set a completion condition, "keep Claude working until X", run an unattended/until-it-passes Claude Code session, or says their /goal "just keeps looping" or "stops too early". Trigger even if they don't say "goal" but describe wanting Claude Code to loop on its own until a measurable end state holds. The point is to stop them writing a PROMPT ("clean up my code") when /goal needs a CONDITION ("npm test exits 0, without editing the test file"), and to refuse any goal whose finish line a transcript-reading evaluator can't check. For crafting the single /goal line; to build a full builder/verifier loop package (spec, prompts, harness, CI) use loop-creator.
phase: execute
hands_off_to: [loop-creator]
reads: []
writes: []
---

# Goal Builder

Helps a user write a Claude Code `/goal` condition that actually works, by interview. The
deliverable is a ready-to-run `/goal …` line (and, when the pattern recurs, a reusable
`.claude/commands/` command). Read `references/goal-mechanics.md` for how `/goal` works and
`references/good-vs-bad-goals.md` for the worked examples.

## The one idea that makes or breaks a goal

`/goal` keeps a Claude Code session looping across turns until a **separate evaluator** (a fresh,
fast model — not the one doing the work) confirms your condition holds. The evaluator **only
reads the transcript**: it does not run commands or open files. So the condition must be
something Claude's own *printed output* can prove.

That single fact is why people get `/goal` wrong: they write a **prompt** (open-ended, judged by
a human) when `/goal` needs a **condition** (resolves to yes/no from the transcript). "Clean up
my code" has no checkable finish line, so the loop either churns forever or quietly declares
victory. "`npm test` exits 0" works, because Claude runs it and the result lands in the
transcript for the evaluator to read.

A durable condition (per Anthropic's docs) has three parts, and is bounded:
1. **A measurable end state** — a test result, a build exit code, a file count, an empty queue.
2. **A stated check** — how Claude should prove it (`npm test` exits 0, `git status` is clean).
3. **Constraints that must hold** — what must not change on the way there (and what would count
   as cheating the check).
Plus a **turn/time cap** so a goal that can't be reached stops instead of burning tokens.

Your job in this skill is to extract those parts through Q&A and **refuse to ship a goal whose
finish line the evaluator can't check** — instead help the user find a real check, or tell them
`/goal` is the wrong tool here.

## Interview workflow

Ask in small clusters — one idea at a time, with a concrete example — not a wall of questions.
On Claude.ai use the tappable question tool; in Claude Code ask inline. Pull anything the
conversation already told you instead of re-asking.

### Phase 1 — Find the real end state
"When this is genuinely done, what is observably *different*?" Push from adjectives to facts. If
they say "clean" / "production-ready" / "better" / "robust," that's a prompt, not a condition —
dig: does "clean" mean the linter reports zero errors? the suite passes? a file is gone? Keep
going until the end state is something that could be observed, not judged.

### Phase 2 — Name the check
"What single command or observation, once Claude prints it, flips this from *no* to *yes*?"
Examples: `npm test` exits 0; `pytest -q` passes; `rg 'getUser' src | wc -l` is 0; `git status`
is clean. If they can't name one, the goal isn't ready: either find a proxy check, split the
goal (Phase 4), or stop and say `/goal` is the wrong fit (suggest a normal prompt + human review,
or a deterministic Stop hook). Remind them the check's **output must actually be printed** — if
Claude writes "fixed" without running it, the evaluator can't confirm.

### Phase 3 — Close the cheat door
"How could a lazy or over-eager model technically pass that check while missing what you meant?"
The classic: make the test pass by hardcoding the expected output, deleting the failing test, or
adding `eslint-disable`. Turn each into a constraint: "without modifying the test file," "without
hardcoding the printed values," "no test is skipped or disabled." This is the guard against the
model gaming the task — the same reward-hacking risk Anthropic documents in system cards.

### Phase 4 — Scope and bound
"Is this one verifiable end state, or several?" A compound objective ("redesign auth, add OAuth,
write tests, update docs") overwhelms the evaluator — split it into **sequential goals**, each
with its own end state, run one at a time (only one goal is active per session). Then add a
**turn or time cap** ("or stop after 20 turns") so it can't run away — there is no built-in token
budget.

### Phase 5 — Assemble and lint
Compose the single-line condition: end state + stated check + constraints + cap. Keep it under
4,000 characters. Then run the linter and fix anything it flags:

```bash
python3 scripts/check_goal.py "<the goal condition text>"
```

It checks for a concrete checkable signal, flags vague/unverifiable language, warns on missing
constraints or cap, detects compound goals, and enforces the length limit. Show the user the
report and the final goal.

### Phase 6 — Make it reusable (when the pattern recurs)
If this goal is a shape they'll want again (e.g. "get the suite green on any branch"), crystallize
it into `.claude/commands/<name>.md` from `assets/templates/slash-command.md.template`, using
`$ARGUMENTS` (or `$1`, `$2`) for the parts that change per run — the check command, the file to
protect. Then they invoke `/<name>` instead of retyping the goal.

## Present

Give the user, concisely:
- The ready-to-run line: `/goal <condition>` (and the headless form
  `claude -p "/goal <condition>"` if they're scripting it).
- One or two sentences on why it's checkable from the transcript.
- For compound work: the ordered list of sequential goals to run one at a time.
- For recurring patterns: the saved command file and how to call it.

Don't over-explain. The value is the correct condition, not a lecture.

## References

- `references/goal-mechanics.md` — how `/goal` works, the commands, limits, reliability tips,
  and `/goal` vs `/loop` vs Stop hooks (grounded in Claude Code's official docs).
- `references/good-vs-bad-goals.md` — before/after examples: prompt vs condition, the cheat
  problem, compound → sequential.

**Next steps:** Once the user has a working `/goal` condition and wants Claude to run it
unattended through a real build/verify cycle — or the goal turned out to be compound and needs a
multi-stage harness rather than a single line — suggest `loop-creator` to scaffold the full loop
package (spec, builder/verifier prompts, queue, harness, CI). Skip if they just wanted the one
condition and are ready to run it.
