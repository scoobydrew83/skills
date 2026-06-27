# Memory Pack Templates

Structures for the files Claude authors during synthesis. The scaffold script
already wrote the boilerplate (integration.py, verification, maintenance); these
are the content-bearing files. Author each into the pack directory printed by
`scaffold_memory.py`. Replace `<project>` with the `project_name` from that output.

Guiding principle: write for the next session, not for an archive. Every file
should help a fresh agent (or the user) pick up the thread quickly. Favor specifics
(names, decisions, reasons, file paths, exact next action) over generic summary.

## Contents
1. MEMORY_INDEX.md
2. conversation_summary.md
3. artifacts_index.md
4. communication_style.md
5. project_context.md
6. seed_data.json
7. personality.yaml
8. Worked mini-example

---

## 1. MEMORY_INDEX.md

The spine of the pack. The "Resume here" line is the single most important thing
you write all session - make it a specific, actionable next step.

```markdown
# <Project Title> - Session Memory (<date>)

## Resume here
<One or two sentences: exactly where things stand and the very next action.>

## Session at a glance
- Project: <title>
- Session: <label or date>
- Phase / status: <where in the work>

## Pack contents
| File | What it holds |
| --- | --- |
| <project>_memory_conversation_summary.md | Decisions, evolution, thread of the work |
| <project>_memory_artifacts_index.md | What was created + relationships |
| <project>_memory_communication_style.md | How to talk with the user / persona |
| <project>_memory_project_context.md | Profile, tech context, goals, metrics |
| <project>_memory_seed_data.json | Machine-readable seed |
| <project>_memory_personality.yaml | Persona configuration |
| integration.py | Places this pack into vault + Claude Code |

## Key decisions this session
- <decision> - <why>

## Open threads / next tasks
- <what the next session picks up>
```

---

## 2. conversation_summary.md

The narrative spine. Capture not just *what* was built but *how the thinking
moved* - the pivots and the reasons behind them are what's expensive to
reconstruct otherwise.

```markdown
# <Project Title> - Conversation Summary (<date>)

## Key decisions made
- <decision> - <reasoning, and what it rules out>

## Project evolution
1. Started with: <starting point>
2. Evolved to: <next state> (because <trigger>)
3. Landed on: <current state>

## Open questions / unresolved
- <thing still undecided, with the options on the table>

## Where we left off
<The concrete state at session end and the immediate next step.>
```

---

## 3. artifacts_index.md

Everything created or substantially changed this session, plus how the pieces
relate. Include file paths where they exist so the next session can find them.

```markdown
# <Project Title> - Artifact Index (<date>)

## Created / changed this session
- <name/path> - <what it is, one line>

## Relationships
- <A> references / depends on -> <B>

## Where things live
- Repo / vault paths, branches, anything needed to locate the work.
```

---

## 4. communication_style.md

How to work *with this user*. Derive these patterns from the actual conversation
rather than restating defaults - the value is the specifics. If a persona is in
play (e.g. a named agent), capture its voice here too.

```markdown
# <Project Title> - Communication Style (<date>)

## How the user likes to work
- Structure: <numbered steps / phases / checkpoints / etc.>
- Detail level: <terse vs thorough, where each applies>
- Pace & energy: <how to adapt>

## What works
- <patterns that landed well this session>

## What to avoid
- <patterns that didn't land>

## Persona voice (if any)
- Signature elements, tone, recurring phrases.
```

Note on persona detail: capture voice/tone/working-style preferences. Do not
infer or record clinical or diagnostic labels about the user; describe observed
working preferences instead (e.g. "prefers explicit checkpoints"), which is what
actually helps the next session.

---

## 5. project_context.md

The durable facts a fresh session needs. This is the file most worth getting
right - it's what makes the assistant feel like it already knows the project.

```markdown
# <Project Title> - Project Context (<date>)

## Profile & working context
- Who, role, relevant background for this project.

## Technical context
- Stack, tools, constraints, conventions, key paths.

## Goals
- Primary, secondary, and what success looks like.

## Success metrics
- How we'll know it's working.

## Constraints & preferences
- Hard limits, standing decisions, things not to re-litigate.
```

---

## 6. seed_data.json

Machine-readable seed for a vector store, MCP memory server, or agent. Keep it
faithful to the prose files - this is the same content in a structured shape.

```json
{
  "project": "<project_name>",
  "session_date": "<date>",
  "conversations": [
    {
      "id": "<short_slug>",
      "summary": "<what happened in this beat>",
      "reasoning": "<why, if a decision>",
      "metadata": {"phase": "<phase>", "key_decisions": ["..."]}
    }
  ],
  "user_profile": {
    "working_preferences": {"structure": "...", "detail_level": "..."},
    "project_preferences": {"...": "..."}
  },
  "project_state": {
    "current_phase": "<phase>",
    "completed_items": ["..."],
    "next_tasks": ["..."],
    "open_questions": ["..."]
  }
}
```

Required keys the validator checks: `conversations` (non-empty list),
`user_profile` (object), `project_state` (object with `next_tasks`).

---

## 7. personality.yaml

Persona configuration, if the project has a named assistant/agent. If there's no
persona, still emit a minimal file with a `personality:` block describing the
default working voice, so the schema check passes and the next session has a
starting point.

```yaml
personality:
  core_traits:
    - <trait>
  communication_style:
    structure: <how it organizes responses>
    detail_default: <terse | thorough | adaptive>
  adaptation:
    high_complexity: break_into_phases_with_checkpoints
    low_bandwidth: lead_with_the_next_action
  signature_elements:
    phrases:
      - <recurring phrase, if any>
```

---

## 8. Worked mini-example

A tiny conversation -> what the key files look like. Illustrative, not a ceiling.

Conversation gist: *the user and the assistant chose a vault-first memory model over
a database for the Conductor Method, deferring the MCP vector store to later, and
agreed the next step is wiring integration.py into your-vault.*

MEMORY_INDEX.md (Resume here):
> Vault-first memory model is decided; next step is running integration.py
> against your-vault/Conductor and confirming the CLAUDE.md pointer loads on a
> fresh Claude Code session.

conversation_summary.md (Key decisions):
> - Vault-first over a standalone DB - keeps memory human-readable in Obsidian
>   and avoids standing up a service just for continuity.
> - MCP vector store deferred, not dropped - integration.py keeps a stub hook so
>   it can be added without reworking the pack format.

seed_data.json (excerpt):
```json
{
  "project": "conductor",
  "project_state": {
    "current_phase": "memory-foundation",
    "next_tasks": ["run integration.py against your-vault", "verify CLAUDE.md pointer"],
    "open_questions": ["which vector backend, if any"]
  }
}
```
