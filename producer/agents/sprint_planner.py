"""sprint_planner — drafts the next 2-week sprint from the backlog and capacity.

Output is explicitly a DRAFT. The team edits it in sprint planning; the agent
never commits stories to a sprint. See notes/02_where_you_come_in.md for why this boundary matters.
"""

from __future__ import annotations

import pathlib

from .. import llm
from ..board import Board
from ..evidence import build_evidence
from . import as_json, load_prompt

SLUG = "sprint_planner"


def run(board: Board, config: dict, *, as_of: str | None = None,
        log_dir: pathlib.Path | None = None) -> str:
    ev = build_evidence(board, config, as_of=as_of)
    backlog = [
        {k: s.get(k) for k in
         ("id", "title", "phase", "estimate_days", "assignee", "blocked_by", "acceptance_criteria")}
        for s in board.not_shipped()
    ]
    user = (
        "TEAM & CAPACITY (person-days available per 2-week sprint):\n"
        f"{as_json(ev['allocation'])}\n\n"
        "NEXT MILESTONE:\n"
        f"{as_json(ev['next_milestone'])}\n\n"
        "SCHEDULE SNAPSHOT:\n"
        f"{as_json(ev['schedule'])}\n\n"
        "BACKLOG (not yet shipped):\n"
        f"{as_json(backlog)}\n\n"
        "Draft the next sprint. Respect each person's available days. Pull work "
        "toward the next milestone. Flag anything you had to leave out for lack "
        "of capacity."
    )
    return llm.run_agent(SLUG, load_prompt(SLUG), user, log_dir=log_dir)
