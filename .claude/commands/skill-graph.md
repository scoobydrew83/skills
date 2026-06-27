---
name: skill-graph
description: Regenerate skill-graph.md from the skill source directories and display it.
---

# /skill-graph

Run `bash tools/skill-graph.sh`, then display the resulting `skill-graph.md`.

This is the canonical "what's the current shape of the library?" view. The
source of truth is the skill directories under
`plugins/coordinated-skills/skills/` — if the regenerated graph differs from
the table in `COORDINATION-STATUS.md`, the source wins and the doc needs
updating. Flag any drift.
