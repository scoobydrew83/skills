---
name: skill-pack
description: Build a distributable .skill archive from a skill's source directory into dist/.
argument-hint: <skill-name | --all>
---

# /skill-pack $ARGUMENTS

Wrapper around `bash tools/pack-skill.sh $ARGUMENTS`.

The skill directories under `plugins/coordinated-skills/skills/` are the source
of truth; this command produces a `dist/<name>.skill` build artifact (gitignored)
for the "drop a single skill into your skills folder" use case. It does **not**
modify the source.

If pack-skill.sh fails, surface its error and stop — don't pretend it
succeeded.
