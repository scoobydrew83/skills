#!/usr/bin/env bash
# Every active skill needs deterministic routing fixtures; fixture files may not
# silently outlive their skill after a rename or removal.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

python3 - "$REPO_ROOT" <<'PY'
import json
import pathlib
import sys

repo = pathlib.Path(sys.argv[1])
skills = repo / ".agents" / "skills"
prompts = repo / "tests" / "triggering-evals" / "prompts"
active = set()
for skill_md in skills.glob("*/SKILL.md"):
    if "DEPRECATED" not in skill_md.read_text(encoding="utf-8").split("---", 2)[1]:
        active.add(skill_md.parent.name)

fixture_names = {p.stem for p in prompts.glob("*.json")}
missing = sorted(active - fixture_names)
orphaned = sorted(fixture_names - {p.parent.name for p in skills.glob("*/SKILL.md")})
bad = []
for name in sorted(active & fixture_names):
    data = json.loads((prompts / f"{name}.json").read_text(encoding="utf-8"))
    if len(data.get("should_trigger", [])) < 5 or len(data.get("should_not_trigger", [])) < 3:
        bad.append(name)

if missing or orphaned or bad:
    if missing: print("missing fixtures:", ", ".join(missing))
    if orphaned: print("orphaned fixtures:", ", ".join(orphaned))
    if bad: print("underspecified fixtures:", ", ".join(bad))
    raise SystemExit(1)
print(f"  PASS  routing fixtures cover {len(active)} active skills")
PY
