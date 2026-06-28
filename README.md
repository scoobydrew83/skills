# Skills

[![CI](https://github.com/scoobydrew83/skills/actions/workflows/test.yml/badge.svg)](https://github.com/scoobydrew83/skills/actions/workflows/test.yml)

A coordinated library of Claude skills with explicit handoffs, shared state, and a maker/checker loop.

Most skill collections are a flat folder of independent prompts. This one is wired together: every skill declares which phase of work it belongs to (`intake`, `plan`, `execute`, `verify`, `communicate`, `bookend`, `meta`), which siblings it hands off to when it finishes, and which shared-state files it reads and writes. That turns a pile of skills into a workflow.

## What's in here

- **[`plugins/coordinated-skills/skills/`](plugins/coordinated-skills/skills)** — the skills themselves, one directory per skill (`SKILL.md` plus any references/scripts). This is the source of truth; edit these directly. A `.skill` zip archive is a build artifact you produce on demand (`tools/pack-skill.sh`) for the drop-in-a-skills-folder use case — it's gitignored, not committed.
- **[`CONVENTIONS.md`](CONVENTIONS.md)** — the contract every skill follows. Coordination header, Next-steps line, phase vocabulary, shared-state files, verdict schema.
- **[`CONTRIBUTING.md`](CONTRIBUTING.md)** — how to add or modify skills, with the `/skill-new` → `/skill-validate` → `/skill-graph` workflow.
- **[`tools/`](tools/)** — bash scripts to validate, graph, pack, and build the plugin from the skill set.
- **[`tests/`](tests/)** — the test suite that enforces CONVENTIONS.md across the library.
- **[`.claude/commands/`](.claude/commands/)** — slash commands (`/skill-new`, `/skill-validate`, `/skill-pack`, `/skill-graph`, `/skill-status`, `/conductor-loop`) that drive the tools.
- **[`skill-graph.md`](skill-graph.md)** — auto-generated phase × handoffs map of the current library.

## Quick start

Install the whole library as a Claude Code plugin (recommended):

```
/plugin marketplace add scoobydrew83/skills
/plugin install coordinated-skills@scoobydrew-skills
```

Skills then load namespaced, e.g. `/coordinated-skills:goal-builder`.

Or grab a single skill à la carte — copy its directory into your skills folder:

```sh
# Cowork / Claude Code skills folder, adjust path for your setup
cp -r plugins/coordinated-skills/skills/overwhelm-breakdown ~/.claude/skills/
```

Prefer a single portable file? Build a `.skill` archive first:

```sh
bash tools/pack-skill.sh overwhelm-breakdown   # → dist/overwhelm-breakdown.skill
```

Run the slash commands (inside Claude Code, from this repo):

```
/skill-status          # show which skills exist and which phase each is in
/skill-validate --all  # run the conventions checks
/skill-graph           # regenerate skill-graph.md
```

Validate the library from the shell:

```sh
bash tools/validate-skill.sh --all
bash tests/run-all.sh
```

A green run is 180 checks pass, 0 fail, 2 warn (the two intended tombstones).

## Usage

Three ways to use the library, smallest to largest.

### 1. One skill, on its own

Every skill is self-contained — most declare `reads: []` / `writes: []` and need
no setup. Once the plugin is installed, invoke one directly:

```
/coordinated-skills:goal-builder     # turn a vague intent into a checkable /goal
/coordinated-skills:loop-creator      # scaffold a builder/verifier loop package
```

Or, outside the plugin, drop a single `.skill` into your skills folder (see Quick
start). Pick skills à la carte — nothing requires the rest of the set.

### 2. The coordinated workflow (skills hand off)

Installed together, the skills route to each other. Each one ends by naming its
likely successor, and Claude's router picks that up — so a session flows through
phases without a top-level controller:

`intake → execute → verify → bookend`, with `communicate` as an overlay.

- **intake** — `overwhelm-breakdown` turns a too-big ask into one doable step.
- **execute** — the builders (`agent-orchestration`, `system-prompt-builder`,
  `prompt-template-generator`, `loop-creator`, `goal-builder`,
  `repo-troubleshooting-guide`) produce the deliverable.
- **verify** — `reality-check` (fabricated claims/tools) and `drift-check`
  (cross-doc contradictions) grade it, emitting `PASS | FAIL | BLOCKED`.
- **bookend** — `session-bookend`, `conductor-memory`, `session-continuity`
  snapshot state so the next session resumes cold.
- **communicate** — `neurodivergent-comms` changes how an answer is packaged,
  not what's produced.

Example chain: `overwhelm-breakdown → agent-orchestration → reality-check →
conductor-memory`. The full map is in [`skill-graph.md`](skill-graph.md).

Coordination is **opt-in**: handoffs are suggestions, and the shared-state files
(`CONTEXT.md`, `MEMORY_BANK.md`) are read only when they exist — see
[`CONVENTIONS.md`](CONVENTIONS.md) §4. A skill never *requires* the others.

**Starting it.** There is no "start coordination" command — coordination is
emergent, not a mode you switch on. You start by invoking whichever skill matches
where you are; it suggests the next when it finishes. For the full chain, the
front door is the only `intake` skill:

```
/coordinated-skills:overwhelm-breakdown
```

It turns a too-big ask into one doable step, then hands off through
execute → verify → bookend. If you already know the work, skip intake and start
at the execute skill that fits (e.g. `:system-prompt-builder`, `:loop-creator`) —
it'll suggest verify/bookend at the end. Two caveats: the handoff is a
*suggestion* the router surfaces, not an auto-chain (you let the next skill run or
invoke it), and the shared-state half only activates if `CONTEXT.md` /
`MEMORY_BANK.md` exist — create them first for a full Conductor loop, skip them
for a one-off.

### 3. The maker/checker loop

For autonomous "iterate until it passes" work, `loop-creator` generates a loop
package (builder prompt, a *separate* verifier, harness, hard stop) and
`goal-builder` writes the single `/goal` condition that drives an unattended
Claude Code run. The repo also ships a `/conductor-loop` command that runs the
builder→verifier pattern directly. The rule the whole library enforces: **the
doer never grades its own work, and "close is FAIL."**

## Add a new skill

See [`CONTRIBUTING.md`](CONTRIBUTING.md). The short version: `/skill-new <name>` to scaffold a directory under `plugins/coordinated-skills/skills/`, edit its `SKILL.md`, `/skill-validate <name>`, then `/skill-graph` to update the map. (`/skill-pack` is only needed when you want a standalone `.skill` file to distribute.)

## Architecture

Each skill is a directory (`plugins/coordinated-skills/skills/<name>/`) containing a `SKILL.md` with frontmatter, body, and optional references/scripts; a `.skill` zip archive of that directory is an optional build artifact for à-la-carte distribution. Beyond the standard `name` / `description`, every SKILL.md in this library carries four coordination keys (`phase`, `hands_off_to`, `reads`, `writes`) and ends with a tailored `**Next steps:**` sentence that names the actual successor skill. Claude's auto-router picks up that closing sentence, so the routing is data-driven rather than orchestrated by a top-level controller. Shared state lives in a small set of files (`CONTEXT.md`, `MEMORY_BANK.md`, `LOOP_QUEUE.md`, `CLAUDE.md`) defined in CONVENTIONS.md §4. Verification skills (`drift-check`, `reality-check`) emit a `Conductor verdict: PASS | FAIL | BLOCKED` block that the maker/checker conductor loop consumes. The full design rationale is in [`COORDINATION-STATUS.md`](COORDINATION-STATUS.md) and the contract is in [`CONVENTIONS.md`](CONVENTIONS.md).

## Status

Phase 1 (headers, merges, conventions) and Phase 1.5 (tooling, slash commands, tests, CONTRIBUTING) are shipped. Phase 2a (repository + CI) is this commit. See [`COORDINATION-STATUS.md`](COORDINATION-STATUS.md) for the full phase log, what's deferred, and the answers to the original design questions.

## License

[MIT](LICENSE). © 2026 scoobydrew83.
