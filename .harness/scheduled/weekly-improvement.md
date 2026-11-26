# Weekly harness improvement (scheduled task prompt)

This is the prompt for a weekly cloud scheduled task (`/schedule`) that runs
`harness-improver` on this repository. It is a prompt only. Create the
scheduled task after the routing and hardening changes have landed and one
supervised `/conductor-loop` run has written real rows to
`.harness/EVIDENCE.jsonl`, so the first unattended run has signal to mine.

Suggested settings when you create it:

1. **Repository:** this repository only.
2. **Schedule:** weekly.
3. **Model and effort:** Opus 5.5 (`opus` alias) at high effort. Claude Code
   defaults to medium, so set high explicitly.
4. **Permissions:** may push branches and open pull requests; may not merge.

## Prompt

```
Run the harness-improver agent (agents/harness-improver.md) on this repository.

1. Mine the last 30 days of .harness/EVIDENCE.jsonl, MEMORY_BANK.md
   (including "(repeat)" lessons) and git log, as the agent describes.
2. Only categories with 3 or more occurrences qualify.
3. Open at most 3 pull requests, one finding each, each with an explicit
   --base equal to the branch you started on. Never merge.
4. Do not edit AGENTS.md, HARNESS-FEATURES.json descriptions, FEATURES.json
   entries or verdict history.
5. Append the run line to MEMORY_BANK.md. A week with no qualifying signal
   ends with a one-line "no signal" note and no pull request.
6. End your report with "Next:" and the one action for a human, or
   "Decision needed:" for an escalation.
```
