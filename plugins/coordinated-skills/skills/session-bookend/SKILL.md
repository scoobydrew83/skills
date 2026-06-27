---
name: session-bookend
description: >-
  Open and close work sessions with clean, grounded continuity. Use at the START
  of a session when someone returns to ongoing work — "where were we", "pick up
  where we left off", "what's the status of X", "back to the project" — to
  produce a recap of what's done, where things stand, decisions made and why, and
  the next step. Use at the END of a session — "let's wrap up", "good place to
  stop", "save where we are" — to produce a clean handoff for next time. The
  defining rule: ground every recap in REAL retrieved context (past-chat search,
  memory, project files, notes), never invented status. Trigger whenever a
  multi-session project is resuming or wrapping. Do NOT fabricate a "where we left
  off" from nothing — if you can't retrieve it, say so and ask.
phase: bookend
hands_off_to: [overwhelm-breakdown, agent-orchestration, conductor-memory]
reads: [CONTEXT.md, MEMORY_BANK.md]
writes: [MEMORY_BANK.md]
---

# Session Bookend

Continuity across sessions is what keeps a long project feeling sane. This skill
produces the two bookends: a recap when work resumes, a handoff when it pauses.

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

**Next steps:** At session open, if today's first option is too big or vague,
suggest `overwhelm-breakdown`; if it's a multi-stage build, suggest
`agent-orchestration`. At session close, if the session produced durable
context worth a snapshot, suggest `conductor-memory`. Skip the suggestion if
the user clearly wants to stop or has already picked their path.
