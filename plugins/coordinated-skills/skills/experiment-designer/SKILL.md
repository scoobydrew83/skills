---
name: experiment-designer
description: Design a single falsifiable experiment with its pass/fail threshold fixed BEFORE the run, so a result can't be rationalized after the fact. Use whenever someone has a hypothesis or risky assumption and is about to just try it and see — "how do I test whether X", "design an experiment for this", "is this optimization worth it", "how would I prove or disprove this", "what would falsify this", or any "let me just run it and look at the numbers" with no threshold named. The method isolates the one decisive question, states the hypothesis and its negation, fixes a numeric metric and a PASS/FAIL/KILL rule up front, picks the cheapest decisive design, controls the confound that would make the result lie (optimization-before-correctness especially), and emits a dated pre-registration plus a falsifiability check. Distinct from reality-check (verifies an existing plan's claims), goal-builder (writes Claude Code /goal conditions), and idea-validator (whole-idea GO/NO-GO); this designs one test and locks its bar.
phase: plan
hands_off_to: [idea-validator, derisk-sequencer]
reads: []
writes: []
---

# Experiment Designer

Turn one risky question into one experiment whose verdict you'll actually believe — because you wrote down what would change your mind *before* you looked at the result.

The one rule everything serves:

> **Fix the pass/fail bar before the run. Then don't move it.**

That single discipline is the difference between a test that informs a decision and a number you rationalize past. The most creditable thing a doomed project can do is die on a bar it set in advance; the most common way good evidence gets wasted is moving the bar once the number is in.

---

## Why this exists

When the result arrives, you are the most biased you will ever be about it — you've now got effort, hope, and a half-built thing riding on it. A threshold chosen *after* seeing data isn't a threshold, it's a justification. So this skill front-loads every judgment call (what we're testing, what counts as pass, what would kill it) into a moment when you have no result yet and therefore nothing to defend.

Two failure modes it specifically targets:
- **The un-falsifiable hypothesis.** "I think this will help" with no number and no fail branch can't be run, only believed. If you can't say what result would make you *abandon* the idea, you don't have an experiment.
- **The confounded test that lies.** An optimization tuned for speed can ship a confident wrong answer if correctness was never the controlled baseline. A test that can pass while being broken is worse than no test.

## When to reach for this vs neighbors

- **idea-validator** decides a whole idea's GO/NO-GO and may *spawn* several experiments. This skill designs *one* of them rigorously.
- **goal-builder** writes a Claude Code `/goal` completion condition (when an agent loop should stop). This designs a *measurement that settles a question*, which is different.
- **reality-check** verifies claims in an *already-written* plan. This builds the test *before* there's a result.

---

## The workflow

### Step 1 — Isolate the one question
Reduce the situation to a single decisive, falsifiable question. One experiment tests one thing. If there are several live questions, pick the one with the highest **risk ÷ cost-to-test** and test that first (and if the whole sequence needs ordering, that's `derisk-sequencer`'s job). A question is decisive if its answer actually changes what you do next; if no answer would change your behavior, don't run it.

### Step 2 — State the hypothesis and its negation
Write **H1** (what you believe) and **H0** (the null / what "it doesn't work" looks like) in plain terms. The test: *what observable result would make H1 false?* If you can't answer, stop here — the idea isn't testable yet, and that itself is the finding.

### Step 3 — Fix the metric and the decision rule (before running)
Name one primary metric, numeric where possible, and write the rule as branches:
- **PASS if** `<metric meets threshold>`
- **FAIL / KILL if** `<metric misses threshold>`
- (optional) **INCONCLUSIVE if** `<underpowered / noisy>` → and what you'll do then.

Vague verbs are not thresholds. "Improves," "seems faster," "works better" must become "≥15% lower p95 latency on N=500 requests" or they don't count. This is the pre-registered core; protect it.

### Step 4 — Choose the cheapest design that's still decisive
- **Emulator beats full build.** The decisive answer rarely needs the real system — a one-page emulator or a hand-built sample often settles it for a fraction of the cost.
- **Decouple confounds.** If two things vary at once, the result can't be attributed. Hold the suspected confound fixed. Especially: **validate correctness before measuring speed** — never let an optimization path be the thing under test until the slow, obviously-correct path is the proven baseline it must match.
- **Power.** State the sample size and be honest about what it can and can't show. A small n is fine if you *label* it small.

### Step 5 — Pre-register and lock it
Emit the pre-registration artifact (template below), dated, with the **Result section left empty**. That emptiness is the proof the bar predates the data. After the run you fill in only the Result and Verdict — you do not touch the threshold. If reality forces a redesign, that's a *new* pre-registration with a new date, not an edit to this one.

Run the bundled check to catch the usual gaps:
```bash
python scripts/falsifiability_linter.py <your-prereg.md>
```
It flags a missing numeric threshold, a missing FAIL/KILL branch, an un-empty Result in a doc still labeled pre-registration, an unstated sample size, and criteria that rest only on vague verbs.

---

## Output template

```markdown
# Pre-registration — <question in one line>
**Date:** <YYYY-MM-DD>  **Status:** PRE-REGISTERED (result not yet observed)

## Question
The one decisive thing this settles:

## Hypotheses
- H1 (believed):
- H0 (null / "doesn't work" looks like):
- Falsifier — the result that would make me abandon H1:

## Metric & decision rule (FIXED before run)
- Primary metric:
- PASS if:
- FAIL / KILL if:
- INCONCLUSIVE if:  → then I will:

## Design
- Cheapest decisive setup (emulator/sample/etc.):
- Sample size / power (honest about limits):
- Confound held fixed (e.g., correctness validated before measuring speed):

## Result  ← leave empty until the run is done
- 
## Verdict  ← fill only after Result; do NOT edit the rule above
- 
```

## Honesty rules
- **No goalpost-moving.** Changing the threshold after seeing data converts an experiment into a sales pitch. If you must change the design, re-register fresh.
- **Report power; don't invent it.** "n=4, underpowered" honestly stated beats a confident fabricated rate. An inconclusive result is a real, reportable outcome.
- **A passing test that could pass while broken is a failed design.** If the metric can be green on a wrong implementation, the metric is wrong — fix the design before running.

---

**Next steps:** Once the experiment is designed and run, suggest `idea-validator` if this test was one leg of a whole-idea GO/NO-GO decision, or `derisk-sequencer` if it's one of several experiments that still need ordering into a build-after-test sequence. Skip if the user only needed this one test designed.
