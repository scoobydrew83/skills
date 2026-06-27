# Output Template

Every generated guide follows this structure. Adapt section names to the repo's actual
subsystems, drop sections that don't apply, and add repo-specific sections when the scan
warrants. Keep it clean and professional: **no emoji, no exclamation-point pep talk, no
filler.** Headers are plain. Each issue gets a real symptom, the literal error text when
known, and **numbered, runnable** fix steps.

Save to `TROUBLESHOOTING.md` at the repo root by default. If a `docs/` directory exists,
offer `docs/TROUBLESHOOTING.md` instead. Never overwrite an existing file without saying so.

---

## Required structure

```markdown
# Troubleshooting Guide — <Repo Name>

Quick solutions for common issues when setting up and running <repo name>.
Generated from the current codebase; verify commands against your environment.

## Quick Checklist

Before diving into specific issues, confirm these common culprits:

- [ ] <runtime> version meets the requirement (`<version command>`)
- [ ] Dependencies installed (`<install command(s)>`)
- [ ] Required services running (`docker ps` / `<service check>`)
- [ ] Environment variables set (`.env` present with all keys)
- [ ] No port conflicts (<list the ports the scan found>)

---

## <Subsystem A, e.g. Memory / Vector Store>

### Issue: <short, specific title>

```
<literal error message if the scan found one, otherwise omit this block>
```

Symptom: <one line describing when this happens>

Fix:
1. <first concrete step, with a command if applicable>
2. <second step>
3. <verification step — how to confirm it's resolved>

### Issue: <next issue>
...

---

## <Subsystem B, e.g. API / Backend>
...

## <Subsystem C, e.g. Frontend>
...

## Environment & Configuration
<env var issues; reference the actual env vars the scan found>

## Docker & Deployment
<only if Docker/compose detected; use the actual service names and ports>

## CI / Build
<only if CI detected; reference the actual workflows>

## Recovery Procedures

### Full reset
Ordered, copy-pasteable steps to return to a clean working state
(stop services, clear ephemeral data/caches, reinstall, reinitialize, restart).
Use the repo's real commands and directories.

## Known Gaps & TODOs
Surface unresolved issues mined from TODO/FIXME/HACK markers and open problem areas,
each with its file location. Keep this factual — it documents where rough edges live.

## Still Stuck?
- Where to find logs (real log commands/paths for this stack)
- How to produce a minimal reproduction
- Which component-level reset to run
```

---

## Authoring rules

1. **Ground every issue in evidence.** Prefer issues built from the scan's raised
   exceptions, error strings, env vars, services, and ports. Use the issue catalog only
   for stack elements the scan confirmed are present.
2. **Use literal error text** from the scan inside the code block. If you don't have the
   literal text, describe the symptom instead — do not fabricate an error string.
3. **Make fixes runnable.** Real commands, real file paths, real service/port names from
   the scan. No placeholders left unfilled.
4. **Order sections by subsystem**, most-likely-to-break first (setup, dependencies,
   services, then app layers).
5. **Numbered fix steps**, each a single action; end multi-step fixes with a verification
   step so the reader knows it worked.
6. **No emoji, no motivational filler.** Professional ops-doc tone.
7. **Length scales to the repo.** A small repo gets a focused guide; a large multi-service
   repo gets more sections. Don't pad.
8. **Don't invent subsystems.** If the scan shows no frontend, omit the frontend section.
