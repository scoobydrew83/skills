---
name: agent-workspace-compatibility
description: >-
  Set up or audit a portable agent-skills repository that uses .agents/skills
  as the canonical source, AGENTS.md as canonical persistent instructions, and
  generated provider packages. Use when migrating Claude, Codex, Gemini, or
  skills.sh skill layouts; do not use for ordinary application code changes.
response_contract: universal
phase: meta
hands_off_to: [drift-check]
reads: [AGENTS.md, CONVENTIONS.md]
writes: []
---

# Agent Workspace Compatibility

1. Inspect the canonical skills directory, provider package outputs, instruction
   aliases, and the build/check commands before making changes.
2. Keep one authored skill tree under `.agents/skills/`. Provider packages that
   disallow external symlinks must be generated as physical copies.
3. Make `AGENTS.md` the canonical always-on instruction file. Create only
   relative aliases for provider-specific filenames; never overwrite a real
   instruction file without explicit approval.
4. Make the build deterministic and add a check mode that detects generated
   output drift. Test clean setup, stale output, incorrect links, and repeated
   runs.
5. Use skills.sh for cross-agent installation and its copy mode where symlinks
   are unavailable.

**Next steps:** After a migration or audit, use `drift-check` to verify the
generated package, instructions, and documentation still agree.
