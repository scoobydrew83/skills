#!/usr/bin/env bash
# build-plugin.sh — generate the self-contained Claude Marketplace package.
#
# Canonical skills live in .agents/skills/. This script copies them into the
# plugin package because Claude Marketplace packages may not follow symlinks
# outside their package directory.

set -euo pipefail

usage() {
  cat <<'EOF'
build-plugin.sh — generate or verify the Claude Marketplace package.

Usage:
  tools/build-plugin.sh
  tools/build-plugin.sh --check
  tools/build-plugin.sh --help

The generated plugins/coordinated-skills/skills/ tree must never be edited.
EOF
}

case "${1:-}" in
  --help|-h) usage; exit 0 ;;
  ''|--check) ;;
  *) usage >&2; exit 2 ;;
esac

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SOURCE_SKILLS_DIR="$REPO_ROOT/.agents/skills"
PLUGIN_NAME="coordinated-skills"
MARKETPLACE_NAME="scoobydrew-skills"
VERSION="1.3.0"
AUTHOR_NAME="scoobydrew83"
AUTHOR_URL="https://github.com/scoobydrew83"
REPO_URL="https://github.com/scoobydrew83/skills"
PLUGIN_DIR="$REPO_ROOT/plugins/$PLUGIN_NAME"
PLUGIN_SKILLS_DIR="$PLUGIN_DIR/skills"
SOURCE_COMMANDS_DIR="$REPO_ROOT/.claude/commands"
PLUGIN_COMMANDS_DIR="$PLUGIN_DIR/commands"
SOURCE_AGENTS_DIR="$REPO_ROOT/agents"
PLUGIN_AGENTS_DIR="$PLUGIN_DIR/agents"
MARKETPLACE="$REPO_ROOT/.claude-plugin/marketplace.json"
PLUGIN_MANIFEST="$PLUGIN_DIR/.claude-plugin/plugin.json"
PLUGIN_README="$PLUGIN_DIR/README.md"

[[ -d "$SOURCE_SKILLS_DIR" ]] || { echo "error: canonical skills missing: $SOURCE_SKILLS_DIR" >&2; exit 1; }

expected_marketplace=$(cat <<EOF
{
  "name": "$MARKETPLACE_NAME",
  "description": "scoobydrew83's coordinated Claude skill library.",
  "owner": { "name": "$AUTHOR_NAME", "url": "$AUTHOR_URL" },
  "plugins": [
    {
      "name": "$PLUGIN_NAME",
      "source": "./plugins/$PLUGIN_NAME",
      "description": "Portable, human-gated Conductor skills and Claude loop commands: orient, plan, execute, verify, communicate, and learn.",
      "version": "$VERSION",
      "author": { "name": "$AUTHOR_NAME", "url": "$AUTHOR_URL" }
    }
  ]
}
EOF
)
expected_manifest=$(cat <<EOF
{
  "name": "$PLUGIN_NAME",
  "description": "A portable, human-gated agent-skill library with loop routing, evidence, independent verification, and Claude adapters.",
  "version": "$VERSION",
  "author": { "name": "$AUTHOR_NAME", "url": "$AUTHOR_URL" },
  "homepage": "$REPO_URL",
  "repository": "$REPO_URL",
  "license": "MIT",
  "keywords": ["skills", "workflow", "conductor", "maker-checker", "agents", "human-gated"]
}
EOF
)
expected_readme=$(cat <<EOF
# $PLUGIN_NAME

A coordinated library of portable, human-gated agent skills. The source of truth is the
repository's .agents/skills/ tree; this self-contained copy is generated for
Claude Marketplace compatibility.

The portable loop follows Orient → Frame → Authorize → Execute → Verify →
Review → Learn. Claude-specific commands are adapters; \`AGENTS.md\` and the
canonical skills remain the cross-runtime contract.

## Claude adapter commands

The plugin bundles \`/coordinated-skills:conductor-loop\`,
\`/coordinated-skills:conductor-route\`, and
\`/coordinated-skills:conductor-doctor\`. They use the installed plugin for
their scripts and operate on Claude's current project directory.

## Install

\`\`\`
/plugin marketplace add scoobydrew83/skills
/plugin install $PLUGIN_NAME@$MARKETPLACE_NAME
\`\`\`
EOF
)

if [[ "${1:-}" == "--check" ]]; then
  fail=0
  if find "$SOURCE_SKILLS_DIR" -type d -name __pycache__ -print -quit | grep -q . \
     || find "$SOURCE_SKILLS_DIR" -name .DS_Store -print -quit | grep -q .; then
    echo "FAIL canonical skills contain generated cache or OS-junk files"; fail=1
  fi
  if find "$PLUGIN_SKILLS_DIR" -type d -name __pycache__ -print -quit | grep -q . \
     || find "$PLUGIN_SKILLS_DIR" -name .DS_Store -print -quit | grep -q .; then
    echo "FAIL generated Claude package contains cache or OS-junk files"; fail=1
  fi
  diff -qr "$SOURCE_SKILLS_DIR" "$PLUGIN_SKILLS_DIR" >/dev/null 2>&1 || { echo "FAIL generated Claude skills differ from .agents/skills"; fail=1; }
  [[ "$(find "$PLUGIN_COMMANDS_DIR" -maxdepth 1 -type f -exec basename {} \; | sort)" == "$(find "$SOURCE_COMMANDS_DIR" -maxdepth 1 -type f -name 'conductor-*.md' -exec basename {} \; | sort)" ]] || { echo "FAIL generated Claude command list differs from canonical conductor commands"; fail=1; }
  for command in conductor-loop.md conductor-route.md conductor-doctor.md; do
    cmp -s "$SOURCE_COMMANDS_DIR/$command" "$PLUGIN_COMMANDS_DIR/$command" || { echo "FAIL generated command differs: $command"; fail=1; }
  done
  for agent in conductor-builder.md conductor-verifier.md; do
    cmp -s "$SOURCE_AGENTS_DIR/$agent" "$PLUGIN_AGENTS_DIR/$agent" || { echo "FAIL generated agent differs: $agent"; fail=1; }
  done
  [[ "$(cat "$MARKETPLACE" 2>/dev/null || true)" == "$expected_marketplace" ]] || { echo "FAIL marketplace manifest is stale"; fail=1; }
  [[ "$(cat "$PLUGIN_MANIFEST" 2>/dev/null || true)" == "$expected_manifest" ]] || { echo "FAIL plugin manifest is stale"; fail=1; }
  [[ "$(cat "$PLUGIN_README" 2>/dev/null || true)" == "$expected_readme" ]] || { echo "FAIL plugin README is stale"; fail=1; }
  [[ $fail -eq 0 ]] && echo "PASS Claude plugin matches canonical skills"
  exit "$fail"
fi

rm -rf "$PLUGIN_SKILLS_DIR" "$PLUGIN_COMMANDS_DIR" "$PLUGIN_AGENTS_DIR"
mkdir -p "$PLUGIN_SKILLS_DIR" "$PLUGIN_COMMANDS_DIR" "$PLUGIN_AGENTS_DIR" "$PLUGIN_DIR/.claude-plugin" "$(dirname "$MARKETPLACE")"
tar -C "$SOURCE_SKILLS_DIR" --exclude='__pycache__' --exclude='.DS_Store' -cf - . \
  | tar -C "$PLUGIN_SKILLS_DIR" -xf -
for command in conductor-loop.md conductor-route.md conductor-doctor.md; do
  cp "$SOURCE_COMMANDS_DIR/$command" "$PLUGIN_COMMANDS_DIR/$command"
done
for agent in conductor-builder.md conductor-verifier.md; do
  cp "$SOURCE_AGENTS_DIR/$agent" "$PLUGIN_AGENTS_DIR/$agent"
done
printf '%s\n' "$expected_marketplace" > "$MARKETPLACE"
printf '%s\n' "$expected_manifest" > "$PLUGIN_MANIFEST"
printf '%s\n' "$expected_readme" > "$PLUGIN_README"
echo "generated Claude plugin from .agents/skills"
