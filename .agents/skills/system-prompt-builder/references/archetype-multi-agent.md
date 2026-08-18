# Archetype D — Multi-Agent / Orchestration System

An orchestrator that coordinates multiple specialized sub-agents, each owning a single clear responsibility, passing structured data between them.

**Read this section before building, even if the user asked for multi-agent directly.** The most common and most damaging mistake in this space is reaching for multiple agents when a single well-structured agent (Archetype B) would be more reliable. Multi-agent structure layered over a shaky foundation amplifies problems instead of solving them. So this archetype starts with a qualification gate.

---

## The qualification gate (do this first)

Before designing any sub-agents, confirm multi-agent is actually warranted. Ask the user:

1. **Why can't a single phased agent (B) do this?** A good answer involves genuinely independent workstreams, distinct tool/permission boundaries, parallelism that materially matters, or context windows a single agent can't hold.
2. **Can the work be cleanly decomposed** into responsibilities that don't constantly need each other's intermediate state?

If the honest answer is "a single agent could do this, it'd just be a bit longer" → **recommend Archetype B instead** and explain why. Don't build complexity the task doesn't earn. (Principles §7.)

Only proceed to the skeleton below once multi-agent is justified.

---

## Required section skeleton

1. **Orchestrator identity** — the coordinating role, and an explicit statement that it routes and assembles but does not do the sub-agents' specialized work itself.
2. **Decomposition rationale** — a short, written justification of why the work is split this way. (This is the qualification gate, captured for the record.)
3. **Sub-agent roster** — a table: each sub-agent's single responsibility, its inputs, its outputs, and the **real** tools it may use. One responsibility per agent.
4. **Orchestration flow** — the sequence (and any parallelism) in which sub-agents run, with the routing logic that decides what runs when.
5. **Handoff contracts** — the structured shape of data passed between agents (define the schema, so handoffs don't silently lose information).
6. **Human oversight points** — explicit checkpoints where the human reviews before the system proceeds or commits anything. (Principles §2.)
7. **Error handling & fallbacks** — what happens when a sub-agent fails, returns low confidence, or produces malformed output. Include termination conditions.
8. **Scope & guardrails** — in/out of scope + redirects.
9. **Few-shot example** — one worked trace showing a request flowing through the orchestrator and sub-agents.

---

## Interview question set

**Round 1 — Qualification (gate)**
1. Why does this need multiple agents rather than one structured agent? What are the genuinely independent workstreams?

**Round 2 — Decomposition**
2. What are the distinct responsibilities, and what single job does each sub-agent own?
3. What real tools does each sub-agent need? (Only confirmed, existing tools.)

**Round 3 — Flow & handoffs**
4. In what order do the sub-agents run? Anything truly parallel?
5. What data passes between them, and in what shape?

**Round 4 — Oversight & failure**
6. Where must a human review before the system continues or commits anything?
7. What should happen when a sub-agent fails or returns something unusable? When should the whole run stop?

---

## Archetype-specific guardrails

- **Qualification gate is mandatory.** If a single agent suffices, recommend B. (Principles §7.)
- **One responsibility per sub-agent.** Overloaded sub-agents recreate the monolith you were trying to decompose.
- **Real tools only, scoped per agent.** Each sub-agent lists only the real tools it's allowed to use. (Principles §1.)
- **Handoff contracts are explicit.** Define the data schema between agents; undefined handoffs silently drop information.
- **Human oversight survives decomposition.** Adding agents must not remove the human checkpoints. (Principles §2.)
- **Termination conditions defined.** The system must know when to stop, including on repeated failure.

---

## Condensed shape (illustrative)

```
## ORCHESTRATOR IDENTITY
You coordinate specialized sub-agents and assemble their outputs. You do not perform their specialized work yourself.

## DECOMPOSITION RATIONALE
This work is split because [genuinely independent workstreams / tool boundaries / ...].

## SUB-AGENT ROSTER
| Agent | Single responsibility | Inputs | Outputs | Real tools |

## ORCHESTRATION FLOW
1. Run [Agent A] → 2. If [condition], run [Agent B] ‖ [Agent C] → 4. Assemble.

## HANDOFF CONTRACTS
A → B: { field: type, ... }

## HUMAN OVERSIGHT
⛔ Human reviews [output] before [commit/proceed].

## ERROR HANDLING
If [agent] fails → [fallback]. Terminate if [condition].
```
