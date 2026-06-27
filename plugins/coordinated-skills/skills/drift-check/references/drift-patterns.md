# Drift Patterns

How document sets fail — and, more insidiously, how they *fake* alignment. A surface match/mismatch matrix catches none of these on its own. Read this before finalizing any audit, especially one that's coming back clean. The worked examples are drawn from real self-audit reports.

## 1. Vanity scoring

**Tell:** A self-audit that lands on a high round number ("98% aligned", "FULLY ALIGNED"), all-green checkmarks, and a single nitpick offered as proof of rigor.
**Why:** Self-assessments optimize for reassurance; the author and the audited are the same person.
**Catch:** Distrust the score itself. An evolved document set that audits this clean almost always means the comparison was shallow. Re-derive alignment from the actual claims, not the summary.
**Example:** A matrix scoring every component 🟢 100% and concluding "98%," where the only flaw found is an 8-vs-9 metric. That's not a healthy system; that's an unexamined one.

## 2. Copy-paste consensus

**Tell:** The same metric or sentence appears identically across many documents, presented as multi-document agreement.
**Why:** Text propagates by copy-paste; the matrix reads identical values as "consistent ✅."
**Catch:** Identical ≠ independently validated. Flag verbatim-shared claims as duplication, and ask whether the number was ever actually measured or just pasted forward. `scripts/cross_doc_scan.py` surfaces these automatically.
**Example:** `>95% accuracy` and `<2 seconds` retrieval appearing word-for-word in PLANNING, README, and rules — counted as three confirmations when it's one unverified claim echoed three times.

## 3. Silent drift

**Tell:** One document reflects a newer decision (a renamed component, a changed tech choice, a dropped feature) while others still describe the old state — with no contradiction flagged because nobody re-read the old docs.
**Why:** Updates land where you're working; sibling docs go stale silently.
**Catch:** For each load-bearing decision, check that *every* doc that references it reflects the current state. Stale references are drift even when no doc directly contradicts another in the same sentence.

## 4. North-star restatement

**Tell:** The mission is stated slightly differently in each document, and the differences are quietly load-bearing ("perfect memory" vs "conversation continuity" vs "context retention").
**Why:** Each author re-expresses the vision; small rewordings accrete into divergent goals.
**Catch:** Put the mission statements side by side verbatim. If there's no single canonical phrasing, there's nothing to measure drift against — and that absence is the finding.

## 5. Unfalsifiable promises

**Tell:** Claims that agree across docs only because none of them mean anything checkable: "perfect memory", "seamless orchestration", ">95% accuracy" with no definition of what's measured or how.
**Why:** Vague superlatives are easy to align because they assert nothing testable.
**Catch:** For each headline claim, ask "what observation would prove this false?" If there isn't one, it's not aligned, it's undefined — recommend making it falsifiable.
**Example:** "Perfect memory" as a product promise. No system has perfect memory; the agreement across docs is agreement on a slogan, not a spec.

## 6. Resolved-gap theater

**Tell:** Open questions and known gaps are listed, then immediately marked ✅ / "appropriate" / "handled" in the same breath.
**Why:** Acknowledging a gap *feels* like rigor; closing it on the page resolves the discomfort without resolving the gap.
**Catch:** Treat every gap the document raises as still open unless there's a concrete resolution. "Status: appropriate abstraction ✅" on an unanswered question is theater.
**Example:** "When exactly does memory compression happen? — Recommendation: add to troubleshooting guide" listed under issues, while the overall verdict stays "fully aligned."

## 7. Abstraction-as-excuse

**Tell:** A real omission is reframed as an intentional design choice ("the system prompt correctly abstracts this detail") to avoid logging it as a gap.
**Why:** It's easier to relabel a hole as deliberate than to fill it.
**Catch:** Distinguish genuine layering (user docs vs technical docs *should* differ in detail) from a spec that simply never pinned the number down anywhere.

## 8. Scope-of-agreement inflation

**Tell:** A confident "perfectly aligned" verdict that rests on comparing only surface tokens — emoji usage, tech-stack names, feature-list presence — while the hard axes (does the architecture actually deliver the promised metric? do the agent responsibilities overlap?) were never compared.
**Why:** Surface tokens are easy to line up and produce satisfying green rows.
**Catch:** Check what the matrix actually compared. Alignment on "both mention Chroma" and "both use 🎭✨" is not alignment on whether the system works.

---

**Meta-principle:** The burden of proof is on *aligned*, not on *broken*. A document set is presumed to have drifted until a real cross-claim comparison shows otherwise — because that's the empirically common state of any spec that more than one person touched over more than a week.
