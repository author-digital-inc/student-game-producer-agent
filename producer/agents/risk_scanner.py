"""risk_scanner — reads the deterministic evidence dict and produces a ranked,
cited list of risks with a recommended owner and next action for each.

It must not introduce numbers that are not in the evidence. Its whole value is
turning "velocity 1.8, projected 9.4 sprints, 6.0 remaining" into "we will miss
Gold by ~6 weeks unless scope drops by a third — here is where to cut."
"""

from __future__ import annotations

import pathlib

from .. import llm
from ..board import Board
from ..evidence import build_evidence
from . import as_json, load_prompt

SLUG = "risk_scanner"


def run(board: Board, config: dict, *, as_of: str | None = None,
        log_dir: pathlib.Path | None = None) -> str:
    ev = build_evidence(board, config, as_of=as_of)
    user = (
        "PROJECT EVIDENCE (every figure below is computed, not estimated — cite "
        "these figures, do not invent new ones):\n\n"
        f"{as_json(ev)}\n\n"
        "Produce the risk register: rank by impact-then-likelihood, one row per "
        "risk with severity, the evidence it rests on, a suggested owner (a role "
        "from the allocation table), and one concrete next action. Call out the "
        "single most important decision the producer needs to bring to the team "
        "this week."
    )
    return llm.run_agent(SLUG, load_prompt(SLUG), user, log_dir=log_dir)
