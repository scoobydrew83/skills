#!/usr/bin/env python3
"""
verify_artifacts.py — Deterministically check whether the packages, repos, and
crates named in an AI-generated plan actually exist (and what the current
version is). This is the highest-leverage verification step for catching
hallucinations: model judgment is exactly what invents a plausible-but-fake
package name, so resolve names against the real registries instead of guessing.

Usage:
  python verify_artifacts.py --npm @modelcontextprotocol/server-sequential-thinking \
                             --pypi mem0 --pypi langchain-neo4j-memory \
                             --crates serde --repo anthropics/claude-code-action

  # or pipe a JSON manifest:
  echo '{"npm":["x"],"pypi":["y"],"crates":["z"],"repo":["o/r"]}' | python verify_artifacts.py --stdin

Exit code is non-zero if ANY artifact fails to resolve, so it can gate a workflow.
Network: only hits registry.npmjs.org, pypi.org, crates.io, api.github.com.
"""
import argparse
import json
import sys
import urllib.request
import urllib.error
import urllib.parse

TIMEOUT = 10


def _get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "reality-check/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, None
    except Exception as e:  # noqa: BLE001
        return None, str(e)


def check_npm(name):
    status, body = _get(f"https://registry.npmjs.org/{urllib.parse.quote(name, safe='@/')}")
    if status == 200 and isinstance(body, dict):
        ver = body.get("dist-tags", {}).get("latest", "?")
        return True, f"latest {ver}"
    if status == 404:
        return False, "not found on npm"
    return None, f"npm check inconclusive ({status})"


def check_pypi(name):
    status, body = _get(f"https://pypi.org/pypi/{urllib.parse.quote(name)}/json")
    if status == 200 and isinstance(body, dict):
        return True, f"latest {body.get('info', {}).get('version', '?')}"
    if status == 404:
        return False, "not found on PyPI"
    return None, f"PyPI check inconclusive ({status})"


def check_crates(name):
    status, body = _get(f"https://crates.io/api/v1/crates/{urllib.parse.quote(name)}")
    if status == 200 and isinstance(body, dict):
        return True, f"latest {body.get('crate', {}).get('max_version', '?')}"
    if status == 404:
        return False, "not found on crates.io"
    return None, f"crates check inconclusive ({status})"


def check_repo(slug):
    status, body = _get(
        f"https://api.github.com/repos/{slug}",
        headers={"User-Agent": "reality-check/1.0", "Accept": "application/vnd.github+json"},
    )
    if status == 200 and isinstance(body, dict):
        archived = " (ARCHIVED)" if body.get("archived") else ""
        return True, f"{body.get('stargazers_count', '?')}★{archived}"
    if status == 404:
        return False, "repo not found"
    if status == 403:
        return None, "rate-limited (set GITHUB_TOKEN to raise limit)"
    return None, f"repo check inconclusive ({status})"


CHECKERS = {"npm": check_npm, "pypi": check_pypi, "crates": check_crates, "repo": check_repo}
ICON = {True: "✅", False: "❌", None: "⚠️"}


def main():
    p = argparse.ArgumentParser()
    for kind in CHECKERS:
        p.add_argument(f"--{kind}", action="append", default=[], metavar="NAME")
    p.add_argument("--stdin", action="store_true", help="read a JSON manifest from stdin")
    args = p.parse_args()

    manifest = {k: list(getattr(args, k)) for k in CHECKERS}
    if args.stdin:
        data = json.loads(sys.stdin.read() or "{}")
        for k in CHECKERS:
            manifest[k].extend(data.get(k, []))

    if not any(manifest.values()):
        p.error("no artifacts given")

    any_fail = False
    rows = []
    for kind, names in manifest.items():
        for name in names:
            ok, note = CHECKERS[kind](name)
            if ok is False:
                any_fail = True
            rows.append((ICON[ok], kind, name, note))

    width = max(len(r[2]) for r in rows)
    print(f"\n{'':2} {'kind':6} {'artifact'.ljust(width)}  note")
    print("-" * (width + 24))
    for icon, kind, name, note in rows:
        print(f"{icon} {kind:6} {name.ljust(width)}  {note}")
    print()
    sys.exit(1 if any_fail else 0)


if __name__ == "__main__":
    main()
