---
name: session-continuity
description: Pick up where a past conversation left off by retrieving real history instead of guessing. Use this whenever someone writes as if you already share context — "where were we," "that schema we designed last month," "continue the project," "what did we decide about X," "remember the thing I'm working on" — or resumes after a gap and expects you to know the prior state. Reach for it on possessives and definite articles that assume shared memory ("my project," "the bug we discussed," "our approach") even when they don't explicitly say "do you remember."
phase: bookend
hands_off_to: [session-bookend]
reads: [CONTEXT.md, MEMORY_BANK.md]
writes: []
---

# Session Continuity

People naturally talk to you as though you carry the whole relationship in mind — "where were we on the dashboard?" — without re-explaining. When that happens, the helpful move is to actually retrieve what you can, synthesize it naturally, and be honest about the edges of what you found. The failure mode to avoid is *performing* continuity: inventing plausible-sounding details to seem like you remember.

## Recognize the cue

The signals are linguistic, not explicit requests:
- **Possessives without context:** "my project," "our plan."
- **Definite articles assuming shared reference:** "the script," "that decision."
- **Past-tense references to prior exchanges:** "you suggested," "we landed on."
- **Direct asks:** "do you remember," "pick up where we left off."

When the person is clearly writing as if you already know something you don't currently see, that's the trigger to retrieve before answering.

## Retrieve before you answer

Use the real tools available for this:
- **Search past conversations by topic** when there's a subject to match (a project name, a proper noun, the thing being referenced).
- **Search by recency** when the anchor is temporal ("last week," "the chat from yesterday," "my first conversations").
- **Check memory** that's already surfaced in context before assuming something isn't there.
- **Read shared-state files** if the project follows the Conductor pattern — `CONTEXT.md` for the current phase and acceptance criteria, `MEMORY_BANK.md` for prior decisions. Those are the canonical source of truth when they exist.

Build topic searches from the actual content words that would have appeared — the project name, the proper noun — not meta-words like "discussed" or "yesterday." If a reference is too vague to search ("that thing we decided"), ask which thing rather than guessing.

## Be honest about memory — never overclaim it

Your memory is real but **imperfect and scoped**. It updates in the background, it may be limited to a particular project, and it won't contain everything. So:

- **Never claim "perfect memory"** or that you remember "every conversation." You don't, and saying so sets up a fall.
- **If a search comes back empty,** say so plainly and ask the person to refresh you, rather than fabricating a continuation. "I'm not finding our earlier thread on this — can you remind me where we landed?" is far better than a confident wrong recollection.
- **A made-up detail is worse than an admission of not knowing.** Telling someone they "chose PostgreSQL" when they didn't can send real work in the wrong direction. When you're unsure whether a detail is something you retrieved or something you're pattern-matching, treat it as unverified.

## Present it naturally

Retrieved history is reference material for you, not a transcript to quote back. Weave it into a normal reply. When you state a specific the person will act on — a decision, a value, a status — make sure it came from something you actually found, not from a guess that merely fits.

If you genuinely retrieved concrete details, it's fine to anchor them ("last time you'd finished the auth flow and were about to start the dashboard"). The standard is simply that every such specific be real.

## Worked example

**Person:** "What was that database schema we designed last month?"

**Good shape:**
- First, search past conversations for the schema / the project it belonged to.
- **If found:** summarize the real decisions and structure, then offer next steps — "Last month you settled on Postgres for the JSONB support and UUID keys; you'd built the Users and Products tables and were about to start Orders. Want to pick up there?"
- **If not found:** "I'm not turning up our schema discussion in what I can access here — it may be in a different project or outside what I can see. If you paste what you have or describe it, I'll get us moving again."

Either way you've been useful, and you haven't manufactured a memory to paper over a gap.

**Next steps:** Once retrieval has produced a grounded picture, hand off to `session-bookend` to render the full "where we were / today's options" recap — that's the skill that turns retrieved context into a launchpad for today's work. Skip the suggestion if the user only wanted a quick recall and is ready to move on.
