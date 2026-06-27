#!/usr/bin/env bash
# build-plugin.sh — (re)generate the plugin + marketplace manifests.
#
# The skill directories under plugins/coordinated-skills/skills/<name>/ are the
# source of truth and are edited directly. This script only regenerates the
# GENERATED manifest files around them:
#
#   .claude-plugin/marketplace.json                 # marketplace manifest (repo root)
#   plugins/<PLUGIN>/.claude-plugin/plugin.json     # plugin manifest
#   plugins/<PLUGIN>/README.md                      # plugin readme
#
# It never touches the skill directories themselves.
#
# Usage:
#   tools/build-plugin.sh
#   tools/build-plugin.sh --help
#
# Re-run after changing identity (author/version/name) below.

set -euo pipefail

usage() { sed -n '2,19p' "$0" | sed 's/^# \{0,1\}//'; }
if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then usage; exit 0; fi

# ---- identity (kebab-case; user-facing in the install command) -------------------------------
MARKETPLACE_NAME="scoobydrew-skills"
PLUGIN_NAME="coordinated-skills"
VERSION="1.0.0"
AUTHOR_NAME="scoobydrew83"
AUTHOR_URL="https://github.com/scoobydrew83"
REPO_URL="https://github.com/scoobydrew83/skills"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PLUGIN_DIR="$REPO_ROOT/plugins/$PLUGIN_NAME"
SKILLS_DIR="$PLUGIN_DIR/skills"

mkdir -p "$SKILLS_DIR" "$PLUGIN_DIR/.claude-plugin" "$REPO_ROOT/.claude-plugin"

# ---- sanity: every skill dir has a SKILL.md --------------------------------------------------
count=0
for d in "$SKILLS_DIR"/*/; do
  [[ -d "$d" ]] || continue
  name="$(basename "$d")"
  [[ -f "$d/SKILL.md" ]] || { echo "error: $name missing SKILL.md" >&2; exit 1; }
  count=$((count + 1))
done
echo "found $count skill(s) in $SKILLS_DIR"

# ---- plugin.json -----------------------------------------------------------------------------
cat > "$PLUGIN_DIR/.claude-plugin/plugin.json" <<JSON
{
  "name": "$PLUGIN_NAME",
  "description": "A coordinated library of Claude skills with explicit phase/handoff routing, shared-state conventions, and a maker/checker loop. Covers intake, execution, verification, communication, and session bookending.",
  "version": "$VERSION",
  "author": { "name": "$AUTHOR_NAME", "url": "$AUTHOR_URL" },
  "homepage": "$REPO_URL",
  "repository": "$REPO_URL",
  "license": "MIT",
  "keywords": ["skills", "workflow", "conductor", "maker-checker", "agents"]
}
JSON

# ---- plugin README ---------------------------------------------------------------------------
cat > "$PLUGIN_DIR/README.md" <<MD
# $PLUGIN_NAME

A coordinated library of Claude skills. Each skill declares its lifecycle phase
and the siblings it hands off to, so the set composes into a workflow rather than
a pile of independent prompts.

The skills under \`skills/\` are the source of truth. See the
[repository]($REPO_URL) for the conventions contract and tooling.

## Install

\`\`\`
/plugin marketplace add scoobydrew83/skills
/plugin install $PLUGIN_NAME@$MARKETPLACE_NAME
\`\`\`
MD

# ---- marketplace.json ------------------------------------------------------------------------
cat > "$REPO_ROOT/.claude-plugin/marketplace.json" <<JSON
{
  "name": "$MARKETPLACE_NAME",
  "description": "scoobydrew83's coordinated Claude skill library.",
  "owner": { "name": "$AUTHOR_NAME", "url": "$AUTHOR_URL" },
  "plugins": [
    {
      "name": "$PLUGIN_NAME",
      "source": "./plugins/$PLUGIN_NAME",
      "description": "Coordinated skill library: intake, execute, verify, communicate, bookend.",
      "version": "$VERSION",
      "author": { "name": "$AUTHOR_NAME", "url": "$AUTHOR_URL" }
    }
  ]
}
JSON

echo "wrote: $REPO_ROOT/.claude-plugin/marketplace.json"
echo "wrote: $PLUGIN_DIR/.claude-plugin/plugin.json"
echo "done. validate with: claude plugin validate $PLUGIN_DIR && claude plugin validate $REPO_ROOT"
