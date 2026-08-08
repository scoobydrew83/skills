# triggering-evals

Description-driven triggering evaluation for the skill library. Asks the
question: **does each skill's `description:` field still cause Claude to fire
on the prompts it claims to handle, and stay quiet on prompts that should
match a sibling?**

This is Phase 2b of the test suite. It is intentionally NOT wired into
`tests/run-all.sh` — the LLM mode needs an API key and the static mode is a
crude approximation. Run it on demand, after editing a `description:` field
or adding a sibling skill that competes for the same triggers.

## Layout

```
tests/triggering-evals/
├── README.md          you are here
├── run.sh             entry point — see --help
├── _match.py          static + LLM matchers (stdlib only)
├── score.py           precision/recall table, per-skill verdict
├── prompts/           one <skill>.json per skill being tested
│   └── overwhelm-breakdown.json
│   └── ...
└── .results/          JSON output, one file per run (gitignored)
```

`.results/` should be added to `.gitignore` by Task A. Only `.gitkeep` is
committed.

## What it tests

For each skill `S` we keep a `prompts/S.json` with two arrays:

- `should_trigger`  — prompts that the skill's own `description:` field claims
  to handle (sourced verbatim from the description's "Use this when…"
  examples). The matcher should pick `S`.
- `should_not_trigger` — confusable prompts that belong to a sibling skill
  (sourced from `skill-graph.md`). The matcher should NOT pick `S`.

We then compute per-skill **precision** (of the prompts the matcher routed to
`S`, how many actually belonged to `S`) and **recall** (of the prompts that
should have gone to `S`, how many did) and require both ≥ 0.8 by default.

## How the static matcher scores (and why)

Three rules exist because the naive version measured its own artifacts rather
than description quality. Each was diagnosed from a real failure:

1. **Negative guidance is not positive evidence.** A description's
   "Do NOT use for X" / "Distinct from Y" / "rather than Z" clauses describe a
   *sibling's* territory. Each sentence is truncated at its first negative
   marker before tokenizing. Without this, `agent-orchestration` — whose
   description ends `Do NOT trigger for single-stage asks ("fix this bug",
   "write this function")` — was matched by those exact prompts, i.e. penalised
   for disambiguating well.

2. **Tokens are IDF-weighted.** Raw overlap counts every shared word equally,
   so generic words present in most descriptions outvote the rare ones that
   actually identify a skill. IDF also stays correct as skills are added,
   unlike a hand-tuned weight table. (It cannot fix *function* words — rare is
   not the same as meaningful — so filler verbs like `keep`/`going`/`let` are
   in `STOPWORDS` alongside `make`/`give`/`get`.)

3. **Ties are ambiguous, not a win for whoever sorts first.** The original
   `max()` handed every tie to the alphabetically earlier skill, inventing a
   false negative for one and a false "grabbed by" for another —
   `reality-check` lost two prompts to `goal-builder` on nothing but its name.
   A tie is now scored **symmetrically**: on a `should_trigger` prompt, being
   among the best matches counts as covered; on a `should_not_trigger` prompt,
   matching as strongly as the rightful owner counts as leaking. Ties are also
   printed in their own section, because *which descriptions compete for the
   same triggers* is the actionable output even when every skill passes.

A tie in keyword space says little about how an LLM would route — treat the
ambiguity list as a prompt for description work, not as a defect.

## How to run

```bash
# Static mode (default — no API key needed, crude keyword-overlap matcher):
tests/triggering-evals/run.sh
tests/triggering-evals/run.sh --skill overwhelm-breakdown

# LLM mode (needs ANTHROPIC_API_KEY — asks Claude haiku which skill to invoke):
ANTHROPIC_API_KEY=sk-... tests/triggering-evals/run.sh --mode llm
```

Tunable thresholds:

```bash
TRIGGER_RECALL_MIN=0.75 TRIGGER_PRECISION_MIN=0.9 \
  tests/triggering-evals/run.sh
```

Exit codes: `0` all skills pass, `1` at least one below threshold, `2`
harness error.

## How static mode works

We extract each skill's `description:` value from its `SKILL.md` (via the
stdlib `zipfile` module — no `unzip` needed). We tokenise both the
description and the prompt (lowercase, stopword-filtered, length ≥ 3) and
score every (prompt, skill) pair as `|prompt ∩ skill| / |prompt|`. For each
prompt we pick the top-scoring skill; if it clears `STATIC_MATCH_MIN`
(default 0.05) we record that skill as the prediction.

Static mode is a **lower bound**, not a real evaluation. It catches the worst
failures (a description that shares no vocabulary with its own examples) but
it cannot distinguish two siblings whose descriptions overlap heavily. Use
LLM mode for the real number.

## LLM mode

For each prompt we POST to `api.anthropic.com/v1/messages` with the prompt,
the full list of skill names and descriptions, and a one-line system prompt
asking the model to reply with a single skill name or `NONE`.
Model defaults to `claude-haiku-4-5` (override with `TRIGGER_LLM_MODEL`).
Requests send `temperature: 0` — routing is a classification and resampling it
only adds noise. **The override must name a model that accepts sampling
parameters** (Haiku 4.5, Sonnet 4.6 and earlier); Opus 4.7+, Opus 5, Sonnet 5,
and Fable 5 reject `temperature` with a 400.

**Read a single run as a noisy estimate.** Each skill has 5 prompts, so recall
moves in steps of 0.20 and one flipped answer crosses the 0.80 gate on its own.
Before treating a FAIL as a real regression, check whether the skill sits at
0.80 — most do — and re-run. Doubling the prompts per skill would halve the
step size; nobody has.

**Descriptions are sent whole — never truncated.** Claude Code's real router
sees the entire `description:` field, so anything shortened here makes the eval
measure a fiction rather than the deployed behaviour. The harness used to slice
each one to 400 chars, which cut `popquiz` mid-word and hid every trigger phrase
its own prompt file tests it on; four skills reported recall failures against
text the model was never shown. `tests/test_trigger_payload.sh` guards this.

Cost is roughly **$1 per full sweep** at current haiku pricing — ~190 requests
carrying the whole ~5.5k-token skill menu each, at $1/MTok input. It scales with
the number of skills, so it grows as the library does. (An earlier note here
claimed one cent; that was wrong even under truncation.) The menu is byte-identical
across every request in a sweep, so prompt caching would cut it to roughly $0.15
— it needs the skill list moved ahead of the per-request prompt in the user
message, since caching matches on a prefix. Not currently implemented.

## Adding prompts for a new skill

Create `prompts/<new-skill>.json`:

```json
{
  "skill": "<new-skill>",
  "should_trigger":     ["prompt 1", "prompt 2", "..."],
  "should_not_trigger": ["confusable from sibling 1", "..."]
}
```

3–5 prompts per array is enough. Source them from the skill's own
`description:` examples for positives, and from the descriptions of skills
that share a row in `skill-graph.md` for negatives.

## Why this is NOT in `tests/run-all.sh`

- LLM mode needs an API key and costs money.
- Static mode is a coarse approximation — false positives at this layer are
  not actionable bugs, they're feedback on how distinguishable a description
  is.
- Both modes are an order of magnitude slower than the structural tests.

Run it deliberately, not on every commit.
