---
name: next-step
description: >-
  Finds the single safest next action for a project and, in a Conductor loop,
  the one legal queue transition. Use when someone says "what now?", "I don't
  know what to do next", "where do I start", returns to a cold project, has an
  unclear Conductor queue, or an agent needs to resume a loop, reconcile queue
  state with verdicts, or decide whether to escalate. It orients from
  CONTEXT.md, MEMORY_BANK.md, LOOP_QUEUE.md, FEATURES.json, and
  .harness/loop-policy.json, separates a blocked human decision from actionable
  work, enforces human gates and the three-failure stop, and never invents
  missing acceptance criteria or does the queue item itself. Not for emotional
  overwhelm that needs a smaller activation-energy step (overwhelm-breakdown).
response_contract: universal
phase: intake
hands_off_to: [assumption-grill, overwhelm-breakdown, agent-orchestration, conductor-doctor]
reads: [CONTEXT.md, MEMORY_BANK.md, LOOP_QUEUE.md]
writes: [MEMORY_BANK.md]
---

# Next Step

The calm on-ramp into a project, and the router for a Conductor queue. Read
available state before asking the person to repeat it.

## 1. Orient (read-only)

When the project has a loop queue, run:

```bash
python3 scripts/route_next.py <repo>
```

It is read-only and returns the first legal transition. The authoritative order
is `FEATURES.json`, `.harness/loop-policy.json`, `LOOP_QUEUE.md`, current
verdict evidence, then narrative context. Without loop files, orient from
whatever project files and conversation context exist.

## 2. Respond

1. **Status** — one sentence: what is known, current queue state, and whether
   work is safe to start.
2. **One next action** — concrete, bounded, and sized to the available evidence.
3. **Why this action** — only the material constraint or dependency.
4. **Decision needed** — only when a human gate or missing criterion blocks it;
   state the smallest decision that unblocks work.

Never turn an unknown into a confident plan. Missing criteria, contradictory
state, or a required gate is a useful answer, not a failure. If the person is
overwhelmed, hand off before presenting a long route.

## 3. Advance a queue item (only when authorized)

When a human or verifier authorizes the transition, persist it with:

```bash
python3 scripts/transition.py <repo> <item-id> <state>
```

It writes only a legal queue transition and redacted evidence. Leaving a
human-gated state requires `--human-decision`; `VERIFYING → DONE` requires a
feature ID and reproducible `--check COMMAND|EXPECTED|ACTUAL` evidence. If the
script rejects the transition, report its message; don't work around it.

| State | Legal move |
|---|---|
| `ORIENTING` | `PENDING` only when criteria and policy exist; otherwise `AWAITING_HUMAN` with the missing decision |
| `PENDING` / `IN_PROGRESS` | Dispatch one bounded item to the builder |
| `VERIFYING` | Dispatch an independent verifier. `PASS` → `DONE`; `FAIL` returns only listed fixes to `IN_PROGRESS`; a third failure → `BLOCKED_HUMAN` |
| `AWAITING_HUMAN` / `BLOCKED_HUMAN` | Do not dispatch. Present `Decision needed` and the evidence behind it |
| `DONE` | Record the evidence; offer the next pending item or a clean stop |

This skill never performs the work item, edits acceptance criteria, approves
assumptions, sends outreach, deploys, merges, or changes policy.

**Next steps:** When state or policy is malformed, suggest `conductor-doctor`.
When an unresolved material assumption blocks progress, suggest
`assumption-grill`. If the task is large and emotionally hard to enter, suggest
`overwhelm-breakdown`; if it is settled and multi-stage, suggest
`agent-orchestration`.
