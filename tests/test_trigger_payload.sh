#!/usr/bin/env bash
# The triggering eval must show the router the WHOLE description.
#
# _match.py once sliced each description to 400 chars before sending it to the
# model. Descriptions run 700-1300 chars, so every skill whose trigger phrases
# sit late in the text was graded on words the model never saw: popquiz was cut
# mid-word ('someone says "me' | 'rge it"'), losing "LGTM" / "ship it" /
# "approve this PR" — the exact prompts its eval feeds it. Four skills reported
# recall failures that were measurement artifacts, and CI stayed red on them.
#
# Claude Code's real router sees the full description, so any truncation here
# makes the eval measure a fiction. This asserts the payload is verbatim.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

python3 - "$REPO_ROOT" <<'PY'
import sys
from pathlib import Path

repo = Path(sys.argv[1])
sys.path.insert(0, str(repo / "tests" / "triggering-evals"))
from _match import build_skill_list, load_skill_descriptions

descs = load_skill_descriptions(repo / "plugins" / "coordinated-skills" / "skills")
payload = build_skill_list(descs)

fail = 0
checks = 0


def check(label, ok):
    global fail, checks
    checks += 1
    print(f"  {'PASS' if ok else 'FAIL'}  {label}")
    if not ok:
        fail += 1


check("descriptions were extracted", bool(descs))

# Every description must appear verbatim — no slice, no ellipsis, no reflow.
missing = [n for n, d in descs.items() if d and d not in payload]
check(
    f"all {len(descs)} descriptions verbatim in the router payload"
    + (f" (truncated: {', '.join(sorted(missing))})" if missing else ""),
    not missing,
)

# The regression had a signature: the longest descriptions lost their tails.
# Guard the tail explicitly so a smaller future cut can't pass the check above
# on the short skills alone.
if descs:
    longest = max(descs, key=lambda n: len(descs[n]))
    check(
        f"tail of the longest description survives ({longest}, {len(descs[longest])} chars)",
        descs[longest][-120:] in payload,
    )

print()
print(f"  {checks} checks · {fail} fail")
sys.exit(1 if fail else 0)
PY
