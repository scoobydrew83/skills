# Output Document Structure

This is the blueprint for the document the skill produces. The goal is a
**copy-paste-ready prompt cookbook tailored to one specific project**: a developer
opens it, copies a block, fills in a couple of `[BRACKETS]`, and pastes it into
Claude / Claude Code / Cursor to start a task with full context already loaded.

## The core principle: filled vs. bracketed

Every template contains two kinds of slots. Getting this split right is the
entire value of the skill.

- **FILLED IN by you, from the analysis** — anything that is true for the whole
  project and stable across tasks. The user should never have to type these:
  project name, tech stack, real source paths, subsystem names, test command,
  CI provider, deploy target, file-size/style conventions, doc filenames that
  actually exist (`CLAUDE.md`, `README.md`, etc.), and any standing communication
  preferences (e.g. a user's neurodivergent-friendly formatting needs).

- **LEFT AS `[BRACKETS]` for the user** — anything that changes per task: the
  specific feature, the specific file being edited, the pasted error message,
  the specific component name, the metric being optimized.

A static template leaves *everything* bracketed. This skill's output leaves only
the per-task blanks, because it already knows the project. If you find yourself
writing `[TECH_STACK]` or `[PROJECT_NAME]` into the output, stop — you have that
fact, fill it in.

## Section order

Generate sections in this order. Skip any whose trigger condition is unmet
(noted per section). Use emoji headers — they make the cookbook scannable, which
is the point.

```
# 🎯 [PROJECT_NAME] — Prompt Templates
> one-line description of what the project is and its stack

## 📋 How to use this
## 🚀 Quick Start            (always)
## 🧩 [one section per detected subsystem]   (always, ≥1)
## 🧪 Testing                (always)
## 🐛 Bug Fixes              (always)
## 🔧 Optimization & Refactor (always)
## 🚀 Build & Deploy         (only if CI / Docker / deploy config detected)
## 🎯 Cross-Cutting Scenarios (always)
## 📝 Project Conventions Cheat-Sheet  (always)
```

---

## Section templates

Below, `‹filled›` marks a slot you populate from analysis; `[BRACKET]` marks a
slot the user fills. Reproduce the fenced code blocks verbatim in the output so
they are copyable.

### 📋 How to use this

A short prose intro, not a template. State: copy a block, fill the `[BRACKETS]`,
paste into your AI coding tool. Note that project-specific values (paths, stack,
conventions) are already filled in. One or two sentences.

### 🚀 Quick Start

Two templates.

**Session kickoff:**
````
I'm working on ‹PROJECT_NAME›, a ‹short stack/purpose description›.

Context:
- Source lives in ‹source_root›/ ; key areas: ‹subsystem list›
- Conventions: ‹e.g. files under 500 lines, TypeScript + Tailwind, Apex test coverage ≥85%›
- ‹any standing communication preference, if known›

Today I'm working on: [WHAT YOU'RE DOING]
Primary file(s): [FILE_PATH]

Please help me implement [SPECIFIC_FEATURE], following the patterns in
‹the actual doc files that exist, e.g. CLAUDE.md / README.md / ARCHITECTURE.md›.
````

**Resume / context restoration:**
````
Continuing on ‹PROJECT_NAME›. Where we left off:

- Last session: [WHAT GOT DONE]
- Current area: [SUBSYSTEM / FILE]
- Blockers: [ANY BLOCKERS]

Next task: [NEXT_TASK]

Keep consistency with ‹source_root›/ structure and our conventions
(‹line limit / style / test rules›).
````

### 🧩 Subsystem sections (one per detected subsystem)

For each subsystem from the analysis (e.g. `memory`, `agents`, `frontend`,
or for Salesforce `classes`, `lwc`, `triggers`), emit a `##` section named after
it. Inside, give **2–4 templates for the tasks most natural to that subsystem.**
Infer the task types from what the subsystem is:

- a data/storage layer → "add a query/model", "migration", "optimize retrieval"
- an agent/orchestration layer → "register an agent", "add routing", "multi-step workflow"
- a UI layer (React/LWC/Vue) → "new component", "wire up state/events", "accessibility pass"
- an API layer → "new endpoint", "validation", "error handling"
- Apex → "new service class + tests", "trigger handler", "SOQL optimization"

Each template should hard-code the subsystem's real path. Skeleton:

````
‹Task verb› for the ‹subsystem_name› subsystem (‹real/path/›).

Goal: [WHAT IT SHOULD DO]
Touching: [FILE_PATH within the subsystem]
‹Any subsystem-specific constraint you can infer, filled in›

Requirements:
1. [REQUIREMENT_1]
2. [REQUIREMENT_2]
3. ‹a real project convention, filled in — e.g. "stays under the 500-line limit"›
````

Don't invent subsystems that aren't there, and don't force exactly four
templates if two are more honest. Quality over symmetry.

### 🧪 Testing

Fill in the **real test command and framework** if detectable (pytest, Jest,
Vitest, Apex/sfdx run tests). Templates: write unit tests, write an integration
test. Reference the real test directory path.

````
Write ‹framework› unit tests for [FUNCTION / CLASS] in [FILE_PATH].

Cover: [HAPPY PATH], [EDGE CASES], [ERROR CASES]
Put them in ‹real test dir›, matching the style of the existing tests there.
Run with: ‹real test command if known›
````

### 🐛 Bug Fixes

One general debugging template. Includes a fenced sub-block for pasting the
error/log, since that's the per-task input.

````
Fix a bug in ‹PROJECT_NAME› (‹area/file›).

Repro:
1. [STEP]
2. [STEP]
Expected: [EXPECTED]   Actual: [ACTUAL]

Error / logs:
```
[PASTE ERROR HERE]
```
Relevant file(s): [FILE_PATH]
Keep the fix consistent with ‹convention›; add/adjust a test that would have caught it.
````

### 🔧 Optimization & Refactor

One template for performance/refactor work with before/after metrics.

### 🚀 Build & Deploy — *only if CI, Docker, or deploy config detected*

Name the real tooling: GitHub Actions / GitLab CI, Docker, sfdx delta deploy,
etc. Templates for "diagnose a failing pipeline" and "prepare a release/deploy".
For Salesforce specifically, reference scratch orgs / delta deployment if the CI
config shows it.

### 🎯 Cross-Cutting Scenarios

Three templates, always: **New feature**, **Architecture decision**
(options-with-tradeoffs format), **Emergency hotfix**. These mirror the
general-purpose blocks in a typical prompt cookbook but with the project's real
constraints filled in.

### 📝 Project Conventions Cheat-Sheet

Not templates — a short reference block the user can paste into any prompt.
Bullet the **real** conventions found: stack, file-size limit, style tooling,
test requirements, the doc files that exist, and any standing communication
preference. This is the "context payload" that makes every other template work.

---

## Tone & formatting of the output file

- Lead with the project name and a one-line description.
- Keep code blocks copyable — use fenced blocks, and for templates that contain
  their own fenced sub-block (logs, errors), use four-backtick outer fences.
- Don't pad. A focused 6–10 section cookbook beats an exhaustive one nobody reads.
- Default output filename: `PROMPT-TEMPLATES.md` in the project root, unless the
  user asks for another name or location.
