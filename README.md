# Skills

[![CI](https://github.com/scoobydrew83/skills/actions/workflows/test.yml/badge.svg)](https://github.com/scoobydrew83/skills/actions/workflows/test.yml)

A coordinated library of portable agent skills with explicit handoffs, shared state, and a maker/checker loop.

Most skill collections are a flat folder of independent prompts. This one is wired together: every skill declares which phase of work it belongs to (`intake`, `plan`, `execute`, `verify`, `communicate`, `bookend`, `meta`), which siblings it hands off to when it finishes, and which shared-state files it reads and writes. That turns a pile of skills into a workflow.

**New here?** [`HOW-TO-USE.md`](HOW-TO-USE.md) is the fast path — the step-by-step chain to run when you have an idea and a PRD.

## What's in here

- **[`HOW-TO-USE.md`](HOW-TO-USE.md)** — start here. The seven-step chain from idea to shipped, with what each step produces and when to skip it.
- **[`.agents/skills/`](.agents/skills)** — the skills themselves, one directory per skill (`SKILL.md` plus any references/scripts). This is the source of truth; edit these directly. A `.skill` zip archive is a build artifact you produce on demand (`tools/pack-skill.sh`) for the drop-in-a-skills-folder use case — it's gitignored, not committed.
- **[`CONVENTIONS.md`](CONVENTIONS.md)** — the contract every skill follows. Coordination header, Next-steps line, phase vocabulary, shared-state files, verdict schema.
- **[`CONTRIBUTING.md`](CONTRIBUTING.md)** — how to add or modify skills, with the `/skill-new` → `/skill-validate` → `/skill-graph` workflow.
- **[`agents/`](agents/)** — the Conductor agent definitions: the `conductor-builder` / `conductor-verifier` maker/checker pair that `/conductor-loop` drives, plus the three scheduled flywheel agents (`harness-improver`, `doc-gardener`, `slop-gc`). `tools/validate-agents.sh` holds them to the same frontmatter contract skills follow.
- **[`HARNESS-FEATURES.json`](HARNESS-FEATURES.json)** + **[`check-harness.mjs`](check-harness.mjs)** — the harness graded by its own pattern. Every "the harness now does X" claim is an entry with a deterministic check; `node check-harness.mjs --repos <dir>` verifies them and a `passes: true` the checker can't reproduce is DRIFT. Run weekly by `.github/workflows/harness-check.yml`.
- **[`tools/`](tools/)** — bash scripts to validate, graph, pack, and build the plugin from the skill set. `tools/validate-skill.sh --all` is the enforcement pass CI runs.
- **[`tests/`](tests/)** — the structural test suite (`bash tests/run-all.sh`) CI runs on top of the validators.
- **[`.claude/commands/`](.claude/commands/)** — optional Claude adapters, including `/conductor-route` and `/conductor-doctor`; the portable loop contract remains in the skills and `AGENTS.md`.
- **[`skill-graph.md`](skill-graph.md)** — auto-generated phase × handoffs map of the current library.

## Quick start

Install for every skills.sh-supported coding agent (recommended):

```sh
npx skills add scoobydrew83/skills --all
```

The installer uses a canonical copy with per-agent symlinks by default; pass
`--copy` on filesystems that do not support symlinks. Claude Marketplace remains
available as a generated self-contained package:

```
/plugin marketplace add scoobydrew83/skills
/plugin install coordinated-skills@scoobydrew-skills
```

Skills then load namespaced, e.g. `/coordinated-skills:goal-builder`.

Or grab a single skill à la carte — copy its directory into your skills folder:

```sh
# Cowork / Claude Code skills folder, adjust path for your setup
cp -r .agents/skills/overwhelm-breakdown ~/.claude/skills/
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
/conductor-doctor       # read-only loop policy, state, and evidence audit
/conductor-route        # show the one next legal lifecycle action
```

Validate the library from the shell:

```sh
bash tools/validate-skill.sh --all   # per-skill CONVENTIONS.md checks
tools/sync-agent-layout.sh --check   # aliases + generated Claude package
bash tests/run-all.sh                 # full structural suite (validators + repo-shape invariants)
```

A green run reports 0 failures. `validate-skill.sh` also enforces Anthropic's
authoring limits (description ≤ 1,024 characters, SKILL.md ≤ 500 lines, valid
name) and warns on non-third-person descriptions.

## Runtime compatibility

The portable unit is a `SKILL.md` directory; skills.sh installs those into its
supported coding agents. Runtime-specific capabilities are deliberately called
out instead of inferred.

| Capability | Support |
| --- | --- |
| Core skills and handoff conventions | Portable through skills.sh-supported coding agents |
| Persistent repository instructions | Codex: `AGENTS.md`; Claude Code: `CLAUDE.md` alias; Gemini CLI: `GEMINI.md` alias |
| Claude Marketplace package and slash commands | Claude Code only |
| `/goal` completion conditions | Claude Code only (`goal-builder`) |
| Builder/verifier loop design | Portable; generated headless harness is Claude Code-specific when selected |
| Session memory packs | Portable; optional resume pointer writes to an explicit session-memory file, never `AGENTS.md` |

For runtimes outside Codex, Claude Code, and Gemini CLI, install the skills with
skills.sh and use that runtime's documented instruction-file mechanism. This
repository does not claim equivalent slash commands, subagents, or autonomous
loop controls where the runtime does not provide them.

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

`orient → frame → authorize → execute → verify → review → learn`, implemented
through the existing intake/plan/execute/verify/bookend phases, with
`communicate` as a universal delivery overlay.

- **intake** — `next-step` recovers one safe action from live state and routes
  one legal Conductor queue transition; `overwhelm-breakdown` turns a too-big
  ask into one doable step; `conductor-init` seeds a fresh repo's harness.
- **plan** — `visual-plan` renders the plan as reviewable, comment-blockable
  blocks over the repo's ground truth; `assumption-grill` turns consequential
  ambiguity into decision cards; `derisk-sequencer` orders tests ahead of
  building and pre-registers single experiments.
- **execute** — the builders (`agent-orchestration`, `system-prompt-builder`,
  `prompt-template-generator`, `loop-creator`, `goal-builder`,
  `repo-troubleshooting-guide`) produce the deliverable.
- **verify** — `reality-check` (fabricated claims/tools), `drift-check`
  (cross-doc contradictions), `hemlock` (should this exist at all),
  `tinfoil` (hostile input), `leftpad` (dependency intake), `grandfather`
  (breaking changes) and `popquiz` (merge comprehension) grade it, emitting
  `PASS | FAIL | BLOCKED`. `conductor-doctor` audits the harness itself. The
  loop's verifier applies `tinfoil`, `leftpad`, and `grandfather` when a diff
  triggers them, and `popquiz` gates merges.
- **bookend** — `session-bookend` (recall, opening recap, closing handoff),
  `conductor-memory` (durable memory pack), and `project-postmortem`
  (end-of-project lessons).
- **communicate** — `neurodivergent-comms` changes how an answer is packaged,
  not what's produced.
- **meta** — `skill-librarian` audits and maintains the library itself,
  including its portable `.agents/skills` layout.

Conductor projects also carry `.harness/loop-policy.json` (human gates and
limits) and `.harness/EVIDENCE.jsonl` (redacted reproducible evidence). The
router never advances an item past a human gate, and the third verifier failure
blocks for human review.

Example chain: `overwhelm-breakdown → agent-orchestration → reality-check →
conductor-memory`. The full map is in [`skill-graph.md`](skill-graph.md).

Coordination is **opt-in**: handoffs are suggestions, and the shared-state files
(`CONTEXT.md`, `MEMORY_BANK.md`) are read only when they exist — see
[`CONVENTIONS.md`](CONVENTIONS.md) §4. A skill never *requires* the others.

**Starting it.** There is no "start coordination" command — coordination is
emergent, not a mode you switch on. You start by invoking whichever skill matches
where you are; it suggests the next when it finishes. For the full chain, the
front door is an `intake` skill — `next-step` when the project already exists,
or `overwhelm-breakdown` when the ask feels too big:

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

See [`CONTRIBUTING.md`](CONTRIBUTING.md). The short version: `/skill-new <name>` to scaffold a directory under `.agents/skills/`, edit its `SKILL.md`, `/skill-validate <name>`, then `/skill-graph` to update the map. (`/skill-pack` is only needed when you want a standalone `.skill` file to distribute.)

## Architecture

Each skill is a directory (`.agents/skills/<name>/`) containing a `SKILL.md` with frontmatter, body, and optional references/scripts; a `.skill` zip archive of that directory is an optional build artifact for à-la-carte distribution. Beyond the standard `name` / `description`, every SKILL.md in this library carries four coordination keys (`phase`, `hands_off_to`, `reads`, `writes`) and ends with a tailored `**Next steps:**` sentence that names the actual successor skill. The portable router makes state transitions explicit rather than assuming a top-level Claude controller. Shared state lives in `CONTEXT.md`, `MEMORY_BANK.md`, `LOOP_QUEUE.md`, `AGENTS.md`, `.harness/loop-policy.json`, and `.harness/EVIDENCE.jsonl` as defined in CONVENTIONS.md §4. Verification skills (`drift-check`, `reality-check`, the reviewer skills, and `conductor-doctor`) emit a `Conductor verdict: PASS | FAIL | BLOCKED` block that the maker/checker conductor loop consumes. The contract is in [`CONVENTIONS.md`](CONVENTIONS.md).

## Status

25 skills. The November 2026 audit ([`docs/SKILLS-AUDIT.md`](docs/SKILLS-AUDIT.md)) merged six overlapping or deprecated skills, brought every description within Anthropic's authoring limits, and added validator checks so they stay there.

## License

[MIT](LICENSE). © 2026 scoobydrew83.
