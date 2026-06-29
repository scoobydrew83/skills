---
name: project-postmortem
description: Generate an evidence-grounded project retrospective — pulled from git history and decision docs, not memory — that grades the project on separate dimensions, splits what went right from wrong, reduces the failure to its root ordering error, extracts transferable lessons for the next project, and names what survives. Use whenever a project ships, stalls, or gets sunset and someone wants the writeup — "post-mortem", "retrospective", "what went wrong with X", "we're sunsetting X, write it up", or mid-project "why did this go sideways". The method cites commit hashes or sources for every claim, builds a timeline of when validation happened vs building, separates pros from cons including uncomfortable symmetries, and ends with a per-dimension scorecard plus a what-survives list — then runs a check that fails any vanity scorecard or uncited narrative. Distinct from drift-check (audits live docs) and conductor-memory/session-bookend (capture session state for continuity); this extracts backward-looking lessons.
phase: bookend
hands_off_to: [conductor-memory]
reads: []
writes: []
---

# Project Post-mortem

Write the retrospective a project earns — grounded in what the git history and decision docs actually show, graded honestly on separate axes, reduced to the one decision that mattered most, and mined for lessons that transfer to the *next* project.

The one rule everything serves:

> **Ground every claim in retrieved evidence, not memory. If you can't cite it, label it as recollection.**

A post-mortem written from memory is a story the team tells itself, and stories drift toward flattering the teller. A post-mortem written from the commit log, the PRs, and the decision docs is a record — and a record can teach the next project something the memory would have smoothed over.

---

## Why this exists

The value of a post-mortem is almost entirely in two things: an *honest* root cause, and *transferable* lessons. Both are easy to fake and easy to get wrong:

- **Memory launders failure.** By the time a project ends, everyone has a tidy narrative. The git history doesn't — it shows that the validation commit came on day four, not day one, regardless of how it felt. Cite the evidence and the real story surfaces.
- **A blended grade hides the killer.** "B+ overall" averages away the fact that engineering was an A and differentiation was an F — and the F is the whole lesson. Grade dimensions *separately* or you erase the finding.
- **Vanity retros teach nothing.** A retro that's all "we learned a lot and grew as a team" is a feeling, not a lesson. The test of a real lesson is whether it would change what you do on an unrelated next project.

This skill also exists to credit what went *right*, including the uncomfortable cases where the same trait caused both the success and the failure — those symmetries are usually the deepest lesson available.

## When to reach for this vs neighbors

- **drift-check** audits a *live* project's docs for internal contradiction (are these still consistent?). This is *backward-looking* — the project is done or being stopped, and the goal is durable lessons.
- **conductor-memory / session-bookend** capture session *state* so work can resume. This captures *judgment* — why it went the way it did and what to carry forward — and is meant to outlive the project.

---

## The workflow

### Step 1 — Pull the evidence first
Before writing a word of narrative, retrieve the record. If a repo is available:
```bash
git log --oneline --stat        # what happened and when
git log --oneline | wc -l       # commit count for the timeline
```
Also gather decision docs, PRDs, PRs, status files. The point is to anchor claims to artifacts — `commit a1b2c3d`, "the PRD dated X", "PR #19" — so anyone can check them. Anything you can't anchor, you'll mark as recollection in the writeup rather than stating as fact.

### Step 2 — Build the timeline by phase
Lay out the project in phases and, crucially, mark **when validation happened relative to building.** The single most diagnostic fact in most failed projects is the gap between "started building" and "first tested the premise." A timeline that shows five build milestones before the first incumbent benchmark *is* the root cause, made visible.

### Step 3 — Separate pros from cons, honestly
Two lists, no hedging:
- **What was genuinely good** — ideas, design principles, engineering, decisions that survived. Be specific and credit them even in a failure.
- **What went wrong** — and reduce each to *why*, not just *what*.

Then the harder pass: **uncomfortable symmetries.** Where did one trait cause both? (Classic: rigor applied lavishly to execution and far too late to the premise — the same discipline that saved the engineering doomed the project by arriving in the wrong order.) These are the lessons worth the most.

### Step 4 — Reduce to the root cause
Push past the proximate failures to the one decision or ordering error they all reduce to. Most multi-symptom failures collapse to a single inversion — usually *the riskiest, cheapest-to-test assumption was tested last instead of first.* State it in one sentence.

### Step 5 — Extract transferable lessons
Write the lessons as guidance for the *next* project, phrased generally enough to apply beyond this one. "Benchmark the incumbent before building the challenger" transfers; "we should have searched for merge queues" doesn't. Each lesson should be something a reader could act on without knowing this project at all.

### Step 6 — Name what survives
Salvage explicitly: the reusable code, the ideas worth keeping, the method worth repeating. A good post-mortem of a killed project is not scorched earth — it hands the next project the parts that still have value. This also models the anti-sunk-cost posture: the project ended, and that's fine, and here's what carries forward.

### Step 7 — Scorecard, graded separately
Grade the project on independent dimensions so a strength can't hide a weakness. Suggested axes (adapt to the project):

| Dimension | What it measures |
|---|---|
| Idea / is the problem real | Was the core need genuine? |
| Differentiation | Did it beat what already existed? |
| Engineering quality | Was the execution clean? |
| Sequencing | Was validation done in the right order? |
| Intellectual honesty | Did it follow its own evidence, even to a kill? |
| Recovery / scope discipline | Did it cut decisively when evidence landed? |

### Step 8 — Lint it
```bash
python scripts/postmortem_linter.py <postmortem.md>
```
The check fails a post-mortem that has no evidence citations, a single blended grade instead of separate dimensions, or missing root-cause / transferable-lessons / what-survives sections — the markers of a vanity retro.

---

## Output template

```markdown
# <project> — Post-mortem
> Written from git history and decision docs, not memory. Claims cite commits/sources.
**Lifespan:** <start> → <end> (<duration>, ~<N> commits).  **Outcome:** <shipped / sunset / pivoted> — <one line>.

## TL;DR
<3-5 sentences: what it was, what happened, the one root cause.>

## Timeline (when validation happened vs building)
<phases, with commit/PR anchors; highlight the build-vs-validate ordering.>

## What was genuinely good
- <specific, with evidence>

## What went wrong
- <specific, reduced to *why*, with evidence>

## The honest split (incl. uncomfortable symmetries)
- <where one trait caused both the win and the loss>

## Root cause (one sentence)
> <the single ordering/decision error everything reduces to>

## Transferable lessons (for the NEXT project)
1. <general enough to apply elsewhere>

## What survives
- <reusable code / ideas / method>

## Scorecard
| Dimension | Grade | One-line reason |
|---|---|---|
| Idea / problem real | | |
| Differentiation | | |
| Engineering quality | | |
| Sequencing | | |
| Intellectual honesty | | |
| Recovery / scope discipline | | |
```

## Honesty rules
- **Cite or flag.** Every load-bearing claim gets a commit/PR/doc anchor, or an explicit "(recollection — unverified)" tag. No confident assertions you can't back.
- **Grade separately, never blend.** The whole diagnostic value is in the spread between dimensions.
- **Credit the survivors.** A kill that scorches everything to feel decisive loses the reusable parts. Name what was right.
- **Lessons must transfer.** If a "lesson" only makes sense for this exact project, push it up a level of generality until it would help a stranger's next project.

---

**Next steps:** When the post-mortem is written, suggest `conductor-memory` to persist the transferable lessons and the what-survives list into durable project memory, so the next project inherits them instead of relearning them. Skip if this is a one-off writeup with no continuing workspace.
