# tools/

Shell scripts that operate on the skill source directories under
`plugins/coordinated-skills/skills/<name>/`. All are plain bash and rely only
on macOS-default `unzip` / `zip`. Run them from the repo root.

The skill directories are the **source of truth** — edit them directly. The
user-facing entry points are the Claude Code slash commands in
`.claude/commands/`; the scripts here are the underlying implementations.

## Scripts

### `validate-skill.sh <skill-name|--all>`

Checks one or all skills against `CONVENTIONS.md`. Verifies:

- the skill's directory and `SKILL.md` exist
- Frontmatter contains `name`, `description`, `phase`, `hands_off_to`,
  `reads`, `writes`
- `phase` is one of `intake | plan | execute | verify | communicate | bookend | meta`
- Every `hands_off_to:` entry names a real skill in this repo
- The body has a `**Next steps:**` line

Returns nonzero on any FAIL. Tombstones (DEPRECATED skills) are flagged with a
WARN and don't fail the run.

```bash
tools/validate-skill.sh --all
tools/validate-skill.sh overwhelm-breakdown
```

### `skill-graph.sh`

Regenerates `skill-graph.md` at the repo root from the skill source
directories. Output: phase × handoffs table + a Mermaid diagram. Source of
truth is the directories — if this drifts from `COORDINATION-STATUS.md`, the
source wins and the doc needs updating.

```bash
tools/skill-graph.sh
# → skill-graph.md (replaced)
```

### `pack-skill.sh <skill-name|--all>`

Builds a distributable `.skill` archive from a skill's source directory into
`dist/<skill-name>.skill`. The archive is a build artifact (gitignored), for
the "drop a single skill into your skills folder" use case — not the source.

```bash
tools/pack-skill.sh overwhelm-breakdown
# → dist/overwhelm-breakdown.skill
tools/pack-skill.sh --all
# → dist/*.skill
```

### `build-plugin.sh`

Regenerates the plugin/marketplace manifests (`marketplace.json`,
`plugin.json`, the plugin `README.md`) around the skill directories. It never
touches the skill directories themselves. Re-run after changing identity
(author/version/marketplace name) at the top of the script.

```bash
tools/build-plugin.sh
```

## Conventions

- All scripts accept `--help`.
- All scripts are idempotent — safe to re-run.
- All scripts use absolute paths derived from their own location; you can
  invoke them from anywhere.
- `.skill` archives and `dist/` are build outputs and gitignored; the skill
  directories under `plugins/coordinated-skills/skills/` are what's committed.

## Dependencies

`bash`, `unzip`, `zip`, plus standard POSIX utilities (`awk`, `sed`, `grep`,
`find`, `sort`, `tr`, `mktemp`). All ship with macOS.
