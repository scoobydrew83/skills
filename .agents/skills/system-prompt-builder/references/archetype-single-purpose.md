# Archetype C — Single-Purpose Task Prompt

One focused instruction for a single, repeatable task. No modes, no phases — just a tightly specified prompt the user can run again and again, usually with variable injection for the parts that change.

Use this archetype when the user wants the AI to do *one job* the same way every time (e.g. "summarize support tickets into this format," "rewrite product copy for VP buyers").

This archetype is built on the **four pillars**: Persona, Task, Context, Format.

---

## Required section skeleton

Use XML tags so the structure is unambiguous and variables are easy to spot:

```
<persona> ... </persona>
<task> ... </task>
<context> ... </context>
<format> ... </format>
<example>   (include when the task involves subjective judgment)
  Input: ...
  Output: ...
</example>
```

Mark every variable the user will inject with a clear placeholder, e.g. `{{TICKET_TEXT}}`, `[TARGET_PERSONA]`.

---

## The four pillars

**Persona** — who the AI is. Include domain expertise, relevant experience context, and behavioral traits where they matter.
- Weak: `You are a helpful assistant.`
- Strong: `You are a B2B customer success manager with expertise in SaaS churn analysis. You communicate in clear, direct language and tie every observation to business impact.`

**Task** — exactly what to do. Active verb + specific deliverable + scope constraints.
- Weak: `Write something about our product.`
- Strong: `Write a 150-word product description for our enterprise CRM targeting VP-level buyers, emphasizing time-to-value and integration capabilities.`

**Context** — what the model can't assume. Audience, constraints (what to exclude/prioritize), background data, prior failed attempts. This is where variable injection points usually live.
- Weak: `Our customers are businesses.`
- Strong: `Audience: operations directors at mid-market manufacturers (200–1,000 employees). Non-technical, cost-sensitive, skeptical of AI claims. Avoid jargon; emphasize ROI and ease of implementation.`

**Format** — the shape of the output. Format type, length, section headers, tone.
- Weak: `Give me a list.`
- Strong: `Return a numbered list of exactly 5 items. Each: (1) recommendation in bold, (2) a 2-sentence rationale, (3) effort estimate (Low/Medium/High).`

---

## Interview question set

Usually answerable in one or two rounds; many answers come straight from the user's framing.

1. **Persona** — what role/expertise should the AI bring to this task?
2. **Task** — what's the single action and deliverable? Any hard constraints (length, count, depth)?
3. **Context** — who's the audience? What must be included, excluded, or prioritized? What background or data gets injected each run (→ variables)?
4. **Format** — exact output structure, length, and tone?
5. **Example** — if the task requires judgment, can you give one good input→output pair? (If not, construct one and label it.)

---

## Archetype-specific guardrails

- **All four pillars present.** A missing pillar is the most common cause of inconsistent output; if the user can't supply one, build a labeled default and flag it.
- **Include a complete example** whenever the task involves subjective judgment — show full input and full output, never a description. (Principles §6.)
- **Variables clearly delimited** so the user knows exactly what to swap each run.
- **Format must be specific enough to be repeatable** — "a list" is not a format; "a numbered list of exactly 5 items with these three fields" is.

---

## Condensed shape (illustrative)

```
<persona>
You are a [role] with [expertise]. You communicate [traits].
</persona>
<task>
[Active verb] a [deliverable] of [scope/length] for [purpose].
</task>
<context>
Audience: [who]. Prioritize [X]. Exclude [Y].
Data to process: {{INJECTED_VARIABLE}}
</context>
<format>
Return [structure]. Length: [bound]. Tone: [style].
</format>
<example>
Input: [real input]
Output: [full ideal output]
</example>
```
