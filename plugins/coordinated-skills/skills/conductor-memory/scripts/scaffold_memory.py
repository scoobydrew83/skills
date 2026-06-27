#!/usr/bin/env python3
"""
scaffold_memory.py - Lay down a memory pack's directory and the boilerplate
files that don't change between runs (integration.py, verification checklist,
maintenance plan). The synthesized, content-bearing files (summary, patterns,
context, seed JSON/YAML, MEMORY_INDEX) are authored by Claude afterward, using
references/templates.md as the structure guide.

Run this FIRST, before authoring. It prints JSON describing the pack: the
resolved directory, the project name, and the exact filenames Claude still needs
to create. Read that output and author those files into the pack directory.

Usage:
    python scaffold_memory.py --output <dir> [--config config.json]
        [--project conductor] [--project-title Conductor]
        [--session-label "v2 planning"] [--vault ~/your-vault]
        [--memory-subdir Conductor/memory] [--claude-md ~/your-vault/Conductor/CLAUDE.md]
"""

import argparse
import json
import os
import re
from datetime import datetime
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATES = SKILL_DIR / "assets" / "templates"

DEFAULT_CONFIG = {
    "project_name": "conductor",
    "project_title": "",
    "session_label": "",
    "vault_path": "~/your-vault",
    "memory_subdir": "Conductor/memory",
    "claude_code_memory": "",
    "session_date": "auto",
}

# Files Claude authors after scaffolding (content-bearing, not boilerplate).
def authored_files(p):
    return [
        "MEMORY_INDEX.md",
        f"{p}_memory_conversation_summary.md",
        f"{p}_memory_artifacts_index.md",
        f"{p}_memory_communication_style.md",
        f"{p}_memory_project_context.md",
        f"{p}_memory_seed_data.json",
        f"{p}_memory_personality.yaml",
    ]


def load_config(args):
    cfg = dict(DEFAULT_CONFIG)
    if args.config:
        cfg.update(json.loads(Path(args.config).expanduser().read_text()))
    # CLI overrides win over the config file.
    overrides = {
        "project_name": args.project,
        "project_title": args.project_title,
        "session_label": args.session_label,
        "vault_path": args.vault,
        "memory_subdir": args.memory_subdir,
        "claude_code_memory": args.claude_md,
    }
    for k, v in overrides.items():
        if v is not None:
            cfg[k] = v
    if cfg.get("session_date", "auto") in ("auto", "", None):
        cfg["session_date"] = datetime.now().strftime("%Y-%m-%d")
    if not cfg.get("project_title"):
        cfg["project_title"] = cfg["project_name"].replace("-", " ").replace("_", " ").title()
    return cfg


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def substitute(text, cfg, pack_dirname):
    tokens = {
        "{PROJECT_NAME}": cfg["project_name"],
        "{PROJECT_TITLE}": cfg["project_title"],
        "{SESSION_LABEL}": cfg.get("session_label", "") or pack_dirname,
        "{VAULT_PATH}": cfg["vault_path"],
        "{MEMORY_SUBDIR}": cfg["memory_subdir"],
        "{CLAUDE_CODE_MEMORY}": cfg.get("claude_code_memory", "") or "",
        "{SESSION_DATE}": cfg["session_date"],
        "{PACK_DIRNAME}": pack_dirname,
    }
    for k, v in tokens.items():
        text = text.replace(k, v)
    return text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True, help="Directory the pack folder is created in.")
    ap.add_argument("--config", help="Optional JSON config (see assets/config.example.json).")
    ap.add_argument("--project")
    ap.add_argument("--project-title", dest="project_title")
    ap.add_argument("--session-label", dest="session_label")
    ap.add_argument("--vault")
    ap.add_argument("--memory-subdir", dest="memory_subdir")
    ap.add_argument("--claude-md", dest="claude_md")
    args = ap.parse_args()

    cfg = load_config(args)
    p = cfg["project_name"]
    date_compact = cfg["session_date"].replace("-", "")
    label = slugify(cfg.get("session_label", "") or "")
    pack_dirname = f"{p}_memory_{date_compact}" + (f"_{label}" if label else "")

    out = Path(args.output).expanduser() / pack_dirname
    out.mkdir(parents=True, exist_ok=True)

    boilerplate = {
        "integration.py.tmpl": "integration.py",
        "verification.md.tmpl": f"{p}_memory_verification.md",
        "maintenance.md.tmpl": f"{p}_memory_maintenance.md",
    }
    written = []
    for tmpl, dest in boilerplate.items():
        text = (TEMPLATES / tmpl).read_text()
        (out / dest).write_text(substitute(text, cfg, pack_dirname))
        written.append(dest)

    result = {
        "pack_dir": str(out),
        "pack_dirname": pack_dirname,
        "project_name": p,
        "project_title": cfg["project_title"],
        "session_date": cfg["session_date"],
        "boilerplate_written": sorted(written),
        "files_to_author": authored_files(p),
        "next_step": "Author the files_to_author into pack_dir using references/templates.md, then run validate_memory.py --dir pack_dir.",
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
