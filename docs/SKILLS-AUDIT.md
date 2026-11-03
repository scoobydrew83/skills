# Skills audit — November 2026

**Result:** the library went from 31 skills to 25. Every skill now meets
Anthropic's Agent Skills authoring limits, and `tools/validate-skill.sh`
enforces them so they stay met. Six overlapping or deprecated skills were
merged or deleted. The reviewer skills are now part of the build loop. A hook
blocks hand edits to the generated plugin.

The Salesforce skills (`scoobydrew83/sfdt-skills`) are audited in
[§6](#6-salesforce-skills-sfdt-skills). That repo is generated from the
`scoobydrew83/sfdt` monorepo, so fixes belong in the monorepo.

## Contents
1. Anthropic best practices: where the library stood and what changed
2. How the skills work together
3. Drops and merges
4. Other improvements made
5. Current inventory
6. Salesforce skills (sfdt-skills)
7. Deferred recommendations

---

## 1. Anthropic best practices: where the library stood and what changed

The guidance in the request comes from two kinds of sources. The Agent Skills
docs at platform.claude.com are authoritative. The "first 100 lines" rule comes
from blog summaries, so it was treated as a sensible heuristic rather than
a spec rule.

| Rule | Source | Before | Now |
|---|---|---|---|
| Description ≤ 1,024 characters | Anthropic docs (spec limit) | 7 over: agent-orchestration 1315, hemlock 1309, neurodivergent-comms 1263, derisk-sequencer 1226, session-bookend 1116, reality-check 1108, visual-plan 1072. Nothing checked length | All 25 between 517 and 994. **FAIL** in the validator |
| Third-person description that says what, then when | Anthropic docs | 9 started "Makes your AI agent think like…", "Use…", or were written in second person | All open with what the skill does. **WARN** in the validator |
| SKILL.md under 500 lines | Anthropic docs | All under 250 ✓ | Same. **FAIL** in the validator |
| Crucial information in the first ~100 lines | Blog summaries (heuristic) | 5 skills opened with backstory: skill-librarian's workflow was at line 111, agent-orchestration's at line 75, hemlock's origin story, visual-plan's competitor framing | Workflow now leads in each |
| Progressive disclosure, one level deep, Contents list for long references | Anthropic docs | 3 references over 100 lines with no table of contents, 1 orphan template, a linter that wasn't named | Contents lists added, template linked, every file referenced. **WARN** in the validator |
| Degrees of freedom | Anthropic docs | Mostly well matched. agent-workspace-compatibility was too loose for a file-moving migration; hemlock was too rigid for casual idea talk | Layout work now names exact commands with a check loop; hemlock's broadest triggers ("let's start on", "kick off") are gone |
| Avoid over-prescription | Anthropic docs / blogs | Low overall: about 0–4 all-caps imperatives per skill | Unchanged. The remaining all-caps rules guard safety or irreversibility, which skill-librarian keeps on purpose |
| Checklists and feedback loops | Anthropic docs | Only 4 skills said "fix and re-run"; none had a copyable checklist | All linter-backed skills now say "run, fix, re-run until it passes"; checklists added to skill-librarian and conductor-init |
| Test across intended models | Anthropic docs | Trigger evals run on Haiku only; no execution evals per model | Unchanged; see [§7](#7-deferred-recommendations) |
| Hooks for rules that must never break | Blog summaries | No hooks. Every hard rule lived only in prose | `.claude/settings.json` adds a PreToolUse hook (`tools/hooks/guard-generated.sh`) that blocks edits to `plugins/coordinated-skills/` |
| No time-sensitive text | Anthropic docs | "Merged June 2026" notes and dated tombstones | Removed |
| Valid name | Anthropic docs | All valid ✓ | **FAIL** in the validator |

The rules are written down for future skills in `CONVENTIONS.md` §6 and in
skill-librarian's authoring checklist. Both point to the same validator, so
each rule has one home.

## 2. How the skills work together

**Lifecycle coverage.** The loop runs Orient → Frame → Authorize → Execute → Verify → Review → Learn.

| Stage | Skills | Assessment |
|---|---|---|
| Orient | next-step, session-bookend, conductor-doctor, overwhelm-breakdown | Was crowded, with 5 skills colliding on "where were we" and "what now". Merging left 4 with distinct jobs |
| Frame | hemlock, assumption-grill, derisk-sequencer, visual-plan, conductor-init | Clear after merging experiment-designer into derisk-sequencer |
| Authorize | next-step (`Decision needed`, `--human-decision`), visual-plan (blocking comments) | **Weak.** No skill assembles the approval packet for a human gate |
| Execute | agent-orchestration, loop-creator, goal-builder, system-prompt-builder, prompt-template-generator, repo-troubleshooting-guide | Good for producing artifacts. Implementing one queue item is the `conductor-builder` agent's job |
| Verify | reality-check, drift-check, tinfoil, leftpad, grandfather, conductor-doctor | Strong. tinfoil, leftpad and grandfather used to be unreachable; the verifier now applies them when a diff triggers them |
| Review | popquiz | **Was unwired.** agent-orchestration and loop-creator now hand off to it before merge, and the verifier names it for the `merge_or_release` gate |
| Learn | project-postmortem, conductor-memory, session-bookend (session lessons) | **Weak.** Turning MEMORY_BANK lessons into AGENTS.md rules is still manual |

**Overlap clusters found and how each was resolved**

| Cluster | Collision | Resolution |
|---|---|---|
| Ideas | hemlock, idea-validator, experiment-designer, derisk-sequencer and reality-check all claimed "is this worth building" | idea-validator deleted. experiment-designer merged into derisk-sequencer. hemlock owns "should this exist". reality-check owns "is this AI plan factually real" and no longer claims "worth doing" or "is this overkill" |
| Sessions | session-bookend and session-continuity on "where were we" and "catch me up"; next-step on "returns to a cold project" | session-continuity merged into session-bookend as a quick-recall mode |
| Routing | conductor-router called `next-step/scripts/route_next.py`, another skill's script, which broke whenever the router was installed alone | Merged into next-step, which now ships both the read script (`route_next.py`) and the write script (`transition.py`) |
| Library audit | agent-workspace-compatibility, skill-librarian and conductor-doctor all checked package drift | agent-workspace-compatibility folded into skill-librarian. conductor-doctor stays the read-only harness check |
| Breaking work down | neurodivergent-comms and overwhelm-breakdown both claimed "break it down" and "chunk this" | Those triggers removed from neurodivergent-comms |
| Response baseline | Stated in AGENTS.md, CONVENTIONS §5, and neurodivergent-comms | neurodivergent-comms now points at AGENTS.md as the baseline and describes itself as the deeper, cue-driven mode |

**Wiring fixes**
- neurodivergent-comms had lost its `**Next steps:**` line, which made the
  repo's own validator fail. It also made the canonical skill and the plugin
  copy disagree. Both are fixed.
- 11 skills had no incoming handoffs. popquiz now has two. tinfoil, leftpad and
  grandfather are reached through the verifier (`agents/conductor-verifier.md`
  and loop-creator's verifier template).
- Handoffs written in skill bodies pointed at deprecated skills
  (conductor-init → task-decomposition; derisk-sequencer → idea-validator).
  Both are fixed.
- conductor-memory handed off to a retrieval skill. It now hands off to
  session-bookend.

## 3. Drops and merges

| Removed | Now lives in | What moved |
|---|---|---|
| `idea-validator` (tombstone) | `hemlock` | Nothing; it was already merged. Deleting it removes 825 characters from every session's context |
| `task-decomposition` (tombstone) | `overwhelm-breakdown` | Nothing; already merged (612 characters saved) |
| `session-continuity` | `session-bookend` | Cue recognition, retrieval tips, memory-honesty rules, and a quick-recall mode with a worked example |
| `experiment-designer` | `derisk-sequencer` | The full pre-registration method in `references/experiment.md`, plus `scripts/falsifiability_linter.py` |
| `conductor-router` | `next-step` | The state-transition table and `scripts/transition.py` |
| `agent-workspace-compatibility` | `skill-librarian` | A portable-layout section that now names the real commands |

The trigger-eval prompts for each removed skill were added to its survivor's
file in `tests/triggering-evals/prompts/`. The old `tests/test_tombstones.sh`
was replaced with `tests/test_retired_skills.sh`, which fails if a retired name
comes back or is still referenced anywhere. Going forward, a retired skill is
deleted outright rather than kept as a stub (CONVENTIONS §6).

## 4. Other improvements made

- `tools/check-best-practices.rb`, called from `tools/validate-skill.sh`,
  checks description length, name format, body length, third-person wording,
  and Contents lists on long references.
- Running Python is now always written `python3 scripts/…`; some bodies used
  `python` and others `python3`.
- conductor-init:
  - The artifact count now matches the six artifacts it creates.
  - A step was added to seed `LOOP_QUEUE.md`, which it already committed but
    never created.
  - `writes:` now lists everything it writes.
  - Baseline checks are a copyable checklist.
  - It falls back gracefully when `tools/validate-loop-policy.py` isn't
    installed.
- Removed paths that only work on claude.ai (`/mnt/user-data/outputs`,
  `present_files`) from system-prompt-builder.
- loop-creator now says to copy `scripts/run_loop.sh` as-is and names
  `loop.config.sh.template`.
- The verifier agent treats FEATURES.json as the authoritative criteria,
  matching CONVENTIONS, and its output gains a `SPECIALIST CHECKS` line.
- Docs:
  - README and HOW-TO-USE now list every skill.
  - HOW-TO-USE had the skill count wrong (26; there are 25) and incorrectly
    said conductor-memory writes MEMORY_BANK.md.
  - CONDUCTOR-LOOP-GUIDE pointed at a nonexistent "update-rules skill".
  - The stale "Phase 2a is this commit" status line is gone.

## 5. Current inventory

| Skill | Phase | Body lines | Description characters | Supporting files | Hands off to |
|---|---|---|---|---|---|
| `agent-orchestration` | execute | 107 | 705 | — | popquiz, reality-check, drift-check, session-bookend |
| `assumption-grill` | plan | 30 | 517 | — | next-step, derisk-sequencer, agent-orchestration |
| `conductor-doctor` | verify | 20 | 524 | scripts | next-step, skill-librarian |
| `conductor-init` | intake | 210 | 888 | assets | loop-creator, agent-orchestration |
| `conductor-memory` | bookend | 181 | 994 | assets, references, scripts | session-bookend |
| `derisk-sequencer` | plan | 99 | 825 | references, scripts | hemlock, agent-orchestration, loop-creator |
| `drift-check` | verify | 108 | 691 | references, scripts | reality-check, conductor-memory |
| `goal-builder` | execute | 112 | 523 | assets, references, scripts | loop-creator |
| `grandfather` | verify | 79 | 761 | scripts | conductor-memory |
| `hemlock` | verify | 123 | 857 | references, scripts | derisk-sequencer |
| `leftpad` | verify | 83 | 761 | scripts | reality-check |
| `loop-creator` | execute | 154 | 682 | assets, references, scripts | reality-check, drift-check, goal-builder, popquiz |
| `neurodivergent-comms` | communicate | 148 | 766 | — | — |
| `next-step` | intake | 62 | 740 | scripts | assumption-grill, overwhelm-breakdown, agent-orchestration, conductor-doctor |
| `overwhelm-breakdown` | intake | 115 | 968 | — | agent-orchestration, neurodivergent-comms, session-bookend |
| `popquiz` | verify | 81 | 677 | scripts | conductor-memory |
| `project-postmortem` | bookend | 131 | 703 | scripts | conductor-memory |
| `prompt-template-generator` | execute | 112 | 815 | references, scripts | drift-check, reality-check |
| `reality-check` | verify | 139 | 762 | references, scripts | drift-check, conductor-memory |
| `repo-troubleshooting-guide` | execute | 91 | 820 | references, scripts | drift-check |
| `session-bookend` | bookend | 112 | 700 | — | overwhelm-breakdown, agent-orchestration, conductor-memory, next-step |
| `skill-librarian` | meta | 124 | 782 | — | drift-check, conductor-doctor |
| `system-prompt-builder` | execute | 94 | 734 | references | reality-check, drift-check, conductor-memory |
| `tinfoil` | verify | 76 | 785 | scripts | conductor-memory |
| `visual-plan` | plan | 85 | 804 | commands, demo-blocks.json, reference.md, tools | agent-orchestration, loop-creator |

## 6. Salesforce skills (sfdt-skills)

`sfdt-skills` is generated by `sfdt skills export --target pack` from the
`scoobydrew83/sfdt` monorepo (`skills/`) and overwritten on every release. Fixes
therefore belong in the monorepo. All 10 skills are under 250 lines with
descriptions of 339–631 characters, so they already meet the hard limits. The
problems are structure, safety and accuracy.

**How they work together:** they don't hand off to each other at all. Natural
chains such as apex-review → test/pmd-scan → deploy and org-audit → the review
skills are never named. Rules are duplicated across skills:

| Duplicated rule | Appears in |
|---|---|
| SOQL/DML in loops | 4 skills |
| CRUD/FLS | 4 skills |
| Test-class standards | 3 skills |
| Scratch push/pull | sf-deploy and sf-scratch-org |
| Data seeding | sf-data and sf-scratch-org |

The coverage-threshold key is documented in two different files. The sfdt-cli
description claims "deployment, testing, coverage", which collides with
sf-deploy and sf-test.

**Ranked fixes**
1. **Production safety.**
   - Add a production gate to sf-deploy: detect production via `isSandbox`,
     require validate → quick-deploy, and stop to confirm before destructive
     changes.
   - Add warnings to `--ignore-conflicts` and `--no-prompt` (sf-scratch-org)
     and to bulk delete and anonymous Apex (sf-data).
   - Longer term, ship a PreToolUse hook through the Claude plugin target.
2. **Code Analyzer v5 accuracy** (sf-pmd-scan; check against
   `sf code-analyzer run --help`):
   - selector syntax `engine=pmd` → `pmd`
   - `rules list --engine` → `rules --rule-selector`
   - remove `--version`
   - update the engine list (`sfge`, `flow`, `regex`, `cpd`, `retire-js`)
3. **Handoffs and anti-triggers.** Give every skill a Next-steps line, narrow
   sfdt-cli's triggers, and drop the over-broad triggers `component`, `query`,
   `SELECT` and `security review`.
4. **De-duplicate by ownership:**
   - apex-review owns the Apex rules
   - sf-test owns test standards and the coverage threshold
   - sf-data owns SOQL and loading
   - sf-scratch-org owns push/pull
   - org-audit delegates to the others
5. **Portability.**
   - "this Salesforce project" → "a Salesforce DX project"
   - read paths from `sfdx-project.json` `packageDirectories` instead of
     hardcoding `force-app/main/default`
   - rename `SF-Rebuild-Ruleset`
6. **Progressive disclosure.**
   - Move the rule catalogs, templates, ruleset XML, CI YAML and command
     catalogs into `references/`, so each SKILL.md opens with its workflow.
   - Add Contents lists to sfdt-cli's `config.md` and `development.md`.
7. **Factual fixes:**
   - sf-test: assert style, the per-class "75%" claim, and an assert in the
     catch-block template
   - sf-deploy: RunLocalTests is not the only option for production
   - sf-flow-review: callout ≠ bulkification; the version-count note
   - sf-data: the OFFSET 2,000-row cap; the COUNT() claim
   - apex-review: prefer `WITH USER_MODE` over `SECURITY_ENFORCED`
8. **Version pins.** Remove API `63.0`, "Spring '26 beta" and Node ≥ 18.
9. **`triggers:` frontmatter.** It is not part of the spec and nothing in
   either repo reads it. Fold its phrases into descriptions unless an sfdt
   export target uses it.
10. **CI.** Add a validator (description length, links, manifest ↔ frontmatter
    match) to the sync job.

## 7. Deferred recommendations

- **Per-model testing.** Trigger evals run on `claude-haiku-4-5` only, and
  nothing runs skill bodies. Add outcome evals that run each skill's
  workflow on Haiku, Sonnet and Opus. Start with the linter-backed skills,
  where pass/fail is mechanical.
- **Linter fixtures.** None of the 10 bundled linters has a fixture test.
  One passing and one failing document per linter would catch regressions.
- **Custom frontmatter keys.** `phase`, `hands_off_to`, `reads`, `writes` and
  `response_contract` sit at the top level. Claude Code ignores unknown keys,
  but the open Agent Skills spec expects them under `metadata:`. Moving them
  touches every skill and every convention test, so it should be its own
  change. `response_contract` is always `universal` and could be dropped.
- **Authorize and Learn gaps.** Candidate skills:
  - a "gate packet" that assembles evidence, options and the smallest
    decision for a human gate;
  - a "lesson → rule" skill that proposes AGENTS.md rules from repeated
    MEMORY_BANK lessons.
- **More hooks for target repos.**
  - Block edits to FEATURES.json `description`/`steps` from builders.
  - Block merge or deploy commands while the queue item is `AWAITING_HUMAN`
    or `BLOCKED_HUMAN`.
- **Shared boilerplate.** The `Conductor verdict` mapping (8 skills) and the
  MEMORY_BANK append text (10 skills) repeat similar prose. A short shared
  section in CONVENTIONS §5, linked from each skill, would give each rule one
  home.
