#!/usr/bin/env bash
# PreToolUse hook: block hand edits to generated output.
#
# plugins/coordinated-skills/ is rebuilt from .agents/skills/ by
# tools/build-plugin.sh, so a direct edit is silently lost on the next build
# (or, worse, makes the package drift from source). Exit 2 tells Claude Code to
# refuse the tool call and shows the message to the model.
set -uo pipefail

input="$(cat)"
path="$(printf '%s' "$input" | python3 -c 'import json,sys
try:
    d=json.load(sys.stdin).get("tool_input",{})
    print(d.get("file_path") or d.get("notebook_path") or "")
except Exception:
    print("")')"

case "$path" in
  */plugins/coordinated-skills/*|plugins/coordinated-skills/*)
    echo "Blocked: $path is generated. Edit the canonical skill under .agents/skills/ and run 'bash tools/build-plugin.sh'." >&2
    exit 2
    ;;
esac
exit 0
