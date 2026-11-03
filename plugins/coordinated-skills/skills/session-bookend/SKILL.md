---
name: session-bookend
description: >-
  Retrieves real prior context and turns it into a quick recall, an opening
  recap, or a closing handoff at a work session's boundary. Use when someone
  writes as if shared context already exists — "where were we", "what did we
  decide about X", "the schema we designed last month", "my project", "the bug
  we discussed" — or returns to ongoing work wanting status ("catch me up",
  "what's the status of X"), or is wrapping up ("let's wrap up", "save where we
  are", "give me a clean handoff for next time"). Every recap is grounded in
  retrieved past chats, memory, project files, or CONTEXT.md and MEMORY_BANK.md;
  when nothing can be retrieved it says so and asks instead of inventing a
  "where we left off".
response_contract: universal
phase: bookend
hands_off_to: [overwhelm-breakdown, agent-orchestration, conductor-memory, next-step]
reads: [CONTEXT.md, MEMORY_BANK.md]
writes: [MEMORY_BANK.md]
---

# Session Bookend

Continuity across sessions is what keeps a long project feeling sane. This skill
has three modes, all built on the same retrieval step:

| Cue | Mode | Output |
|---|---|---|
| "where were we", "what did we decide about X", "the bug we discussed" | **Quick recall** | The retrieved answer, woven into a normal reply |
| "catch me up", "back to the project", "what's the status of X" | **Opening recap** | Launchpad with today's options |
| "let's wrap up", "save where we are", "handoff for next time" | **Closing handoff** | Cold-start note for next session |

## Recognize the cue

The signals are usually linguistic, not explicit requests: possessives without
context ("my project", "our plan"), definite articles that assume a shared
referent ("the script", "that decision"), past-tense references ("you
suggested", "we landed on"), or a direct "do you remember". When the person
writes as if context exists that isn't in view, retrieve before answering.

## The one rule that makes this work: retrieve, then summarize

Fabricated continuity is worse than none. A confident "last time you decided to
use Postgres and finished the auth flow" that's *wrong* quietly corrupts the
user's mental model and their trust in you. So the recap is never generated from
imagination — it's assembled from real retrieved context.

Before producing any "where we left off":

1. **Actually pull the context** using whatever real retrieval the environment
   offers — past-conversation search, memory, uploaded project files, connected
   notes (an Obsidian vault, a project tracker, a repo). For Conductor-style
   projects, that means reading `CONTEXT.md` and `MEMORY_BANK.md` first; they
   are the source of truth. Look before you speak.
2. **If you can't retrieve it, say so.** "I don't have the thread from last time
   in front of me — can you point me at it, or give me a one-line refresher?" is
   the correct move. Asking is not a failure; confabulating is.
3. **Only state what you can ground.** Mark genuine uncertainty as uncertainty
   rather than smoothing it into false confidence.

Retrieval tips:
- Search past conversations by **topic** using the content words that would have
  appeared (project name, proper nouns), not meta-words like "discussed".
- Search by **recency** when the anchor is temporal ("last week", "yesterday").
- Check memory already surfaced in context before assuming something is missing.
- If a reference is too vague to search ("that thing we decided"), ask which one.

Memory is real but imperfect and scoped. Never claim to remember "every
conversation". A made-up detail ("you chose PostgreSQL") can send real work in
the wrong direction; an admission of not knowing costs one message.

## Quick recall

When the person only wants one fact back, answer it directly from what was
retrieved, without the full recap ceremony. Example:

- **Found:** "Last month you settled on Postgres for JSONB support and UUID keys;
  Users and Products were built and Orders was next. Want to pick up there?"
- **Not found:** "I'm not turning up our schema discussion in what I can access —
  it may be in another project. If you paste or describe it, I'll get us moving."

If the recall turns into "so what now?", switch to the opening recap.

## Start-of-session recap

Keep it a launchpad, not a transcript. Aim for:

- **Last touchpoint** — when you last worked on this, in one line.
- **Done** — the things actually completed. Brief.
- **Where we are** — the one in-progress thing, stated precisely.
- **Key decisions + why** — the choices that constrain what's next, with the
  reasoning, so they're not silently re-litigated.
- **Open follow-ups** — anything flagged for "later" that's now relevant.
- **Today's options** — one to three sized choices for where to go now.

End on the options, so the recap flows straight into action.

## End-of-session handoff

Write it for a cold start — assume future-you remembers nothing:

- **Done today** — what got accomplished this session.
- **Exact current state** — where things literally stand right now (which file,
  which step, what's half-finished).
- **The very next step** — the single concrete thing to pick up first next time,
  specific enough to start without re-deriving context.
- **Open questions / pending decisions** — anything left unresolved.
- **Where the artifacts live** — paths, links, filenames, so nothing has to be
  hunted for.

When the project uses `MEMORY_BANK.md`, append a one-line "session lesson" entry
to it as part of the handoff so tomorrow's session is smarter than today's.

## Boundaries and handoffs

- **Don't re-narrate everything.** A recap is a runway, not a replay. Tight beats
  thorough here.
- **Deliver it cleanly** — pairs well with `neurodivergent-comms` pacing
  (chunked, scannable, one clear next action).
- **Hand off the "today's options".** If a chosen option is a big vague push,
  that's an `overwhelm-breakdown` moment; if it's a full multi-stage build, hand
  to `agent-orchestration`. If the session is closing for real and produced
  something worth carrying forward, `conductor-memory` is the right next move.

**Next steps:** After a quick recall, skip any suggestion unless the person
asks what to do next; in a Conductor project with loop files, suggest
`next-step`. At session open, if today's first option is too big or vague,
suggest `overwhelm-breakdown`; if it's a multi-stage build, suggest
`agent-orchestration`. At session close, if the session produced durable
context worth a snapshot, suggest `conductor-memory`. Skip the suggestion if
the user clearly wants to stop or has already picked their path.
