---
name: prompt-template-generator
description: Analyze a software project's files and generate a tailored, copy-paste-ready prompt-template cookbook (a Markdown "PROMPT-TEMPLATES.md") with the project's real stack, paths, subsystems, and conventions already filled in. Use this whenever the user wants to create prompt templates, a prompt cookbook, a prompt library, prompt scaffolding, reusable AI-coding prompts, or a "prompt template generator" for a codebase — or says things like "make prompt templates for my project", "build a prompt guide for this repo", "generate copy-paste prompts for my codebase", or "turn my project into a set of reusable Claude/Cursor prompts". Trigger it even when the user just points at a project and asks for ready-to-use prompts, since the value is filling templates with project-specific facts they'd otherwise type by hand.
phase: execute
hands_off_to: [drift-check, reality-check]
reads: []
writes: []
---

# Prompt Template Generator

Turn any codebase into a **tailored prompt cookbook**: a single Markdown file of
copy-paste-ready prompts (session kickoff, per-subsystem tasks, testing, bug
fixes, optimization, deploy, feature/architecture/hotfix) where the project's
real stack, paths, subsystems, and conventions are **already filled in**. The
user copies a block, fills a couple of `[BRACKETS]`, and pastes it into Claude,
Claude Code, or Cursor to start a task with full context loaded.

This generalizes the hand-built "prompt template" documents developers make for
a single project — but produced automatically for *any* project from its files.

## The one idea that matters

Every template has two kinds of slots:

- **Filled by you, from the analysis** — facts true for the whole project:
  name, stack, real source paths, subsystem names, test command, CI/deploy
  tooling, file-size/style conventions, the doc files that actually exist, and
  any standing user communication preferences. The user must never retype these.
- **Left as `[BRACKETS]`** — per-task blanks: the specific feature, file, error
  message, component, or metric.

A generic template leaves everything bracketed. This skill's output is valuable
precisely because it already knows the project. If you ever write `[PROJECT_NAME]`
or `[TECH_STACK]` into the output, stop — you have that fact; fill it in.

## Workflow

Work in clear phases.

### Phase 1 — Locate the project

Find the project root. It's usually an uploaded folder, a path the user names, a
repo in the working directory, or (if the user is vague) ask which directory.
You need the files on disk, not just a description.

### Phase 2 — Analyze

Run the inventory script:

```bash
python scripts/analyze_project.py <project_root>
```

It prints a summary and writes `.prompt-template-analysis.json` with: project
name, ecosystems, source root, **subsystems** (immediate source subdirs, with
code-file counts — these become document sections), test setup, CI/Docker,
signal files, and parsed conventions (e.g. file-size limits).

Then **read the high-signal files by hand** to enrich the skeleton —
README, CLAUDE.md/.cursorrules, ARCHITECTURE/PLANNING docs, CI workflows. See
`references/analysis-guide.md` for what each ecosystem's directories mean and
how to map them to natural task templates (it covers Node/TS, Python,
Salesforce/sfdx, monorepos, and thin-detection fallbacks).

### Phase 3 — Generate the document

Follow `references/document-structure.md` exactly — it specifies section order,
per-section templates, and the filled-vs-bracketed convention. In short:

```
# 🎯 [name] — Prompt Templates   (+ one-line description)
## 📋 How to use this
## 🚀 Quick Start                 (session kickoff + resume)
## 🧩 <one section per detected subsystem, with 2–4 task templates each>
## 🧪 Testing
## 🐛 Bug Fixes
## 🔧 Optimization & Refactor
## 🚀 Build & Deploy              (only if CI/Docker/deploy detected)
## 🎯 Cross-Cutting Scenarios     (new feature / architecture decision / hotfix)
## 📝 Project Conventions Cheat-Sheet
```

Map each detected subsystem to the tasks natural to it (a UI dir gets component +
accessibility templates; an Apex `classes/` dir gets service-class-plus-tests
templates; etc.). Hard-code real paths and real conventions into every template.
Keep code blocks copyable; use four-backtick outer fences for templates that
contain their own fenced sub-block (logs, errors). Favor a focused cookbook over
an exhaustive one.

### Phase 4 — Save and present

Write the file as `PROMPT-TEMPLATES.md` in the project root (or a name/location
the user prefers). If the `present_files` tool is available, present it. Then
give a 2–3 line summary of what got generated (which subsystems became sections,
which conventions were baked in) and invite tweaks.

## Quality bar

- Every project-wide fact is filled in; only per-task slots stay bracketed.
- Sections reflect the **actual** subsystems — no invented ones, no forced
  symmetry. Two honest templates beat four padded ones.
- Real paths, real test command, real conventions appear verbatim.
- Standing user preferences (if known) are baked into Quick Start + cheat-sheet,
  never invented.

## Files

- `scripts/analyze_project.py` — pure-stdlib project inventory → JSON. Run first.
- `references/document-structure.md` — the output blueprint. Read before writing.
- `references/analysis-guide.md` — how to interpret the inventory per ecosystem.

**Next steps:** After delivery, suggest `drift-check` to audit the generated
cookbook against the project's existing CLAUDE.md, README, and any
PLANNING docs — that's where copy-paste consensus and stale convention
references usually hide. Suggest `reality-check` if you baked in command names,
package versions, or "best-practice" patterns that the user should verify
before relying on them. Skip the suggestion if they just wanted the file and
nothing else.
