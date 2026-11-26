# Skill trim

The library has 25 skills, and every enabled skill's description is loaded
into each session. A skill that never fires still costs context and can be
picked by mistake. This page is the procedure for cutting the library down to
the skills that earn their place. It removes nothing by itself.

## 1. Gather usage

1. In each project where you use these skills, run `/skill-doctor` in Claude
   Code (v2.1.252 or later). It lists each skill with its context cost and how
   often it was used. It does not run over Remote Control, so run it in a
   local terminal or desktop session.
2. Run `/insights` in the same projects for a wider view of what you asked
   Claude to do.
3. Run `tools/skill-usage.sh <project-root> ...` from this repository, passing
   the roots of those projects. It counts each skill's MEMORY_BANK.md lines and
   `.harness/EVIDENCE.jsonl` rows and flags skills never seen. A skill can be
   used without writing a line, so treat NEVER-SEEN as a prompt to check, not
   proof of disuse.

## 2. Write the keep list

Fill in the table below. A skill stays if `/skill-doctor` shows real use, if
it guards something you can't afford to skip (for example `tinfoil` or
`leftpad` before a ship), or if you name a reason to keep it.

| Skill | /skill-doctor uses | skill-usage.sh | Decision | Reason |
| --- | --- | --- | --- | --- |
| | | | keep / try off / retire | |

## 3. Try before you retire

For a skill you are unsure about, switch it to `user-invocable-only` first,
so its description stops loading but `/<skill>` still works. Use the
`/skills` menu, which writes the choice to `.claude/settings.local.json`
under `skillOverrides`. The accepted values are `on`, `name-only`,
`user-invocable-only` and `off`. Live with it for a week or two.

## 4. Retire in a follow-up pull request

For each skill marked retire:

1. Delete its directory under `.agents/skills/`. Do not leave a stub, because
   a stub still loads a description.
2. Add `name=survivor` (or `name=-`) to `RETIRED` in
   `tests/test_retired_skills.sh`.
3. Remove references from the docs and skills that `test_retired_skills.sh`
   searches, and from `skill-graph.md`.
4. Run `bash tools/build-plugin.sh`, `bash tools/sync-agent-layout.sh --check`
   and `bash tests/run-all.sh`.
5. Note the retirement in MEMORY_BANK.md:
   `- YYYY-MM-DD · skill-librarian · DECISION · retired <skill>, <reason>`.
