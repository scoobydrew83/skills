---
name: visual-plan
description: >-
  Plan visually instead of dumping markdown: structure a plan as typed,
  lint-able blocks (.harness/plan/blocks.json — diagrams, wireframes,
  decisions, annotated real code, questions), render it to a plan.html derived
  entirely from ground truth (FEATURES.json, telemetry.jsonl, git), and serve
  it locally so the human reviews IN the page — pinned comments land in
  tracked comments.jsonl and BLOCK the features they cite until resolved with
  an answer. Use whenever someone says "visual plan", "/vplan", "plan this
  feature", "show me the plan", "make the plan reviewable", wants to review or
  comment on a plan, says "address my comments" / "/address-comments", or asks
  to see plan status rendered. Also use to structure a captured plan-mode plan
  (blocks tagged needs-structuring from the ExitPlanMode hook). The defining
  rule: the plan is a RENDERING of ground truth plus authored blocks — never a
  second source of truth; plan.html is generated and never hand-edited. Do NOT
  use for seeding a fresh repo's harness (that is conductor-init) or for
  designing loops (loop-creator).
phase: plan
hands_off_to: [agent-orchestration, loop-creator]
reads: [CONTEXT.md, FEATURES.json, MEMORY_BANK.md]
writes: [FEATURES.json, MEMORY_BANK.md]
---

# Visual Plan

Planning as a reviewable surface, not a wall of markdown. Inspired by
agent-native's `/visual-plan`, inverted to fit the Conductor Method: their plan
is a hosted document that can drift from the code; ours is a **lens over the
repo's existing ground truth** plus one small authored file, all tracked, all
lint-able, all blockable. Full analysis and rationale: [reference.md](./reference.md).

## The artifacts (all under the target repo)

| File | Who writes it | Role |
|---|---|---|
| `.harness/plan/blocks.json` | planner (you) | The authored plan: typed blocks, schema v2 |
| `.harness/plan/comments.jsonl` | human (page/CLI) + you (resolutions) | The review channel — comments are BLOCKED-criteria |
| `FEATURES.json` | planner commit | Acceptance criteria the plan promises; verifier grades these |
| `.harness/plan/plan.html` | `tools/render-plan.mjs` | DERIVED. Never hand-edit — same sin as editing `generated/*` |

## Block schema v2 (the contract)

Every block: stable `id` (comments pin to it), `type`, `section`, `title`,
`features` (ids that must exist in FEATURES.json). Types: `note`, `diagram`
(mermaid source), `wireframe` (ASCII sketch), `decision` (choice + rationale +
rejected — rationale mandatory), `annotated-code` (file + per-line notes; the
renderer pulls live source, so wrong lines are visible), `question` (needs
`answer` or it blocks its features).

## The rituals

**Planning (`commands/vplan.md`):** investigate → write blocks + FEATURES
entries → `node tools/render-plan.mjs` → serve with `tools/plan-serve.mjs`
(background) → hand over the URL → **stop**. No product code in a planning
session.

**Review loop (`commands/address-comments.md`):** list open comments
(`tools/plan-comment.mjs --list --open`) → answer each **by changing the
artifact** (block, decision, FEATURES entry) → resolve with a mandatory answer
→ re-render → report per-comment. An unresolved comment blocks every feature
its block cites; the verifier honors this.

**Capture (`tools/capture-plan.mjs`):** PostToolUse hook on ExitPlanMode so
Claude Code's default plan mode feeds the system too — raw plan preserved
under `.harness/plan/captured/`, placeholder block tagged needs-structuring.
Structure those blocks on your next planning pass.

## Installing into a repo

Copy `tools/*.mjs` into the repo's `tools/`, `commands/*.md` into
`.claude/commands/`, and add the ExitPlanMode hook to `.claude/settings.json`
(snippet in reference.md). Seed a first `blocks.json` from `demo-blocks.json`
if useful. Wire a `check:plan` lint into the repo's contract checks (see
reference.md H-031) so block/feature refs and unresolved comments are enforced
mechanically, not by convention.

## Rules

- Derived means derived: regenerate plan.html, never edit it.
- Comments are telemetry: resolved threads stay in comments.jsonl for the
  improver to mine (recurring questions = missing docs or lints).
- Never resolve a comment without changing something; the tool refuses empty
  answers, and a hollow answer is worse — it converts review into noise.
- No blocks without features, no features without a source.

**Next steps:** When the plan is approved (open comments at zero), suggest
`agent-orchestration` to sequence the build it describes, or `loop-creator` if
the work should run as an unattended builder/verifier loop. Skip if the user
clearly wants to stop at the plan.
