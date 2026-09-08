"""The four agents. Each is one function that takes structured input and returns
Markdown. None of them use tools, mutate the board, or make decisions — they
produce a draft or an assessment for a human to act on.

  sprint_planner       backlog + capacity      -> a proposed 2-week sprint (DRAFT)
  standup_synthesizer  updates + commits + AC   -> the weekly status write-up
  ac_checker           stories "ready for done" -> per-story pass / needs-work
  risk_scanner         evidence dict            -> ranked, cited risk list

Keeping them tiny and uniform is intentional: a student can read all four in a
few minutes and see that the only real content is the prompt file each one loads.
"""

from __future__ import annotations

import json
import pathlib

PROMPTS_DIR = pathlib.Path(__file__).resolve().parent.parent.parent / "prompts"


def load_prompt(slug: str) -> str:
    return (PROMPTS_DIR / f"{slug}.md").read_text(encoding="utf-8")


def as_json(obj) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False)
