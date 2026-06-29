---
name: derisk-sequencer
description: Turn a validated idea into a risk-ordered sequence of experiments and build steps, with one hard rule — no product code is scheduled before the test that de-risks it. Use whenever someone has an idea worth building and asks what to do in what order — "what should I build first", "what order do I tackle this", "sequence this plan", "de-risk this roadmap", or presents a build plan that front-loads construction ahead of validation. The method lists the load-bearing assumptions, scores each by risk divided by cost-to-test, orders experiments cheapest-decisive first with kill-gates between them, places every build step after its unlocking test, and defers governance, breadth, and optimization until their gates clear — then emits an ordered sequence and a linter that flags build-before-its-test. Distinct from task-decomposition and overwhelm-breakdown (which collapse a big task to one next step for momentum) and agent-orchestration (which sequences build phases); this sequences de-risking ahead of building.
phase: plan
hands_off_to: [experiment-designer, agent-orchestration]
reads: []
writes: []
---

# De-risk Sequencer

Given something worth building, decide **what order to attack it in** so that the cheapest tests that could kill the project run before the expensive construction that assumes the project lives.

The one rule everything serves:

> **Every build step comes after the test that de-risks it. No construction before its validation.**

This is the direct antidote to the most expensive mistake in software: build-first, validate-last. The pattern that wastes weeks is de-risking the parts that were never in doubt (can we build it? — usually yes) while the load-bearing doubt (is it needed? does it beat what exists? does the hard assumption hold?) sits untested until there's too much built to walk away from.

---

## Why this exists

Risk doesn't retire evenly. A plan has a few assumptions that, if false, kill everything — and a lot of work that only matters if those hold. Sequencing by *what's easy to start* or *what's exciting* puts construction first and validation last, which is exactly backwards: you pay the big costs before learning whether they were warranted.

Sequencing by **risk retired per unit cost** flips it. You spend the first, cheapest hours buying down the biggest uncertainties. Most plans that are going to fail, fail at a cheap test you could have run first — so running it first is nearly free insurance, and a NO here saves the entire build.

## When to reach for this vs neighbors

- **task-decomposition / overwhelm-breakdown** collapse a big, vague, overwhelming thing down to *one doable next step* — they optimize for momentum and emotional unblocking. This skill is colder and analytical: it orders the *whole* sequence by risk, and its "first step" is whatever retires the most risk cheapest, which is not always the most motivating thing.
- **agent-orchestration** sequences the *phases of construction* (design → plan → implement → test → deploy). This sequences *validation ahead of construction* — a different axis. Often you run this skill first, then orchestrate the build of whatever survives.
- **idea-validator** produces the GO and the ranked assumptions; this turns that ranking into an executable order. They share the same risk ÷ cost-to-test currency on purpose.

---

## The workflow

### Step 1 — List the load-bearing assumptions
Inherit them from an idea-validator run if one exists, or surface them now. A load-bearing assumption is one where *false → the project doesn't work or doesn't matter*. Convenience assumptions ("we'll use Postgres") aren't load-bearing; differentiation and demand and the hard technical "can this even be done" usually are.

### Step 2 — Score each by risk ÷ cost-to-test
- **Risk** = (fatal if false?) × (how likely to be false). A non-fatal or near-certain assumption scores low even if it's important-sounding.
- **Cost-to-test** = effort to get a real answer. A web search or a one-page emulator is cheap; a built feature is not.
- Rank by **risk ÷ cost-to-test**. The top of that list — high-risk *and* cheap-to-test — is where you start.

### Step 3 — Order the experiments, cheapest-decisive first, with kill-gates
Lay the validating experiments in order. Between each, a **kill-gate**: if this test fails its (pre-registered) bar, you stop — you do *not* proceed to the next step or its build. When two unknowns must both hold, test the cheaper, more decisive one first so a failure ends things before you pay for the expensive leg.

### Step 4 — Place build steps after their unlocking test
Every construction task names the validation that unlocks it. A build step with no prior validating test is the smell this skill exists to catch — it means you're building on an unchecked assumption. Rewrite the sequence so the test comes first.

### Step 5 — Defer the success-problems
Governance, open protocols, multi-platform breadth, and performance optimization are answers to problems you only have if the thing succeeds. Schedule them *after* the gate that proves the success, not before:
- **Governance / protocol / breadth** → after product-market validation. Building capture-resistance for a product with no proven need is scaffolding on sand.
- **Optimization** → after a correct baseline exists. Optimizing before correctness is validated is a correctness-bug generator.

### Step 6 — Emit the sequence and lint it
Produce the ordered table (template below) and run:
```bash
python scripts/sequence_linter.py <your-sequence.md>
```
The linter flags any build step with no `unlocked-by` test, any governance/breadth/optimization step scheduled before its gate, and any step missing a kill-condition.

---

## Output template

Emit a table where every row is a step. `Type` is `test`, `build`, or `defer`. `Unlocked-by` names the prior step (by number) whose pass is required first; tests that gate the project can say `—`. `Kill-if` states what result stops the sequence here.

```markdown
# De-risk sequence — <project>

| # | Step | Type | Unlocked-by | Kill-if |
|---|------|------|-------------|---------|
| 1 | Search incumbents; name the axis we beat them on | test | — | a competitor already ships this on our axis |
| 2 | One-page emulator vs incumbent on the hero case | test | 1 | we're not measurably better on the axis |
| 3 | Build the minimal core (the differentiated slice only) | build | 2 | — |
| 4 | Optimize the hot path | defer | 3 (correct baseline exists) | optimization changes the output |
| 5 | Governance / protocol | defer | PMV gate | — |

**Risk-retirement order (why this sequence):** step 1 is highest risk ÷ cheapest test, so it runs first; no build (step 3) is scheduled before its unlocking test (step 2); success-problems (4, 5) are deferred behind their gates.
```

## Honesty rules
- **A motivating first step is not the same as the right first step.** If the cheapest decisive test is boring, it still goes first. (If the person is stuck/overwhelmed rather than mis-sequenced, hand off to overwhelm-breakdown — momentum is a different need than risk-ordering.)
- **Don't smuggle build work into a "test" label.** A "test" that requires building the product isn't a cheap de-risking step; be honest about cost so the ordering stays valid.
- **Deferring isn't dropping.** Governance and optimization are real and scheduled — just behind the gate that earns them.

---

**Next steps:** With the sequence in hand, suggest `experiment-designer` to lock the pass/fail bar on the first de-risking test before it runs, then `agent-orchestration` to sequence the build of whatever survives the kill-gates. Skip if the ordering was all the user wanted.
