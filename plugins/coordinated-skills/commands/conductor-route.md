---
name: conductor-route
description: Read Conductor state and report the one next legal lifecycle action.
---

# /conductor-route

Use the portable `conductor-router` contract; this command is a Claude adapter,
not a second loop implementation.

1. Set `skills_root="${CLAUDE_PLUGIN_ROOT:-.}/skills"`. When this command runs
   from the repository rather than the installed plugin, use
   `skills_root=".agents/skills"` instead.
2. Run `python3 "$skills_root/conductor-doctor/scripts/doctor.py"
   "${CLAUDE_PROJECT_DIR:-.}"`.
3. If it returns nonzero, report the first repair as **Next** and stop.
4. Run `python3 "$skills_root/next-step/scripts/route_next.py"
   "${CLAUDE_PROJECT_DIR:-.}"`.
5. Report its result in the response baseline: status, one legal action, and
   `Decision needed` if the item is at a human gate.

Never change queue state, invoke a builder, merge, deploy, or bypass policy from
this command. The user or the portable router owns the next transition.
