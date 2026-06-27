---
name: system-prompt-builder
description: Interview-driven builder for enterprise-grade AI system prompts and agent architectures. Use whenever the user wants to design, build, scaffold, or rebuild a system prompt, custom assistant, AI agent, project instructions, custom GPT, multi-agent system, or any reusable LLM instruction set. Trigger on phrases like "build me a prompt system", "design an agent", "write system instructions", "turn this into an agent", "create project instructions", "I want an AI that does X reliably", or any request to architect how an AI should behave across many future interactions — even when the user never says the words "system prompt." Also trigger when the user pastes an existing system prompt and wants it rebuilt, hardened, or extended.
phase: execute
hands_off_to: [reality-check, drift-check, conductor-memory]
reads: []
writes: []
---

# System Prompt Builder

Build production-grade system prompts and agent architectures by interviewing the user, then generating a complete, ready-to-paste instruction set. This skill does not hand back generic templates — it asks the right questions, enforces a set of hard-won design principles, and produces a system prompt the user can deploy as-is.

The output is always a **complete, self-contained system prompt as a `.md` file**, optionally followed by a **review pass** that scores the result and names the single highest-impact improvement.

---

## The four archetypes

Every system you'll build falls into one of four shapes. Each has a different skeleton, a different interview, and different failure modes. Your first job is to classify, because everything downstream depends on it.

| Archetype | Build when the user wants… | Reference file |
|-----------|----------------------------|----------------|
| **A — Mode-based assistant** | A reusable assistant/tool that handles several distinct request types (commands/modes), each with its own output shape. *(e.g. a prompt-engineering helper with BUILD / REVIEW / GENERATE modes)* | `references/archetype-mode-based-assistant.md` |
| **B — Phased human-in-the-loop agent** | An agent that researches/analyzes/plans across sequential phases, pausing for human confirmation, while the human keeps decision authority | `references/archetype-phased-agent.md` |
| **C — Single-purpose task prompt** | One focused, repeatable instruction for a single task (often with variable injection) | `references/archetype-single-purpose.md` |
| **D — Multi-agent / orchestration** | An orchestrator coordinating multiple specialized sub-agents | `references/archetype-multi-agent.md` |

**Classification guidance:**
- Several distinct "things the user can ask for," each routed differently → **A**.
- A workflow with stages, where a human should review between stages → **B**.
- One job, done the same way every time → **C**.
- The user explicitly wants multiple agents — but **read `references/archetype-multi-agent.md` first**, because the most common mistake is reaching for multi-agent when a single well-structured agent (B) would be more reliable. Qualify before you build.

If the request is ambiguous, ask **one** crisp classifying question with concrete options (e.g. "Is this one assistant with several modes, or a step-by-step agent that checks in with you between stages?"). Don't front-load a form.

---

## Workflow

Follow these steps in order. Don't skip the principles step — it's where most system prompts fail.

### Step 1 — Classify and load context

1. Determine the archetype using the table above. If the user pasted an existing system to rebuild, classify *that*.
2. Read `references/design-principles.md` (always — these guardrails apply to every archetype).
3. Read the matching `references/archetype-*.md` file. It contains the required section skeleton, the interview question set, and archetype-specific guardrails.

### Step 2 — Interview

Run the interview defined in the archetype reference. The goal is to gather exactly what's needed to build all required sections — no more.

- **Pull from context first.** If the conversation, uploaded files, or prior turns already answer a question, don't ask it. Confirm assumptions rather than re-asking.
- **Batch logically, don't dump.** Group questions so the user answers in 2–4 short rounds, not one giant form. On mobile especially, prefer a handful of grouped questions over a wall of fields.
- **Ask only what blocks the build.** If a section can be built well from a reasonable, clearly-labeled assumption, make the assumption and flag it — don't stall the user for it.
- **Never fabricate the things that matter.** Tools, data sources, audience, and constraints must come from the user. If you don't know what tools exist, ask — do not invent capabilities (see principles).

### Step 3 — Apply the design principles

Before writing, walk the generated design against `references/design-principles.md`. The non-negotiables:

1. **Real tools only.** Reference only tools the user has confirmed exist. Never list a fictional capability as real.
2. **Human oversight for agents.** Agents (B, D) keep the human as decision-maker with explicit checkpoints. Removing oversight is an architectural flaw, not a feature.
3. **Realistic goals.** No extreme or guaranteed outcomes — they create implicit pressure that distorts behavior on ambiguous instructions.
4. **Explicit routing.** Mode/phase separation uses unambiguous IF/THEN logic, not vibes.
5. **Anchored rubrics.** Any scoring criteria include concrete anchors per tier, or they're unenforceable.
6. **Complete examples.** Few-shot examples show full prompt/output text, not skeletal descriptions.
7. **Earned complexity.** Don't layer multi-agent structure over an unsound foundation. Get the single-agent version right first.

### Step 4 — Generate the system prompt

Build the complete system prompt following the archetype's required skeleton. Write it to a file:

```
/mnt/user-data/outputs/<short-name>-system-prompt.md
```

Requirements:
- **Complete and self-contained** — the user can paste it directly into a project, custom GPT, or API system field with no further editing (beyond filling any clearly-marked `[VARIABLES]`).
- Use **XML tags** to delimit sections when structure aids parsing (personas, phases, examples).
- Include **at least one complete worked example** for any archetype with subjective judgment or routing.
- Mark every assumption you made inline, so the user can correct it.

Present the file with `present_files`. Then give a short plain-language summary of what you built and which assumptions you made.

### Step 5 — Offer the review pass (optional)

After delivering, offer: *"Want me to run a review pass — score it against the rubric and flag the single highest-impact improvement?"*

If yes, read `references/review-rubric.md`, score the generated prompt against it, and return the scorecard plus the one priority fix. Lead with the priority fix — a list of ten changes gets none of them done.

---

## Output standards

- Deliver the system prompt as a `.md` file, never only inline.
- Use semantic heading hierarchy; tables for comparative data; code/XML blocks for structured sections.
- Keep the user's voice and naming where they've expressed a preference (command names, tone, domain terms).
- If the user asked for a specific deployment target (Claude Project, custom GPT, API), note any target-specific conventions inline.

## A note on quality

The user is often building something they'll rely on repeatedly. A focused system prompt that handles its real cases well beats an exhaustive one that buries the core behavior. Specificity over completeness, every time.

**Next steps:** After delivery, suggest `reality-check` to pressure-test the generated prompt for fabricated tool names, invented capabilities, or other hallucinations before the user deploys it. If they've now built several related prompts/specs, `drift-check` catches contradictions across the set. If the build session produced reasoning worth carrying forward, `conductor-memory` snapshots it. Skip the suggestion if the user only wanted a quick scaffold and is done.
