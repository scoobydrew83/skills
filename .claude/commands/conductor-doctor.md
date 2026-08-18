---
name: conductor-doctor
description: Audit the local Conductor harness without changing it.
argument-hint: [repo path]
---

# /conductor-doctor $ARGUMENTS

Run the portable diagnostic and present its result without repairing files:

When installed as a plugin, run:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/conductor-doctor/scripts/doctor.py" "${ARGUMENTS:-${CLAUDE_PROJECT_DIR:-.}}"
```

When used from this repository's `.claude/commands`, replace
`${CLAUDE_PLUGIN_ROOT}/skills` with `.agents/skills`.

Lead with `PASS`, `FAIL`, or `BLOCKED`. List only failed checks, then one
**Next** action. A required approval must be labeled **Decision needed**.
