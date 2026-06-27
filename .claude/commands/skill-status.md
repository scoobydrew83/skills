---
name: skill-status
description: Print current state of the skill library — counts, phase distribution, validation results, open questions.
---

# /skill-status

Snapshot of the skill library, intended as the "where are we?" entry point.

When invoked, do the following:

1. Run `bash tools/validate-skill.sh --all` and capture its output. The exit
   code tells you whether anything is failing; the summary line at the end
   tells you how many checks ran.
2. Run `bash tools/skill-graph.sh` to refresh `skill-graph.md` so the phase
   counts you report match reality. Then read the regenerated file.
3. From `skill-graph.md`, count:
   - Total skills (rows in the phase × handoffs table)
   - Active vs tombstone (look for "DEPRECATED tombstone" in the notes column)
   - Distribution across the seven phases
4. Open `COORDINATION-STATUS.md` and surface the "Open questions" / "What's
   deferred" sections — those are the live unknowns.

Output a short status block:

```
Skill library status
  Total skills: <n> (<active> active, <tombstones> tombstones)
  Phase distribution:
    intake: …  plan: …  execute: …  verify: …  communicate: …  bookend: …  meta: …
  Validation: <PASS|FAIL>  (<n> checks, <m> warnings)
  Open items: …list from COORDINATION-STATUS.md…
```

Keep it terse. If validation FAILED, name the failing skills and point at
CONVENTIONS.md for the convention they're breaking. Don't try to fix anything
here — that's `/skill-validate <name>` territory.
