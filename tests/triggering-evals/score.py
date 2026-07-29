#!/usr/bin/env python3
"""
score.py — score triggering-eval results.

Reads a results JSON from stdin or a path. Computes per-skill precision/recall
against expected labels and prints a human-readable table plus a summary line.

Exit codes:
  0  every skill meets TRIGGER_RECALL_MIN and TRIGGER_PRECISION_MIN
  1  at least one skill below threshold
  2  malformed input

The results file format (produced by run.sh in static mode):

{
  "mode": "static",
  "thresholds": {"recall": 0.8, "precision": 0.8},
  "skills": {
    "<skill-name>": {
      "expected_positives": N,
      "expected_negatives": M,
      "true_positives":  ["prompt..."],
      "false_negatives": ["prompt..."],
      "true_negatives":  ["prompt..."],
      "false_positives": ["prompt that wrongly matched this skill"]
    },
    ...
  }
}
"""
from __future__ import annotations

import json
import os
import sys


def fmt_pct(n: int, d: int) -> str:
    return f"{(n / d * 100):5.1f}%" if d else "  n/a "


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] not in ("-",):
        path = sys.argv[1]
        try:
            with open(path) as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"score.py: cannot read {path}: {exc}", file=sys.stderr)
            return 2
    else:
        try:
            data = json.load(sys.stdin)
        except json.JSONDecodeError as exc:
            print(f"score.py: stdin is not valid JSON: {exc}", file=sys.stderr)
            return 2

    rmin = float(os.environ.get("TRIGGER_RECALL_MIN", data.get("thresholds", {}).get("recall", 0.8)))
    pmin = float(os.environ.get("TRIGGER_PRECISION_MIN", data.get("thresholds", {}).get("precision", 0.8)))

    skills = data.get("skills", {})
    if not skills:
        print("score.py: no skills in results", file=sys.stderr)
        return 2

    print(f"mode: {data.get('mode', 'unknown')}    "
          f"thresholds: recall ≥ {rmin:.2f}, precision ≥ {pmin:.2f}")
    print()
    print(f"{'skill':36s}  {'recall':>8s}  {'precision':>10s}  "
          f"{'TP/FN':>7s}  {'FP/TN':>7s}  {'verdict':>7s}")
    print("-" * 90)

    failures = []
    for name in sorted(skills):
        s = skills[name]
        tp = len(s.get("true_positives", []))
        fn = len(s.get("false_negatives", []))
        tn = len(s.get("true_negatives", []))
        fp = len(s.get("false_positives", []))

        recall    = tp / (tp + fn) if (tp + fn) else 1.0
        precision = tp / (tp + fp) if (tp + fp) else 1.0

        verdict = "PASS" if recall >= rmin and precision >= pmin else "FAIL"
        if verdict == "FAIL":
            failures.append(name)

        print(f"{name:36s}  {recall:8.2f}  {precision:10.2f}  "
              f"{tp:>3d}/{fn:<3d}  {fp:>3d}/{tn:<3d}  {verdict:>7s}")

    print("-" * 90)

    # Routing collisions: a should_trigger prompt that the matcher handed to a
    # *different* real skill (predicted != expected and not None). The data is
    # already in false_negatives[].predicted — just surface it.
    collisions = []
    for name in sorted(skills):
        for fn in skills[name].get("false_negatives", []):
            pred = fn.get("predicted") if isinstance(fn, dict) else None
            if pred and pred != name:
                collisions.append((name, pred, fn.get("prompt", "")))
    if collisions:
        print(f"\nrouting collisions ({len(collisions)}): expected → grabbed by")
        for want, got, prompt in collisions:
            print(f"  {want:28s} → {got:28s}  {prompt[:46]}")
        print("-" * 90)

    # Ties: several descriptions cover a prompt equally well. These do not
    # necessarily fail a threshold, but they are the actionable signal about
    # which descriptions are competing for the same triggers — so they are
    # reported even when everything passes.
    ties = []
    for name in sorted(skills):
        s = skills[name]
        for bucket in ("ties", "false_negatives", "false_positives"):
            for row in s.get(bucket, []):
                if isinstance(row, dict) and row.get("tied"):
                    ties.append((name, row["tied"], row.get("prompt", "")))
    if ties:
        print(f"\nambiguous — descriptions tied for the lead ({len(ties)}):")
        seen = set()
        for name, tied, prompt in ties:
            key = (prompt, tuple(tied))
            if key in seen:
                continue
            seen.add(key)
            print(f"  {' + '.join(tied)}")
            print(f"      {prompt[:80]}")
        print("-" * 90)

    print(f"summary: {len(skills)} skill(s) scored, "
          f"{len(skills) - len(failures)} pass, {len(failures)} fail")
    if failures:
        print(f"failing: {', '.join(failures)}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
