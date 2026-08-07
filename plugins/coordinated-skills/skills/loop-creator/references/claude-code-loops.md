# Claude Code loops: codebase mode and headless execution

Read this only when the loop is in scope of a real codebase or Claude Code execution. Grounding:
Claude Code best practices (explore→plan→code→commit, headless mode, verification subagents,
git workflow) and the documented headless safeguards.

## Explore before you build

Letting the model jump straight to code produces code that solves the wrong problem. Separate
research/planning from implementation.

1. **Explore (read-only).** Map the repo before touching it: `glob`/`grep` for structure, read
   `README` and any `CLAUDE.md`, find the real build / test / lint commands, check CI config and
   package manifests. Agentic search (glob + grep) beats indexing here — code drifts out of sync
   with any vector store. In Claude Code this is plan mode or a read-only Explore pass.
2. **Plan.** Produce a step-by-step plan with acceptance criteria and a test plan *before* the
   diff exists, so the approach is reviewable.
3. **Code in small commits.** One goal per change, reviewable diffs, commit per checkpoint.
4. **Commit.** Treat green CI / passing tests as the minimum bar, not the finish line.

## Deriving acceptance criteria from the repo

The verifier's checks must be **real commands from this project**: the actual test runner
(`npm test`, `pytest`, `sfdx force:apex:test:run`, etc.), the actual linter, a build that exits
0, a specific assertion. "Looks done" is not a criterion. Pull these from the repo during
exploration so the loop verifies against ground truth.

## Headless execution

Claude Code runs non-interactively for CI, pre-commit hooks, build scripts, and automation:

```bash
# one builder turn, headless
claude -p "$BUILDER_PROMPT" --output-format stream-json

# verifier as a separate, fresh invocation (separate context = real second opinion)
claude -p "$VERIFIER_PROMPT" --output-format stream-json
```

Notes:
- Headless mode does **not** persist between sessions — each turn is triggered explicitly. The
  harness carries state (queue, counters, feedback) between turns, not the model.
- Tune `--max-turns`: too few and a step can't finish; too many wastes tokens. Set it per step,
  not for the whole run.
- The builder and verifier being *separate invocations* is the point — it's the cheap version of
  "a fresh model tries to refute the result."

## `claude -p` drains stdin — never drive a queue with `while read`

This is the single most expensive bug a shell harness can have, because it fails in
the direction that looks like success.

```bash
# BROKEN: processes exactly one unit, then prints "queue complete"
while IFS= read -r line; do
  process_unit "$line"        # <- a `claude -p` lives in here
done < "$QUEUE_FILE"
```

`claude -p` inherits the loop's stdin — which *is* the queue file — and reads it to
EOF on the first turn. Iteration two gets nothing, the loop exits normally, and the
harness reports a clean run over one of twenty units. No error, no non-zero exit.

Two fixes, both cheap; use both:

1. **Read the whole queue up front**, then iterate an array. The loop body no longer
   holds an open fd on the input.
2. **Redirect every `claude` call from `/dev/null`** (`claude -p "$P" </dev/null`).
   This is the general fix — it protects any `claude -p` in any shell read loop,
   not just this harness.

Related shell landmines in the same file, all of which pass a structural lint:

- **`${line#- [ ] }` strips nothing.** Unquoted, `[ ]` is a glob bracket expression
  matching one space. Quote the prefix: `${line#"- [ ] "}`.
- **`(( n++ ))` returns exit status 1 when `n` is 0** (post-increment evaluates to
  the old value). Under `set -e` that kills the run at the first FAIL. Use
  `n=$((n + 1))` — an assignment always exits 0.
- **`sed -i` is not portable.** BSD/macOS requires an argument, GNU forbids one.
  For a literal line rewrite, skip sed: a bash read loop into a temp file needs no
  regex escaping of arbitrary task text.
- **`git checkout -B` force-resets the branch**, orphaning commits earned by an
  earlier run. On resume, check out the existing branch; only `-b` when absent.

## Never report completion from the plan

The harness knows how many units it *intended* to process. That is not evidence.
Before printing success, assert against the source of truth — count the remaining
`- [ ]` lines in the queue file, or the unmet features in `FEATURES.json` — and exit
non-zero if any remain. Every bug above was survivable; what made them costly is
that the harness announced "complete" from its own control flow.

The corollary for the validator: a package lint made entirely of governance checks
(prompts distinct, verdict parseable, ceiling present, no auto-merge) can score a
harness 14/14 while that harness is structurally incapable of running unit two.
Ship one runtime check — stub `CLAUDE_BIN` with a counter script, run a 3-item
queue, assert the invocation count and the final queue state. It needs no API key,
takes a second, and it is the only check that catches any of this. See
`scripts/smoke_harness.sh`.

## Evidence-based verification

The builder must surface the command it ran and its output (test results, lint output, the diff)
as part of its turn. The verifier judges that evidence against the acceptance criteria. Tell the
verifier to flag **only** gaps that affect correctness or the stated requirements — a reviewer
asked for problems will always invent some, and chasing them all leads to over-engineering
(defensive code, tests for impossible cases, extra abstraction).

## GitHub Actions: triage, not autonomous fixing

A scheduled or event-triggered workflow can run `claude -p` to *scan and label* — e.g. read new
issues and append candidates to `LOOP_QUEUE.md`, or summarize a failing nightly build. Keep it
to queueing and annotation. The actual fixer loop stays human-authorized. See
`assets/templates/loop-triage.yml`.

## Safeguards (apply to every codebase loop)

- **Least privilege.** Give the loop only the tools and paths it needs. A docs step doesn't need
  shell; a read-only explore step doesn't need write.
- **Prefer reversible actions.** Work on a branch. Open a PR. Never auto-merge to the default
  branch. Gate deletes, deploys, and migrations behind explicit human approval.
- **Clear stopping conditions.** Define exactly what "done" is so the loop doesn't over-execute,
  plus the max-iteration and consecutive-FAIL ceilings.
- **Human approval queue for ambiguity.** Route uncertain decisions to a human rather than
  letting the loop guess and proceed.
- **Sandbox before loosening permissions.** Only consider `--dangerously-skip-permissions` inside
  a container without network access. Never on a live machine with credentials.
- **CLAUDE.md as context.** Keep project conventions, commands, and constraints in `CLAUDE.md`
  so every loop turn inherits them; keep it concise and human-readable.
