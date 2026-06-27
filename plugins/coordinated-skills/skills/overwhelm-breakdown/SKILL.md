---
name: overwhelm-breakdown
description: >-
  Break an overwhelming project — or any large, vague task someone can't find an
  entry point into — down to a single concrete next step. Use whenever someone
  faces something big and signals they're stuck or overwhelmed: "I need to build
  a whole reporting system but I don't know where to start", "this feels like
  too much", "where do I even begin with X", "I'm drowning in this project",
  "can you break this down", "chunk it for me", "I'm paralyzed by the size of
  this". The goal is momentum, not a master plan: decompose into a few major
  parts, then collapse all the way down to one doable step sized by time AND
  energy, with a clear definition of done for today. Trigger on the combination
  of a large or ambiguous task PLUS stuck-ness, overwhelm, or an explicit
  request to break the work down — even if the person never uses the words
  "overwhelm" or "breakdown". Do NOT use this to produce a full project plan —
  that's the opposite of what an overwhelmed person needs.
phase: intake
hands_off_to: [agent-orchestration, neurodivergent-comms, session-bookend]
reads: []
writes: []
---

# Overwhelm Breakdown

When someone is frozen in front of something big, the job is to get them moving,
not to map the whole thing.

> *Merged June 2026: this skill absorbed the former `task-decomposition` skill.
> The two had the same job (shrink a big thing to one small first step) and were
> competing for the same triggers. The richer description, the worked example,
> and the energy-awareness all live here now.*

## Why "one step", not "the whole plan"

Overwhelm comes from trying to hold the entire staircase in your head at once.
The instinct — yours and theirs — is to respond with a complete project plan. For
an already-overwhelmed person that often makes it *worse*: now there's a
forty-item list confirming how big the thing is. The actual fix is to shrink the
visible surface down to one step small enough to start today. Momentum does the
rest; a single finished thing changes the whole emotional picture.

The barrier here is almost never ability — it's the inability to find an entry
point. Your job is to shrink the visible scope down to a single doable action
without hiding the larger shape of the work.

## The process

1. **Name the whole thing in one sentence.** Just so it's contained and out of
   their head. "So — a reporting system for your team's sales data."
2. **Split into a few major parts.** Three to five, names only, no detail.
   Resist elaborating. The point is to show the beast has a small number of
   pieces, not to plan them.
3. **Pick the first/simplest part.** The one with the lowest activation energy,
   not necessarily the "most important". Starting beats optimizing.
4. **Collapse to ONE next step inside that part.** Something concrete that takes
   roughly 15–45 minutes. "List the 3–5 reports you actually need — just the
   names." Specific enough to start without deciding anything else.
5. **Define done-for-today.** Small and concrete, so the win is unambiguous:
   "Success today = one report name and its 5–10 data points. That's the whole
   goal." Then stop. Do not plan steps two through forty unless they ask.

## Size by time *and* energy

A step can be small in time but heavy in energy (a dreaded decision) or vice
versa. Account for both, and always leave a smaller rung available:

- **Time-box** to something believable — 15 to 45 minutes, not "an afternoon."
- **Lower the energy cost.** The first step should be listing, naming, or
  choosing — not the hardest part of the work. Save the heavy lifting for when
  there's momentum.
- **Offer to go smaller.** "If even that feels like a lot right now, we can
  shrink it to just the single simplest report."

## Then hand control back

After laying out the step, offer two or three honest options for how to proceed
— for example: walk through the first step together now, set up a simple
template they fill in, or map out the full breakdown. Let them pick. Don't
assume the highest-effort path.

## Use real tools only

If the person wants the breakdown captured somewhere, use capabilities that
actually exist in this environment — a reminders/to-do tool, or a task-
management skill if one is available — rather than narrating handoffs to
specialist "agents" or systems that aren't really there. Promising a coordinator
that doesn't exist erodes trust the moment it's tested. If a useful tool isn't
available, say so and offer what you *can* do.

## When the step is done

Mark it plainly — the win is the point. Then offer, lightly, the next single
step. Don't dump the remaining plan on them the moment they finish; let the
momentum stay intact. Keep the encouragement proportionate: a little warmth
helps ("nice — that's a real start"), relentless celebration of trivial actions
gets patronizing fast.

## Worked example

**Person:** "I need to build a whole reporting system and I don't know where to
start, it feels overwhelming."

**Response shape:**

> **The whole thing:** a system that collects data, stores it, and shows it as
> reports. That's really just **four parts**: (1) what to track, (2) where to
> keep it, (3) how to display it, (4) how people use it.
>
> **Today is only the first slice of part 1 — ~30 min:**
> - List the 3–5 reports you most need (just names).
> - Pick the single simplest one.
> - Write down the 5–10 data points it needs.
>
> **Done for today =** one report name + its data points on a page. Nothing
> else.
>
> Want to (a) do the listing together now, (b) get a fill-in template, or
> (c) map out all four parts first?

Notice what it does: bounds the project, shows the structure, then collapses
the actual ask to one small, finishable thing — and leaves the person in
charge of what happens next.

## Boundaries and handoffs

- **Don't produce the master plan here.** A Gantt chart is the wrong medicine.
  If they get unstuck and explicitly want the full sequenced plan, that's a
  different mode — hand off to `agent-orchestration`.
- **Deliver it gently.** This pairs naturally with `neurodivergent-comms`
  pacing: chunked, one next action, no wall of text. Run it as an overlay if
  the person has signalled they need that style.
- **Don't minimize the feeling.** "This is a lot" is allowed and often true.
  Acknowledge it, then make the next step tiny. Avoid "just" and "simply".

**Next steps:** When the user finishes the first step (or asks for the rest),
suggest `agent-orchestration` if they now want the full sequenced plan, or
`session-bookend` if it's a good place to stop and save state for next time.
If they're still in the work and just want softer packaging, layer
`neurodivergent-comms` on top. Skip the suggestion if they clearly want to
stop.
