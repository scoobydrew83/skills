---
name: repo-troubleshooting-guide
description: Generate a clean, professional troubleshooting guide (a TROUBLESHOOTING.md) by analyzing a code repository — detecting its tech stack and mining real evidence (raised exceptions, error strings, env vars, ports, Docker services, CI) to document common failure modes with step-by-step fixes. Use this whenever the user wants to create, build, or generate a troubleshooting doc, guide, runbook, or ops reference for a repo, codebase, or project; wants to document common errors, setup problems, failure modes, or "how to fix X"; or points Claude at a repository and asks for a debugging/operations reference. Trigger even if the user doesn't say the exact word "troubleshooting" — e.g. "document the common errors in this repo", "make a debugging runbook", "build a setup-issues guide", "write an ops doc for this project".
phase: execute
hands_off_to: [drift-check]
reads: []
writes: []
---

# Repo Troubleshooting Guide

Turn a repository into a structured, professional troubleshooting guide. The guide is
grounded in two sources: (1) the **detected stack** (languages, frameworks, services,
infra) and (2) **mined evidence** from the actual code (raised exceptions, human-readable
error strings, env vars, ports, Docker services, CI, and TODO/FIXME markers). Generic
advice is a fallback; repo-specific evidence always wins.

## What you produce

A single Markdown file (default `TROUBLESHOOTING.md` at the repo root) with: a quick
setup checklist, issue sections organized by subsystem, recovery procedures, a known-gaps
section from TODO markers, and a "still stuck" section. Clean professional tone — no emoji,
no motivational filler. See `references/output-template.md` for the exact structure.

## Workflow

Follow these phases in order. Each phase has a clear endpoint so you can checkpoint.

### Phase 1 — Locate the repo
Determine the repository path. If the user uploaded or cloned a repo, use that path. If
they named a public repo, clone it (shallow): `git clone --depth 1 <url> /tmp/<name>`.
If the path is ambiguous, ask which directory is the repo root before proceeding.

### Phase 2 — Scan for evidence
Run the scanner to produce a structured inventory. It is stdlib-only Python and writes
JSON describing the stack and failure-mode signals:

```bash
python scripts/scan_repo.py <repo-path> --out /tmp/evidence.json
```

Read `/tmp/evidence.json`. Key fields:
- `languages`, `frameworks`, `services`, `docker`, `ports`, `ci` — the detected stack
- `env_vars` — environment variables the code reads
- `evidence.raised_exceptions`, `evidence.thrown_errors`, `evidence.exception_classes` —
  error types defined/raised in the code
- `evidence.error_messages` — literal human-readable error strings found in the code
- `evidence.todo_markers` — TODO/FIXME/HACK/XXX/BUG comments with file locations
- `existing_docs`, `run_commands` — README/docs present and how the project is run

If `scan_truncated` is true, the repo is large; the scan is still representative but note
that the evidence list is partial.

### Phase 3 — Map evidence to issues
Read `references/issue-catalog.md`. For each detected stack element, pull the relevant
catalog entries **only if that technology is actually present** in the scan, and adapt
their error text, ports, and commands to what the scan found. Then, for each notable
mined signal (a raised exception, a literal error string, a cluster of related TODOs),
draft a repo-specific issue: name it after the real error, state the likely trigger, and
give the most plausible numbered fix. Do not fabricate error strings you didn't find —
if you only have a symptom, describe the symptom.

Prefer depth on what the repo actually does over breadth of generic advice. A repo with
no frontend gets no frontend section.

### Phase 4 — Write the guide
Read `references/output-template.md` and write the guide to that structure. Hard rules:
- No emoji; professional ops-doc tone.
- Put literal error text (from the scan) in code blocks; otherwise describe the symptom.
- Fix steps are numbered, runnable, and use the repo's real commands, paths, ports, and
  service names. End multi-step fixes with a verification step.
- Order sections by subsystem, most-likely-to-break first (setup → deps → services → app).
- Length scales to the repo; don't pad.
- Include a "Known Gaps & TODOs" section built from `evidence.todo_markers`.

### Phase 5 — Save and report
Write the file to `TROUBLESHOOTING.md` at the repo root (or `docs/TROUBLESHOOTING.md` if a
`docs/` directory exists). If a troubleshooting file already exists, say so and confirm
before overwriting. Then give the user a 2–3 line summary: which subsystems are covered,
how many issues, and anything the scan flagged (e.g. truncation, no env example, unresolved
TODOs). If `present_files` is available, present the file.

## Reference files
- `scripts/scan_repo.py` — the repo scanner (Phase 2). Run it; don't reimplement it.
- `references/issue-catalog.md` — common failure modes per technology (Phase 3).
- `references/output-template.md` — the exact output structure and authoring rules (Phase 4).

## Notes
- The scanner is read-only and dependency-free; safe to run on any repo.
- Treat the scan as evidence, not gospel: if you can see the code, verify a detail before
  documenting it. The goal is a guide a teammate could follow without you in the room.

**Next steps:** After delivery, suggest `drift-check` to confirm the new
TROUBLESHOOTING.md doesn't contradict the existing README, CONTEXT.md, or
CONTRIBUTING — the most common drift pattern after generating an ops doc is a
stale port number, a renamed service, or a setup step that disagrees with the
canonical install instructions. Skip the suggestion if the repo has no other
docs to cross-check.
