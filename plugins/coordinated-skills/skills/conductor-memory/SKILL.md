---
name: conductor-memory
description: Extract and build a complete memory pack from a Claude conversation or session, synthesizing it into vault-ready artifacts so the next session resumes with full context. Produces a conversation summary, artifact index, communication-style and project-context notes, a machine-readable seed JSON and persona YAML, verification and maintenance checklists, and a generalized integration.py that copies the pack into an Obsidian vault and updates a Claude Code resume pointer (with an optional MCP/vector-store hook). Use this whenever the user says 'build conductor memory', 'extract memory from this conversation', 'capture this session', 'snapshot our progress', 'save this to memory', or 'update conductor memory' - and also when wrapping up a substantial working session that should persist for continuity across Claude Code, Obsidian, or MCP, even if they don't say the word 'memory'. Built for the Conductor Method continuity system; works for any project needing durable cross-session memory.
phase: bookend
hands_off_to: [session-continuity]
reads: [CONTEXT.md, MEMORY_BANK.md]
writes: [MEMORY_BANK.md, CONTEXT.md]
---

# Conductor Memory

Turn a working session into a durable memory pack so the next session starts
already knowing the project, the decisions, the working style, and the exact next
step. The expensive thing to lose between sessions isn't the code - it's the
*reasoning and context*. This skill captures that and lands it where the next
session will actually read it: an Obsidian vault and a Claude Code resume pointer.

The work splits cleanly: scripts handle the deterministic scaffolding and checks;
Claude handles the one thing only Claude can do well - reading the session and
synthesizing what mattered.

## When to reach for this

Whenever a session produced decisions, state, or context worth carrying forward.
the user may say it directly ("build conductor memory", "snapshot this") or it may
just be the natural end of a substantial session. When in doubt, offer it.

## What gets produced

A single timestamped pack folder containing:

- `MEMORY_INDEX.md` - the spine; a "resume here" pointer plus links to everything
- `<project>_memory_conversation_summary.md` - decisions, evolution, where we left off
- `<project>_memory_artifacts_index.md` - what was created and how it connects
- `<project>_memory_communication_style.md` - how to work with the user / persona
- `<project>_memory_project_context.md` - profile, stack, goals, success metrics
- `<project>_memory_seed_data.json` - the same content, machine-readable
- `<project>_memory_personality.yaml` - persona configuration
- `<project>_memory_verification.md` - how to confirm the pack is good
- `<project>_memory_maintenance.md` - the upkeep routine
- `integration.py` - places the pack into the vault + updates Claude Code

`<project>` defaults to `conductor`; override it for other projects.

---

## The workflow

Five phases. Stop at each **Checkpoint** - they exist so a wrong assumption gets
caught early instead of propagating through ten files.

### Phase 0 - Locate the input and settle config

**0.1 Find the source.** Two cases:
- **The live conversation** (most common): synthesize from the current session's
  own context. No file to read - the conversation *is* the input.
- **An exported transcript** the user points to (`.md`, `.json`, etc.): read that file
  first, in full, before synthesizing.

If it's genuinely unclear which, ask one short question. Otherwise proceed.

**0.2 Settle config.** Defaults: project `conductor`, vault `~/your-vault`, memory
subdir `Conductor/memory`. These are starting points, not commitments - if the
session is about a different project, use that project's name and paths. Only ask
the user if something can't be reasonably inferred. You can pass overrides as flags
(see Phase 1) or write a small JSON config from `assets/config.example.json`.

**0.3 Pick where the pack is created.**
- In **Claude Code / a local environment** with the vault reachable: create it in a
  working directory; integration will copy it into the vault in Phase 4.
- On **claude.ai** (no access to the user's machine): create it under
  `/mnt/user-data/outputs/` so the user can download it, and treat Phase 4 integration
  as instructions for him to run locally rather than something you execute.

> **Checkpoint 0:** You know the input source, the project name + paths, and where
> the pack will be written. If any of those is a guess that would be costly to get
> wrong, confirm before continuing.

### Phase 1 - Scaffold the pack

Run the scaffold script. It creates the timestamped folder and writes the three
boilerplate files (integration.py, verification, maintenance) with your config
substituted in, so you never hand-write that boilerplate.

```bash
python scripts/scaffold_memory.py --output <where-to-create> \
  --project conductor --vault ~/your-vault --memory-subdir Conductor/memory \
  --claude-md ~/your-vault/Conductor/CLAUDE.md
```

(Or `--config path/to/config.json`.) It prints JSON with `pack_dir`,
`project_name`, and `files_to_author`. Read that output - those are the exact
filenames and location for Phase 2.

> **Checkpoint 1:** Scaffold printed a `pack_dir` and the list of files to author.

### Phase 2 - Synthesize the content (the core)

This is the part that matters. Read `references/templates.md` for the structure of
each authored file, then write them into `pack_dir`. Author all seven from
`files_to_author`: the five prose files, the seed JSON, and the persona YAML.

Synthesis principles - these are what separate a useful pack from a useless one:

1. **Write for the next session, not for an archive.** The reader is a future
   agent or the user trying to resume. The "resume here" line in MEMORY_INDEX is the
   highest-leverage sentence in the whole pack - make it a specific next action,
   not a vague status.

2. **Capture reasoning, not just outcomes.** "Chose X" is half a memory. "Chose X
   over Y because Z" is the part that's expensive to reconstruct and the part that
   stops the next session from relitigating a settled call.

3. **Derive style from the actual session.** The communication-style and
   personality files should reflect what you observed working *this* session -
   specific patterns, not generic boilerplate. If nothing distinctive emerged,
   keep it short rather than padding.

4. **Keep the structured files faithful to the prose.** seed_data.json and
   personality.yaml are the same content in a machine shape, for a vector/MCP
   store later. Don't introduce facts there that aren't in the prose.

5. **Describe working preferences, not diagnoses.** Capture *how the user likes to
   work* (e.g. "prefers explicit checkpoints and numbered phases"). Don't infer or
   record clinical or personal-sensitive labels - observed preferences are what
   actually help the next session and keep the pack appropriate to share.

> **Checkpoint 2:** All seven authored files exist in `pack_dir`, each filled with
> real synthesized content (no leftover `_TODO_` placeholders).

### Phase 3 - Verify

Run the validator. It objectively checks presence, that JSON/YAML parse and carry
required keys, and that the prose files were actually filled in.

```bash
python scripts/validate_memory.py --dir <pack_dir>
```

If anything FAILs, fix it and re-run. Common misses: a `_TODO_` left in
MEMORY_INDEX, or seed_data.json missing `next_tasks`. The validator is the
automated half of the verification checklist that's also written into the pack.

> **Checkpoint 3:** Validator reports all checks passed.

### Phase 4 - Integrate and report

**If the vault is reachable** (local / Claude Code), run the integration script
that scaffold generated inside the pack:

```bash
python <pack_dir>/integration.py            # add --dry-run first to preview
```

It copies the pack into the vault's memory subdir, updates a rolling `MEMORY_LOG`,
and refreshes a managed "Session Memory" block in the target `CLAUDE.md` so a fresh
Claude Code session loads the resume pointer automatically. The vector/MCP push is
an opt-in stub (`--push-store`) - leave it off unless the user has wired a backend.

**On claude.ai**, don't try to reach the vault. Instead, present the pack files for
download and tell the user the one command to run locally:
`python <pack_dir>/integration.py`.

Then report briefly: where the pack is, the "resume here" line, and any FAIL the
validator flagged that you couldn't resolve. Keep it short - the pack is the
deliverable, not a long write-up about it.

---

## Notes

- **Idempotent-ish:** re-running for the same project+date overwrites that day's
  boilerplate but won't clobber a different session's pack (folders are
  timestamped, and `--session-label` adds a slug to disambiguate same-day runs).
- **Other projects:** nothing here is conductor-specific except the defaults. Pass
  `--project`, `--vault`, `--memory-subdir`, `--claude-md` for any project.
- **Don't over-capture:** a throwaway exploratory session may not be worth a pack.
  Memory is for continuity, not a log of everything. Smaller, denser packs beat
  many shallow ones.
- **Files referenced here:** `scripts/scaffold_memory.py`,
  `scripts/validate_memory.py`, `references/templates.md`,
  `assets/config.example.json`, `assets/templates/` (boilerplate sources).

**Next steps:** This skill is the close-bookend for substantive sessions.
After the pack lands, suggest `session-continuity` as the matching open
skill for the next session — pointing at the resume line is exactly the
retrieval it's built for. Skip the suggestion when the snapshot is for
archival only and no follow-up session is planned.
