#!/usr/bin/env python3
"""
cross_doc_scan.py — Deterministic aid for drift-check. Point it at a set of
project documents and it surfaces two things that semantic reading easily
misses:

  1. CONFLICTING METRICS — numeric thresholds with the same unit that take
     DIFFERENT values across files (e.g. ">8/10" in PLANNING vs ">9/10" in
     README). These are contradiction candidates.

  2. COPY-PASTE CONSENSUS — substantial lines that appear verbatim in 2+ files.
     Identical text across docs is duplication, not independent validation.

This is a flashlight, not a verdict: it finds candidates fast, but deciding
whether a given hit is a real contradiction or a benign restatement is still
semantic work the model does.

Usage:
  python cross_doc_scan.py PLANNING.md README.md .cursorrules system-prompt.md
"""
import re
import sys
from collections import defaultdict
from pathlib import Path

# Numeric thresholds with a unit, e.g. "<2 seconds", ">95%", "<500ms", ">9/10".
METRIC_RE = re.compile(
    r"([<>]=?|≤|≥)\s*(\d+(?:\.\d+)?)\s*"
    r"(%|ms|milliseconds?|seconds?|secs?|s\b|/\s*10|/\s*5|x\b)",
    re.IGNORECASE,
)

UNIT_CANON = {
    "%": "percent", "ms": "ms", "millisecond": "ms", "milliseconds": "ms",
    "second": "seconds", "seconds": "seconds", "sec": "seconds", "secs": "seconds",
    "s": "seconds", "/10": "out-of-10", "/ 10": "out-of-10",
    "/5": "out-of-5", "/ 5": "out-of-5", "x": "x",
}


def canon_unit(u):
    u = u.lower().replace(" ", "")
    return UNIT_CANON.get(u, u)


def norm_line(s):
    return re.sub(r"\s+", " ", s.strip().lower())


def main():
    files = sys.argv[1:]
    if not files:
        sys.exit("usage: python cross_doc_scan.py <file> <file> ...")

    # metric_bucket[unit] -> {value -> set(files)}
    metrics = defaultdict(lambda: defaultdict(set))
    # line -> set(files), plus a representative original
    lines_seen = defaultdict(set)
    line_original = {}

    for f in files:
        p = Path(f)
        if not p.exists():
            print(f"⚠️  skipped (not found): {f}")
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        name = p.name
        for raw in text.splitlines():
            for op, num, unit in METRIC_RE.findall(raw):
                metrics[canon_unit(unit)][f"{op}{num}"].add(name)
            n = norm_line(raw)
            # Only consider substantial lines; skip table rules / headers / bullets-only.
            if len(n) >= 40 and not set(n) <= set("|-: "):
                lines_seen[n].add(name)
                line_original.setdefault(n, raw.strip())

    # --- Report 1: conflicting metrics ---
    print("\n=== CONFLICTING METRICS (same unit, different values across files) ===")
    found_conflict = False
    for unit, values in sorted(metrics.items()):
        if len(values) > 1:  # more than one distinct value for this unit
            found_conflict = True
            print(f"\n  unit [{unit}] has {len(values)} distinct values:")
            for val, fs in sorted(values.items()):
                print(f"    {val:<8} in {', '.join(sorted(fs))}")
    if not found_conflict:
        print("  none — every metric unit took a single consistent value "
              "(note: consistent ≠ validated)")

    # --- Report 2: copy-paste consensus ---
    print("\n=== COPY-PASTE CONSENSUS (substantial lines verbatim in 2+ files) ===")
    dupes = {ln: fs for ln, fs in lines_seen.items() if len(fs) >= 2}
    if not dupes:
        print("  none detected")
    else:
        for ln, fs in sorted(dupes.items(), key=lambda kv: -len(kv[1])):
            snippet = line_original[ln]
            if len(snippet) > 90:
                snippet = snippet[:87] + "..."
            print(f"\n  [{len(fs)} files: {', '.join(sorted(fs))}]")
            print(f"    \"{snippet}\"")

    print("\n(These are candidates. Classify each as real contradiction, benign "
          "restatement, or unvalidated copy-paste using judgment.)\n")


if __name__ == "__main__":
    main()
