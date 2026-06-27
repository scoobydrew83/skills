---
name: skill-new
description: Scaffold a new skill with the right frontmatter and a Next steps placeholder.
argument-hint: <skill-name>
---

# /skill-new $ARGUMENTS

Scaffold a new skill directory at `plugins/coordinated-skills/skills/<name>/`
ready for editing. The skill directories are the source of truth.

Workflow:

1. Parse `$ARGUMENTS` as the bare skill name. Reject if it isn't hyphen-case
   (`^[a-z][a-z0-9-]*$`) — point at CONVENTIONS.md §6 if the user gave
   something else.
2. Refuse if `plugins/coordinated-skills/skills/<name>/` already exists.
3. Ask the user (one question at a time) for:
   - One-paragraph `description` with trigger phrases and anti-triggers
   - `phase` (one of intake/plan/execute/verify/communicate/bookend/meta —
     see CONVENTIONS.md §3)
   - `hands_off_to:` — 0–4 sibling skill names. Validate that each is a real
     skill in the repo by checking the directories under
     `plugins/coordinated-skills/skills/`; reject unknowns.
   - `reads:` and `writes:` — defaults `[]`. Suggest CONTEXT.md /
     MEMORY_BANK.md if the user describes interaction with shared state.
4. Write `plugins/coordinated-skills/skills/<name>/SKILL.md` with this
   template, substituting the answers:

   ```
   ---
   name: <name>
   description: >-
     <description>
   phase: <phase>
   hands_off_to: [<comma-separated>]
   reads: [<comma-separated or empty>]
   writes: [<comma-separated or empty>]
   ---

   # <Title-Cased Name>

   _TODO: body. Replace this paragraph with the actual instructions a Claude
   running this skill should follow._

   **Next steps:** When this skill finishes, suggest one of `<name-a>` or
   `<name-b>`. Skip if the user clearly wants to stop. _(Replace with a
   tailored line — see CONVENTIONS.md §2.)_
   ```

5. Remind the author of next steps:
   - Edit `plugins/coordinated-skills/skills/<name>/SKILL.md` to write the real body.
   - Run `/skill-validate <name>` to check conventions.
   - Run `/skill-graph` to regenerate the handoff map.
   - Run `/skill-pack <name>` only if you need a standalone `.skill` file to distribute.
