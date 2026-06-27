# Contributing

This library is distributable: people fork it, copy individual skills out,
or extend it for their own projects. The conventions and tooling exist so
those workflows don't break.

Start here:

- **[`CONVENTIONS.md`](CONVENTIONS.md)** — the contract every skill in this
  set follows. Coordination header, Next-steps line, phase vocabulary,
  shared-state files, verdict schema. Read first.
- **[`tools/README.md`](tools/README.md)** — the shell scripts that validate,
  graph, pack, and build the plugin from the skill directories. Plain bash, no install.
- **[`tests/README.md`](tests/README.md)** — the test suite that enforces
  CONVENTIONS.md across the library. `tests/run-all.sh` is the entry point.
- **[`COORDINATION-STATUS.md`](COORDINATION-STATUS.md)** — current state of
  the library and what's deferred to later phases.
- **[`skill-graph.md`](skill-graph.md)** — auto-generated map of the
  current phases and handoffs. Regenerate with `tools/skill-graph.sh`.

## Add a new skill in 4 steps

The Claude Code slash commands in `.claude/commands/` are the user-facing
entry points. Each one wraps a `tools/` script and adds a bit of guidance. The
skill directories under `plugins/coordinated-skills/skills/<name>/` are the
source of truth — you edit them directly.

1. **`/skill-new <name>`** — scaffold
   `plugins/coordinated-skills/skills/<name>/SKILL.md` with the right
   frontmatter and a Next-steps placeholder. The command will ask you for
   description, phase, and `hands_off_to:` targets.
2. **Edit the new `SKILL.md`.** Write the real body. Replace the Next-steps
   placeholder with a tailored one that names the actual successor skills
   (see CONVENTIONS.md §2 for the format).
3. **`/skill-validate <name>`** — run the conventions check. Fix any FAILs
   it reports (each one points at the CONVENTIONS.md section that defines
   the rule).
4. **`/skill-graph`** — confirm the new skill appears in the phase ×
   handoffs table and that no edges look wrong.

When you're done, run `tests/run-all.sh` to confirm the library is still
all-green. To hand someone a single skill as one file, run
`tools/pack-skill.sh <name>` → `dist/<name>.skill` (a build artifact, not
committed).

## Style notes

- Skill names are hyphen-case (`my-skill`) and match the skill's directory
  name under `plugins/coordinated-skills/skills/`.
- Descriptions list real trigger phrases and anti-triggers — Claude routes
  on description matching, so this is what determines whether the skill
  actually fires.
- `hands_off_to:` is 0–4 sibling skill names; empty list is valid for
  overlays and terminal skills.
- Verification skills emit a `Conductor verdict: PASS | FAIL | BLOCKED`
  block on top of their rich output.
- If you change `name`, update every `hands_off_to:` and every Next-steps
  line that mentions the old name. The tests will catch dangling refs.

## Changing a convention

CONVENTIONS.md is a living contract, not a law. If something in it gets in
the way of a real workflow, update CONVENTIONS.md first (including a brief
note on why), then update the affected skills and tests, then run the test
suite to confirm everything's still consistent.
