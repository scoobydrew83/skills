# Review Rubric (Optional Review Pass)

Use this to score a system prompt — one you just built, or one the user pasted to evaluate. Return a scorecard grounded in specific evidence from the prompt text, then lead with the **single highest-impact fix**. A list of ten changes gets none of them done; one priority gets acted on.

Never return a score without pointing to the specific element that earned it.

---

## Dimensions

Score each 1–4. Skip dimensions that don't apply to the archetype (e.g. "Human oversight" only applies to agents B/D; "Routing" applies to A).

| # | Dimension | What a strong version looks like |
|---|-----------|----------------------------------|
| 1 | **Identity & scope** | Clear role with real expertise; explicit in/out-of-scope with a redirect pattern |
| 2 | **Routing / phasing** | (A) explicit IF/THEN, no blending. (B/D) clear phases/flow with defined transitions |
| 3 | **Tool honesty** | Only real tools referenced; no invented capabilities; tool discipline stated |
| 4 | **Human oversight** *(agents only)* | Explicit checkpoints; human holds decisions; honest action verbs |
| 5 | **Realistic framing** | No guaranteed outcomes; ranges/expected-value logic; assumptions labeled |
| 6 | **Rubric anchoring** *(if it scores)* | Concrete anchors per tier with worked examples |
| 7 | **Example quality** | Complete worked examples (full text), not skeletal descriptions |
| 8 | **Format discipline** | Output structures shown literally; consistent, parseable section structure |

### Anchors (per dimension)

- **4 — Excellent:** Fully specified, no ambiguity, includes the supporting detail (constraints/examples/anchors) the dimension calls for.
- **3 — Good:** Mostly specified; minor gaps that won't meaningfully degrade behavior.
- **2 — Weak:** Partially specified; a gap likely to cause inconsistent behavior.
- **1 — Missing/Broken:** Absent, or present in a form that actively misleads (e.g. a fictional tool, an unanchored score, a removed human checkpoint).

---

## Composite

Average the applicable dimensions and translate:

| Mean of applied dimensions | Verdict |
|----------------------------|---------|
| 3.5 – 4.0 | Deploy-ready; high-confidence behavior expected |
| 3.0 – 3.4 | Usable with minor refinements |
| 2.0 – 2.9 | Will behave inconsistently; needs work before deployment |
| 1.0 – 1.9 | Not yet sound; rebuild the failing dimensions first |

Any dimension scoring **1 on tool honesty, human oversight, or realistic framing** caps the verdict at "needs work" regardless of the average — these are the failure modes that make a system actively unsafe, not just mediocre.

---

## Output structure for the review

```
## Scorecard
| Dimension | Score (1–4) | Evidence |
|-----------|-------------|----------|
| Identity & scope | X | "[quote/paraphrase from the prompt]" |
| ... | | |
Composite: X.X/4 → [verdict]

## Priority Fix
[The single change with the largest impact, and why it ranks first.]

## Other notes (brief)
[2–4 smaller items, one line each.]
```
