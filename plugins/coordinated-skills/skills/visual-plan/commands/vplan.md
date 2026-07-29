---
description: Visual plan — structure the plan as blocks, render it, serve it for review
---

# /vplan — plan visually, then wait for review

You are planning $ARGUMENTS. Do NOT write product code in this session. Produce a reviewable visual plan instead:

1. **Investigate** the repo enough to plan honestly: read CLAUDE.md's pointer table, FEATURES.json, ROADMAP/CONTEXT if present, and the code areas the task touches. Read `.harness/plan/blocks.json` and `comments.jsonl` if they exist — you may be revising a plan, not starting one.

2. **Write the plan as blocks**, not prose: create/update `.harness/plan/blocks.json` (schema v2 — every block has a stable `id`, a `section`, and `features` refs). Use the right block for the thought:
   - `note` for intent and scope (keep to 2-3);
   - `diagram` (mermaid) for any flow you'd otherwise describe in a paragraph;
   - `decision` for every choice with a rejected alternative — rationale mandatory;
   - `annotated-code` for the files you'll touch, pinned to real line numbers (the renderer pulls live source — a wrong line number will be visible);
   - `question` for anything you need the human to decide — do NOT guess and bury the guess in a note.

3. **Seed/extend FEATURES.json** with the plan's acceptance criteria (planner commit — you are the planner right now; entries you add must cite a source doc or this plan's block ids in `source`). Every block should cite the features it serves.

4. **Lint, render, and serve:** run `node tools/render-plan.mjs --check` — it exits 1 on structural defects (dangling feature refs, duplicate block ids, `annotated-code` citing lines that don't exist). Fix them; do not hand over a plan that fails its own lint. Then start the server in the background (`node tools/plan-serve.mjs` via run_in_background) and tell the human: the URL, how many blocks/questions/features, and that comments they pin will block features until answered.

5. **Stop.** Planning ends here. The human reviews in the browser (or ignores it and replies in chat — both land in the same loop). When they come back, /address-comments is the next move, not building.

Rules: blocks.json and FEATURES.json edits only — no product code, no test edits. If the repo has no harness files at all, say so and offer conductor-init instead of improvising.
