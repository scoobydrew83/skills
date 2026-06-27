# Skill Library Coordination — Status

*Phase 1 (headers, merges, CONVENTIONS.md) shipped 2026-06-16. Phase 1.5
(tooling, slash commands, test suite, CONTRIBUTING) shipped 2026-06-17.
Read this file to see what's done, what's deferred, and how the open
questions were answered.*

## Phase 1.5 — tooling, commands, tests

Built 2026-06-17. The library now has the scaffolding for distribution and
ongoing maintenance:

- **`tools/`** — `validate-skill.sh`, `skill-graph.sh`, `pack-skill.sh`,
  `build-plugin.sh`, plus a `tools/README.md`. Plain bash, idempotent,
  `--help` on every script. The skill directories under
  `plugins/coordinated-skills/skills/` are the source of truth;
  `validate-skill.sh --all` enforces CONVENTIONS.md across the library;
  `skill-graph.sh` regenerates `skill-graph.md` from those directories
  (drift from this doc is the doc's problem); `pack-skill.sh` builds an
  optional `.skill` archive into `dist/` for à-la-carte distribution.
- **`.claude/commands/`** — `/skill-status`, `/skill-new`, `/skill-validate`,
  `/skill-pack`, `/skill-graph`, `/conductor-loop`. Thin wrappers around the
  shell scripts and the existing conductor-builder / conductor-verifier pair.
- **`tests/`** — `test_structure.sh`, `test_consistency.sh`,
  `test_roundtrip.sh`, `test_tombstones.sh`, `test_conventions.sh`, run by
  `tests/run-all.sh`. Pure bash, no install. Triggering tests (does each
  skill actually fire on its description?) are flagged as phase 2 in
  `tests/README.md` — they need an LLM in the loop.
- **`CONTRIBUTING.md`** — distribution-facing entry point linking
  CONVENTIONS.md, the tools and tests READMEs, and a 5-step "add a new
  skill" using the slash commands.
- **`skill-graph.md`** — auto-generated phase × handoffs table + Mermaid
  diagram. Matches the table below.

Validation as of 2026-06-17:

- `tools/validate-skill.sh --all` → 182 checks, 182 pass, 0 fail, 2 warn
  (the warns are the two intended tombstones).
- `tests/run-all.sh` → 5 test scripts, all pass.
- `tools/skill-graph.sh` → regenerates cleanly; output matches the table
  in this doc.

## What changed

## What changed

### Count: 14 → 12

| Removed (merged) | Surviving target |
|---|---|
| `task-decomposition` | `overwhelm-breakdown` |
| `adaptive-communication` | `neurodivergent-comms` |

Both merged source files still exist on disk as tiny tombstone `.skill`
archives because the build environment couldn't delete them. Each tombstone's
description begins with "DEPRECATED" and routes to its survivor; treat them
as no-ops and remove them from the folder when you can delete locally.

### Coordination headers added to every SKILL.md

Each surviving skill now carries four new frontmatter keys:

```yaml
phase: intake | plan | execute | verify | communicate | bookend | meta
hands_off_to: [skill-name, skill-name]
reads:  [CONTEXT.md, MEMORY_BANK.md]
writes: [MEMORY_BANK.md]
```

…and a tailored `**Next steps:**` sentence at the bottom of the body. The
final phase × neighbors map is below; see `CONVENTIONS.md` for the rules.

| Skill | phase | hands_off_to |
|---|---|---|
| `session-continuity` | bookend | session-bookend |
| `session-bookend` | bookend | overwhelm-breakdown, agent-orchestration, conductor-memory |
| `overwhelm-breakdown` | intake | agent-orchestration, neurodivergent-comms, session-bookend |
| `agent-orchestration` | execute | reality-check, drift-check, conductor-memory, session-bookend |
| `system-prompt-builder` | execute | reality-check, drift-check, conductor-memory |
| `prompt-template-generator` | execute | drift-check, reality-check |
| `repo-troubleshooting-guide` | execute | drift-check |
| `reality-check` | verify | drift-check, conductor-memory |
| `drift-check` | verify | reality-check, conductor-memory |
| `conductor-memory` | bookend | session-continuity |
| `neurodivergent-comms` | communicate | — (overlay) |

(Tombstones — `adaptive-communication`, `task-decomposition` — are phase
`meta` and route to their survivors only.)

### Verdict block in verification skills

`drift-check` and `reality-check` now emit a `Conductor verdict: PASS | FAIL
| BLOCKED` line inside their reports, alongside the existing rich tables.
That brings them into compositional reach of `conductor-builder` /
`conductor-verifier`, which already use that schema.

### `CONVENTIONS.md` added at the folder root

Documents the header format, Next-steps requirement, phase vocabulary,
shared-state contract (CONTEXT.md / MEMORY_BANK.md / LOOP_QUEUE.md /
CLAUDE.md, plus a `MEMORY_BANK.md` line format), the verdict schema, and
the one open question still pending. ~1 page; this is the contract anyone
extending the library should read first.

### Backup of originals

Every original `.skill` and `.md` was copied to `backups-2026-06-16/`
before any edits. If something here broke, restore from there.

## What's deferred (later phases)

- **Top-level router skill.** The maintainer confirmed yes, eventually — but not yet.
  Wait until we have 1–2 weeks of data on how the headers route in real
  conversations. If the headers do all the routing the library needs, the
  router never gets built; if obvious gaps appear, the router design is
  informed by them.
- **Conductor loop ingesting non-code work.** The maintainer confirmed yes, later
  phase. The verdict schema in `CONVENTIONS.md` is forward-compatible with
  this, so when it happens the verifier won't need re-engineering. The
  changes will be in `CONDUCTOR-LOOP-GUIDE.md` and the `LOOP_QUEUE.md`
  item shape, not in the skill set.
- **Session-close auto-fire signal for `conductor-memory`.** Genuinely
  open — the maintainer flagged it as TBD. Today `conductor-memory` only fires when
  the user asks; the answer needs real-session data to pick the right
  signal among the four candidates (`session-bookend` end-block,
  `agent-orchestration` deploy completion, `conductor-verifier` PASS on
  the last queue item, or an explicit user phrase). Captured in
  `CONVENTIONS.md` §7 so it's not forgotten.

## Answers to the six open questions (from the proposal)

1. **Where does shared state live across non-Conductor skills?** YES —
   `drift-check` and `reality-check` reports append to `MEMORY_BANK.md`.
   The line format is documented in `CONVENTIONS.md` §4 and is a starting
   point: `- YYYY-MM-DD · <skill-name> · <verdict-or-decision> · <one-line summary>`.

2. **Personal use or distribution?** DISTRIBUTABLE. Conventions are
   documented in `CONVENTIONS.md`. Headers and the phase vocabulary are
   stable enough for others to fork from.

3. **Top-level router skill eventually?** YES, but not yet. Deferred to
   phase 2 once header data exists.

4. **Merge or coexist for the duplicate pairs?** MERGE. Both pairs are
   merged; the survivors absorbed the best content from each side and
   note the merge in their bodies.

5. **Should the conductor loop ingest non-code work?** YES, later phase.
   Verdict schema unified in advance to make this cheap when it happens.

6. **Canonical "session is closed" signal?** STILL OPEN. Captured in
   `CONVENTIONS.md` §7; revisit after a week or two of real use.

## What to watch for now that this is live

- **Do the Next-steps lines fire in practice?** The hypothesis is that
  Claude's auto-router picks them up because descriptions are how it
  routes. If chains start emerging unprompted (e.g.
  `system-prompt-builder` → `reality-check` without the user naming the
  second skill), the convention is working.
- **Does any handoff feel wrong in real use?** A few of the
  `hands_off_to:` choices were judgment calls. If
  `repo-troubleshooting-guide → drift-check` keeps firing in cases where
  there's nothing to drift-check, that's a signal to drop the handoff.
- **Does the `MEMORY_BANK.md` line format hold up?** It's a starting
  shape; refine once there are real entries from multiple skills in the
  same project.

## Judgment calls worth sanity-checking

A few choices the maintainer should glance at:

- **`conductor-memory` writes to `CONTEXT.md` as well as `MEMORY_BANK.md`.**
  Its `integration.py` refreshes the managed "Session Memory" block in
  the project's CLAUDE.md and produces a project-context note that
  effectively *is* a CONTEXT.md snapshot. Listing `CONTEXT.md` in its
  `writes:` reflects that. If you'd rather CONTEXT.md stay human-only,
  drop it from the `writes:` list.
- **`agent-orchestration` listed under `phase: execute`** rather than
  giving it its own phase. The proposal called it "execute (multi-phase)";
  I kept it in `execute` and documented the sub-phases inside the skill.
  If a workflow runs into a case where the outer phase mismatches, this
  is the first thing to revisit.
- **`session-bookend` hands off to `conductor-memory`** at the close
  end. That's the natural pairing, but it means the bookend skill is
  signaling toward the bookend-close skill, which is unusual. Reads fine
  in practice — flagging it so you notice if it feels odd.

## Phase 2a — Repository & CI

Shipped 2026-06-16: [`README.md`](README.md) (front door), [`LICENSE`](LICENSE) (MIT), and [`.github/workflows/test.yml`](.github/workflows/test.yml) (runs `validate-skill.sh --all` + `tests/run-all.sh` on every push/PR to `main`, with an optional gated step for triggering evals).

---

*Built on the proposal. Refer back to `backups-2026-06-16/COORDINATION-PROPOSAL.md`
for the original design rationale.*
