"""standup_synthesizer — turns five written updates + commit activity + last
week's commitments into the weekly status section of the report.

It answers the three check-in questions from the brief:
  * Did we complete last sprint's acceptance criteria?
  * Did we hit our target? Why / why not?
  * What blockers exist?
"""

from __future__ import annotations

import pathlib

from .. import llm
from ..board import Board
from . import as_json, load_prompt

SLUG = "standup_synthesizer"


def run(board: Board, config: dict, updates_text: str, commits: list[dict],
        previous_run: dict | None, *, log_dir: pathlib.Path | None = None) -> str:
    last_sprint = board.current_sprint
    committed = [
        {"id": s["id"], "title": s["title"], "phase": s["phase"],
         "acceptance_criteria": s.get("acceptance_criteria", []),
         "evidence": s.get("evidence", [])}
        for s in board.in_sprint(last_sprint)
    ]
    user = (
        f"SPRINT UNDER REVIEW: {last_sprint}\n\n"
        "WHAT WAS COMMITTED TO THIS SPRINT (with acceptance criteria and the "
        "evidence recorded so far):\n"
        f"{as_json(committed)}\n\n"
        "LAST WEEK'S RECORDED RESULT (from the tool's own history, may be null):\n"
        f"{as_json(previous_run)}\n\n"
        "COMMIT ACTIVITY THIS WEEK (author, count, last message):\n"
        f"{as_json(commits)}\n\n"
        "TEAM UPDATES (verbatim, one block per person):\n"
        f"{updates_text}\n\n"
        "Write the weekly status. Be specific about which acceptance criteria "
        "are met vs. outstanding, and cite the evidence or the update line you "
        "based each call on. Do not mark a criterion met on a team member's word "
        "alone if no evidence is recorded — say 'claimed, unverified'."
    )
    return llm.run_agent(SLUG, load_prompt(SLUG), user, log_dir=log_dir)
