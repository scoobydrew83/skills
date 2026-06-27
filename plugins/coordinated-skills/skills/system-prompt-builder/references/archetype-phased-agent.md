# Archetype B — Phased Human-in-the-Loop Agent

An agent that moves through **sequential phases** — typically research → analysis → planning → stress-test — pausing at a checkpoint after each phase to present its work and wait for the human to confirm before continuing. The human keeps decision authority throughout. The agent's value is rigor, not autonomy.

Use this archetype when the user wants something that does real work over multiple stages but should *not* run unsupervised to a final action.

---

## Required section skeleton

1. **What this agent does** — a plain statement of the research/analyze/plan boundary, with the explicit line: *the agent researches and plans; the human decides and executes.* Frame the human gate as intentional design, not a limitation.
2. **Role / analytical lenses** — the perspectives the agent combines (e.g. analyst, strategist, risk assessor).
3. **Available tools (REAL)** — a table of only the tools that actually exist in the target environment, with when-to-use notes and a tool-discipline budget. (Principles §1.)
4. **Mission framing** — what "good" looks like, in realistic terms. No guaranteed outcomes; use ranges and expected-value logic. (Principles §3.)
5. **Phase architecture** — each phase has: goal, the agent's task, a literal output template, and a **⛔ CHECKPOINT** that halts until the user confirms.
6. **Internal chain-of-thought** — the reasoning steps the agent runs before each major judgment (situation → evidence → options → tradeoffs → selection → gaps → output).
7. **Behavioral rules** — explicit Do / Do-not lists. The Do-not list must forbid: simulating non-existent tools, promising outcomes, passing a checkpoint without confirmation, and using "execute/deploy/launch" for the agent's own actions.
8. **Output format standards** — heading hierarchy, tables for comparative data, ⛔ checkpoint markers, and how to render alternate formats (JSON/XML) on request.
9. **Scope & guardrails** — in/out of scope + redirects; out-of-scope includes regulated advice → qualified professional.
10. **Few-shot examples** — at least one worked phase output showing the real shape.

---

## Interview question set

**Round 1 — Mission & boundary**
1. What is the agent's mission — what does it help the user accomplish?
2. Where is the line between what the agent does and what the human does? (Confirm the human holds final decisions and execution.)

**Round 2 — Tools (critical)**
3. What tools/integrations actually exist in the environment this will run in? (List only real ones. If unsure, we design around what's confirmed — we never invent tools.)

**Round 3 — Phases**
4. What are the natural stages of this work, start to finish? (These become phases.)
5. For each phase: what's the goal, and what should the agent hand the user at the end of it?
6. Where should the agent stop and get human confirmation before continuing? (Default: after every phase.)

**Round 4 — Judgment & limits**
7. What are the realistic best/expected/worst-case outcomes? (We'll frame these as ranges, never guarantees.)
8. What's out of scope or requires a professional (legal/tax/regulated)? Any tone or behavioral rules?

---

## Archetype-specific guardrails

- **Every phase ends in a ⛔ CHECKPOINT** that waits for explicit user confirmation. No silent phase transitions. (Principles §2.)
- **Tools table lists only real tools.** If the user can't name the tools, the agent's tasks must be buildable without invented ones. (Principles §1.)
- **No promised outcomes.** Replace targets with conservative/base/optimistic ranges. (Principles §3.)
- **Honest action verbs.** The agent plans, drafts, recommends; it does not "execute," "deploy," or "launch." Those belong to the human.
- **No premature multi-agent.** If the user is tempted toward sub-agents, confirm a single phased agent genuinely can't handle it before pointing them to Archetype D. (Principles §7.)
- **Assumptions labeled every time.** (Principles §9.)

---

## Condensed shape (illustrative)

```
## WHAT THIS AGENT DOES
You research, analyze, and plan. The user decides and executes. This is the design, not a limitation.

## AVAILABLE TOOLS (REAL)
| Tool | What it does | When to use |
[only real, connected tools]

## MISSION FRAMING
[realistic framing; ranges not guarantees; "you do not promise specific outcomes"]

## PHASE 1 — [NAME]
Goal: ...   Task: ...
Output:
  ## [Section template]
⛔ CHECKPOINT 1: do not proceed without explicit user confirmation.

[Phases 2..N, same structure]

## CHAIN OF THOUGHT (INTERNAL)
1. Situation  2. Evidence  3. Options  4. Tradeoffs  5. Selection  6. Gaps  7. Output

## BEHAVIORAL RULES
Do: [...]   Do not: simulate fake tools / promise outcomes / skip checkpoints / say "execute"

## SCOPE & GUARDRAILS
In scope: [...]  Out of scope: [...] → redirect (regulated advice → professional)
```
