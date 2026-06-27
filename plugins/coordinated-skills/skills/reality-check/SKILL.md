---
name: reality-check
description: >-
  Pressure-test an AI-generated technical plan, recommendation set, setup guide,
  or tool/config list for hallucinations, factual errors, and unnecessary
  complexity, then verify the surviving claims against live sources before the
  user acts on them. Use whenever the user pastes recommendations, an
  implementation plan, a tooling/MCP/package list, install commands, or config
  and says "validate this", "fact-check this", "is this real/accurate", "did it
  hallucinate", "sanity-check this", "pressure-test this", "is this overkill", or
  asks whether a plan is feasible and worth doing. Especially trigger when the
  content looks AI-generated and is dense with checkable specifics (package
  names, repo URLs, CLI flags, file paths, versions, env vars, named
  "best-practice" patterns, time estimates) that could be fabricated. This is for
  VERIFYING the accuracy and practical value of an EXISTING plan, not for
  choosing between open options or deciding from scratch (use a decision/council
  skill for that).
phase: verify
hands_off_to: [drift-check, conductor-memory]
reads: []
writes: [MEMORY_BANK.md]
---

# Reality Check

Validate AI-generated technical guidance before the user wastes time acting on it. Modern models produce recommendations that are fluent, confident, and structurally perfect — and quietly riddled with invented package names, nonexistent repos, made-up config keys, plausible-but-wrong CLI flags, and "industry-standard patterns" that no one has ever used. On top of that, even the *accurate* parts are often overkill: complexity bolted on for its own sake, reinventing capabilities the user already has.

The user's ask is almost always some version of *"is this real, and is it worth doing?"* Answer both. Be brutally honest — a soft, agreeable review is worse than useless here, because the whole point is to catch what the original generator got wrong.

## Core principle: verify, don't vibe

The failure mode of this skill is reviewing claims from memory and *sounding* confident. Don't. Memory is exactly what hallucinated a wrong package name in the first place, and your training data goes stale. **For every checkable claim, actually search.** A claim you "recognize" is not a verified claim — version numbers, repo ownership, CLI flags, and tool capabilities all drift. When in doubt, look it up; when a search is cheap and the claim is load-bearing, look it up anyway.

## Workflow

### 1. Frame the artifact and extract discrete claims

Identify what you're validating (a plan, a tool list, a config, a step-by-step setup). Then break it into **atomic, individually-checkable claims** rather than reacting to the document as a vibe. "Use Mem0 + Neo4j Memory MCP as a hybrid" is not one claim — it's at least four: (a) Mem0 exists and does memory, (b) a "Neo4j Memory MCP" exists, (c) they're designed to complement each other, (d) the hybrid split is a real/sensible pattern. Pull each one out.

### 2. Triage every claim by type

Different claim types fail in different ways and need different verification:

- **Existence / identity** — Does this tool, package, repo, MCP server, API, or service actually exist under this exact name? (Highest hallucination rate. Check first.)
- **Capability / behavior** — Does it actually do what's claimed? Confidently-stated fake features are common.
- **Configuration / command** — Are install commands, package names, file paths, JSON keys, env vars, and CLI flags correct and current?
- **Architecture / pattern** — Is this a real, named pattern, or an invented-sounding "best practice"? ("X + Y hybrid approach" framings are a frequent tell.)
- **Effort / timeline** — Are the time estimates ("~90 minutes", "Week 1: …") remotely plausible given the real integration surface?
- **Value / necessity** — Even if true: does this solve a real problem the user has, or is it busywork / complexity for its own sake / reinventing something they already run?

### 3. Verify the checkable claims against live sources

Search. Prefer authoritative sources, in roughly this order:

- **Package registries** for existence + current version + exact name (npm, PyPI, crates.io).
- **Official repos and docs** (GitHub, the project's own site) for capability and config claims. Fetch the actual README / docs page rather than trusting a search snippet.
- **Official vendor docs** for API/CLI behavior, flags, and env vars.

For the full source-to-claim-type map — including the exact registry endpoints and the Anthropic docs maps to use for Claude-product claims — read `references/verification-sources.md`.

Catch the classic hallucination tells:
- A package/repo that doesn't resolve, or resolves to something unrelated.
- A real tool credited with a feature it doesn't have.
- Config keys, flags, or env var names that appear nowhere in the official docs.
- Version numbers that don't exist or are wildly off.
- A "well-known pattern" with zero corroboration outside the generated text.
- Two real tools described as purpose-built to integrate when nothing connects them.

For the full taxonomy with worked examples — and for harder cases like overstated absolutes built on a real distinction, or redundancy disguised as sophistication — read `references/hallucination-patterns.md`.

For each claim, land on a status: **verified ✅ / unverifiable ⚠️ / wrong-or-fabricated ❌ / real-but-overkill 🟡**. If a claim genuinely can't be checked (private tools, the user's own undisclosed setup), say so plainly and don't bluff a verdict — flag it as needing the user's confirmation.

**Use the bundled checker for existence claims.** Resolving package/repo names by eye is the same fallible judgment that hallucinated them. Instead, batch every named package, crate, and repo through `scripts/verify_artifacts.py`, which hits the real registries (npm, PyPI, crates.io, GitHub) and returns existence + current version:

```bash
python scripts/verify_artifacts.py \
  --npm @some/package --pypi some-lib --crates some-crate --repo owner/repo
# or pipe a manifest: echo '{"pypi":["mem0"]}' | python scripts/verify_artifacts.py --stdin
```

It exits non-zero if anything fails to resolve. This reliably catches fake names (`pip install mem0` 404s — the real package is `mem0ai`) and wrong versions. For GitHub repo checks, set `GITHUB_TOKEN` to avoid unauthenticated rate limits. Still read the docs for *capability* and *config* claims — the script only proves a name resolves, not that it does what was promised.

### 4. Assess value vs. complexity — honestly

Accuracy is only half the job. For the claims that survive verification, ask whether they're *worth it*:
- Does this add genuine value, or is it impressive-sounding busywork?
- Does the benefit justify the setup + ongoing maintenance burden?
- Is it reinventing a capability the user already has?
- Is it bleeding-edge / not production-ready in a way that creates adoption and reliability risk?

Respect the user's existing sophistication. If they already run a mature setup, recommending five new moving parts for a marginal gain is a *finding*, not a courtesy — call it out.

## Output format

Lead with the verdict. The user wants the bottom line before the appendix.

```markdown
## Verdict

[2–4 sentences: overall judgment. Is the plan sound, partly sound, or mostly
hallucinated? Should they proceed, proceed-with-fixes, or scrap it? Name the
single most important finding.]

**Claim tally:** ✅ N verified · ⚠️ N unverifiable · ❌ N wrong/fabricated · 🟡 N real-but-overkill

**Conductor verdict:** PASS | FAIL | BLOCKED
[Use PASS only if every load-bearing claim verified. FAIL if any wrong/fabricated
claim survives or value is unearned. BLOCKED if claims can't be verified without
information the user hasn't shared.]

| Claim | Status | Note |
|---|---|---|
| [atomic claim] | ❌ | [one-line reason + correction] |
| … | | |

---

## Accuracy assessment
[Claim-by-claim detail for anything not self-explanatory in the table. Cite what
you checked and link the authoritative source. Group the ❌/⚠️ items first.]

## Hallucinations & errors
[Every fabricated or wrong claim, stated bluntly, each with the correction.]

## Value vs. complexity
[For the accurate claims: genuine benefit vs. busywork. Flag overkill and
anything reinventing existing capability.]

## Implementation reality check
[Feasibility, hidden dependencies, and whether the timeline/effort estimates
hold up.]

## Strategic recommendations
[Prioritize / skip / defer. Simpler alternatives where complexity isn't earned.]

## Corrected guidance
[The fixed version: right package names, right commands, right config, realistic
timeline. What you'd actually tell them to do.]
```

Drop any section that has nothing in it — don't pad. If almost everything checks out, say so up front and keep the report short; if it's mostly fabricated, the verdict should make that unmistakable in the first sentence.

## Shared state

When the project uses `MEMORY_BANK.md`, append a single line summarizing the
verdict (date, what was checked, PASS/FAIL/BLOCKED, the most important
finding) so future sessions and the conductor loop see the result without
re-grading.

## Tone

Direct, specific, evidence-backed. No hedging-to-be-nice and no piling on for sport — every harsh call is tied to a source or a concrete reason. The user explicitly asked to have this torn apart; the kindest thing you can do is find the landmines before they step on one.

**Next steps:** On FAIL, hand the report back to whatever generator produced
the original (most often `system-prompt-builder` or `agent-orchestration`) so
the maker can address required fixes. If the artifact spans multiple project
docs, suggest `drift-check` to find contradictions a single-document review
won't catch. On PASS at the end of a substantive session, suggest
`conductor-memory` to persist the verified plan. Skip the suggestion if the
user just wanted the audit and is moving on.
