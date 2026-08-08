# Skill Library — Coordination Conventions

These are the rules every skill in this library follows so they compose into a
real workflow instead of fourteen silos. If you add a skill to this set, or
fork one of these for your own project, hold to the contract below.

Status: phase 1 conventions, applied 2026-06-16. Phase 2 (top-level router,
non-code conductor-loop ingestion, session-close auto-fire) is deferred.

## 1. Coordination header (required in every SKILL.md)

Every SKILL.md frontmatter MUST include these four keys in addition to
`name` and `description`:

```yaml
phase: intake | plan | execute | verify | communicate | bookend | meta
hands_off_to: [skill-name, skill-name]
reads:  [CONTEXT.md, MEMORY_BANK.md]
writes: [MEMORY_BANK.md]
```

- **`phase`** — which lifecycle phase this skill belongs to. Single value from
  the vocabulary in §3.
- **`hands_off_to`** — the 0–4 sibling skills this skill should suggest next
  when it finishes. Empty list `[]` is valid for overlays and terminal skills.
  Use the exact skill `name`; don't guess.
- **`reads`** — shared-state files this skill reads before acting. Use `[]`
  when the skill is self-contained.
- **`writes`** — shared-state files this skill appends to. Use `[]` when the
  skill produces only its own artifact.

The descriptions, scripts, and references inside the skill don't change
shape — only the header gains these four keys.

## 2. Next-steps line (required at the end of the body)

Every SKILL.md MUST end with a single sentence (1–4 sentences when tailoring
helps) of the form:

> **Next steps:** When this skill finishes, suggest one of `<skill-a>` or
> `<skill-b>`. Skip if the user clearly wants to stop.

Tailor it per skill — don't paste a generic line. Name actual skills, and say
the condition that makes each one the right next move. This is what turns
the coordination header into actual behavior: Claude routes on description
text, so the closing sentence puts the next skill on the radar.

## 3. Phase vocabulary

Seven phases. Pick one per skill:

- **`intake`** — orient on a fresh ask, especially when the user is stuck
  or the request is too big or vague to act on directly. Output: a doable
  next step, not a plan.
- **`plan`** — turn a settled intake into ordered, sized work. Output: a
  task list, sequence, or design note.
- **`execute`** — do the actual work: generate the code, the doc, the
  prompt, the configuration, the response. Output: the deliverable.
- **`verify`** — grade existing work against acceptance criteria or
  external reality. Output: a structured verdict (see §5).
- **`communicate`** — a delivery overlay. Doesn't replace the underlying
  task; changes how the answer is packaged.
- **`bookend`** — open or close a session, snapshot state, retrieve
  prior context. Output: a launchpad or a handoff.
- **`meta`** — about the library itself (tombstones, deprecated stubs,
  router skills if/when added). Not user-triggered work.

A skill belongs to exactly one phase. If something legitimately spans phases
(e.g. `agent-orchestration` runs design → plan → build → test), put it in the
phase that owns its primary output and document the sub-phases inside.

## 4. Shared state contract

Five files coordinate state across skills. Three originate in the Conductor
Method and predate this convention set; `CLAUDE.md` is project-standard; and
`FEATURES.json` is the ground-truth artifact added with the harness. Use the
same filenames every time so skills can find them.

- **`CONTEXT.md`** — the project's mission, current phase, and acceptance
  criteria. Set up once per project; updated when scope or acceptance
  criteria change. Read by every skill that needs to know "what does done
  look like here?". Written by `agent-orchestration` (phase notes) and
  `conductor-memory` (project-context snapshots).
- **`MEMORY_BANK.md`** — the rolling log of settled decisions, verdicts,
  and "lessons" from completed work. Append-only in spirit. Every
  verification skill (`drift-check`, `reality-check`, `conductor-verifier`)
  appends a one-line verdict summary. `session-bookend`, `agent-orchestration`,
  and `conductor-memory` append lessons and decisions. Read by every skill
  that needs to avoid relitigating settled calls.
- **`LOOP_QUEUE.md`** — the conductor-loop work queue: pending, in
  progress, done. Created and maintained by the conductor loop
  infrastructure (`conductor-builder`, `conductor-verifier`, the nightly
  triage Action). Most skills here don't read or write it directly today;
  that may change in a later phase.
- **`CLAUDE.md`** — the per-project Claude Code instruction file. Holds
  loop protocol, gating rules, and the managed "Session Memory" block that
  `conductor-memory` refreshes. Read by Claude Code at session start.
- **`FEATURES.json`** — the phase's acceptance criteria as machine-checkable
  entries, and the thing verification grades against. JSON on purpose: models
  mangle JSON less than Markdown. Seeded from the spec by `conductor-init`;
  read by every skill that needs to know "what does done look like here?" in
  a form it can actually run. Where `CONTEXT.md` holds the prose mission and
  the constraints that aren't feature-shaped, `FEATURES.json` holds the
  criteria — when the two disagree, the JSON wins.

### FEATURES.json edit rules

The file is only useful if its entries can't be quietly reshaped to match
whatever got built. One entry per behavior, each with `id`, `category`,
`description`, `steps` (a runnable command plus its expected outcome),
`passes`, and `evidence`:

- **Builders may edit `passes` and `evidence` only.** Everything else —
  descriptions, steps, adding or removing entries — is a planner or human
  change, made in its own commit.
- **Editing or deleting a description or step is unacceptable**, because it
  hides missing or buggy functionality rather than reporting it.
- **`passes: true` requires `evidence`** a verifier can re-run: a test name,
  command output, or `file:line`. No evidence means the criterion failed.
- **A `passes: true` that can no longer be reproduced is drift, and fails the
  run** — the same rule the harness applies to itself.
- **A phase with zero entries is `BLOCKED`,** not passing. Missing criteria
  is a finding, never a free pass.

Skills that don't operate inside a Conductor-style project use `reads: []`
and `writes: []`. The convention is opt-in: a skill MAY read/write these
files when they exist, but MUST NOT require them.

### MEMORY_BANK.md line format

When a skill appends to `MEMORY_BANK.md`, use this line shape so multiple
skills' entries can be scanned together:

```
- YYYY-MM-DD · <skill-name> · <verdict-or-decision> · <one-line summary>
```

Example:

```
- 2026-06-16 · reality-check · PASS · validated MCP recommendation list, all 7 claims verified
- 2026-06-16 · agent-orchestration · DECISION · chose Postgres over SQLite for JSONB support
```

This is a starting format — refine it once we've run a week with real entries.

## 5. Verdict schema

Verification skills (`drift-check`, `reality-check`, `conductor-verifier`)
emit a `Conductor verdict:` block alongside their richer report:

- **`PASS`** — every load-bearing criterion is satisfied with evidence.
- **`FAIL`** — at least one criterion is unmet, fabricated, or
  contradicted. The report MUST include a `REQUIRED FIXES:` list (max 5,
  most severe first) so the producing skill can address them in order.
- **`BLOCKED`** — verification can't proceed without information that
  isn't available (missing acceptance criteria, no canonical mission to
  audit against, claims that need user confirmation). The block must say
  what would unblock it.

The verdict is in addition to whatever rich output the skill normally
produces — don't drop the tables and detail. `conductor-builder` reads
the verdict; humans read the detail.

### Skill telemetry

The skill graph in `skill-graph.md` describes which handoffs are *declared*.
Nothing today records which are *taken*, so no one can say which skills
produce FAILs or which `hands_off_to` edges are decoration. Two rules fix
that, and neither needs new infrastructure:

- **A skill records its own firing** using the §4 MEMORY_BANK line format —
  the same line it already writes, treated as the telemetry event rather
  than just a note. `- YYYY-MM-DD · <skill-name> · <verdict-or-decision> ·
  <one-line summary>`. The `<skill-name>` field is what makes the log
  groupable; use the exact frontmatter `name`, never a prose description.
- **A loop harness records which skill drove a phase** in the verdict row it
  persists, as `summary.skill`. Where a run-history DB exists (`sfdt
  history --type verdict --json`), that field is what joins a verdict back
  to the skill that produced the work.

Together these make the graph measurable: skills whose firings cluster with
FAILs are the ones to fix, and a declared handoff that never appears in a
following line is an edge to delete. This is the substrate `harness-improver`
mines — its ≥3-occurrence threshold needs a `<skill-name>` field it can
cluster on, so a skipped or free-text line is a silently lost signal.

Telemetry never blocks work: a skill that can't write its line proceeds
anyway. A missing line is a missing measurement, never a failed run.

## 6. Skill description hygiene

The library coordinates by description matching, so descriptions carry
weight:

- Use a hyphen-case `name` that matches the skill's directory name
  (`my-skill` → `plugins/coordinated-skills/skills/my-skill/SKILL.md`).
- Frontmatter description should list real trigger phrases the user might
  type, anti-triggers ("Do NOT trigger when…"), and the explicit
  partner-skill suggestions when relevant.
- The body's `**Next steps:**` line names successors by their exact
  `name`. Renaming a skill means updating every `hands_off_to:` and every
  Next steps line that references it.

## 7. Session close (resolved)

Phase 1 left one question open: **what signal closes a session and fires
`conductor-memory`?** The candidates were a `session-bookend` end-block, an
explicit user phrase, an `agent-orchestration` deploy-phase completion, or a
`conductor-verifier` PASS on the last queue item.

**Resolved: session close is itself the signal, and the clean-state exit
contract is where it's encoded.** None of the candidates generalized —
`session-bookend` only fires when invoked, a user phrase can't be relied on,
a deploy phase is one workflow among many, and a verifier PASS marks work
complete rather than a session ending. What every session has is an end, and
something already has to happen at that end: the tree must be left clean.

The contract, which lives in `agents/conductor-builder.md` and applies to any agent
ending a working session:

1. **The branch passes the same smoke test the next session runs on entry.**
   A session that ends red hands its breakage to a cold agent that can't tell
   it from its own.
2. **Commit, or revert/stash — never hand off a broken tree.** Half-finished
   work left in place reads as intentional to whoever picks it up.
3. **Append the MEMORY_BANK.md line** (§4 format, §5 skill telemetry). This
   is the durable trace of the session.
4. **Then fire the memory write** — `conductor-memory` for a session with
   decisions or context worth carrying forward, `session-bookend` for a
   routine stop. Step 3 is mandatory; step 4 is the fuller snapshot.

So `conductor-memory` no longer waits to be asked: reaching the end of a
session *is* the trigger, and the exit checklist is what makes it fire.
Sessions that produced nothing worth carrying still complete steps 1–3.

## 8. Tooling

The library ships with a small toolchain that enforces this contract.
`tools/validate-skill.sh --all` checks every skill against §1–§3,
`tools/skill-graph.sh` regenerates `skill-graph.md` from the skill source
directories so doc-drift is caught immediately, and `tests/run-all.sh`
runs the full structural + cross-skill consistency suite. The Claude Code
slash commands in `.claude/commands/` (e.g. `/skill-new`, `/skill-validate`,
`/skill-graph`) are the user-facing entry points and delegate to those
scripts. See `tools/README.md` and `tests/README.md` for details, and
`CONTRIBUTING.md` for the "add a new skill" workflow.

---

*Conventions are working agreements, not laws. When something here gets in
the way of a real workflow, change the convention and write down why —
this is a living contract.*
