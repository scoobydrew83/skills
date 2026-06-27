#!/usr/bin/env python3
"""
analyze_project.py — Inventory a codebase so the prompt-template-generator skill
can fill a tailored prompt-template document with REAL project facts.

Pure standard library. No external dependencies.

Usage:
    python analyze_project.py <project_root> [--json] [--max-depth N]

Default prints a human-readable summary. With --json it prints a JSON object
(also written to <project_root>/.prompt-template-analysis.json) that the skill
reads to populate the template.

What it detects:
  - Project name (from manifests or directory name)
  - Tech stack / ecosystems (Node, Python, Salesforce, Go, Rust, Java, Ruby, PHP, .NET)
  - Key manifest + config files (CLAUDE.md, .cursorrules, CI, Docker, etc.)
  - Candidate "subsystems" (the immediate subdirectories of the main source root)
  - Test setup, CI provider, containerization, deploy hints
  - File-size / style conventions parsed from CLAUDE.md / .cursorrules when present
"""

import argparse
import json
import os
import re
import sys
from collections import Counter

# Directories that never carry signal and bloat the walk.
IGNORE_DIRS = {
    ".git", "node_modules", ".venv", "venv", "env", "__pycache__",
    ".mypy_cache", ".pytest_cache", "dist", "build", ".next", ".nuxt",
    "target", "out", "coverage", ".idea", ".vscode", ".gradle",
    "vendor", ".terraform", ".cache", "site-packages", ".sf", ".sfdx",
}

# Manifest file -> ecosystem label.
MANIFESTS = {
    "package.json": "Node/JavaScript",
    "pnpm-lock.yaml": "Node/JavaScript",
    "yarn.lock": "Node/JavaScript",
    "tsconfig.json": "TypeScript",
    "requirements.txt": "Python",
    "pyproject.toml": "Python",
    "setup.py": "Python",
    "Pipfile": "Python",
    "sfdx-project.json": "Salesforce",
    "go.mod": "Go",
    "Cargo.toml": "Rust",
    "pom.xml": "Java/Maven",
    "build.gradle": "Java/Gradle",
    "composer.json": "PHP",
    "Gemfile": "Ruby",
    "*.csproj": ".NET",
}

# Config / signal files worth surfacing to the model.
SIGNAL_FILES = [
    "CLAUDE.md", ".cursorrules", ".cursor/rules", "AGENTS.md",
    "README.md", "README.rst", "CONTRIBUTING.md", "ARCHITECTURE.md",
    "PLANNING.md", "TASK.md", "TASKS.md",
    ".editorconfig", ".eslintrc", ".eslintrc.json", ".eslintrc.js",
    ".prettierrc", "ruff.toml", ".ruff.toml", "Makefile",
    "Dockerfile", "docker-compose.yml", "docker-compose.yaml",
    ".env.example", "renovate.json",
]

SOURCE_ROOTS = ["src", "app", "lib", "force-app", "source", "packages"]

CODE_EXTS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".cls", ".trigger", ".apex",
    ".go", ".rs", ".java", ".rb", ".php", ".cs", ".vue", ".svelte",
    ".html", ".css", ".scss", ".sql",
}


def walk(root, max_depth):
    """Yield (dirpath, dirnames, filenames) pruned of ignored dirs and depth-limited."""
    root = os.path.abspath(root)
    for dirpath, dirnames, filenames in os.walk(root):
        rel = os.path.relpath(dirpath, root)
        depth = 0 if rel == "." else rel.count(os.sep) + 1
        if depth > max_depth:
            dirnames[:] = []
            continue
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS and not d.startswith(".git")]
        yield dirpath, dirnames, filenames


def detect_ecosystems(root, max_depth):
    found = {}
    for dirpath, _dirs, files in walk(root, max_depth):
        for f in files:
            if f in MANIFESTS:
                found.setdefault(MANIFESTS[f], []).append(
                    os.path.relpath(os.path.join(dirpath, f), root))
            elif f.endswith(".csproj"):
                found.setdefault(".NET", []).append(
                    os.path.relpath(os.path.join(dirpath, f), root))
    return found


def find_signal_files(root):
    out = []
    for sf in SIGNAL_FILES:
        p = os.path.join(root, sf)
        if os.path.exists(p):
            out.append(sf)
    # CI workflows
    wf_dir = os.path.join(root, ".github", "workflows")
    if os.path.isdir(wf_dir):
        wfs = [f for f in os.listdir(wf_dir) if f.endswith((".yml", ".yaml"))]
        if wfs:
            out.append(".github/workflows/ (" + ", ".join(sorted(wfs)[:6]) + ")")
    for ci in [".gitlab-ci.yml", "azure-pipelines.yml", ".circleci/config.yml",
               "Jenkinsfile", "bitbucket-pipelines.yml"]:
        if os.path.exists(os.path.join(root, ci)):
            out.append(ci)
    return out


def project_name(root, ecosystems):
    # package.json name
    pkg = os.path.join(root, "package.json")
    if os.path.exists(pkg):
        try:
            with open(pkg, encoding="utf-8") as fh:
                name = json.load(fh).get("name")
                if name:
                    return name
        except Exception:
            pass
    # sfdx-project.json
    sfdx = os.path.join(root, "sfdx-project.json")
    if os.path.exists(sfdx):
        try:
            with open(sfdx, encoding="utf-8") as fh:
                data = json.load(fh)
                pkgs = data.get("packageDirectories", [])
                for p in pkgs:
                    if p.get("package"):
                        return p["package"]
        except Exception:
            pass
    # pyproject
    pyproj = os.path.join(root, "pyproject.toml")
    if os.path.exists(pyproj):
        try:
            with open(pyproj, encoding="utf-8") as fh:
                m = re.search(r'(?m)^\s*name\s*=\s*["\']([^"\']+)["\']', fh.read())
                if m:
                    return m.group(1)
        except Exception:
            pass
    return os.path.basename(os.path.abspath(root))


def find_source_root(root):
    for sr in SOURCE_ROOTS:
        p = os.path.join(root, sr)
        if os.path.isdir(p):
            return sr
    return None


def detect_subsystems(root):
    """Subsystems = immediate subdirs of the main source root (or top-level if none)."""
    sr = find_source_root(root)
    base = os.path.join(root, sr) if sr else root
    # Salesforce: dig to force-app/main/default
    sf_default = os.path.join(root, "force-app", "main", "default")
    if os.path.isdir(sf_default):
        base = sf_default
        sr = "force-app/main/default"
    subs = []
    try:
        for d in sorted(os.listdir(base)):
            full = os.path.join(base, d)
            if os.path.isdir(full) and d not in IGNORE_DIRS and not d.startswith("."):
                # count code files inside for signal
                n = 0
                for _dp, _dn, fns in os.walk(full):
                    _dn[:] = [x for x in _dn if x not in IGNORE_DIRS]
                    n += sum(1 for f in fns if os.path.splitext(f)[1] in CODE_EXTS)
                subs.append({"name": d, "path": os.path.join(sr, d) if sr else d,
                             "code_files": n})
    except Exception:
        pass
    subs.sort(key=lambda s: s["code_files"], reverse=True)
    return sr, subs


def detect_tests(root, max_depth):
    test_dirs, test_files = [], 0
    patterns = ("test", "tests", "__tests__", "spec")
    for dirpath, dirs, files in walk(root, max_depth):
        base = os.path.basename(dirpath).lower()
        if base in patterns:
            test_dirs.append(os.path.relpath(dirpath, root))
        for f in files:
            fl = f.lower()
            if (fl.startswith("test_") or fl.endswith(("_test.py", ".test.ts",
                ".test.tsx", ".test.js", ".spec.ts", ".spec.js", ".test.jsx"))):
                test_files += 1
    return sorted(set(test_dirs))[:10], test_files


def language_histogram(root, max_depth):
    c = Counter()
    for _dp, _dn, files in walk(root, max_depth):
        for f in files:
            ext = os.path.splitext(f)[1]
            if ext in CODE_EXTS:
                c[ext] += 1
    return dict(c.most_common(12))


def parse_conventions(root):
    """Pull explicit conventions out of CLAUDE.md / .cursorrules if present."""
    conv = {"source_files": [], "line_limit": None, "notes": []}
    for fname in ["CLAUDE.md", ".cursorrules", "AGENTS.md"]:
        p = os.path.join(root, fname)
        if not os.path.exists(p):
            continue
        try:
            with open(p, encoding="utf-8", errors="ignore") as fh:
                text = fh.read()
        except Exception:
            continue
        conv["source_files"].append(fname)
        m = re.search(r'(\d{2,4})\s*[- ]?line', text)
        if m and conv["line_limit"] is None:
            conv["line_limit"] = int(m.group(1))
    return conv


def directory_tree(root, max_depth=2):
    lines = []
    rootabs = os.path.abspath(root)
    for dirpath, dirnames, _files in walk(root, max_depth):
        rel = os.path.relpath(dirpath, rootabs)
        depth = 0 if rel == "." else rel.count(os.sep) + 1
        dirnames.sort()
        if rel != ".":
            lines.append("  " * (depth - 1) + os.path.basename(dirpath) + "/")
    return lines[:60]


def analyze(root, max_depth):
    root = os.path.abspath(root)
    ecosystems = detect_ecosystems(root, max_depth)
    sr, subs = detect_subsystems(root)
    test_dirs, test_files = detect_tests(root, max_depth)
    return {
        "project_name": project_name(root, ecosystems),
        "root": root,
        "ecosystems": ecosystems,
        "primary_ecosystem": (sorted(ecosystems, key=lambda k: len(ecosystems[k]),
                              reverse=True)[0] if ecosystems else "Unknown"),
        "signal_files": find_signal_files(root),
        "source_root": sr,
        "subsystems": subs,
        "test_dirs": test_dirs,
        "test_file_count": test_files,
        "language_histogram": language_histogram(root, max_depth),
        "conventions": parse_conventions(root),
        "containerized": any("Dockerfile" in s or "docker-compose" in s
                             for s in find_signal_files(root)),
        "directory_tree": directory_tree(root, min(max_depth, 2)),
    }


def print_human(a):
    print(f"PROJECT: {a['project_name']}")
    print(f"ROOT:    {a['root']}")
    print(f"STACK:   {a['primary_ecosystem']}  (all: {', '.join(a['ecosystems']) or 'none detected'})")
    print(f"SOURCE:  {a['source_root'] or '(top-level)'}")
    print()
    print("SUBSYSTEMS (candidate sections):")
    for s in a["subsystems"][:15]:
        print(f"  - {s['name']:<24} {s['path']}  ({s['code_files']} code files)")
    if not a["subsystems"]:
        print("  (none detected — treat the whole repo as one subsystem)")
    print()
    print(f"TESTS:   {a['test_file_count']} test files in {len(a['test_dirs'])} dir(s): "
          f"{', '.join(a['test_dirs']) or 'none'}")
    print(f"CONFIG:  {', '.join(a['signal_files']) or 'none'}")
    print(f"DOCKER:  {'yes' if a['containerized'] else 'no'}")
    if a["conventions"]["line_limit"]:
        print(f"CONV:    ~{a['conventions']['line_limit']}-line file limit "
              f"(from {', '.join(a['conventions']['source_files'])})")
    print()
    print("LANGUAGES:", ", ".join(f"{k}:{v}" for k, v in a["language_histogram"].items()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--max-depth", type=int, default=6)
    args = ap.parse_args()
    if not os.path.isdir(args.root):
        print(f"error: not a directory: {args.root}", file=sys.stderr)
        sys.exit(1)
    a = analyze(args.root, args.max_depth)
    out_path = os.path.join(args.root, ".prompt-template-analysis.json")
    try:
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(a, fh, indent=2)
    except Exception:
        out_path = None
    if args.json:
        print(json.dumps(a, indent=2))
    else:
        print_human(a)
        if out_path:
            print(f"\n(JSON inventory written to {out_path})")


if __name__ == "__main__":
    main()
