# Archetype A — Mode-Based Assistant / Tool System

A reusable assistant that handles several **distinct request types**, each routed to its own behavior and output shape. Think of a system with named commands or modes (BUILD / REVIEW / GENERATE / EVALUATE / OPTIMIZE), where the right response structure depends entirely on what the user asked for.

Use this archetype when the user describes an assistant that does *several different jobs* and needs to behave consistently for each one.

---

## Required section skeleton

Build the system prompt with these sections, in this order:

1. **Identity & Role** — who the assistant is, its domain expertise, and an explicit "you are not a generalist here; stay in scope" line.
2. **Scope guardrails** — in-scope / out-of-scope lists + a redirect pattern.
3. **Routing** — the IF/THEN block mapping every trigger to exactly one mode. State the no-blending rule.
4. **Shared frameworks** — any framework, taxonomy, or classification the assistant applies across modes (e.g. a four-pillar model, a use-case taxonomy).
5. **Mode instructions** — one block per mode: trigger, input it expects, numbered step sequence, and an explicit output structure (show the literal template).
6. **Rubric** (only if any mode scores or evaluates) — anchored 1–N scale with per-tier descriptions and worked examples. See `design-principles.md` §5.
7. **Ambiguity handling** — what to do when no mode signal is present: ask exactly one option-based question.
8. **Few-shot examples** — at least one complete worked example per primary mode, showing real input and full output.
9. **Operating principles** — 3–6 behavioral rules (e.g. specificity over completeness, one priority at a time).

---

## Interview question set

Gather these. Pull from context first; batch into 2–4 rounds.

**Round 1 — Identity & scope**
1. What domain does this assistant specialize in, and what role/expertise should it embody?
2. What is explicitly *out* of scope? (What requests should it redirect rather than attempt?)

**Round 2 — Modes**
3. What are the distinct things a user can ask this assistant to do? (These become the modes/commands. List them.)
4. For each mode: what triggers it, what input does it need, and what should the output look like?

**Round 3 — Frameworks & quality**
5. Is there a framework, checklist, or taxonomy the assistant should apply consistently? (If yes, capture its structure.)
6. Do any modes produce a score or quality judgment? (If yes, we'll build an anchored rubric.)

**Round 4 — Voice & examples**
7. What tone/communication style? Any behavioral rules (e.g. always show the improved version, never just describe it)?
8. Can you give one real example of a request + the ideal response for the most important mode? (If not, you'll construct a plausible one and label it.)

---

## Archetype-specific guardrails

- **Explicit routing is mandatory** — the IF/THEN block comes before mode instructions, and every mode has a distinct trigger. (Principles §4.)
- **Each mode's output structure must be shown literally**, not described. Give the template the model fills in.
- **No mode blending** unless the user explicitly wants a combined mode; otherwise state that combined requests are handled sequentially.
- **If any mode scores**, the rubric must be anchored. An unanchored "rate 1–10" is a defect. (Principles §5.)
- **Ambiguity handling asks one option-based question**, never an open-ended "tell me more about everything."

---

## Condensed shape (illustrative)

```
## IDENTITY & ROLE
You are a [domain] specialist... You are not a generalist here. Stay in scope: [scope].

## ROUTING
IF user says [TRIGGER A] → Enter [MODE A]
IF user says [TRIGGER B] → Enter [MODE B]
IF ambiguous → ask ONE option-based question.
Do not blend modes.

## [SHARED FRAMEWORK]
[the taxonomy/model applied across modes]

## MODE A
Step 1 — ...  Step 2 — ...
Output structure:
  ## [Section]
  [template]

## RUBRIC  (if scoring)
4 — Excellent: [anchor + example]   ...   1 — Missing: [anchor]

## FEW-SHOT EXAMPLES
[complete request + full output, per mode]

## OPERATING PRINCIPLES
1. Specificity over completeness.  2. One priority at a time.  ...
```
