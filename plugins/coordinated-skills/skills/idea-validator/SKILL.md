---
name: idea-validator
description: Pressure-test whether an idea, product, or feature is worth building — BEFORE sinking days into it. Use whenever someone weighs building something and the real risk is the premise rather than the code. Triggers include "should I build X", "is this idea worth it", "validate this idea", "does this beat what already exists", "should this exist", "I'm about to build X", or mid-build "should I keep going or kill it". The method names the incumbent you must beat, ranks assumptions by risk × cost-to-test, attacks the cheapest riskiest one first, pre-registers kill criteria before any test, separates whether it's real from whether it's differentiated (real-but-commodity is a NO), and ends with a GO / NO-GO / CONDITIONAL-GO verdict plus scorecard. Trigger even on enthusiasm ("I have a great idea for…"), not just doubt. Distinct from reality-check (verifies an existing plan for hallucinations); this decides whether a thing should be built at all.
phase: verify
hands_off_to: [derisk-sequencer, experiment-designer]
reads: []
writes: []
---

# Idea Validator

A structured way to find out whether an idea deserves to be built **before** you build it — by attacking the one assumption that is both most likely to kill the project and cheapest to test, instead of polishing the parts that were never in doubt.

The whole skill compresses to one sentence:

> **Validate the riskiest, cheapest-to-test assumption first — not the easiest component first.**

Everything below is in service of that ordering.

---

## The failure this exists to prevent

Picture a representative failure — the kind this skill exists to prevent. The diagnosis is worth internalizing, because the trap is seductive and almost invisible from the inside:

A project applies **rigor lavishly to execution** — clean code, a governance model, an open protocol, a conformance suite, falsifiable experiments — and applies it to the **premise far too late**. It de-risks the parts that were never in doubt ("can we build a clean version of this?" — yes, trivially) and leaves the load-bearing doubt untouched until dozens of commits in: *"is this actually better than what already exists?"* The answer, available on day one from a single web search, is no — the core mechanic is a commodity that several established products already ship. Almost everything built gets deleted later.

The lesson is not "be less rigorous." It is **rigor in the wrong order is expensive rigor.** The riskiest assumption is almost never the engineering. It is usually the market/premise question — *is this needed, and does it beat the incumbent?* — which is also, maddeningly, the **cheapest thing to test and the thing teams test last.**

So the job of this skill is to invert that order, on purpose, every time.

## When to reach for this

- **Best case — pre-build.** Someone has an idea and is about to start. This is the hour-long check that saves the four-day mistake.
- **Rescue case — mid-build.** Someone is already deep in and asking "should I keep going?" The skill still applies: pre-register kill criteria *now*, run the cheap decisive test *now*, and be willing to delete scope decisively if the evidence says so. (No sunk-cost clinging — see below.)
- **Even on pure enthusiasm.** "I have a great idea for…" is a trigger, not an exception. The excitement is exactly when validation is cheapest and most needed, before it hardens into commitments and code.

Reach for a *different* tool when the shape is different: **reality-check** verifies an already-written technical plan for hallucinations and feasibility. This skill answers the prior question — *should this thing exist at all, and is it differentiated?*

---

## The workflow

Five gates, run in order. Each gate can produce an early **KILL** — and that's a feature, not a failure. A validator that can't kill is just a hype machine. The most creditable thing a project can do here is talk itself *into* the grave it deserves rather than out of it.

Work through them with the person conversationally — you don't have to dump the whole template at once. But do produce the structured report (below) at the end so the verdict is legible and the reasoning is checkable later.

### Gate 1 — Name the bet and name the incumbent

State the idea in one plain sentence, then force the comparison that the failure case skipped:

- **The idea, one sentence.** No jargon, no vision-speak.
- **The core claim.** "This is better than `<X>` because `<Y>`." If you can't write this, that's the finding.
- **The incumbent(s).** What *already exists* that does this, or something close enough that a user would pick it instead? Name them specifically.
- **The axis you beat them on.** Cheaper? Faster? Catches a case they miss? Easier to adopt?

The hard rule here: **if you cannot name the competitor and the specific axis you beat them on, you do not yet have a project — you have a feature that may already be commodity.** This is the single most important gate, because it is the one the failure case skipped entirely, and skipping it is what made everything downstream dead weight.

**Actually search.** When you have web access, *run the incumbent search here, now* — it's the cheapest decisive test there is, and "benchmark the incumbent before building the challenger" is the lesson that kills a doomed idea on day one instead of day four. Don't reason about what competitors *might* exist; go find out.

### Gate 2 — Surface and rank the assumptions

List every load-bearing assumption the idea rests on. For each, score two things:

- **Risk** — how likely is it to be false, and how fatal if it is?
- **Cost to test** — how much work to get a real answer? (A web search is cheap; a built prototype is not.)

Then rank by **risk ÷ cost-to-test** and attack the top of that list first. The characteristic mistake is to instead attack the *easiest component* first (usually "can we build it?", which is rarely the real risk) and feel productive while the load-bearing doubt sits untouched.

Within this gate, force one split that teams reliably blur:

> **Is it REAL?** (does the thing actually work / is the problem genuine)
> **vs. Is it DIFFERENTIATED?** (does it beat what already exists)

These are different questions with different tests, and **"real but commodity" is a NO.** A feature can be genuinely correct, genuinely useful, and still not a business, because the incumbents already ship it. Correctness is necessary, not sufficient. Most enthusiasm dies on the *differentiated* question, not the *real* one — so test differentiation early, not after you've proven the easy half.

### Gate 3 — Pre-register the kill criteria

**Before running any test, write down what result would make you stop.** Fix the pass/fail thresholds *now*, while you have no result and therefore no incentive to rationalize.

- Make each criterion **falsifiable** and, where possible, **numeric** ("selection narrows the suite below 0.5 on a median repo", not "selection seems to help").
- State, for each planned test: **PASS if `<X>`, KILL/NO-GO if `<Y>`.**
- Then honor them. **No tuning the threshold after seeing the number.** That one discipline — deciding the bar before the result — is what lets a project die honestly instead of talking past its own evidence. Without it, you *will* find a reason the disappointing number doesn't count.

If the person resists naming a kill threshold ("well, it depends…"), that resistance is usually the tell that they don't want the idea to be killable. Gently hold the line: an idea you've made unfalsifiable can't be validated, only believed.

### Gate 4 — Run the cheapest decisive test first

Now run tests — in order of **decisiveness per unit cost**, cheapest first.

- **Decouple the variables.** If the idea needs *two* unknowns to both hold, find the one that is cheaper to measure and more likely to be fatal, and test *that* one first. If it fails, you're done — you never pay for the expensive test. (For example, a static structural fact may be independent of a dynamic one and far cheaper to measure across several samples; measuring it can settle the question for almost nothing.)
- **A half-day emulator beats a four-day build.** The incumbent benchmark that produces the kill is often, in the end, a one-page emulator. You rarely need the real system to learn the decisive thing.
- **Do not optimize before correctness is validated.** Optimization-before-correctness is a *correctness-bug generator*: a speed feature can silently ship a broken result in nearly every trial when it's tuned for speed before the slow-but-obviously-correct path is the proven baseline. Never let a performance path ship until the slow, plainly-correct version is the baseline it has to match.

### Gate 5 — Verdict, scorecard, and what survives

Render a verdict grounded in the **pre-registered** criteria — not in how attached anyone has become.

- **GO** — the riskiest assumptions survived their tests; the differentiation axis is real.
- **NO-GO** — a pre-registered kill criterion fired. Say so plainly. Then **salvage, don't cling**: name what's genuinely reusable (a correct sub-idea, clean code, the validation method itself) and stop. Decisive scope deletion with no sunk-cost drag is a strength, not a loss.
- **CONDITIONAL-GO** — the thesis fails but a *smaller* product might survive. This is only honest if you name the **exact surviving condition** and the **specific test** that would confirm it. A vague "maybe there's something here" is a NO-GO wearing a costume.

Then grade the idea on a **scorecard** that scores dimensions *separately*, because the whole point is that a project can be an A on engineering and an F on differentiation at the same time — and the average would hide the thing that kills it.

---

## Output template

Produce this at the end. Keep it tight; this is a decision artifact, not an essay.

```markdown
# Idea Validation — <name>

## The bet
- Idea (one sentence): …
- Core claim: "Better than <incumbent> because <axis>."
- Incumbent(s): … | Axis we beat them on: …
- (If incumbent/axis is blank → that is the finding. Stop here.)

## Riskiest assumptions (ranked by risk ÷ cost-to-test)
| # | Assumption | Fatal if false? | Cost to test | Real? / Differentiated? |
|---|------------|-----------------|--------------|--------------------------|
| 1 | …          | …               | cheap/med/hi | …                        |
- Riskiest + cheapest to test → attack first: …

## Kill criteria (pre-registered — fixed before any test)
- Test A: PASS if … | KILL if …
- Test B: PASS if … | KILL if …
- (No threshold changes after seeing results.)

## Cheapest decisive test — result
- What was run, why it's decisive, what it cost:
- Result (report n / limits honestly; don't invent numbers):

## Verdict: GO / NO-GO / CONDITIONAL-GO
- Grounded in which pre-registered criterion:
- If CONDITIONAL-GO → exact surviving condition + the test that confirms it:

## Scorecard
| Dimension | Grade | One-line reason |
|---|---|---|
| Problem is real | | |
| Differentiation vs incumbents | | |
| Feasibility / can we build it | | |
| Sequencing risk (validating in the right order?) | | |
| Honesty of this validation (criteria pre-registered? evidence, not vibes?) | | |

## What survives (esp. if NO-GO)
- Reusable ideas / code / method:
```

---

## Anti-patterns to flag (the "taxes")

These are the recurring ways effort gets spent *ahead of* the validation that would have told you whether to spend it at all. Call them out whenever you see them forming:

1. **Governance / protocol / breadth before there's anything to govern.** Foundations, open protocols "other people will adopt," conformance levels, multi-language/multi-platform support — these are answers to *success* problems. Building them around an unvalidated premise is scaffolding on sand. Defer the apparatus of a standard until an external party actually demands it.
2. **Eight canonical docs instead of one.** Every additional source-of-truth document you must keep mutually consistent turns future work into bookkeeping ("resync docs" commits). Keep one canonical doc; let the rest be generated or explicitly subordinate. Drift tax is real and compounds.
3. **Optimization before correctness.** Covered in Gate 4 — the fastest path to a confident wrong answer.
4. **Real-but-commodity treated as a win.** Correctness feels like validation. It isn't, if the incumbents already ship it.
5. **Sunk-cost clinging.** "We've already built so much" is not evidence the idea is good. The strongest move after a kill is decisive deletion.

## Honesty rules (how to keep the validation itself trustworthy)

- **Pre-register, then don't move the goalposts.** If you change a threshold, you've stopped validating and started persuading.
- **Distinguish a real kill from an underpowered test.** "The graph is dense, so selection can't help" (a real, structural kill) is different from "our extractor bailed on this repo" (a fixable gap). Conflating them either kills good ideas or rescues dead ones.
- **Report n and limits; never invent numbers.** A small sample honestly labeled "n=4, underpowered" is worth more than a confident fabricated rate. If a leg is underpowered, say so and lean on the leg that isn't.
- **Credit what's genuinely good even in a NO-GO.** In the worked NO-GO example, the bug diagnosis was correct and one design principle survived every pivot. A good kill names the survivors; it doesn't scorch everything to feel decisive.

## Worked examples

See `references/worked-examples.md` for two fully worked validations: a **NO-GO done right** (a real, correct mechanic that turned out to be commodity, killed on pre-registered evidence) and a **CONDITIONAL-GO** (a thesis that failed but left a smaller, testable product standing). Read them when you want to see the gates and the scorecard applied end to end, or when you're unsure how to phrase a CONDITIONAL-GO honestly.

---

**Next steps:** On a GO or CONDITIONAL-GO, suggest `derisk-sequencer` to turn the ranked assumptions into a build-after-test sequence, or `experiment-designer` to rigorously design the single decisive test a CONDITIONAL-GO hinges on. On a NO-GO, stop — name what survives and don't sequence a dead idea.
