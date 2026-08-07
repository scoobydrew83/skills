# How to use this system

**The short version:** you have an idea and a PRD. Run these seven skills in
order. Each one tells you the next when it finishes.

```
hemlock → conductor-init → visual-plan → agent-orchestration
        → reality-check → drift-check → conductor-memory
```

That's it. The rest of this page is detail you can take or leave.

---

## First: pick your path

You don't always need the whole chain. **Three paths, smallest to largest.**

| Your situation | What to run | Roughly |
|---|---|---|
| One specific job ("write me a system prompt") | That one skill, alone | minutes |
| **New idea + PRD** ← *you are here* | The seven-step chain below | a session or two |
| "Iterate until it passes", unattended | `loop-creator` + `goal-builder`, then `/conductor-loop` | setup, then hands-off |

Skills are self-contained. Nothing forces you to run the rest.

---

## Before you start

**Install once:**

```
/plugin marketplace add scoobydrew83/skills
/plugin install coordinated-skills@scoobydrew-skills
```

After that every skill is namespaced: `/coordinated-skills:hemlock`.

**Two things that will otherwise surprise you:**

1. **Nothing auto-chains.** Each skill ends by naming its likely successor.
   Claude surfaces that suggestion. **You** decide whether to run it. There is
   no "start coordination" command, because coordination isn't a mode.
2. **Shared state is opt-in.** Skills read `CONTEXT.md` and `MEMORY_BANK.md`
   *only if those files exist*. Step 2 creates them. Skip step 2 and the
   skills still work — they just won't pass state to each other.

---

## The seven steps

### Step 1 of 7 — Kill the idea first

```
/coordinated-skills:hemlock
```

Point it at your PRD. It runs a 6-rung kill ladder: name the incumbent, rank
your riskiest assumption, design the cheapest test that kills the idea, write
the kill bar **before** you run the test, run it, verdict.

It will refuse to authorize building until every rung is climbed. That refusal
is the feature.

**Done when:** you have a verdict and a written kill bar.
**Rough time:** 15–30 min of real thinking, not typing.

> **Why this comes first:** the riskiest thing about a new project is the
> premise, not the code. A PRD is a description of what you'd build, not
> evidence that you should.

---

### Step 2 of 7 — Set up the repo

```
/coordinated-skills:conductor-init
```

Turns your PRD into machine-readable ground truth:

- `FEATURES.json` — features seeded from the spec, each with acceptance criteria
- `CONTEXT.md` and `MEMORY_BANK.md` — the shared-state files everything else reads
- A verified one-command test and one-command lint
- A baseline commit: `loop(0): baseline green + criteria defined`

**Done when:** test and lint both pass on a clean checkout, baseline commit landed.
**Rough time:** 20–45 min, longer if the repo has no test command yet.

**Skip this step if:** you're doing a one-off and don't want the loop. Everything
downstream still runs, just without shared state.

**Safe to ignore:** it may report a half-finished Phase 0 and repair it. That's
normal on an existing repo.

---

### Step 3 of 7 — Make the plan reviewable

```
/coordinated-skills:visual-plan
```

Renders your plan as typed blocks — diagrams, wireframes, decisions, annotated
real code, open questions — into a local `plan.html` built entirely from ground
truth (`FEATURES.json`, git, telemetry). Not a markdown dump.

You review **in the page**. Pinned comments land in a tracked `comments.jsonl`
and **block the features they cite** until you resolve them with an answer.

**Done when:** no unresolved blocking comments.
**Rough time:** 10 min to generate, however long your review takes.

---

### Step 3.5 — Only if unknowns survived step 1

Optional detour. Skip if hemlock left nothing open.

- **One unknown to test** → `/coordinated-skills:experiment-designer`
  (locks the threshold before the run)
- **Several unknowns to order** → `/coordinated-skills:derisk-sequencer`
  (sequences the tests cheapest-decisive-first)

Then come back to step 4.

---

### Step 4 of 7 — Build it

```
/coordinated-skills:agent-orchestration
```

This is the execute phase. It produces the actual deliverable.

**Alternatives if that's not the shape of your work:**

| You're building | Use instead |
|---|---|
| An unattended "run until it passes" loop | `loop-creator`, then `goal-builder` |
| A system prompt | `system-prompt-builder` |
| Reusable prompts for this codebase | `prompt-template-generator` |
| A troubleshooting runbook | `repo-troubleshooting-guide` |

**Done when:** the thing exists and your tests pass.

---

### Step 5 of 7 — Check for fabrication

```
/coordinated-skills:reality-check
```

Hunts hallucinated packages, invented CLI flags, fake file paths, imaginary
config keys, made-up "best practices." Anything checkable that could have been
confabulated.

**Done when:** you get a verdict block: `PASS`, `FAIL`, or `BLOCKED`.
**On FAIL:** fix what it names, run it again. Do not proceed.

---

### Step 6 of 7 — Check for contradictions

```
/coordinated-skills:drift-check
```

Different job from step 5. This one compares your documents against each other
and against the code: does the PRD still match the plan? Does the plan still
match what got built? Does the README still describe reality?

**Done when:** `PASS` verdict, or you've accepted the drift deliberately.

> **The rule the whole library enforces:** the doer never grades its own work,
> and *close is FAIL*. That's why steps 5 and 6 are separate skills, not a
> self-review at the end of step 4.

---

### Step 7 of 7 — Save state for next time

```
/coordinated-skills:conductor-memory
```

Snapshots what happened into `MEMORY_BANK.md` so a cold session tomorrow picks
up without you re-explaining anything.

**Done when:** `MEMORY_BANK.md` reflects this session.

**This is the last step.** The chain is complete.

---

## Cheat sheet

**"I'm at ___, what do I run?"**

| Where you are | Run |
|---|---|
| Just had the idea | `hemlock` |
| Idea survived, need a repo | `conductor-init` |
| Need to see and approve the plan | `visual-plan` |
| One assumption to test | `experiment-designer` |
| Many assumptions to order | `derisk-sequencer` |
| Ready to build | `agent-orchestration` |
| Built it, is any of it made up? | `reality-check` |
| Built it, do the docs still match? | `drift-check` |
| Adding a dependency | `leftpad` |
| Making a breaking change | `grandfather` |
| Handling untrusted input | `tinfoil` |
| About to merge something you didn't write | `popquiz` |
| Wrapping up | `conductor-memory`, then `session-bookend` |
| Project's over | `project-postmortem` |
| Too big, don't know where to start | `overwhelm-breakdown` |

---

## The lazy version

For a small idea, four steps is enough:

```
hemlock → visual-plan → build → reality-check
```

Skip `conductor-init` unless you actually want the maker/checker loop. It's
real Phase 0 setup work, not free.

---

## Your next action

Run this, with your PRD to hand:

```
/coordinated-skills:hemlock
```

---

## Where the detail lives

Everything above is the fast path. If you want the full picture:

- **[README.md](README.md)** — the three usage modes, in prose
- **[CONVENTIONS.md](CONVENTIONS.md)** — the contract every skill follows;
  §4 defines the shared-state files
- **[skill-graph.md](skill-graph.md)** — auto-generated map of all 26 skills,
  their phases, and every handoff edge
- **[CONDUCTOR-LOOP-GUIDE.md](CONDUCTOR-LOOP-GUIDE.md)** — the maker/checker loop
- **[CONTRIBUTING.md](CONTRIBUTING.md)** — adding your own skill

If this page ever disagrees with `skill-graph.md`, **the graph wins** — it's
generated from the skill directories themselves.
