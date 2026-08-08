#!/usr/bin/env python3
"""
_match.py — static & LLM matchers for the triggering-eval harness.

Static mode:
  For every skill we extract a keyword set from its SKILL.md description
  (stopword-filtered, lowercased, length ≥ 3). For each prompt we compute an
  overlap score against every skill's keyword set; the skill with the highest
  score is the "predicted" skill for that prompt. A prompt is recorded as
  "triggering skill X" iff X is the top scorer AND the score clears
  STATIC_MATCH_MIN (default 0.05 — Jaccard-style; tiny because descriptions
  are long and prompts are short).

LLM mode:
  For each prompt, send a tiny classification request to Claude haiku via the
  REST API (anthropic.com) and parse the returned skill name.

Both modes emit the same results JSON shape consumed by score.py.

Usage:
  _match.py --mode static  --prompts-dir <dir> --skills-root <root> [--skill <name>]
  _match.py --mode llm     --prompts-dir <dir> --skills-root <root> [--skill <name>]

The skills-root must contain `<skill>.skill` archives (zip files containing
SKILL.md). We extract SKILL.md from each archive with the stdlib zipfile module
so we don't depend on the unzip CLI.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import urllib.request
import zipfile
from pathlib import Path

# --- description extraction ------------------------------------------------- #

STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "then", "else", "for", "to",
    "of", "in", "on", "at", "by", "with", "from", "as", "is", "are", "was",
    "were", "be", "been", "being", "this", "that", "these", "those", "it",
    "its", "they", "them", "their", "there", "here", "what", "which", "who",
    "whom", "whose", "when", "where", "why", "how", "do", "does", "did",
    "done", "doing", "have", "has", "had", "having", "you", "your", "yours",
    "me", "my", "mine", "we", "us", "our", "ours", "i", "so", "not", "no",
    "any", "all", "some", "use", "uses", "used", "using", "user", "users",
    "skill", "skills", "trigger", "triggers", "triggering", "claude", "ai",
    "want", "wants", "wanted", "wanting", "need", "needs", "needed",
    "even", "also", "just", "ever", "never", "always", "very", "really",
    "into", "onto", "than", "much", "many", "more", "most", "less", "least",
    "etc", "eg", "ie", "vs", "via", "per", "out", "up", "down", "off", "over",
    "under", "across", "between", "through", "about", "against", "without",
    "within", "around", "before", "after", "still", "yet", "thing", "things",
    "stuff", "something", "anything", "everything", "nothing", "one", "two",
    "three", "first", "second", "next", "last", "new", "old", "good", "bad",
    "will", "would", "could", "should", "shall", "may", "might", "must",
    "can", "cannot", "cant", "wont", "doesnt", "didnt", "isnt", "arent",
    "way", "ways", "make", "makes", "made", "making", "give", "gives", "gave",
    "get", "gets", "got", "say", "says", "said", "asks", "ask", "asked",
    "says", "tell", "tells", "told", "talk", "talks", "talked",
    "real", "really", "actual", "actually", "kind", "type", "types",
    "lot", "lots", "case", "cases", "step", "steps", "part", "parts",
    "set", "sets", "list", "lists", "people", "person", "someone", "anyone",
    "whenever", "wherever", "whatever", "whoever", "however",
    # Generic doing-verbs. Same category as make/give/get/say above, and the
    # reason hemlock ("should I keep going or kill it") outscored
    # session-continuity ("remember the thing I'm working on") on the filler
    # `keep`/`going`/`let` while the decisive `remember`/`working` sat unused.
    # IDF cannot catch these: they appear in few enough descriptions to look
    # rare, and rare is not the same as meaningful for function words.
    "keep", "keeps", "keeping", "kept", "go", "goes", "going", "gone", "went",
    "let", "lets", "look", "looks", "looking", "looked", "come", "comes",
    "coming", "take", "takes", "taking", "taken", "put", "puts", "fine",
}

WORD_RE = re.compile(r"[a-zA-Z][a-zA-Z\-]+")

# Descriptions deliberately carry disambiguation clauses — "Do NOT use for X",
# "Distinct from Y", "rather than Z". The examples inside them belong to a
# SIBLING skill, so counting them as evidence FOR this skill inverts the signal
# and penalises exactly the descriptions that route best. agent-orchestration
# ends with `Do NOT trigger for single-stage asks ("fix this bug", "write this
# function")` and was being matched by those very prompts.
#
# Truncate each sentence at its first negative marker rather than dropping the
# whole sentence: "This is for VERIFYING an EXISTING plan, not for choosing
# between options" has a positive first half worth keeping.
NEGATIVE_MARKERS = re.compile(
    r"\b(?:do\s+not\s+(?:use|trigger|reach)"
    r"|don'?t\s+(?:use|trigger|reach)"
    r"|never\s+(?:use|trigger)"
    r"|not\s+for\b"
    r"|distinct\s+from"
    r"|rather\s+than"
    r"|instead\s+of"
    r"|supersed(?:es|ed)"
    r"|use\s+\S+\s+instead)",
    re.IGNORECASE,
)

SENTENCE_SPLIT = re.compile(r"(?<=[.;])\s+")


def strip_negative_guidance(text: str) -> str:
    """Drop the 'what this is NOT for' half of each sentence."""
    kept = []
    for sentence in SENTENCE_SPLIT.split(text):
        m = NEGATIVE_MARKERS.search(sentence)
        kept.append(sentence[: m.start()] if m else sentence)
    return " ".join(kept)


def tokenize(text: str) -> set[str]:
    """Lowercase, split on non-letters, drop stopwords + short tokens."""
    out = set()
    for m in WORD_RE.findall(text.lower()):
        tok = m.strip("-")
        if len(tok) >= 3 and tok not in STOPWORDS:
            out.add(tok)
    return out


def extract_description(skill_md_text: str) -> str:
    """Pull the `description:` value (YAML scalar, possibly multi-line) from a
    SKILL.md frontmatter block. Tolerant of `>-` folded style."""
    if not skill_md_text.startswith("---"):
        return ""
    end = skill_md_text.find("\n---", 3)
    if end == -1:
        return ""
    fm = skill_md_text[3:end]
    lines = fm.splitlines()
    desc_parts: list[str] = []
    capturing = False
    for line in lines:
        if line.startswith("description:"):
            capturing = True
            rest = line.split(":", 1)[1].strip()
            # strip YAML folded indicators
            rest = rest.lstrip(">").lstrip("-").lstrip("|").strip()
            if rest:
                desc_parts.append(rest)
            continue
        if capturing:
            if line.startswith((" ", "\t")):
                desc_parts.append(line.strip())
            else:
                break
    return " ".join(desc_parts)


def load_skill_descriptions(skills_root: Path) -> dict[str, str]:
    """Find every skill directory under skills_root, return {name: description}.

    Each skill lives at skills_root/<name>/SKILL.md (the source of truth).
    """
    descs: dict[str, str] = {}
    for skill_md in sorted(skills_root.glob("*/SKILL.md")):
        name = skill_md.parent.name
        try:
            md = skill_md.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            print(f"_match.py: skipping {skill_md}: {exc}", file=sys.stderr)
            continue
        desc = extract_description(md)
        # Skip tombstones — they explicitly tell Claude not to trigger.
        if "DEPRECATED" in desc and "Do NOT trigger" in desc:
            continue
        descs[name] = desc
    return descs


def keyword_source(desc: str) -> str:
    """The part of a description that is evidence FOR the skill."""
    return strip_negative_guidance(desc)


# --- static matcher --------------------------------------------------------- #

def build_idf(skill_tokens: dict[str, set[str]]) -> tuple[dict[str, float], float]:
    """Inverse document frequency over the skill corpus.

    Raw overlap counts every shared word equally, so generic doing-verbs that
    appear in most descriptions ("keep", "going", "run", "write") outvote the
    rare words that actually identify a skill. hemlock beat session-continuity
    on `keep`/`going`/`let` while session-continuity held the decisive
    `remember`/`working`. Weighting by IDF makes a word worth what it
    discriminates — and unlike a hand-curated stopword list, it stays correct
    as skills are added.

    Returns (idf, default) where default is the weight for a token seen in no
    description at all (maximally rare, so maximally specific).
    """
    n = len(skill_tokens) or 1
    df: dict[str, int] = {}
    for toks in skill_tokens.values():
        for t in toks:
            df[t] = df.get(t, 0) + 1
    idf = {t: math.log((n + 1) / (c + 1)) for t, c in df.items()}
    return idf, math.log(n + 1)


def static_score(prompt_tokens: set[str], skill_tokens: set[str],
                 idf: dict[str, float], default_idf: float) -> float:
    """IDF-weighted share of the prompt's meaning this description covers."""
    if not prompt_tokens:
        return 0.0
    total = sum(idf.get(t, default_idf) for t in prompt_tokens)
    if not total:
        return 0.0
    hit = sum(idf.get(t, default_idf) for t in prompt_tokens & skill_tokens)
    return hit / total


# Scores this close are the same score; float noise must not decide routing.
TIE_EPSILON = 1e-9


def static_predict(prompt: str, skill_tokens: dict[str, set[str]],
                   min_score: float, idf: dict[str, float],
                   default_idf: float) -> tuple[str | None, dict[str, float], list[str]]:
    """Return (best_skill, all_scores, tied).

    best_skill is None when no skill clears min_score, OR when several skills
    tie for the lead — a tie means the descriptions do not discriminate, and
    silently handing the win to whichever sorts first (the old `max()`
    behaviour) invents a false negative for one skill and a false "grabbed by"
    for another. `tied` names them so the ambiguity is reported, not buried.
    """
    ptoks = tokenize(prompt)
    scores = {s: static_score(ptoks, toks, idf, default_idf)
              for s, toks in skill_tokens.items()}
    if not scores:
        return None, scores, []
    best_score = max(scores.values())
    if best_score < min_score:
        return None, scores, []
    tied = sorted(s for s, v in scores.items() if abs(v - best_score) <= TIE_EPSILON)
    if len(tied) > 1:
        return None, scores, tied
    return tied[0], scores, []


# --- LLM matcher ------------------------------------------------------------ #

LLM_SYSTEM = (
    "You are a skill-routing classifier. Given a user prompt and a numbered "
    "list of skill descriptions, reply with ONLY the name of the single best-"
    "matching skill, or the word NONE if no skill should be invoked. Output "
    "nothing else."
)


def build_skill_list(descriptions: dict[str, str]) -> str:
    """The routing menu shown to the LLM. Descriptions are never truncated.

    Claude Code's real router sees the whole `description:` field, so slicing it
    here measured a fiction. At the old [:400] cut, popquiz was severed mid-word
    ('someone says "me' | 'rge it"') and every trigger phrase the eval then
    tested it on — "LGTM", "ship it", "approve this PR" — sat past the cut. Four
    skills scored recall failures on text the model was never shown. Anything
    that shortens a description here re-creates that bug; test_trigger_payload.sh
    guards it.
    """
    return "\n".join(f"- {name}: {desc}" for name, desc in descriptions.items())


def llm_predict(prompt: str, descriptions: dict[str, str],
                api_key: str, model: str) -> str | None:
    """Ask Claude haiku which skill to invoke. Returns the skill name or None."""
    skill_list = build_skill_list(descriptions)
    user = (
        f"User prompt:\n{prompt}\n\n"
        f"Available skills:\n{skill_list}\n\n"
        f"Reply with one skill name from the list above, or NONE."
    )
    body = json.dumps({
        "model": model,
        "max_tokens": 32,
        # Routing is a classification, so resampling it is pure noise. Without
        # this the API default (1.0) applied: two CI runs on identical code
        # scored session-bookend 0.80 then 0.60 and flipped the build red, and
        # with 5 prompts per skill one resampled answer moves recall by a whole
        # 0.20 — straight through the 0.80 gate. Determinism isn't perfect at
        # temperature 0, but a gate that fails on a coin toss gates nothing.
        # NOTE: sampling params are rejected on Opus 4.7+/Opus 5/Sonnet 5/Fable
        # 5. TRIGGER_LLM_MODEL must name a model that accepts them.
        "temperature": 0,
        "system": LLM_SYSTEM,
        "messages": [{"role": "user", "content": user}],
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=body,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = json.load(resp)
    except Exception as exc:
        print(f"_match.py: LLM call failed: {exc}", file=sys.stderr)
        return None
    try:
        text = payload["content"][0]["text"].strip()
    except (KeyError, IndexError, TypeError):
        return None
    text = text.strip().strip(".").strip()
    if text.upper() == "NONE":
        return None
    # the model may wrap in backticks or add explanation despite instructions
    for tok in re.split(r"[\s,;`'\"]+", text):
        if tok in descriptions:
            return tok
    return None


# --- runner ----------------------------------------------------------------- #

def load_prompt_files(prompts_dir: Path, only_skill: str | None) -> dict[str, dict]:
    out: dict[str, dict] = {}
    pattern = f"{only_skill}.json" if only_skill else "*.json"
    for f in sorted(prompts_dir.glob(pattern)):
        try:
            with open(f) as fh:
                doc = json.load(fh)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"_match.py: skipping {f}: {exc}", file=sys.stderr)
            continue
        name = doc.get("skill") or f.stem
        out[name] = doc
    return out


def run(mode: str, prompts_dir: Path, skills_root: Path,
        only_skill: str | None) -> dict:
    descs = load_skill_descriptions(skills_root)
    if not descs:
        print("_match.py: no skill descriptions found", file=sys.stderr)
        sys.exit(2)

    # Positive evidence only — a skill's "Do NOT use for X" clause describes a
    # sibling's territory, not its own.
    skill_tokens = {s: tokenize(keyword_source(d)) for s, d in descs.items()}
    idf, default_idf = build_idf(skill_tokens)
    prompt_docs = load_prompt_files(prompts_dir, only_skill)
    if not prompt_docs:
        print(f"_match.py: no prompt files matched (only_skill={only_skill})", file=sys.stderr)
        sys.exit(2)

    min_static = float(os.environ.get("STATIC_MATCH_MIN", "0.05"))

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    model = os.environ.get("TRIGGER_LLM_MODEL", "claude-haiku-4-5")
    if mode == "llm" and not api_key:
        print("_match.py: ANTHROPIC_API_KEY required for --mode llm", file=sys.stderr)
        sys.exit(2)

    results: dict = {
        "mode": mode,
        "thresholds": {
            "recall": float(os.environ.get("TRIGGER_RECALL_MIN", "0.8")),
            "precision": float(os.environ.get("TRIGGER_PRECISION_MIN", "0.8")),
        },
        "static_match_min": min_static if mode == "static" else None,
        "model": model if mode == "llm" else None,
        "skills": {},
    }

    # Initialise an entry for every skill mentioned in a prompt file.
    for skill_name in prompt_docs:
        results["skills"].setdefault(skill_name, {
            "expected_positives": 0,
            "expected_negatives": 0,
            "true_positives": [],
            "false_negatives": [],
            "true_negatives": [],
            "false_positives": [],
            "ties": [],
        })

    def predict(p: str) -> tuple[str | None, list[str]]:
        if mode == "static":
            best, _, tied = static_predict(p, skill_tokens, min_static,
                                           idf, default_idf)
            return best, tied
        return llm_predict(p, descs, api_key, model), []

    # A tie means several descriptions cover the prompt equally well. Scored
    # SYMMETRICALLY, never in the skill's favour twice: on a should_trigger
    # prompt, being among the best matches counts as covered; on a
    # should_not_trigger prompt, matching as strongly as the sibling that
    # should own it counts as leaking. Ties are also reported in their own
    # right — they are the actionable signal about colliding descriptions even
    # when the verdict passes.
    for expected_skill, doc in prompt_docs.items():
        entry = results["skills"][expected_skill]
        for p in doc.get("should_trigger", []):
            entry["expected_positives"] += 1
            pred, tied = predict(p)
            if pred == expected_skill or expected_skill in tied:
                entry["true_positives"].append(p)
                if tied:
                    entry["ties"].append({"prompt": p, "tied": tied})
            else:
                entry["false_negatives"].append(
                    {"prompt": p, "predicted": pred, "tied": tied})
        for p in doc.get("should_not_trigger", []):
            entry["expected_negatives"] += 1
            pred, tied = predict(p)
            if pred == expected_skill or expected_skill in tied:
                # The expected_skill was wrongly chosen (or tied) for a negative.
                entry["false_positives"].append(
                    {"prompt": p, "predicted": pred, "tied": tied})
            else:
                entry["true_negatives"].append(
                    {"prompt": p, "predicted": pred, "tied": tied})

    return results


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("static", "llm"), default="static")
    ap.add_argument("--prompts-dir", required=True)
    ap.add_argument("--skills-root", required=True)
    ap.add_argument("--skill", default=None,
                    help="Limit to a single skill (by name).")
    ap.add_argument("--out", default=None,
                    help="Write JSON results to this path; default stdout.")
    args = ap.parse_args()

    results = run(args.mode, Path(args.prompts_dir), Path(args.skills_root),
                  args.skill)
    payload = json.dumps(results, indent=2, sort_keys=True)
    if args.out:
        Path(args.out).write_text(payload + "\n")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
