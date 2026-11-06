"""Single source of truth: loads humanizer_spec.json and builds the portable prompt from it.

The exact same prompt text is exported to dist/ so it can be pasted into any model or app
(Grok, ChatGPT, Claude, Gemini, local models). Python and the exported files can never drift.
"""
from __future__ import annotations

import json
import pathlib

SPEC_PATH = pathlib.Path(__file__).with_name("humanizer_spec.json")
SPEC: dict = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
VERSIONS = list(SPEC["versions"])


def build_prompt(version: str = "default") -> str:
    if version not in SPEC["versions"]:
        raise ValueError(f"unknown version {version!r}; choose from {VERSIONS}")
    v = SPEC["versions"][version]
    lines = [
        f"# {SPEC['name']} v{SPEC['spec_version']} ({v['label']} version)",
        "",
        "You are an experienced human editor. Rewrite the text the user gives you so it reads naturally.",
        "Follow EVERY rule below exactly. These rules are fixed; do not reinterpret or soften them.",
        "",
        "## Rules",
    ]
    rules = SPEC["core_rules"] + v["rules"]
    lines += [f"{i}. {r}" for i, r in enumerate(rules, 1)]
    lines += [
        "",
        "## Banned words (never use, in any form)",
        ", ".join(SPEC["banned_words"]),
        "",
        "## Banned phrases (never use)",
        "; ".join(SPEC["banned_phrases"]),
    ]
    if v["markers"]:
        lines += ["", "## Casual markers to weave in", ", ".join(v["markers"])]
    lines += [
        "",
        "## Example",
        "Input:",
        v["example_input"],
        "",
        "Output:",
        v["example_output"],
        "",
        "## Procedure",
        "1. Rewrite the text following all rules.",
        "2. Silently re-read your draft and check: no banned words/phrases, no groups of exactly three parallel items, no three sentences starting with the same word, no em dashes"
        + (", marker frequency within limits" if v["markers"] else "")
        + ", all facts and numbers unchanged.",
        "3. Fix any violation, then output ONLY the final text. No preamble, no notes, no quotation marks around it.",
    ]
    return "\n".join(lines)
