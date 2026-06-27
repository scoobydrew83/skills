---
name: drift-check
description: >-
  Audit a set of related project documents for internal contradictions and
  drift from their stated mission, with a skeptical eye that distrusts
  suspiciously clean alignment. Use whenever the user points at multiple docs
  (spec, PLANNING.md, README, CLAUDE.md, .cursorrules, system prompt, TASK
  tracker, ADRs) and asks "are these consistent", "do my docs agree", "has my
  spec drifted", "check alignment", "is my README in sync", "audit my project
  for consistency", or shares a self-alignment/audit report. Especially trigger
  when documents should agree on the same facts (tech stack, metrics, feature
  lists, naming, architecture, tone) and the task is finding where they silently
  diverge, or where identical copy-pasted claims masquerade as validation. Lead
  with the real state of alignment and the biggest contradiction, never a vanity
  score. For cross-document consistency and mission-drift within a project's own
  materials, not verifying external claims (use reality-check) or choosing
  between options (use a council skill).
phase: verify
hands_off_to: [reality-check, conductor-memory]
reads: []
writes: [MEMORY_BANK.md]
---

# Drift Check

Audit a set of project documents — specs, planning docs, READMEs, rules files, system prompts, task trackers — for two failures: **contradiction** (the docs disagree with each other) and **drift** (the docs have wandered from the mission they claim to serve). The output the user needs is an honest map of where their materials actually stand, not reassurance.

## Core principle: clean alignment is a smell

The dangerous failure mode here is the opposite of harsh — it's being agreeable. A document set that audits to "98% aligned, all green" is not evidence of health; it's usually evidence that nobody looked hard. Real document sets that evolved over time accumulate contradictions, stale references, and quiet redefinitions. If your audit comes back glowing, you didn't dig — go back and find the contradiction the rosy summary is papering over.

Two things in particular masquerade as alignment:
- **Identical claims are not corroboration.** When the same metric (`>95% accuracy`, `<2 seconds`) or the same sentence appears verbatim across five documents, that is copy-paste, not five independent validations. It tells you the number propagated, not that it's right or achievable.
- **Unfalsifiable promises aren't aligned, they're just vague.** "Perfect memory", "seamless orchestration", ">95% accuracy" with no measurement defined — these agree across docs only because none of them mean anything checkable yet.

## Workflow

### 1. Anchor the north star

Find the stated mission / vision / source-of-truth spec. Everything else is judged against it. If the user named a canonical document, anchor there. If no single source of truth exists — or the mission is worded differently in different places — that ambiguity is itself a finding, because there's nothing to drift *from*.

### 2. Extract the claims that should agree

Pull the load-bearing, cross-cutting facts each document makes a claim about: tech-stack choices, performance metrics and targets, feature/agent lists and counts, naming, architecture decisions, scope, and tone/personality. These are the axes where docs are *supposed* to match, so they're where contradiction and drift show up.

### 3. Build the cross-document matrix — skeptically

Lay the claims (rows) against the documents (columns), but don't just mark match/mismatch. Classify the *kind* of agreement, because "they match" hides more than it reveals:

- ✅ **Genuine agreement** — independently stated in a way that corroborates.
- 📋 **Copy-paste consensus** — identical wording/number; consistent but unvalidated. Not evidence of correctness.
- ❌ **Contradiction** — the documents actually disagree.
- 🟡 **Silent drift** — one document moved (a renamed component, a changed decision) and the others still reference the old state.
- ⚠️ **Vacuous / unfalsifiable** — the claim can't be checked as written ("perfect memory", undefined ">95%").
- ⬜ **Gap** — a document that should address this axis is silent on it.

### 4. Hunt drift and fake-alignment

Go past the matrix and look for the patterns a surface comparison misses — vanity scoring, north-star restatement, resolved-gap theater, abstraction used as an excuse for omission. The full taxonomy with worked examples is in `references/drift-patterns.md`; read it before finalizing, especially if the audit is coming back clean.

### 5. Use the scan as an aid, not a verdict

`scripts/cross_doc_scan.py` is a deterministic helper: point it at the document set and it surfaces (a) metric values that differ across files for the same unit (likely contradictions) and (b) long lines duplicated verbatim across files (the copy-paste signal). It's a flashlight, not the judgment — it finds candidates fast, but classifying them is still semantic work you do.

```bash
python scripts/cross_doc_scan.py PLANNING.md README.md .cursorrules system-prompt.md
```

If you were given only a self-audit/alignment report rather than the source documents, say so: you can audit the report (and a perfect self-score is the first thing to distrust), but the real check needs the underlying docs.

## Output format

Lead with the verdict. **Do not emit a single feel-good percentage** — a "98% aligned" headline is the exact anti-pattern this skill exists to puncture. If the user insists on a score, give a calibrated one with the problems foregrounded, not a vanity number.

```markdown
## Verdict

[2–4 sentences: the real state of alignment. Name the single most important
contradiction or drift up front. If the docs look clean, say what you dug into
to confirm that, rather than just declaring victory.]

**Findings:** ❌ N contradictions · 🟡 N silent drifts · 📋 N copy-paste consensus · ⚠️ N vacuous claims · ⬜ N gaps

**Conductor verdict:** PASS | FAIL | BLOCKED
[PASS only when no contradictions and no silent drifts remain. FAIL on any
contradiction or unresolved drift. BLOCKED if there's no canonical mission to
audit against — that gap must be filled before re-grading.]

| Claim / axis | Across docs | Type | Note |
|---|---|---|---|
| [e.g. user-satisfaction target] | README >9/10 vs PLANNING >8/10 | ❌ | Real conflict, not a rounding difference |
| … | | | |

---

## Contradictions
[Docs that actually disagree, with the specific conflicting values and which to treat as canonical.]

## Silent drift
[Where one doc evolved and others didn't follow — stale names, superseded decisions, mission reworded.]

## Suspicious consensus
[Copy-paste agreement and unfalsifiable claims. State plainly that these are NOT validated just because they match.]

## North-star integrity
[Is the mission stated consistently? Has any doc wandered from it? Is there even a single source of truth?]

## Recommendations
[What to reconcile, which doc wins each conflict, what to make falsifiable, what gap to fill. Concrete.]
```

Drop empty sections. If the set is genuinely coherent, say so — but only after the matrix and the drift-pattern pass actually back that up.

## Shared state

When the project uses `MEMORY_BANK.md`, append a single line summarizing the
verdict (date, doc set audited, PASS/FAIL/BLOCKED, the single most important
contradiction or drift) so future sessions don't re-discover the same drift.

## Tone

Skeptical, specific, fair. The job is to find the problem the cheerful summary is hiding, not to manufacture problems where none exist — but the burden of proof is on "aligned," not on "broken." Every finding ties to a specific value, sentence, or omission across named documents.

**Next steps:** If the audit surfaced claims that should be checked against
external reality (a "best-practice" pattern, a package name, a metric that
might be fabricated), suggest `reality-check` for those. On PASS at the end
of a substantive consolidation session, suggest `conductor-memory` to
persist the reconciled state. Skip the suggestion if the user only wanted
the audit and is moving on to fixes themselves.
