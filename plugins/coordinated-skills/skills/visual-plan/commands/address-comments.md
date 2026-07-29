---
description: Read open plan comments, answer each by changing the plan, resolve with evidence
---

# /address-comments — the review loop, agent side

The human has reviewed the visual plan. Work the queue:

1. `node tools/plan-comment.mjs --list --open` — read every open comment. Also check `question` blocks in `.harness/plan/blocks.json` with no `answer`.

2. For EACH open item, in order:
   - Understand what it's really asking. A comment is a BLOCKED-criterion, not a suggestion — the features its block cites cannot pass while it's open.
   - **Answer by changing the artifact, not by replying.** Wrong assumption → fix the block. Missing alternative → extend the decision block's rationale/rejected list. Scope challenge → adjust FEATURES.json (planner edit, cite the comment id in `source`). Genuine question back to the human → answer what you can and leave the rest as a NEW `question` block; never resolve a comment you haven't actually addressed.
   - Resolve with the answer: `node tools/plan-comment.mjs --resolve <id> --answer "<what changed and where>"`. The tool refuses empty answers by design. The answer should point at the block/feature you changed.

3. Re-render and re-lint (`node tools/render-plan.mjs --check`). If plan-serve is running the human just reloads. A nonzero exit means your edits broke the plan's structure — fix before reporting.

4. Report: one line per comment — id, what it asked, what changed, resolved/bounced-back. Then the plan's new state: blocks, open questions, blocked features.

5. If zero comments were open, say exactly that and stop — do not manufacture plan changes to look busy.

Commit `.harness/plan/` changes as a planner commit (`plan: address review comments c-00X..c-00Y`). Product code remains out of scope until the human says build.
