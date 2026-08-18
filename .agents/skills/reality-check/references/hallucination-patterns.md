# Hallucination Patterns

Common ways AI-generated technical plans go wrong, each with the tell, why it happens, how to catch it, and a real example. Most hallucinations aren't random noise — they're *plausible*, which is exactly what makes them dangerous. The worked examples below are drawn from real validation runs.

## 1. Fabricated package / scope names

**Tell:** A package named with confident, on-brand precision — often scoped under an org that wouldn't actually publish it (`@anthropic/...`, `@openai/...`).
**Why:** Models pattern-match the *shape* of real package names and fill in a plausible slug.
**Catch:** Resolve it against the registry. Never assume a name is real because it "sounds right."
**Example:** `@anthropic/claude-mcp-orchestrator` — looks official, 404s on npm. No such package exists.

## 2. Near-miss real names

**Tell:** An install command for a tool that *does* exist, but under a slightly different name.
**Why:** The project is real; the exact published name got blurred.
**Catch:** Run the actual install string against the registry, don't trust the prose.
**Example:** `pip install mem0` 404s — Mem0 is real, but the package is `mem0ai` (latest 2.0.6). A copy-pasted `pip install mem0` just fails.

## 3. Overstated absolutes built on a real distinction

**Tell:** A sweeping "only / never / always / cannot" about fast-moving tooling, usually wrapped around a genuine kernel of truth.
**Why:** A real nuance ("X and Y are different runtimes") gets compressed into a false certainty ("so Y can't do what X does").
**Catch:** Separate the true distinction from the false conclusion. Verify the conclusion against current official docs specifically.
**Example:** "MCPs only work in Claude Desktop, not GitHub Actions." The real part: Actions use a different runtime (Claude Code Action) configured in YAML, not `claude_desktop_config.json`. The false part: the Action fully supports MCP via `--mcp-config` and even auto-runs GitHub + file MCP servers. The overstatement would stop you from doing something supported.

## 4. Invented "best-practice patterns"

**Tell:** A confidently-named architecture ("the X + Y hybrid approach"), often pairing two real tools as if they were purpose-built to integrate, with a clean rationale and zero external corroboration.
**Why:** Models are fluent at post-hoc justification; a tidy split *sounds* like wisdom.
**Catch:** Search for the pattern independently. If only the generated text asserts it, it's invented. Check whether one tool already does what the second is being added for.
**Example:** "Mem0 for business context + Neo4j Memory MCP for technical context." Mem0 already ships graph memory (often Neo4j-backed) and a graph+vector+key-value datastore — so the second system is largely redundant, and the crisp business-vs-technical split is a rationalization, not an established practice.

## 5. Fake config keys, CLI flags, and JSON fields

**Tell:** A config key or flag that reads plausibly but appears nowhere in the official schema/docs (`selfHealing: true`, invented `--flags`).
**Why:** Models infer that a desirable behavior "should" have a setting and invent the knob.
**Catch:** Grep the official docs / schema / `--help`. Absent = invented.

## 6. Plausible-but-wrong version numbers

**Tell:** A pinned version (`==4.2.0`) that looks specific and authoritative.
**Why:** Specificity reads as confidence; the number is often fabricated or stale.
**Catch:** Compare against the registry's current/`latest`. A pin to a version that doesn't exist is a hard fail.

## 7. Redundancy disguised as sophistication

**Tell:** A stack of tools that heavily overlap, presented as a layered system.
**Why:** More components *look* more rigorous; the model optimizes for impressiveness.
**Catch:** Map each tool to the problem it solves. Multiple tools solving the same problem is a finding — collapse them.
**Example:** Stacking Mem0 + a Neo4j memory MCP + Memory Bank MCP + Obsidian — four overlapping knowledge stores where one would do.

## 8. Optimistic effort estimates

**Tell:** A suspiciously tidy timeline ("~90 minutes", "Week 1: …") that doesn't survive contact with the dependency chain.
**Why:** Estimates are generated from vibes, not from the actual step list.
**Catch:** Enumerate the real prerequisites (services to stand up, plugins, per-tool permissions, learning curve) and re-estimate. Setup that requires a database + plugin + per-tool allowlists is not a 90-minute job.

## 9. Citing nonexistent docs or endpoints

**Tell:** A confident link or "as documented in…" reference to a page that doesn't exist.
**Why:** Models generate plausible URLs and citations.
**Catch:** Actually fetch the URL. A 404 (or a page that doesn't say what was claimed) is the answer.

---

**Meta-principle:** The strongest signal across all of these is *confidence without corroboration*. When a plan states something specific and checkable that you can only find inside the plan itself, that's the claim to verify first.
