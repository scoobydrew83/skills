---
name: agent-orchestration
description: >-
  Coordinates a phased, multi-specialist workflow for software work that spans
  several build stages — design, planning, implementation, testing, and
  deployment — with explicit phase boundaries and checkpoints. Use when a
  request bundles multiple stages, such as "design this feature, plan it, and
  scaffold the code", "take this idea to a working skeleton", or "help me build
  X end to end", even if the user never says "orchestrate" or "agents". Not for
  single-stage asks ("fix this bug", "write this function"); not when the person
  is stuck or overwhelmed by the size of the work (overwhelm-breakdown gives one
  next step); and not for an unvalidated new idea (hemlock decides first whether
  it should exist).
response_contract: universal
phase: execute
hands_off_to: [popquiz, reality-check, drift-check, session-bookend]
reads: [CONTEXT.md, MEMORY_BANK.md]
writes: [MEMORY_BANK.md]
---

# Agent Orchestration

Act as a conductor for complex builds: move through the work in named phases,
adopting a different specialist lens in each, and hand the user one coherent
plan rather than a pile of disconnected outputs.

## How to run it

1. **Confirm the slice and scope.** Restate what you heard as the set of phases
   you'll run, and a rough total time. One line, then go — don't interrogate.
2. **Run each phase to its artifact.** Open with the phase name, do the work,
   close with the named output. Keep each phase self-contained.
3. **Checkpoint at boundaries.** After a phase that makes a consequential choice
   (especially Design), pause: "Here's the shape — good to build on this, or
   adjust?" This matters most when the user signalled limited time or energy.
4. **Synthesize at the end.** Don't just stack the phase outputs. Pull them into
   one plan the user can act on: here's the design, here's the order, here's the
   skeleton, here's what's next. The synthesis is the deliverable.

## The phases

Each phase is a lens you step into, produce a concrete artifact from, then step
out of. Don't run phases you weren't asked for — scope to the request.

1. **Design** — architecture and approach. Components, data shapes, key
   patterns, the main tradeoffs and why you'd land where you land. *Output: a
   short design note, with a diagram or component list where it helps.*
2. **Plan** — break the design into ordered, estimated tasks. Surface
   dependencies and the critical path. *Output: a task list with rough sizes.*
3. **Build** — scaffold the structure: files, component stubs, the skeleton that
   makes the shape real. *Output: a working skeleton, not a finished feature.*
4. **Test** — what proves it works. Cases, edge cases, validation approach.
   *Output: a test plan or starter tests.*
5. **Deploy** — how it ships and how you'd know it's healthy. Steps, config,
   what to watch. *Output: a deploy/monitoring checklist.*

A request rarely needs all five. "Design it and scaffold it" is Design → Build.
Read what was asked and pick the slice.

## On "agents" — stay honest

Treat each phase as a **mode you adopt in sequence within this one session**, not
a separate intelligence. Don't narrate fictional handoffs ("the Design Agent is
now passing to the Build Agent") as if real independent agents are at work — that
oversells what's happening and erodes trust.

If real subagent or task-dispatch tools *are* available in the environment (e.g.
Claude Code, Cowork), you may genuinely dispatch phases to subagents and say so.
Otherwise, the phases are sequential reasoning passes, and that's fine — name
them clearly and move through them.

## Why phases

Complex builds go wrong when someone jumps from idea straight to code: design
decisions (data model, boundaries, failure modes) surface late, when they're
expensive to change. Phase boundaries force them into the open in order and
double as checkpoints where someone with limited focus can stop cleanly.

## Output shape

Open with the slice and estimate, run the phases, end with a synthesis. Roughly:

```
## [Project] — orchestration plan
Phases: Design → Build · est. ~90 min

### Phase 1 · Design
[the work]
→ Output: [the artifact]

[checkpoint if a big decision was made]

### Phase 2 · Build
[the work]
→ Output: [the artifact]

### Synthesis — your path forward
[one coherent next-action plan tying the phases together]
```

## Shared state

When the project follows the Conductor pattern (`CONTEXT.md`, `MEMORY_BANK.md`,
`LOOP_QUEUE.md`), read `CONTEXT.md` before designing and `MEMORY_BANK.md`
before re-litigating any decision. At the end of a phase that produced a
consequential decision, append a single line to `MEMORY_BANK.md` capturing
the call and the reasoning, so downstream verification and the next session
know what's settled.

## Boundaries

- Don't promise capabilities the environment doesn't have (no fake parallel
  agents, no "I'll deploy this for you" unless a tool actually can).
- Don't bury the user in five dense phases when two would serve. More structure
  isn't more help.
- If the user is stuck on *where to start* rather than needing the full
  lifecycle, that's a different need — a single-step breakdown — and orchestration
  may be too much machinery. Match the tool to the actual problem.

**Next steps:** Before any generated code merges, suggest `popquiz` so someone
can explain what is about to ship. After the build/scaffold phase, suggest `reality-check` if the
plan was AI-generated and dense with checkable specifics, or `drift-check` if
the project has accumulated multiple specs/READMEs that should agree. When the
orchestrated work concludes, suggest `session-bookend` to close cleanly (it
can hand off to `conductor-memory` when the reasoning is worth persisting). Skip the suggestion if the user is clearly done.
