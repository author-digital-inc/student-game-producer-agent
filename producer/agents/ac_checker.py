"""ac_checker — for every story sitting in QA or Polish, checks whether its
acceptance criteria are actually satisfied by the recorded evidence before it is
allowed to move to Shipped.

This is the gate that stops "it works on my machine" from becoming "done".
"""

from __future__ import annotations

import pathlib

from .. import llm
from ..board import Board
from . import as_json, load_prompt

SLUG = "ac_checker"
REVIEW_PHASES = {"QA", "Polish"}


def run(board: Board, config: dict, *, log_dir: pathlib.Path | None = None) -> str:
    candidates = [
        {"id": s["id"], "title": s["title"], "phase": s["phase"],
         "acceptance_criteria": s.get("acceptance_criteria", []),
         "evidence": s.get("evidence", [])}
        for s in board.stories if s["phase"] in REVIEW_PHASES
    ]
    if not candidates:
        return "_No stories in QA or Polish this week — nothing to check._"
    user = (
        "Stories currently in QA or Polish. For each, decide PASS (every "
        "acceptance criterion is backed by concrete evidence) or NEEDS WORK "
        "(list exactly which criteria are unproven and what evidence would "
        "close them). Do not accept vague evidence like 'tested' — name the "
        "build, PR, or playtest.\n\n"
        f"{as_json(candidates)}"
    )
    return llm.run_agent(SLUG, load_prompt(SLUG), user, log_dir=log_dir)
