# Issue Catalog

Common failure modes keyed by technology. Use this as a *starting library* when the
scanner detects a given stack element. **Always prefer repo-specific evidence**
(actual raised exceptions, error strings, env vars, ports from the scan) over these
generics. Pull a catalog entry only when the scan shows that technology is present,
and adapt the error text, ports, and commands to what the scan actually found —
never paste an entry verbatim if the repo's real details differ.

If the scan surfaces a raised exception or error string with no matching catalog
entry, write a repo-specific issue for it anyway: name the issue after the error,
state the likely trigger, and give the most plausible numbered fix.

## Contents
- [Docker & Compose](#docker--compose)
- [Python / Poetry / pip](#python--poetry--pip)
- [Node / npm / build](#node--npm--build)
- [Web frameworks (FastAPI, Flask, Django, Express)](#web-frameworks)
- [Frontend (React / Vite / Next.js)](#frontend)
- [Databases & stores (Postgres, Redis, Mongo)](#databases--stores)
- [Vector databases (Chroma, Pinecone, etc.)](#vector-databases)
- [WebSockets & CORS](#websockets--cors)
- [Environment & secrets](#environment--secrets)
- [Ports & networking](#ports--networking)
- [CI / GitHub Actions](#ci--github-actions)
- [Salesforce / SFDX](#salesforce--sfdx)

---

## Docker & Compose
**Container won't start / driver failed**
- Error: `Cannot start service <x>: driver failed` or `Cannot create container`
- Fix steps: clean state (`docker compose down -v`), prune (`docker system prune -af`),
  re-up; check Docker daemon is running (`docker ps`); raise resource limits in Docker
  Desktop if builds OOM.

**Volume permission denied**
- Error: `permission denied` writing to a mounted volume
- Fix steps: `sudo chown -R $USER:$USER <data-dir>`; `chmod -R 755 <data-dir>`; confirm
  the compose `volumes:` path matches the in-container path.

**Image build cache stale**
- Symptom: code changes not reflected after rebuild
- Fix steps: `docker compose build --no-cache <service>`; verify the `COPY`/`.dockerignore`
  aren't excluding changed files.

## Python / Poetry / pip
**Wrong interpreter / version**
- Error: `SyntaxError` on modern syntax, or `requires Python >=3.x`
- Fix steps: check `python --version` against the manifest's required version; recreate
  the virtualenv; for Poetry run `poetry env use 3.x` then `poetry install`.

**Module not found / import errors**
- Error: `ModuleNotFoundError: No module named '<pkg>'` or `Could not import module "<app>"`
- Fix steps: confirm the env is activated (`poetry shell` / `source .venv/bin/activate`);
  reinstall (`poetry install` / `pip install -r requirements.txt`); set `PYTHONPATH=.`
  if a local package isn't found; run modules with `python -m <pkg.module>`.

**Dependency resolution conflict**
- Error: `SolverProblemError` / `ResolutionImpossible`
- Fix steps: delete the lockfile and re-lock (`poetry lock --no-update` then `poetry install`);
  pin the conflicting transitive dependency.

## Node / npm / build
**Module not found at build/runtime**
- Error: `Module not found: Can't resolve '<pkg>'`
- Fix steps: clean install (`rm -rf node_modules package-lock.json && npm install`);
  confirm the import path/casing; check `baseUrl`/`paths` in `tsconfig.json` for alias
  imports.

**Node version mismatch**
- Error: `The engine "node" is incompatible` or native build failures
- Fix steps: match the version in `.nvmrc`/`engines` (`nvm use`); clear cache
  (`npm cache clean --force`); rebuild native modules.

## Web frameworks
**FastAPI/uvicorn won't start**
- Error: `Error loading ASGI app. Could not import module "<pkg.api.main>"`
- Fix steps: set `PYTHONPATH=.`; verify the `app` object path; run explicitly with
  `python -m uvicorn <module>:app --reload`.

**Flask/Django app context / migration errors**
- Symptoms: `RuntimeError: Working outside of application context`; `no such table`
- Fix steps: ensure app/factory is initialized; run migrations
  (`alembic upgrade head` / `python manage.py migrate`).

**Express server crashes on boot**
- Error: unhandled promise rejection / `EADDRINUSE`
- Fix steps: add error handlers; free the port (see Ports section); verify env-driven
  config is loaded before `listen()`.

## Frontend
**Dev server / HMR not updating**
- Symptom: edits don't reflect; blank screen
- Fix steps: restart dev server; clear `.vite`/`.next` cache; check the browser console
  for a runtime error masking the render.

**Build fails on type errors**
- Error: TypeScript errors only at build time
- Fix steps: run the type checker locally (`tsc --noEmit`); fix or, as a temporary
  measure, isolate the offending module; confirm `tsconfig` paths.

## Databases & stores
**Connection refused**
- Error: `connection refused` / `could not connect to server` (Postgres),
  `ECONNREFUSED` (Redis/Mongo)
- Fix steps: confirm the service container is up (`docker ps`); check host/port in the
  connection string vs. compose; wait for healthcheck; verify credentials/env vars.

**Migrations out of sync**
- Symptom: schema errors at runtime
- Fix steps: run pending migrations; if drift, generate a new migration; never edit
  applied migrations by hand.

## Vector databases
**Connection refused to vector DB**
- Error: `Could not connect to <ChromaDB/Qdrant/...> at localhost:<port>`
- Fix steps: confirm the container is running and the port matches; restart the service;
  check the client URL/env var.

**Embedding dimension mismatch**
- Error: `Embedding dimension <a> does not match collection dimension <b>`
- Fix steps: ensure the embedding model is the same everywhere; recreate the collection
  with the correct dimension, or migrate existing vectors to the new model.

**Persistence/corruption after restart**
- Symptom: index empty or errors after restart
- Fix steps: confirm the data volume is mounted and persistent; back up before resetting;
  rebuild the index from source records.

## WebSockets & CORS
**WebSocket connection fails / drops**
- Error: `WebSocket connection to 'ws://<host>/ws' failed`
- Fix steps: enable CORS for the WS origin on the server; add client reconnection logic
  with backoff; confirm the proxy (Caddy/nginx) forwards upgrade headers.

**CORS blocked request**
- Error: `blocked by CORS policy`
- Fix steps: add the frontend origin to allowed origins on the API; allow required methods
  and headers; set credentials handling consistently on both ends.

## Environment & secrets
**Missing or malformed env var**
- Symptoms: `KeyError`/`undefined`, `Invalid key format`, silent misconfig
- Fix steps: copy `.env.example` to `.env` and fill every required key; for generated keys
  (e.g. Fernet) regenerate with the documented command; validate format at startup and
  fail fast with a clear message.

## Ports & networking
**Address already in use**
- Error: `EADDRINUSE` / `address already in use :::<port>`
- Fix steps: find and kill the process (`lsof -ti:<port>` → `kill -9 ...`); or change the
  external port in compose; confirm no duplicate instance is running.

## CI / GitHub Actions
**Workflow fails on a step**
- Fix steps: open the failing run's logs; reproduce the failing command locally with the
  same env; cache dependencies to rule out flaky installs; pin action versions.

**Secrets not available in CI**
- Symptom: auth failures only in CI
- Fix steps: confirm repo/environment secrets are set and referenced by the exact name;
  remember secrets aren't exposed to PRs from forks by default.

## Salesforce / SFDX
**Deploy/auth failures**
- Errors: `INVALID_SESSION_ID`, `Deploy failed`, component errors
- Fix steps: re-authorize the org (`sf org login web`); verify the target org alias and
  API version in `sfdx-project.json`; check for failing required tests; for delta deploys
  confirm the manifest/package.xml includes dependencies.

**Managed package / namespace issues**
- Symptom: components not found, namespace prefix mismatches
- Fix steps: confirm the namespace in `sfdx-project.json`; ensure dependent packages are
  installed in the target org; align API versions across metadata.
