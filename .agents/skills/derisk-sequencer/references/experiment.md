# Single experiment: pre-register one falsifiable test

Use this when one risky question needs one test whose verdict will be believed,
or when the first step of a de-risk sequence needs its pass/fail bar locked.

## Contents
- The rule and the two failure modes
- Workflow (steps 1–5)
- Output template
- Honesty rules

## The rule

> **Fix the pass/fail bar before the run. Then don't move it.**

A threshold chosen after seeing data is a justification, not a threshold. This
method front-loads every judgment call to a moment with no result to defend.
It targets two failure modes:
- **The un-falsifiable hypothesis.** If no result would make you abandon the
  idea, it isn't an experiment.
- **The confounded test that lies.** An optimization tuned for speed can pass
  while wrong if correctness was never the controlled baseline.

## The workflow

### Step 1 — Isolate the one question
Reduce the situation to a single decisive, falsifiable question. One experiment tests one thing. If there are several live questions, pick the one with the highest **risk ÷ cost-to-test** and test that first (ordering several tests is the main SKILL.md workflow). A question is decisive if its answer actually changes what you do next; if no answer would change your behavior, don't run it.

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
python3 scripts/falsifiability_linter.py <your-prereg.md>
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
