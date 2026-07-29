# Conductor Visual Plans — the plan is the ground truth, rendered

**Prompted by:** BuilderIO/agent-native's `/visual-plan` + `/visual-recap` (structured plan blocks, hosted app, shareable links, comments). **Verdict on theirs:** right instinct — plans should be structured blocks agents can read and update, not walls of markdown — wrapped in the failure mode our harness exists to kill: the plan is a **second source of truth**, hosted outside the repo, with **no grading**. Nothing detects a beautiful plan drifting from reality, and their recap is narrative, not evidence.

**Our inversion, one sentence:** the visual plan is not a document the agent writes — it is a **rendering of ground truth the harness already maintains** (FEATURES.json, `.harness/telemetry.jsonl`, git history), plus repo-local plan blocks that are linted like everything else. Derived, never authoritative (golden principle #2). A plan that cannot drift, and a recap that cites verdict rows instead of telling a story.

## Why ours is better, point by point

| | agent-native Plans | Conductor Visual Plans |
|---|---|---|
| Source of truth | The hosted plan app | The repo; plan.html is derived, read-only |
| Drift | Undetected — plan and code diverge silently | Impossible by construction: re-render = re-truth; block lint runs in `check:all-contracts` |
| "Done" claims | Whatever the plan says | FEATURES.json `passes` + dated evidence; verifier-graded |
| Recap | Narrative from a diff | Rendered from persisted verdicts + git — the telemetry the improver already mines |
| Dependencies | Their app, their infra, network | Zero-dep node script; works offline; mermaid CDN optional with `<pre>` fallback |
| Versioning | App database | Git — every plan state is a commit, diffable, revertable |
| Comments | Hosted comment threads | `question` blocks in-repo: reviewer adds, builder must answer before the phase passes (lintable); PR review stays the human channel |
| Sharing | Their URLs | Static plan.html — commit it, attach to a PR, or serve via `sfdt ui` |

What we adopt from them without shame: the block-library idea (typed blocks with schemas, not free HTML), wireframes-grounded-in-your-product, and plan-before-build as a ritual.

## V2 — the review loop (the back-and-forth, analyzed)

**The gap v1 left:** plan.html is derived and read-only — the human could look but not answer back. A visual plan without a write channel is a poster. The channel options, ranked:

1. *Hand-edit blocks.json* — tracked and agent-readable, but nobody pins comments by editing JSON; that friction is why visual tools exist at all.
2. *Static HTML with export-a-file* — browsers can't write to the repo; download-and-save dies of neglect.
3. *PR review as the channel* — already works and already mined by the flywheel, but comments can't pin to blocks and don't block features. Keep it as the merge-time channel, not the planning channel.
4. *Hosted app with comments (agent-native's answer)* — solves pinning, breaks repo-locality and gradeability.
5. **Chosen: tracked `comments.jsonl` + two writers.** `plan-comment.mjs` today (CLI, zero deps); the `sfdt ui` Plan page tomorrow (POST → same file — the GUI already runs a local Express server over local JSON, so pin-and-click costs one endpoint, zero new state).

**The protocol — comments are BLOCKED-criteria, not chat:**

1. Planner renders plan.html; human reviews.
2. Human pins a comment to a block (or directly to a feature). The row lands in `.harness/plan/comments.jsonl` — tracked, so committing it is how the builder sees it.
3. **An unresolved comment blocks every feature its target cites.** The board shows BLOCKED, the status header counts it, "Next action" points at it, and the verifier may not flip those features. Enforced by the same lint that guards blocks.
4. Builder's get-bearings step surfaces open comments (`plan-comment.mjs --list --open`). It answers by changing the plan or code, then `--resolve <id> --answer "..."` — an answer is mandatory; silent resolution is refused.
5. Re-render: the thread shows inline under its block with resolution state. The commit that resolves the comment carries the change that answers it.

**The part agent-native doesn't have:** comments.jsonl is *telemetry*. Resolved threads persist, so harness-improver can mine what humans keep asking — a recurring question is a missing doc or a missing lint, and the flywheel already knows how to convert those. Review friction becomes fuel. (Open question c-002 in the demo asks exactly this — whether the improver's agent definition should say so explicitly. It should.)

**Schema v2 (what changed and why):** every block gains a required stable `id` (nothing can pin to an anonymous block — this is the load-bearing addition) and an optional `section` (nav groups by it, authoring order preserved). Comments: `{id, block?, features?, author, text, created, resolved, answer?, resolvedAt?}`. Render structure: status header first (progress, blocked count, open comments, **next action** — the page answers "what do I do?" before "what is this?"), sticky section nav, feature↔block cross-links both directions, threads inline, recap and git last because they're reference, not decision.

## Architecture (v1 — repo-local, shipped as prototype)

```
.harness/plan/blocks.json     Authored plan blocks (the ONLY hand-written part)
FEATURES.json                 Already exists — the plan's task board
.harness/telemetry.jsonl      Already exists — the plan's live status + recap feed
git log                       Already exists — the plan's actual history
tools/render-plan.mjs         Zero-dep renderer -> .harness/plan/plan.html (derived, gitignored or committed, never edited)
```

**Block types (v1):** `note` (markdown-ish text), `diagram` (mermaid source — text, diffable, agent-writable), `wireframe` (ASCII/box sketch — deliberately low-fi, renders in a styled `<pre>`), `decision` (choice + rationale + rejected alternatives, mirrors MEMORY_BANK), `annotated-code` (file + per-line notes; renderer pulls the real lines from the repo so annotations can't cite code that doesn't exist), `question` (reviewer→builder, with `answer` field; unanswered = plan renders it red).

**Contracts (same spirit as FEATURES.json):**
- Blocks reference feature ids (`features: ["F-001"]`); the renderer cross-links; the lint fails a block citing a nonexistent feature id.
- `annotated-code` blocks fail lint if the file or line range doesn't exist — annotations are grounded, agent-native-style, but *enforced*.
- plan.html is derived output. Editing it by hand is the same sin as editing `generated/*`.
- The verifier may treat unanswered `question` blocks as BLOCKED for the features they reference.

**The two rituals, ours:**
- `/visual-plan` (skill: `conductor-plan`, phase: intake/planning) — planner writes/updates blocks.json + FEATURES entries, runs the renderer, hands the human a plan.html. Plan approval = the human's planner commit.
- `/visual-recap` — no new artifact needed: the renderer's recap section IS the telemetry timeline + git log since the last planner commit, each row linking verdict → feature → commit. Evidence-backed by construction.

## Roadmap (each layer optional, in order)

1. **v1 — now:** `render-plan.mjs` + blocks.json + lint (`check:plan` in check:all-contracts) + `conductor-plan` skill in the skills repo. Prototype in this folder, tested against real sfdt data.
2. **v2 — sfdt ui page:** the GUI already reads local JSON snapshots (audit/monitor pattern); a "Plan" page reads FEATURES.json/blocks.json/telemetry.jsonl live. Same data, zero new state.
3. **v3 — hosted with comments:** conductor-platform is the natural home (it already models workflow runs + approval gates); studio-by-sfdt's block-rendering machinery is the natural editor. Only build when PR-review comments prove insufficient — the platform gets a real feature with a proven local pattern behind it, not a speculative app.

## H-entries to add when adopting (planner commit to skills/HARNESS-FEATURES.json)

- **H-031** sfdt: `tools/render-plan.mjs` + `tools/plan-comment.mjs` exist and `check:plan` (block/comment lint) is wired into check:all-contracts.
- **H-032** skills: `conductor-plan` skill exists (phase: planning, hands_off_to: [conductor-builder]) documenting block schema v2 + the comment protocol; conductor-builder.md's get-bearings step gains "read open plan comments".
- **H-033** sfdt: `.harness/plan/blocks.json` exists for the active phase and passes lint (stable ids, live feature refs, no unresolved comments at phase close).
- **H-034** skills: harness-improver.md names comments.jsonl as a mining source (recurring questions → doc/lint conversions).

## Build prompts (after reviewing the prototype)

**Run from `$REPOS/sfdt`:** "Adopt the visual-plan prototype: copy render-plan.mjs from <folder> into tools/, write tools/check-plan-blocks.mjs (lint: schema per block type, feature ids exist in FEATURES.json, annotated-code files/lines exist, questions answered or phase != closing), wire `check:plan` into check:all-contracts, seed .harness/plan/blocks.json for the 1.0-stabilization phase from ROADMAP.md + FEATURES.json (one diagram of the release pipeline, one decision block per MEMORY_BANK decision, questions empty). One commit per H-feature, verify with check-harness."

**Run from `$REPOS/skills`:** "Add conductor-plan skill (phase: planning): documents block schema v1, the two rituals, the derived-never-authoritative contract; hands_off_to conductor-builder. Add H-031..H-033 to HARNESS-FEATURES.json with checks in check-harness.mjs (planner commit). Validate with tools/validate-skill.sh."
