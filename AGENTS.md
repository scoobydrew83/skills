# Skills repository agent guide

## Canonical sources

- Author skills only in `.agents/skills/<name>/`; each directory requires `SKILL.md`.
- `plugins/coordinated-skills/skills/` is generated for Claude Marketplace. Never edit it directly; run `bash tools/build-plugin.sh` after changing canonical skills.
- `CLAUDE.md` and `GEMINI.md` are aliases of this file. Put cross-agent instructions here, not in provider-specific copies.

## Conductor contract

Follow `CONVENTIONS.md`: declare phase, handoffs, reads, and writes; use
`CONTEXT.md`, `MEMORY_BANK.md`, and `LOOP_QUEUE.md` for mutable shared state.
`AGENTS.md` is durable cross-agent policy, not session storage. Preserve the
required `Next steps` line. Verification skills use `Conductor verdict: PASS |
FAIL | BLOCKED`.

## Loop-first operating model

Every Conductor project follows: **Orient → Frame → Authorize → Execute →
Verify → Review → Learn**. Read `.harness/loop-policy.json` when it exists; it
is the machine-readable authority for retry limits, budgets, and human gates.
Do not begin implementation when the item is `AWAITING_HUMAN` or
`BLOCKED_HUMAN`.

Humans approve scope or acceptance-criteria changes, consequential unresolved
assumptions, secrets or spending, external communication, destructive work,
deployments, permission expansion, merge/release, and every third consecutive
verification failure. Agents may inspect, plan, test, and make bounded,
reversible branch changes without approval. Never silently cross a gate.

## Response baseline

Make every response easy to resume: lead with the result or current status,
state material assumptions and blockers plainly, chunk only the necessary
detail, and end with one **Next** action. At a human gate, end with
**Decision needed** and the smallest decision that unblocks work. Respect an
explicit request for a different format or detail level. This is an
accessibility baseline, not a diagnosis or a rigid template.

## Before handoff

Run `bash tools/sync-agent-layout.sh --check` and `bash tests/run-all.sh`. Use `bash tools/sync-agent-layout.sh --apply` only to create missing aliases and regenerate the Claude package; it refuses to overwrite existing files.
