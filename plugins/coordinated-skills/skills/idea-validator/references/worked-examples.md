# Worked Examples

Two end-to-end validations showing the gates and the scorecard in action. The first is an illustrative **NO-GO**. The second is a **CONDITIONAL-GO**, so the method doesn't read as a kill-everything machine — sometimes a failed thesis leaves a real, smaller product standing. Both are illustrative composites, not reports on any specific shipped project.

---

## Example 1 — NO-GO done right: "a merge gate for parallel coding agents"

**Context.** The idea: a tool that verifies the *merged* state of several AI coding agents' branches and only advances mainline if the combined program is green. It catches a real bug class git is blind to — two branches each green alone, textually clean when merged, broken when combined (a renamed symbol still called, a changed return shape, an enum divergence).

### The bet
- **Idea:** Gate mainline on the merged state of parallel agent branches, not the individual branches.
- **Core claim:** "Better than plain `git merge` because it catches separated-edit semantic conflicts."
- **Incumbent(s):** *Here's the gate that was skipped.* Plain git was named as the competitor — but a five-minute search surfaces **GitHub Merge Queue, Mergify, Bors, and Aviator**, all of which already verify the merged state. The *real* incumbent was never plain git.
- **Axis we beat them on:** …unclear. This blank is the whole story.

### Riskiest assumptions (ranked)
| # | Assumption | Fatal if false? | Cost to test | Real? / Differentiated? |
|---|---|---|---|---|
| 1 | "Verifying the merged state is a *differentiator*" | Fatal | **Cheap** (one web search) | Differentiation — and it's the load-bearing one |
| 2 | The bug class is real | Fatal | Cheap (5 hand-built cases) | Real |
| 3 | We can build a clean gate | Not fatal | Medium (it's just code) | Feasibility — never in doubt |

The inversion that kills a project like this: it spends dozens of commits de-risking #2 and #3 (both of which were fine) and doesn't test #1 — the cheapest and riskiest — until day four.

### Kill criteria (pre-registered)
- **Leg A:** gate beats *git* on the 5 bug classes → PASS if 5/5.
- **Leg B:** vs a merge-queue emulator → KILL the "differentiator" thesis if the correct config is *more expensive* than the queue, or the cheap config ships a broken mainline.

### Cheapest decisive test — result
- **Leg A:** 5/5. ✅ But a merge queue catches all five too → **table stakes, not a differentiator.**
- **Leg B (the half-day emulator that should have come first):** the *correct* gate was **1–8× more expensive** than the queue (it pays a full test suite per change; the queue amortizes one run across a batch), and the *cheap* gate **shipped red in 19/20 trials** — an optimization that silently defeated correctness.

### Verdict: **NO-GO** on the thesis
Fired on the pre-registered Leg B criterion. A later, even cheaper structural test (is the dependency graph sparse enough for test-selection to ever pay off?) failed on 4 of 4 real repos, removing the last surviving edge.

### Scorecard
| Dimension | Grade | One-line reason |
|---|---|---|
| Problem is real | A | Bug class real, correctly diagnosed, 5/5. |
| Differentiation vs incumbents | F | Commodity; four products already ship it. Never checked until day 4. |
| Feasibility | A− | Clean, dependency-free, tested. |
| Sequencing | F | Built five milestones before the first incumbent benchmark. |
| Honesty of validation | A+ | Pre-registered criteria; killed itself on evidence, no goalpost-moving. |

### What survives
- The bug-class demonstration (a clean, correct reference for anyone who wants one).
- One design principle — "agents just `git push`; intent is derived from the diff, not declared" — that was elegant and survived every pivot.
- **The validation method itself** — the discipline this skill encodes.

**The one-line lesson:** the riskiest, cheapest-to-test assumption ("does it beat what exists?") was tested *last*. Everything built before that test was dead weight.

---

## Example 2 — CONDITIONAL-GO: "a CSV reconciler for a specific accounting niche"

**Context.** The idea: a small tool that reconciles export CSVs from two specific SaaS products that a particular kind of bookkeeper uses together daily, and that — the claim goes — neither product nor the big incumbents reconcile cleanly.

### The bet
- **Idea:** One-click reconciliation between Product A's and Product B's exports for niche bookkeepers.
- **Core claim:** "Better than doing it by hand in Excel, and better than the big reconciliation tools because they don't understand A↔B's specific ID mismatch."
- **Incumbent(s):** Excel-by-hand; the large reconciliation suites; A's and B's own native exports.
- **Axis we beat them on:** handles the *specific* ID-format mismatch between A and B out of the box.

### Riskiest assumptions (ranked)
| # | Assumption | Fatal if false? | Cost to test | Real? / Differentiated? |
|---|---|---|---|---|
| 1 | The big suites *don't* already handle A↔B | Fatal | **Cheap** (trials + docs search) | Differentiation |
| 2 | Enough bookkeepers feel this pain to pay | Fatal | Cheap-ish (10 user conversations) | Real demand |
| 3 | The ID mismatch is reconcilable at all | Medium | Cheap (one real data sample) | Feasibility |

### Kill criteria (pre-registered)
- **#1:** KILL the differentiation thesis if either big suite reconciles A↔B cleanly in a trial.
- **#2:** KILL if fewer than ~3 of 10 bookkeepers call this a real, recurring pain worth paying for.

### Cheapest decisive test — result
- **#1:** The big suites *partially* handle it but mangle the A↔B ID mismatch on real data — the specific gap is real. ✅ (differentiation survives, narrowly)
- **#2:** 4 of 10 called it a weekly annoyance; 2 said they'd pay a small monthly fee. Real but **thin** — and the sample is small (n=10, self-selected). Honestly underpowered.

### Verdict: **CONDITIONAL-GO**
The grand "reconciliation platform" framing is a NO-GO (the big suites own the general case). But a **narrow** product — *just the A↔B mismatch, nothing else* — survives, **conditional on** one named test: a paid pilot landing **≥10 paying users in 60 days**. If that bar isn't met, it's a NO-GO. The condition is specific and falsifiable, which is what separates an honest CONDITIONAL-GO from wishful thinking.

### Scorecard
| Dimension | Grade | One-line reason |
|---|---|---|
| Problem is real | B | Real but thin; n=10, self-selected. |
| Differentiation vs incumbents | B+ | Narrow gap is genuine; general case is not winnable. |
| Feasibility | A | The mismatch reconciles cleanly on real data. |
| Sequencing | A | Tested differentiation + demand before building anything. |
| Honesty of validation | A | Named the underpowered sample; set a falsifiable pilot bar. |

### What survives if the pilot fails
- The reconciliation logic (reusable inside a broader bookkeeping tool).
- The validated knowledge that the general market is owned — saving the *next* idea from re-testing it.

**The one-line lesson:** differentiation and demand were tested *first*, cheaply; the verdict scoped the product down to exactly the part that survived, with a hard, dated condition to confirm the rest.
