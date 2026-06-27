#!/usr/bin/env python3
"""
scan_repo.py — Deterministic repository scanner for the troubleshooting-guide skill.

Walks a repo and emits a JSON "evidence inventory" describing the tech stack and
concrete failure-mode signals (raised errors, error strings, TODOs, env vars,
docker services, ports, CI, existing docs). Stdlib-only so it runs in any repo.

Usage:
    python scan_repo.py [REPO_PATH] [--out evidence.json] [--max-bytes 800000]

The output is a single JSON object printed to stdout (and optionally written to
--out). It does NOT decide what goes in the guide — it just gathers evidence.
Claude reads the JSON plus references/issue-catalog.md to author the guide.
"""

import argparse
import json
import os
import re
import sys

# ---- What to skip while walking -------------------------------------------------
SKIP_DIRS = {
    ".git", "node_modules", ".venv", "venv", "env", "__pycache__", ".mypy_cache",
    ".pytest_cache", ".ruff_cache", "dist", "build", ".next", ".nuxt", "target",
    "vendor", ".gradle", ".idea", ".vscode", "coverage", ".terraform", "out",
    ".cache", "site-packages", ".tox", "bin", "obj",
}
# Source extensions we will grep for error evidence.
CODE_EXT = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java", ".rb", ".php",
    ".cs", ".kt", ".swift", ".cls", ".trigger", ".apex", ".c", ".cpp", ".scala",
}
MAX_FILE_BYTES = 400_000          # skip files bigger than this when grepping
MAX_MATCHES_PER_KIND = 60         # cap each evidence list so output stays sane

# ---- Dependency → framework / service mapping ----------------------------------
# Substrings checked (lowercased) against collected dependency names.
FRAMEWORK_SIGNALS = {
    "react": "React", "next": "Next.js", "vue": "Vue", "nuxt": "Nuxt",
    "svelte": "Svelte", "angular": "Angular", "vite": "Vite",
    "express": "Express", "fastify": "Fastify", "nestjs": "NestJS",
    "fastapi": "FastAPI", "uvicorn": "Uvicorn", "starlette": "Starlette",
    "flask": "Flask", "django": "Django", "gunicorn": "Gunicorn",
    "celery": "Celery", "pydantic": "Pydantic", "sqlalchemy": "SQLAlchemy",
    "alembic": "Alembic (migrations)", "prisma": "Prisma",
    "spring": "Spring", "rails": "Rails", "laravel": "Laravel",
    "tailwind": "Tailwind CSS", "framer-motion": "Framer Motion",
    "websocket": "WebSockets", "socket.io": "Socket.IO",
}
SERVICE_SIGNALS = {
    "postgres": "PostgreSQL", "psycopg": "PostgreSQL", "pg": "PostgreSQL",
    "mysql": "MySQL", "mariadb": "MariaDB", "sqlite": "SQLite",
    "redis": "Redis", "mongo": "MongoDB", "mongoose": "MongoDB",
    "elasticsearch": "Elasticsearch", "opensearch": "OpenSearch",
    "chroma": "ChromaDB (vector)", "pinecone": "Pinecone (vector)",
    "weaviate": "Weaviate (vector)", "qdrant": "Qdrant (vector)",
    "pgvector": "pgvector", "faiss": "FAISS (vector)",
    "kafka": "Kafka", "rabbitmq": "RabbitMQ", "amqp": "RabbitMQ",
    "boto3": "AWS (boto3)", "supabase": "Supabase",
    "ollama": "Ollama", "openai": "OpenAI API", "anthropic": "Anthropic API",
    "sendgrid": "SendGrid", "mailgun": "Mailgun", "twilio": "Twilio",
}

# ---- Error-evidence regexes -----------------------------------------------------
RAISE_RE = re.compile(r"\braise\s+([A-Z][A-Za-z0-9_]*)")
THROW_RE = re.compile(r"\bthrow\s+new\s+([A-Z][A-Za-z0-9_]*)")
EXC_DEF_RE = re.compile(r"\bclass\s+([A-Z][A-Za-z0-9_]*(?:Error|Exception))\b")
LOG_ERR_RE = re.compile(r"(?:logger|log|console)\.(?:error|critical|fatal|warn)\s*\(")
TODO_RE = re.compile(r"(?:#|//|/\*|\*)\s*(TODO|FIXME|HACK|XXX|BUG)\b[:\- ]?(.{0,160})")
# Human-readable error/failure messages: match a single string literal (no newline
# inside, so we never span two adjacent strings), then keep it only if its CONTENT
# contains a failure keyword. Matching the gap between two literals was the old bug.
STRLIT_RE = re.compile(r'"([^"\n]{8,200})"' + r"|'([^'\n]{8,200})'")
ERR_KEYWORDS_RE = re.compile(
    r"error|failed|\bfail\b|cannot|could ?not|couldn|unable|invalid|missing|"
    r"not found|timeout|timed out|refused|denied|exceeded|unauthorized|"
    r"unsupported|conflict|required|already in use|does not (?:match|exist)",
    re.IGNORECASE,
)
ENV_RE = re.compile(r"(?:os\.environ(?:\.get)?\(|process\.env\.|getenv\()\s*['\"]?([A-Z][A-Z0-9_]{2,})")
PORT_RE = re.compile(r"\b(?:port|PORT)['\"]?\s*[:=]\s*['\"]?(\d{2,5})")
EXPOSE_RE = re.compile(r"^\s*EXPOSE\s+(\d{2,5})", re.MULTILINE)


def read_text(path, limit=MAX_FILE_BYTES):
    try:
        if os.path.getsize(path) > limit:
            return ""
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except OSError:
        return ""


def looks_like_message(s):
    """Keep human-readable error strings; drop import paths, CSS classes, idents."""
    if " " not in s:                       # real messages are phrases, not tokens
        return False
    if s[0] in "./@#":                      # import paths, css selectors
        return False
    if any(c in s for c in "/\\{}[]<>"):    # paths, CSS utilities, schema refs, JSX
        return False
    return True


def add_capped(target, items):
    for it in items:
        if it and it not in target and len(target) < MAX_MATCHES_PER_KIND:
            target.append(it)


MANIFEST_NAMES = {
    "package.json": "package.json",
    "pyproject.toml": "pyproject.toml",
    "requirements.txt": "requirements.txt",
    "requirements-dev.txt": "requirements-dev.txt",
    "go.mod": "go.mod", "Cargo.toml": "Cargo.toml", "pom.xml": "pom.xml",
    "build.gradle": "build.gradle", "Gemfile": "Gemfile",
    "composer.json": "composer.json", "sfdx-project.json": "sfdx-project.json",
}


def collect_manifests(root, max_depth=4):
    """Find dependency manifests anywhere in the tree (handles monorepos)."""
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        depth = dirpath[len(root):].count(os.sep)
        if depth >= max_depth:
            dirnames[:] = []
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in filenames:
            if fn in MANIFEST_NAMES:
                rel = os.path.relpath(os.path.join(dirpath, fn), root)
                found.append((rel, os.path.join(dirpath, fn), MANIFEST_NAMES[fn]))
    return found


def parse_dependencies(root):
    """Collect dependency / package names from all manifests in the tree."""
    deps = set()
    manifest_labels = []
    raw_blobs = []

    for rel, full, label in collect_manifests(root):
        manifest_labels.append(rel)
        txt = read_text(full)
        raw_blobs.append(txt.lower())
        if label == "package.json":
            try:
                data = json.loads(txt)
                for key in ("dependencies", "devDependencies", "peerDependencies"):
                    deps.update((data.get(key) or {}).keys())
            except (ValueError, AttributeError):
                pass
        elif label == "pyproject.toml":
            # Works for Poetry, PEP 621 [project] dependencies, and PDM.
            deps.update(re.findall(r'["\']([A-Za-z0-9_.\-]+)\s*[=<>~^!\[]', txt))
            deps.update(re.findall(r'^\s*([A-Za-z0-9_.\-]+)\s*=\s*["\^~]', txt, re.MULTILINE))
        elif label in ("requirements.txt", "requirements-dev.txt"):
            for line in txt.splitlines():
                m = re.match(r"\s*([A-Za-z0-9_.\-]+)", line)
                if m and not line.strip().startswith("#"):
                    deps.add(m.group(1))

    # Substring signal scan across ALL manifest text — format-agnostic, so it catches
    # frameworks/services regardless of Poetry vs PEP 621 vs pip vs go.mod, etc.
    blob = "\n".join(raw_blobs)
    for sig in list(FRAMEWORK_SIGNALS) + list(SERVICE_SIGNALS):
        if sig in EXACT_ONLY:
            continue  # these need a real exact dep name, not a substring in the blob
        if sig in blob:
            deps.add(sig)

    return {d.lower() for d in deps}, manifest_labels


EXACT_ONLY = {"next", "pg"}  # too generic as substrings (next-themes, pgvector, etc.)


def detect_from_deps(deps, mapping):
    found = {}
    for dep in deps:
        tokens = set(re.split(r"[^a-z0-9]+", dep))
        for sig, label in mapping.items():
            if sig in EXACT_ONLY:
                if dep == sig:
                    found[label] = True
            elif sig in tokens or (len(sig) >= 5 and sig in dep):
                found[label] = True
    return sorted(found)


def parse_env_examples(root, max_depth=4):
    """Extract env var KEY names from .env* files (names only, never values)."""
    keys = set()
    for dirpath, dirnames, filenames in os.walk(root):
        depth = dirpath[len(root):].count(os.sep)
        if depth >= max_depth:
            dirnames[:] = []
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and d != ".git"]
        for fn in filenames:
            if fn.startswith(".env") or fn in ("env.example", "env.sample"):
                for line in read_text(os.path.join(dirpath, fn)).splitlines():
                    m = re.match(r"\s*([A-Z][A-Z0-9_]{2,})\s*=", line)
                    if m:
                        keys.add(m.group(1))
    return keys


def scan_docker(root):
    services, ports = [], set()
    for name in ("docker-compose.yml", "docker-compose.yaml",
                 "docker-compose.dev.yml", "compose.yml", "compose.yaml"):
        p = os.path.join(root, name)
        if os.path.isfile(p):
            txt = read_text(p)
            # top-level service keys: two-space indented "name:" under services:
            in_services = False
            for line in txt.splitlines():
                if re.match(r"^services:\s*$", line):
                    in_services = True
                    continue
                if in_services:
                    if re.match(r"^\S", line):       # dedented out of services
                        in_services = False
                    else:
                        m = re.match(r"^\s{2}([A-Za-z0-9_.\-]+):\s*$", line)
                        if m:
                            services.append(m.group(1))
            for m in re.findall(r'["\s](\d{2,5}):\d{2,5}', txt):
                ports.add(m)
    df = os.path.join(root, "Dockerfile")
    has_dockerfile = os.path.isfile(df)
    if has_dockerfile:
        for m in EXPOSE_RE.findall(read_text(df)):
            ports.add(m)
    return sorted(set(services)), sorted(ports, key=lambda x: int(x)), has_dockerfile


def detect_ci(root):
    ci = []
    if os.path.isdir(os.path.join(root, ".github", "workflows")):
        wf = [f for f in os.listdir(os.path.join(root, ".github", "workflows"))
              if f.endswith((".yml", ".yaml"))]
        if wf:
            ci.append({"system": "GitHub Actions", "workflows": sorted(wf)[:20]})
    for name, label in ((".gitlab-ci.yml", "GitLab CI"),
                        ("Jenkinsfile", "Jenkins"),
                        (".circleci", "CircleCI"),
                        ("azure-pipelines.yml", "Azure Pipelines")):
        if os.path.exists(os.path.join(root, name)):
            ci.append({"system": label})
    return ci


def detect_docs(root):
    docs = []
    for name in ("README.md", "README.rst", "CONTRIBUTING.md", "SETUP.md",
                 "INSTALL.md", "TROUBLESHOOTING.md", "RUNBOOK.md", "FAQ.md"):
        if os.path.isfile(os.path.join(root, name)):
            docs.append(name)
    if os.path.isdir(os.path.join(root, "docs")):
        docs.append("docs/")
    return docs


def detect_run_commands(root):
    cmds = {}
    scripts = set()
    for rel, full, label in collect_manifests(root):
        if label == "package.json":
            try:
                s = json.loads(read_text(full)).get("scripts") or {}
                scripts.update(s.keys())
            except (ValueError, AttributeError):
                pass
    if scripts:
        cmds["npm_scripts"] = sorted(scripts)[:25]
    mk = os.path.join(root, "Makefile")
    if os.path.isfile(mk):
        targets = re.findall(r"^([A-Za-z0-9_\-]+):", read_text(mk), re.MULTILINE)
        if targets:
            cmds["make_targets"] = sorted(set(targets))[:25]
    return cmds


def grep_evidence(root, budget_bytes):
    ev = {
        "raised_exceptions": [], "thrown_errors": [], "exception_classes": [],
        "error_messages": [], "todo_markers": [], "env_vars": [], "ports": [],
    }
    spent = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in filenames:
            ext = os.path.splitext(fn)[1].lower()
            if ext not in CODE_EXT:
                continue
            full = os.path.join(dirpath, fn)
            text = read_text(full)
            if not text:
                continue
            spent += len(text)
            rel = os.path.relpath(full, root)
            add_capped(ev["raised_exceptions"], RAISE_RE.findall(text))
            add_capped(ev["thrown_errors"], THROW_RE.findall(text))
            add_capped(ev["exception_classes"], EXC_DEF_RE.findall(text))
            for m in STRLIT_RE.finditer(text):
                literal = m.group(1) or m.group(2)
                if literal and ERR_KEYWORDS_RE.search(literal) and looks_like_message(literal):
                    add_capped(ev["error_messages"], [literal.strip()])
            add_capped(ev["env_vars"], ENV_RE.findall(text))
            add_capped(ev["ports"], PORT_RE.findall(text))
            for kind, msg in TODO_RE.findall(text):
                tag = f"[{kind}] {msg.strip()} ({rel})"
                add_capped(ev["todo_markers"], [tag])
            if spent > budget_bytes:
                return ev, True
    return ev, False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo", nargs="?", default=".")
    ap.add_argument("--out", default=None)
    ap.add_argument("--max-bytes", type=int, default=8_000_000,
                    help="total source bytes to grep before stopping")
    args = ap.parse_args()

    root = os.path.abspath(args.repo)
    if not os.path.isdir(root):
        print(json.dumps({"error": f"not a directory: {root}"}))
        sys.exit(1)

    deps, manifests = parse_dependencies(root)
    services, docker_ports, has_dockerfile = scan_docker(root)
    evidence, truncated = grep_evidence(root, args.max_bytes)

    all_ports = sorted(set(evidence["ports"]) | set(docker_ports),
                       key=lambda x: int(x))

    inventory = {
        "repo_path": root,
        "repo_name": os.path.basename(root),
        "manifests": manifests,
        "languages": detect_languages(root),
        "frameworks": detect_from_deps(deps, FRAMEWORK_SIGNALS),
        "services": detect_from_deps(deps, SERVICE_SIGNALS),
        "docker": {
            "has_dockerfile": has_dockerfile,
            "compose_services": services,
        },
        "ports": all_ports,
        "ci": detect_ci(root),
        "existing_docs": detect_docs(root),
        "run_commands": detect_run_commands(root),
        "env_vars": sorted(set(evidence["env_vars"]) | parse_env_examples(root))[:MAX_MATCHES_PER_KIND],
        "evidence": {
            "raised_exceptions": sorted(set(evidence["raised_exceptions"])),
            "thrown_errors": sorted(set(evidence["thrown_errors"])),
            "exception_classes": sorted(set(evidence["exception_classes"])),
            "error_messages": evidence["error_messages"],
            "todo_markers": evidence["todo_markers"],
        },
        "scan_truncated": truncated,
    }

    out = json.dumps(inventory, indent=2)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(out)
    print(out)


def detect_languages(root):
    """Rough language presence by counting source files per extension."""
    counts = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in filenames:
            ext = os.path.splitext(fn)[1].lower()
            if ext in CODE_EXT:
                counts[ext] = counts.get(ext, 0) + 1
    label = {
        ".py": "Python", ".js": "JavaScript", ".jsx": "JavaScript (React)",
        ".ts": "TypeScript", ".tsx": "TypeScript (React)", ".go": "Go",
        ".rs": "Rust", ".java": "Java", ".rb": "Ruby", ".php": "PHP",
        ".cs": "C#", ".kt": "Kotlin", ".swift": "Swift",
        ".cls": "Apex (Salesforce)", ".trigger": "Apex Trigger (Salesforce)",
        ".c": "C", ".cpp": "C++", ".scala": "Scala",
    }
    ranked = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    return [label.get(ext, ext) for ext, _ in ranked if ext in label][:8]


if __name__ == "__main__":
    main()
