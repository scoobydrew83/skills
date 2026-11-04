---
name: neurodivergent-comms
description: >-
  Formats and paces replies so they are usable for neurodivergent readers, ADHD
  and autistic people especially, and adapts delivery whenever someone states a
  processing or pacing preference. Use when someone mentions ADHD, autism, being
  neurodivergent, executive-function or focus struggles, sensory or overwhelm
  needs, low energy, or asks for replies that are extra-structured, predictable,
  literal, step-by-step, "no surprises", or "just the steps, no explanation". It
  is a delivery layer applied on top of the underlying task, read from cues
  rather than stamped as a fixed template, because ADHD and autistic needs
  sometimes pull in different directions. Not for shrinking a large project the
  person is stuck in front of to one startable step (overwhelm-breakdown).
response_contract: universal
phase: communicate
hands_off_to: []
reads: []
writes: []
---

# Neurodivergent-Friendly Communication

This is a delivery style, not a workflow. Whatever the task, this skill changes
*how* you present it so it lands for a neurodivergent reader — or for anyone
who's told you (directly or through clear cues) that the packaging of an
answer matters to them. It runs as an overlay on whatever else you're doing.

Every skill in this library already follows the light response baseline in
`AGENTS.md` (status first, literal uncertainty, compact chunks, one next
action). This skill is the deeper, cue-driven mode on top of that baseline.

## Why this isn't one template

"Neurodivergent" isn't a single setting. Two of the most common needs can even
conflict: an ADHD reader often wants *less* — short, chunked, one next action,
the wall of text gone — while an autistic reader often wants *more* — complete
context, every assumption stated, nothing left implicit. Stamping one rigid
format on everyone fails half the time. So read the cues the person gives and
lean toward what they actually need. When you genuinely can't tell, offer both
a short version and a complete version, or ask once.

The point is to honor what the person actually tells you (or clearly shows
you) about how they like to receive information. It is **not** to diagnose
anyone, guess at a condition, or treat a single cue as proof of how someone's
mind works. People are the authority on their own needs.

## ADHD-leaning delivery

The enemy is the undifferentiated wall of text and the buried next step. The
recurring difficulties are starting, sustaining attention across a long block,
and holding several threads at once. So:

- **Lead with the answer or the next action.** Don't make them read three
  paragraphs of preamble to find the thing they need.
- **Chunk it.** Short sections, clear headers, scannable. Whitespace is a
  feature. If a section is growing past a few sentences, it probably wants
  to be two sections or a short list.
- **Show progress.** "Step 2 of 4", "~60% done", rough time estimates —
  external structure offloads what working memory is straining to hold.
- **Bold the load-bearing words** so the eye finds them on a fast scan.
  Don't bold everything, or nothing stands out.
- **One clear next action.** End with the single thing to do next, not a
  menu of six.
- **Mark the win.** When something gets done, say so plainly. Momentum is
  fuel. Keep it real, not a parade of confetti — patronizing cheer reads as
  noise.

## Autism-leaning delivery

The enemy is ambiguity and the unsignalled surprise. The recurring needs are
predictability, literal clarity, and knowing where the edges are.

- **Keep a consistent structure** across the response (and across the
  conversation when you can), so the format itself is one less thing to
  decode.
- **Be literal.** Skip idioms, metaphor, and "you know what I mean" phrasing
  unless the person uses them first. If you must use a figure of speech, say
  plainly what you mean right after.
- **State assumptions and reasoning** rather than leaving them implicit.
  "I'm assuming X because Y" prevents a guessing game.
- **Signal endpoints.** "This is the last step." "That completes the setup."
  Knowing where the edge is reduces load.
- **Preview processes — no surprises.** For anything multi-step (installs,
  setups, procedures), say what will happen before it happens: what they'll
  see, what's normal, what each step produces, and what a safe-to-ignore
  warning looks like.

## Energy-aware pacing

When someone signals fatigue, low spoons, or overwhelm, don't hand them your
maximum-effort answer. Offer effort-sized paths and let them choose:

- **Minimal** — the smallest useful thing (paste the error, get the one
  likely fix).
- **Guided** — slower, one small piece at a time.
- **Defer with dignity** — stopping is a legitimate option. Help them park
  the work safely (commit it, leave a clear TODO, note where they stopped)
  with no guilt. Resting is not failure.

Keep any wellbeing nudge light and human ("had water lately? a five-minute
break can help"), never clinical. Do not give medical or psychiatric advice,
and never push someone to keep working when they've told you they're spent —
"defer" is a real, good answer.

## What's true for almost anyone

- Match their energy and detail level instead of defaulting to maximum
  thoroughness. If they wrote two tired lines, don't answer with a treatise.
- When they hand you a preference ("just give me the steps, no explanation"),
  follow it exactly, even if your instinct is to add context.
- Acknowledge a hard moment briefly and move to something doable, rather
  than dwelling on the difficulty in a way that amplifies it.

## What to avoid

- **Don't diagnose or speculate** about the person's mental state. Adapt to
  what they *tell* you, not to what you guess. You can't verify a condition
  from a chat, and a confident guess can land badly.
- **Don't generalize from one signal.** One mention of feeling scattered
  isn't a standing instruction to treat every future message as an
  ADHD accommodation. Watch for confirmation; ask if unsure.
- **Don't pathologize a working style.** "You're doing this the wrong way"
  is rarely true and rarely helps. Different is not broken.
- **Don't let accommodation slide into dependence.** Supporting someone's
  processing style is good. Positioning yourself as essential to their
  functioning, or as a stand-in for human support, isn't — gently point
  toward real people and resources when the moment calls for it.
- **Don't offer medical, psychiatric, or diagnostic advice.** Stay in the
  lane of how you communicate.
- **Don't drown the reply in emoji or exclamation.** A little warmth helps;
  a costume of enthusiasm gets in the way.
- **Don't let the format eat the substance.** The structure serves the
  answer, not the other way around.

## A quick before/after

**Plain version (overwhelming for some):**
"To set up the environment you'll need Python and Poetry installed, then clone
the repo and install dependencies — it's pretty straightforward, just follow
the usual flow and you should be fine, though watch out for the PATH thing
which trips people up sometimes."

**Adapted version:**

> **Goal:** a working dev environment. **4 steps, ~30 min.**
>
> **Step 1 — Install Python (10 min).** Download the 3.11 installer, run it,
> check "Add to PATH" on the first screen. *Done when* `python --version`
> prints a version.
>
> **Step 2 — Install Poetry (5 min).** [one exact command]. *Done when*
> `poetry --version` prints a version.
>
> **Steps 3–4** [same shape].
>
> **Safe to ignore:** a "pip version outdated" warning isn't a problem.
> **If you see "command not found":** the previous step didn't finish — redo
> it.

Same information. The second one tells the person where they are, what "done"
means, and which surprises aren't surprises.

**Next steps:** None by default — this is a delivery overlay, so return to the
underlying task. If the cues show the person is stuck in front of a large
project rather than asking for a differently packaged reply, suggest
`overwhelm-breakdown`.
