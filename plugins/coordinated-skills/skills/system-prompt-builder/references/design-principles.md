# Design Principles (Universal Guardrails)

These apply to **every** system prompt you build, regardless of archetype. They are distilled from real failure modes — each one exists because skipping it produced a system that looked fine and behaved badly. Enforce them during the interview and again before you generate.

---

## 1. Real tools only

Reference only tools, integrations, and data sources the user has **confirmed exist** in the target environment.

- If you don't know what tools are available, **ask** — don't assume `web_search`, a database, or an API exists.
- Never present a fictional capability as real. A system prompt that tells an AI it can "query the CRM" when no such tool is connected will produce confident hallucinated outputs and silent failures.
- When a desired capability has no real tool behind it, say so and design around it (e.g. "ask the user to paste the data" instead of "fetch the data").

**Why it matters:** Fictional tools break system integrity. The model will narrate tool use that never happened, and the user can't tell real output from invented output.

---

## 2. Human oversight is non-negotiable for agents

For any agent (Archetypes B and D), the **human stays the decision-maker.** Build in explicit checkpoints where the agent pauses, presents its work, and waits for confirmation before proceeding or committing resources.

- Never design an agent that executes financial transactions, sends communications, or commits resources without a human gate.
- Use language honestly: the agent *researches, analyzes, drafts, recommends*; the human *decides and executes*. Avoid "execute / deploy / launch" to describe what the agent itself does.

**Why it matters:** Removing oversight isn't a convenience feature — it's a structural flaw. It creates pressure toward unsafe interpretations of ambiguous instructions and turns a helpful tool into a liability.

---

## 3. Realistic goals only

Frame the system's mission in achievable terms. No extreme targets, no guaranteed outcomes.

- Replace "10x returns" / "guaranteed results" with expected-value logic and explicit ranges (conservative / base / optimistic).
- State plainly that outcomes depend on execution, timing, and factors outside the system's control.

**Why it matters:** Unrealistic goals corrupt behavior. An extreme target creates implicit pressure that distorts how the model interprets every ambiguous instruction downstream — it will cut corners to chase the impossible number.

---

## 4. Routing and phase logic must be explicit

When a system has multiple modes (A) or phases (B), separate them with unambiguous **IF/THEN** logic stated up front, before any mode-specific instructions.

- Each mode/phase needs a clear trigger signal and a defined output structure.
- Forbid mode-blending unless explicitly designed for it.

**Why it matters:** Without explicit routing, the model guesses which behavior the user wants and blends them inconsistently. Explicit routing is the difference between a reliable tool and a coin flip.

---

## 5. Rubrics must be anchored

Any evaluation criteria, scoring, or quality bar you write into a system must include **concrete anchors per tier** — ideally a worked example of what each score looks like.

- "Rate 1–10" with no anchors is unenforceable; the model will drift.
- Tie every score to specific, observable evidence in the thing being scored.

**Why it matters:** An unanchored rubric is decoration. The model can't apply it consistently, so the scores mean nothing.

---

## 6. Examples show complete text

Few-shot examples must contain the **full prompt or output text**, not a structural description of one.

- Bad: "Then provide a well-structured persona section."
- Good: the actual persona section, written out in full, that the model can pattern-match against.

**Why it matters:** Skeletal examples don't transfer. The model learns from concrete instances, not from descriptions of instances.

---

## 7. Complexity must be earned

Don't add architectural layers the foundation can't support. Specifically: don't reach for multi-agent orchestration (D) when a single well-structured agent (B) would do the job more reliably.

- Get the single-agent version sound first. Multi-agent over a shaky foundation amplifies problems, it doesn't solve them.
- Before building D, make the user justify *why* a single agent can't handle it.

**Why it matters:** Premature complexity is dangerous. Each added agent multiplies handoff failures, coordination bugs, and surface area for ambiguity.

---

## 8. Scope guardrails with graceful redirects

Every system gets an explicit **in-scope / out-of-scope** section and a redirect pattern for out-of-scope requests.

- The redirect should be helpful, not just a refusal — offer the nearest in-scope thing the system *can* do.
- For agents, out-of-scope includes regulated advice (legal, tax, specific securities) → redirect to a qualified professional.

**Why it matters:** A scoped system stays reliable. An unscoped one gets pulled into tasks it wasn't designed for and degrades.

---

## 9. Label every assumption

Whenever the system (or you, while building it) fills a gap with an assumption, **mark it explicitly** as an assumption rather than presenting it as fact.

**Why it matters:** Labeled assumptions are correctable; hidden ones become silent errors the user inherits.
