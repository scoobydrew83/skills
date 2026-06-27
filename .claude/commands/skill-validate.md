---
name: skill-validate
description: Validate one or all skills against CONVENTIONS.md.
argument-hint: <skill-name | --all>
---

# /skill-validate $ARGUMENTS

Run `bash tools/validate-skill.sh $ARGUMENTS`.

If `$ARGUMENTS` is empty, default to `--all`.

Surface the output as-is, then summarize: how many checks passed, how many
failed, how many warnings. For each FAIL, name:

- The skill
- The check that failed
- The exact section of CONVENTIONS.md to consult (§1 for frontmatter keys,
  §2 for Next steps, §3 for phase vocabulary, §6 for naming hygiene)

Don't auto-fix. The repair path is: edit
`plugins/coordinated-skills/skills/<name>/SKILL.md` directly →
`/skill-validate <name>`.
