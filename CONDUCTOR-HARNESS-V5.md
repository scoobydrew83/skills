# Conductor Harness V5 — Determinism All the Way Down

**Supersedes:** CONDUCTOR-HARNESS-V4.md. V4's five-layer framework and flywheel survive intact — V5 re-verified every grounding claim against fresh clones (2026-07-18, same day) and adds the one thing V4 described in prose but never shipped: **the harness graded by its own pattern.** Adoption state now lives in `HARNESS-FEATURES.json` and is checked by `check-harness.mjs`, not by re-reading a Markdown plan and hoping.

**Sources:** Anthropic, "Effective harnesses for long-running agents" · OpenAI, "Harness engineering" · full reads of `sfdt`, `skills`, `sfdt-skills` · V3, V4, DRIFT-FIXLIST.md, conductor-v4-starter.zip (all in this folder).

**Thesis (unchanged since V3):** the maker/checker loop is best-in-class; the loop *above* it is missing. Every FAIL verdict, escalation, and doc drift is discarded exhaust. The flywheel turns exhaust into lints, docs, and escalations. **V5's addition:** the framework's own adoption was itself un-verified prose — the exact failure mode the framework exists to kill. Now it's twenty-nine machine-checkable features across all six repos, currently 0/29 passing, which is the honest starting state.

---

## Part 1 — What re-verification found (V4 → V5 delta)

**All seven DRIFT-FIXLIST items are still live.** Nothing was fixed between the V4 read and today: skills CI still invokes gitignored `tests/run-all.sh`; the lockfile is still tracked; `runFixLoop` outcomes still evaporate; CLAUDE.md is 239 lines; the mirror still says v0.18.0 against a v0.18.1 CLI. Phase 0 has not been eaten. `check-harness.mjs` output: **0/15 passing** (H-010 verified false-positive-free: sfdt's four baseline lints are `check-auth-docs`, `check-catalog-drift`, `check-license-consistency`, `check-node-version-consistency`).

**Corrections to V4's record:**

- `runFixLoop` is called from `src/commands/deploy.js` (V4 said `smart-deploy.js`). The one-call fix is unchanged.
- Dangling `COORDINATION-STATUS.md` references: **8 files**, not 5/6 — add `CONTRIBUTING.md`, `tools/skill-graph.sh`, and `.claude/commands/skill-graph.md` to V4's list. The fix-list count in H-002 uses the verified number.

**The three private repos are now grounded** (local clones in `repos/`, read 2026-07-18). V4's guesses about them were wrong in instructive ways — see Part 4 — and the read surfaced the single biggest estate-level finding:

**There are two parallel agent methodologies in this estate, and they don't share a word of vocabulary.** The **Conductor Method** (skills repo: builder/verifier, VERDICT blocks, MEMORY_BANK line format, LOOP_QUEUE) and **SFAOS / Agent OS** (agents + conductor-platform: spec-driven workflow, plan-verifier/implementation-verifier/spec-verifier, `task_runs` telemetry, approval gates). A full keyword sweep of conductor-platform finds zero occurrences of `harness`, `flywheel`, `sfdt`, `conductor-builder`, `conductor-verifier`, or `FEATURES.json` — the platform named after the Conductor Method doesn't speak it. Both methodologies independently reinvented maker/checker and telemetry, which is validation of the pattern and an indictment of the split: every flywheel improvement currently has to be made twice or benefits only half the estate. V5's position: **don't merge the frameworks; merge the contracts.** The verdict schema (CONVENTIONS §5), the FEATURES.json edit rules, and the clean-state exit contract become shared interfaces both methodologies emit and consume — conductor-platform's `run_status` enum (`queued/running/passed/failed/healed/escalated`) is already a superset of PASS/FAIL/BLOCKED and maps cleanly.

---

## Part 2 — The framework (five layers + flywheel, unchanged; compact restatement)

```
L5 FLYWHEEL     harness-improver · doc-gardener · slop-gc — mine L4, PR against L1–L3
L4 TELEMETRY    run-history.db gains verdict/escalation/agent-fix/gc types; skill telemetry
L3 ENFORCEMENT  tools/check-*.mjs lints, error text = remediation instruction
L2 EXECUTION    conductor-init → builder → verifier → gate · clean-state exit · one item/session
L1 KNOWLEDGE    map-file ≤100 lines · docs/ tree · FEATURES.json · golden-principles.md
```

The meta-rule (OpenAI, verbatim): *when the agent struggles, identify what is missing — tools, guardrails, documentation — and feed it back into the repository, always by having the agent itself write the fix.* L4 makes struggle visible; L5 converts it; L3 receives mechanical conversions, L1 receives knowledge. Full prose for each layer: V4 Part 2, still authoritative. Starter assets (FEATURES template, three flywheel agent definitions, improver workflow, sfdt golden principles, agent-loop patch) are in `conductor-v4-starter.zip` — unchanged and still correct.

Everything the layers build on was re-verified today: `generated/` catalogs + `check:all-contracts` (drift-CI pattern), `command-policy` test, `claude-code-review.yml` + `claude.yml` (agent review substrate), `scheduled-audit.yml` + nightly cron (scheduling substrate), `notifier.js` with generic-webhook channel (n8n escalation edge), `run-history.js` with free-text `type` and never-throws `recordRun` (telemetry substrate). The locked decisions stand: GitHub Actions runs agents, n8n owns only notify/escalation; the `skills` repo is the method's system of record.

---

## Part 3 — The V5 spine: L0, the reflexive layer

**The rule:** any claim of the form "the harness now does X" must exist as an entry in `HARNESS-FEATURES.json` with a deterministic check in `check-harness.mjs`, or it isn't a claim — it's an intention. This is Anthropic's FEATURES.json contract applied to the harness itself, with the same edit rules:

- **The checker is the only writer**, and only of `passes`/`evidence` (`--update`). Descriptions and steps change only by planner/human commit. Removing an entry to make the suite green is the reflexive version of deleting a failing test.
- **DRIFT is the third verdict.** `passes: true` that the checker can't reproduce today fails the run (exit 1). Adoption can regress, and the file can't lie about it. This is what makes the loop *self-correcting* rather than merely self-describing: the same mechanism that records progress detects its loss.
- **Evidence is dated and re-checkable** — a command output or path, never "done."

**How the flywheel eats it:** the twenty-nine failing H-features are harness-improver's bootstrap queue — no telemetry mining needed for its first runs, the queue is already written. doc-gardener's scheduled job is `node check-harness.mjs --json` plus its V4 duties; a DRIFT result is exactly the class of finding it exists to PR. When a phase lands, the landing PR runs `--update` and commits the flipped entries — adoption history accrues in git like any other work product.

**Where it lives:** `HARNESS-FEATURES.json` + `check-harness.mjs` move to the `skills` repo alongside this doc (system of record, per the locked decision), with the checker wired into the skills CI on the existing `test.yml` pattern — existence-guarded, unlike the current `tests/run-all.sh` step it will sit next to. It needs only `node`, `git`, `grep`, and local clones (`--repos` points at the parent dir of `sfdt/`, `skills/`, `sfdt-skills/`).

---

## Part 4 — Repo fit

**sfdt** — testbed, unchanged sequence, now keyed to H-IDs: H-005 (six-line agent-loop patch, starter provided) → H-006/H-007 (verdict tool + FEATURES.json) → H-008/H-009 (map split + golden principles) → H-010 (first new lint into `check:all-contracts`) → H-012 (improver workflow). Every slot named exists today.

**skills** — system of record. Eats H-001…H-004 first (its own rot), then hosts H-011 (three flywheel agents), H-015 (conductor-init), and the L0 pair. CONVENTIONS.md gains the FEATURES.json artifact (§4) and skill-telemetry line (§5-adjacent); CONDUCTOR-LOOP-GUIDE gains Phase 6 — Flywheel. §7's open question resolves as in V4: session close is the conductor-memory trigger, encoded in the builder's clean-state exit checklist.

**sfdt-skills** — stays a pure mirror; H-014 goes green only by making sync a release-pipeline step, never by hand-editing the mirror.

**agents — not what V4 guessed.** Not a conductor-agents distribution point: it's **SFAOS**, a full profile-based Salesforce agent framework — 64 agent definitions across `.claude/agents/` (11 meta + 11 Salesforce specialists), profile templates, a Python compiler (~36 test files, ~1100 test functions actually run by CI), and `compiler/conductor_cli.py`, a 518-line JSON-only boundary (`agent-os.conductor.v1`) that is the real bridge to conductor-platform. It already has its own maker/checker family (plan-verifier PASS/GAPS_FOUND, implementation-verifier, spec-verifier) and the claude-review workflows — but **no cron, no telemetry store, no conductor artifacts, and zero mechanical agent validation** across two incompatible frontmatter styles. Its drift is textbook OpenAI-post material: CI push triggers target `main`/`work` while the repo lives on `master` (push CI never fires — H-016); "222 tests" claimed where ~1100 exist (H-017); README claims API 66.0 vs versions.yml 63.0 (H-018); nine legacy agents pin a dead model string (H-019). The conductor-agents distribution point stays the `skills` repo (H-011); what agents needs is H-020's validate-agents gate — the same check the skills repo needs, one implementation shared.

**conductor-platform — real, and further along on L4 than sfdt.** A substantial FastAPI + Next.js control plane (~140 backend files, ~1,483 backend test functions, 85% coverage gate in CI, k8s + Prometheus infra). Its `task_runs` table with `run_status` enum (`queued/running/passed/failed/healed/escalated`), `test_results` JSONB, and `self_healing_attempts` **is the productized L4** — Postgres where sfdt uses SQLite. But the harness around it drifted exactly as the posts predict: CLAUDE.md is a 134-line monolith triplicating CONTEXT.md and MASTER_PROMPT_V2 (H-021); MEMORY_BANK.md names Celery — a library the codebase *removed* — as a live decision, and CLAUDE.md/README point agents at `celery_app.py`, which doesn't exist (H-022); DATABASE_SCHEMA.sql omits the six tables the migrations added (H-023); docs declare "LAUNCHED / 100% COMPLETE" on 2026-03-19 while git shows the core Agent OS execution engine being wired through 2026-06-27, and the "30-day build" spanned 6 calendar days. The brain lives out-of-repo (`AGENTS_REPO_PATH` → the agents repo), hardcoded as `/home/drew/agents` in two integration tests and the env examples (H-024). MEMORY_BANK adopting the CONVENTIONS §4 dated line format (H-025) is the first contract-merge step from Part 1.

**studio-by-sfdt — V4's one good guess, confirmed.** A genuinely runnable React 19 + Vite npm-workspace MVP (prompt → validated Salesforce component spec → safe preview → SFDX export) with Supabase RLS persistence and a clean typecheck+test+build CI. Exactly as V4 predicted for a UI product, the verification gap is the browser: 12 vitest files, all jsdom, **zero Playwright/Puppeteer** (H-026) — the verifier cannot drive the UI like a human, which is where agents declare victory early. Ports 5174/4175 are hardcoded in `dev.mjs`, so parallel worktrees collide (H-028 — the per-worktree-bootable-app lesson from the OpenAI post). No Conductor artifacts at all; a 35-line AGENTS.md carries the real invariants (strict TS, no-execute-generated-JS safety boundary) and should keep carrying them — it's already a map, not a manual. README drift: hardcoded `/home/drew/workspace` paths and personal LAN/Tailscale IPs (H-027), plus a stale "no ZIP export" claim above a documented ZIP-export button.

---

## Part 5 — Build sequence (acceptance = H-features flipping, nothing else)

- **Phase 0 — eat the fix-list:** H-001, H-002, H-003, H-014 (+H-004 if same sitting). One sitting, by hand or as the first supervised builder/verifier run. The flywheel's credibility starts with the harness fixing its own known rot.
- **Phase 1 — telemetry + ground truth:** H-005, H-006, H-007. Accept additionally when a deliberately broken criterion produces a persisted FAIL row.
- **Phase 2 — map-not-manual:** H-008, H-009. Accept additionally when a cold session answers "how do I add a command?" by visibly navigating docs/.
- **Phase 3 — enforcement:** H-010 (then the rest of V4's five lints). Accept additionally when violating each rule yields an error message a fresh agent session acts on correctly — test literally.
- **Phase 4 — flywheel:** H-011, H-012, H-015, then H-013 — one full self-improvement cycle observed end to end. H-013 is the only manual-verify feature and the only one that matters for the headline claim: a flywheel that can't demonstrably turn is decoration.
- **Phase 5 — estate drift sweep:** H-016…H-019 (agents), H-022…H-024 (conductor-platform), H-027 (studio). All small, mechanical, doable in one or two sittings — and the exact material doc-gardener will own once scheduled, so fixing them by hand once is also its training set.
- **Phase 6 — contract merge:** H-020 (shared validate-agents), H-021 (platform map split), H-025 (MEMORY_BANK line format). The Conductor↔Agent OS bridge from Part 1, starting with the cheapest shared artifacts.
- **Phase 7 — studio harness:** H-026 (browser E2E), H-028 (env-overridable ports), H-029 (UI FEATURES.json). Accept fully when the verifier reproduces a UI bug and validates the fix by driving the app; route browser-native-modal criteria to human spot-checks (Anthropic's caveat).

Run `node check-harness.mjs --repos <roots>` before and after every phase (roots = comma-separated dirs holding the six clones; missing repos SKIP). The before-run is the get-bearings ritual applied to the harness; the after-run with `--update` is the clean-state exit. Current state: **0/29 passing, 0 drift** — the honest baseline.

---

## Part 6 — Design tensions (V4's six carry forward, plus two)

Self-improving ≠ self-approving · bounded flywheel (≤3 PRs/agent/run) · telemetry never throws · docs split needs the gardener · quiet weeks are PASSes · the ≥3-occurrence threshold is tunable telemetry — all unchanged, see V4 Part 5.

**New — the checker must stay dumb.** Every check is a file/grep/version assertion a human can rerun in ten seconds. The moment a check needs an LLM to evaluate, it's not an H-feature; it's a verifier criterion in the ordinary loop. H-013 shows the honest pattern: mark it MANUAL rather than fake determinism.

**New — L0 measures adoption, not virtue.** A green H-file means the mechanisms exist, not that they're working — that's what L4 telemetry and H-013 are for. Resist adding H-entries for outcomes ("fewer FAILs this month"); outcomes belong to the improver's mining, where they can be wrong without corrupting ground truth.
