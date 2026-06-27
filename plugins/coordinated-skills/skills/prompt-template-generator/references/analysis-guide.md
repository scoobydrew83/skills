# Project Analysis Guide

The `scripts/analyze_project.py` script does the mechanical inventory (manifests,
subsystems, config files, conventions). This guide tells you how to *interpret*
that inventory and what to read by hand to enrich it before generating the
document. The script gives you the skeleton; a few targeted reads give you the
muscle.

## Workflow

1. Run the script to get the JSON inventory.
2. Read the high-signal files it flagged (the ones below) to confirm and enrich.
3. Map subsystems → sections and infer the natural tasks for each.
4. Generate the document per `references/document-structure.md`.

## Always read these if present (they define the project's "voice")

- **README** — purpose, the one-line description, how to run/test. The single
  best source for the project's tagline and stack.
- **CLAUDE.md / .cursorrules / AGENTS.md** — explicit rules the AI is expected to
  follow (file-size limits, style, architectural patterns, forbidden moves).
  These go straight into the Conventions cheat-sheet and into individual
  templates as filled-in constraints. The script extracts a line-limit heuristic
  but read for the rest.
- **ARCHITECTURE.md / PLANNING.md / docs/** — subsystem responsibilities and
  patterns. Use these to name subsystem tasks accurately rather than guessing.
- **CI workflow files** (`.github/workflows/*.yml`, etc.) — reveal the real test
  command, build steps, deploy target. These make the Testing and Build & Deploy
  sections concrete instead of generic.

## Reading the main manifest to nail the stack

- **package.json** → `name`, framework deps (react, next, vue, express, fastify),
  `scripts.test` (the real test command), TypeScript via `tsconfig.json`.
- **pyproject.toml / requirements.txt** → framework (fastapi, django, flask),
  test runner (pytest), lin/format (ruff, black).
- **sfdx-project.json** → Salesforce. `packageDirectories` names the package(s);
  `force-app/main/default/` holds the metadata subfolders that become subsystems.
- **go.mod / Cargo.toml / pom.xml / Gemfile / composer.json / *.csproj** → the
  language and, usually, the test convention for that ecosystem.

## Ecosystem-specific subsystem mapping

The script lists subsystems as immediate subdirs of the source root. Interpret
them per ecosystem so the task templates ring true:

**Node / TypeScript web app**
- `components/`, `pages/` or `app/`, `hooks/`, `services/`/`api/`, `lib/`,
  `store/`/`state/`. UI dirs → component + accessibility templates; services/api
  → endpoint + validation templates; store → state-management templates.

**Python service**
- `models/`, `routers/`/`api/`, `services/`, `db/`/`repositories/`, `tasks/`,
  `agents/`. Map to model, endpoint, service-logic, and migration templates.

**Salesforce (force-app/main/default/)**
- `classes/` (Apex) → "new service class + test class (coverage ≥ the org's
  requirement)", "trigger handler", "SOQL/governor-limit optimization".
- `lwc/` / `aura/` → component templates with accessibility + `@wire`/Apex
  binding.
- `triggers/` → trigger-handler-pattern templates.
- `objects/`, `flows/`, `permissionsets/` → metadata/config templates.
- If the CI shows delta deployment (e.g. sfdx-git-delta) or scratch orgs,
  reflect that in Build & Deploy.

**Monorepo (packages/ with multiple manifests)**
- Treat each top-level package as its own subsystem section, or ask the user
  whether to scope the cookbook to one package.

## When detection is thin

- **No clear subsystems** (flat repo): treat the whole project as one subsystem
  and lead with task-type sections (feature, fix, test, refactor) instead.
- **Multiple ecosystems** (e.g. a Python backend + React frontend in one repo):
  generate subsystem sections for both, and make the stack line in Quick Start
  name both halves.
- **Unknown stack**: still generate the universal sections (Quick Start, Testing,
  Bug Fixes, Optimization, Cross-Cutting) and note in the cheat-sheet that the
  stack was inferred from file extensions.

## Standing user preferences

If you know durable preferences about how the user wants AI help formatted
(e.g. numbered steps, explicit phases, neurodivergent-friendly structure), bake
them into the Quick Start template and the Conventions cheat-sheet so every
copied prompt carries them. Don't invent preferences — only include ones you
actually have evidence for.
