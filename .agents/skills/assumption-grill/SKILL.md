---
name: assumption-grill
description: >-
  Surface and resolve the assumptions that would make a plan unsafe before
  implementation starts. Use when a request has consequential ambiguity,
  competing interpretations, unclear ownership, irreversible choices, missing
  success measures, or a person asks "what are we assuming?". It creates a
  compact decision card with evidence, reversibility, owner, and the smallest
  test or human decision that resolves each material unknown. Do NOT use for
  routine implementation details that can safely be decided while building.
response_contract: universal
phase: plan
hands_off_to: [next-step, derisk-sequencer, agent-orchestration]
reads: [CONTEXT.md, MEMORY_BANK.md]
writes: [MEMORY_BANK.md]
---

# Assumption Grill

Find only assumptions that can change scope, safety, cost, or the definition of
done. Do not manufacture a risk register for ordinary implementation details.

For each material assumption, emit a decision card:

```
Assumption: <literal claim>
Evidence: <known fact / missing evidence>
If wrong: <concrete consequence>
Reversible: yes | no
Owner: agent | human
Resolution: <smallest test or exact decision>
Gate: none | <loop-policy human gate>
```

Classify a decision as human-owned when it changes acceptance criteria, causes
spend, touches secrets, affects external people, is destructive, expands
permissions, deploys, merges, or remains unresolved after the available
evidence. End with the one decision or experiment that unlocks the most work.
Append only settled decisions to `MEMORY_BANK.md`; open assumptions belong in
the decision card or queue, not durable memory.

**Next steps:** When a card names a safe experiment, suggest `derisk-sequencer`
for risk-ordered execution. When a human must decide, hand off to `next-step`
to present the smallest gate. When assumptions are settled, suggest
`agent-orchestration` for the implementation sequence.
