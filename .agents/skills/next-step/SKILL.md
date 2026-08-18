---
name: next-step
description: >-
  Find the single safest next action when someone says "what now?", "I don't
  know what to do next", "where do I start", returns to a cold project, or has
  an unclear Conductor queue. Use it to orient from CONTEXT.md, MEMORY_BANK.md,
  LOOP_QUEUE.md, FEATURES.json, and loop policy before proposing work. It
  distinguishes a blocked human decision from actionable work and never invents
  missing acceptance criteria. Do NOT use for emotional overwhelm that needs a
  smaller activation-energy step; use overwhelm-breakdown instead.
response_contract: universal
phase: intake
hands_off_to: [assumption-grill, overwhelm-breakdown, agent-orchestration, conductor-router]
reads: [CONTEXT.md, MEMORY_BANK.md, LOOP_QUEUE.md]
writes: [MEMORY_BANK.md]
---

# Next Step

Use this as the calm on-ramp into a project. Read available state before asking
the user to repeat it. Run `scripts/route_next.py` when the project has a loop
queue; it is read-only and returns the first legal transition.

Respond in this order:

1. **Status** — one sentence: what is known, current queue state, and whether
   work is safe to start.
2. **One next action** — concrete, bounded, and sized to the available evidence.
3. **Why this action** — only the material constraint or dependency.
4. **Decision needed** — only when a human gate or missing criterion blocks it;
   state the smallest decision that unblocks work.

Never turn an unknown into a confident plan. Missing criteria, contradictory
state, or a required gate is a useful answer, not a failure. If the person is
overwhelmed, hand off before presenting a long route. If a consequential
assumption blocks planning, create a decision card with `assumption-grill`.

**Next steps:** When a known queue item is ready, suggest `conductor-router` to
advance its lifecycle. When an unresolved material assumption exists, suggest
`assumption-grill`. If the task is large and emotionally hard to enter, suggest
`overwhelm-breakdown`; if it is settled and multi-stage, suggest
`agent-orchestration`.
