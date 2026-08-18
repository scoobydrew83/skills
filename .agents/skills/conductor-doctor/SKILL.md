---
name: conductor-doctor
description: >-
  Audit a repository's Conductor harness without changing it. Use when someone
  asks whether the loop is ready, why routing is blocked, whether state and
  policy agree, or to diagnose aliases, generated packages, criteria, evidence,
  queue transitions, and required tests. With `--library-root`, it also audits
  instruction aliases and the generated Marketplace package. It returns Conductor verdict PASS,
  FAIL, or BLOCKED with directly actionable repairs. Do NOT use it to silently
  repair a repository; it is read-only by design.
response_contract: universal
phase: verify
hands_off_to: [next-step, conductor-router, agent-workspace-compatibility]
reads: [CONTEXT.md, MEMORY_BANK.md, LOOP_QUEUE.md]
writes: [MEMORY_BANK.md]
---

# Conductor Doctor

Run `scripts/doctor.py <repo>` before a new loop, after moving work between
agents, and whenever the state feels unreliable. Add `--library-root <path>`
when auditing this skills library's aliases and generated Marketplace package.
It performs no writes.

Report in this order: **Status**, failed checks, exact repair, and one **Next**
action. A missing criteria/policy/queue artifact is `BLOCKED`; contradictory
state, illegal transition, stale generated package, or missing evidence for a
claimed pass is `FAIL`. Use `PASS` only when every available check is clean.

Do not turn a diagnostic result into a fix. Route the user to the owner of the
repair, and preserve the evidence for a verifier to reproduce.

**Next steps:** When the doctor finds state that needs a human decision,
suggest `next-step`. When the harness is healthy and a queue item is ready,
suggest `conductor-router`. When cross-agent aliases or package layout fail,
suggest `agent-workspace-compatibility`.
