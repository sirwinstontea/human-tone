"""Deterministic verifier: does a text satisfy the spec? Works on output from ANY model.

Heuristic rule checks only. It does not predict any AI detector's result.
"""
from __future__ import annotations

import math
import re

from .spec import SPEC

_ITEM = r"[A-Za-z'’-]+(?: [A-Za-z'’-]+){0,4}"
# exactly three parallel items in one sentence: "A, B, and C" / "A, B or C" (not part of a longer list)
_TRICOLON = re.compile(rf"(?<!, )\b({_ITEM}), ({_ITEM}),? (?:and|or) ({_ITEM})")


def _word_re(w: str) -> re.Pattern:
    stem = re.escape(w)
    # allow simple inflections: foster -> fosters/fostered/fostering, delve -> delves/delved
    return re.compile(rf"\b{stem}(?:s|es|d|ed|ing|e|ly)?\b", re.I)


_BANNED_WORDS = [(w, _word_re(w)) for w in SPEC["banned_words"]]
_BANNED_PHRASES = [(p, re.compile(re.escape(p).replace("\\ ", r"\s+").replace("'", "['’]"), re.I)) for p in SPEC["banned_phrases"]]


def _sentences(text: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s]


def check(text: str, version: str = "default") -> dict:
    v = SPEC["versions"][version]
    out: list[dict] = []
    words = len(text.split())

    for w, rx in _BANNED_WORDS:
        for m in rx.finditer(text):
            out.append({"rule": "banned_word", "detail": m.group(0)})
    for p, rx in _BANNED_PHRASES:
        for m in rx.finditer(text):
            out.append({"rule": "banned_phrase", "detail": m.group(0)})
    for m in _TRICOLON.finditer(text):
        out.append({"rule": "tricolon", "detail": m.group(0)})

    sents = _sentences(text)
    firsts = [re.sub(r"\W", "", s.split()[0]).lower() for s in sents if s.split()]
    for i in range(len(firsts) - 2):
        if firsts[i] and firsts[i] == firsts[i + 1] == firsts[i + 2]:
            out.append({"rule": "triple_same_opening", "detail": f"3 sentences start with '{firsts[i]}'"})

    if "—" in text:
        out.append({"rule": "em_dash", "detail": f"{text.count('—')} em dash(es)"})

    markers = v["markers"]
    counts: dict[str, int] = {}
    if markers:
        for mk in markers:
            counts[mk] = len(re.findall(rf"\b{re.escape(mk)}\b", text, re.I))
        total = sum(counts.values())
        lo = max(1, words // v["marker_min_per_words"])
        hi = max(lo, math.ceil(words / v["marker_max_per_words"]))
        if total < lo:
            out.append({"rule": "too_few_markers", "detail": f"{total} found, need at least {lo}"})
        if total > hi:
            out.append({"rule": "too_many_markers", "detail": f"{total} found, max {hi}"})
        # same marker in consecutive sentences
        for a, b in zip(sents, sents[1:]):
            for mk in markers:
                rx = re.compile(rf"\b{re.escape(mk)}\b", re.I)
                if rx.search(a) and rx.search(b):
                    out.append({"rule": "repeated_marker", "detail": f"'{mk}' in consecutive sentences"})
        if re.match(r"\s*though\b", text, re.I) or any(re.match(r"though\b", s, re.I) for s in sents):
            out.append({"rule": "though_at_start", "detail": "sentence starts with 'though'"})
    else:
        for mk in ("kind of", "to be honest", "not really"):
            if re.search(rf"\b{mk}\b", text, re.I):
                out.append({"rule": "casual_marker_in_default", "detail": mk})

    return {"version": version, "ok": not out, "words": words, "marker_counts": counts, "violations": out}
