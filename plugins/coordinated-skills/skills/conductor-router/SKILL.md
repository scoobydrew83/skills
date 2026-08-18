---
name: conductor-router
description: >-
  Route one Conductor queue item through Orient, Frame, Authorize, Execute,
  Verify, Review, and Learn without doing the item itself. Use when an agent
  needs to determine the next legal lifecycle phase, resume a loop, reconcile a
  queue state with verdicts, or decide whether to escalate. It enforces loop
  policy, explicit human gates, evidence requirements, and the three-failure
  stop. Do NOT use it to bypass a human decision or to implement a queue item.
response_contract: universal
phase: meta
hands_off_to: [next-step, assumption-grill, conductor-doctor]
reads: [CONTEXT.md, MEMORY_BANK.md, LOOP_QUEUE.md]
writes: [MEMORY_BANK.md]
---

# Conductor Router

Read the project state and return one legal transition only. The authoritative
order is `FEATURES.json`, `.harness/loop-policy.json`, `LOOP_QUEUE.md`, current
verdict evidence, then narrative context. Use `next-step/scripts/route_next.py`
for the deterministic queue read.

When a human or verifier authorizes the transition, use
`scripts/transition.py <repo> <item-id> <state>`. It persists only a legal
queue transition and redacted evidence. Leaving a human-gated state requires
`--human-decision`; `VERIFYING → DONE` requires a feature ID and reproducible
`--check COMMAND|EXPECTED|ACTUAL` evidence. The runner never performs the work
item, sends outreach, deploys, or merges.

- **ORIENTING:** choose `PENDING` only when criteria and policy exist; otherwise
  choose `AWAITING_HUMAN` with the missing decision.
- **PENDING / IN_PROGRESS:** dispatch one bounded item to the builder.
- **VERIFYING:** dispatch an independent verifier. `PASS` becomes `DONE`; a
  `FAIL` returns only listed fixes to `IN_PROGRESS`; a third failure becomes
  `BLOCKED_HUMAN`.
- **AWAITING_HUMAN / BLOCKED_HUMAN:** do not dispatch. Present `Decision needed`
  and the evidence that makes it necessary.
- **DONE:** record the evidence and offer the next pending item or a clean stop.

The router never edits acceptance criteria, approves assumptions, merges, or
changes policy. It records only the chosen transition and its reason.

**Next steps:** When state or policy is malformed, suggest `conductor-doctor`.
When the person does not know the work's next action, suggest `next-step`.
When a material assumption blocks progress, suggest `assumption-grill`.
