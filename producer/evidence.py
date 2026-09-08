"""Deterministic project metrics — the facts the agents are NOT allowed to invent.

Every number a risk or status claim rests on is computed here, in plain Python,
from the board and the team config. The agents receive this as JSON and must
cite it. If the agent says "we are 3 sprints behind", that phrase has to trace
back to `schedule` in this dict.

This split is the point (see notes/01_what_got_automated.md). An LLM is
good at reading five messy stand-up updates and writing a fair summary. It is
bad at arithmetic it wasn't given. So we give it the arithmetic.
"""

from __future__ import annotations

import datetime as dt

from .board import PHASES, Board

AGING_DAYS = 10          # a non-shipped story untouched this long is "aging"
STALL_SPRINTS_AMBER = 1.0  # projected finish within remaining sprints -> amber
GREEN_HEADROOM = 0.8     # need to project finishing in <=80% of remaining time to be green


def _date(s: str) -> dt.date:
    return dt.date.fromisoformat(s)


def _weeks_between(a: dt.date, b: dt.date) -> float:
    return round((b - a).days / 7, 1)


def build_evidence(board: Board, config: dict, as_of: str | None = None) -> dict:
    today = _date(as_of) if as_of else dt.date.today()
    ship = _date(config["ship_date"])
    sprint_weeks = config.get("sprint_length_days", 14) / 7

    # ---- schedule math ---------------------------------------------------
    weeks_left = _weeks_between(today, ship)
    sprints_left = round(weeks_left / sprint_weeks, 1) if sprint_weeks else 0.0

    remaining = board.not_shipped()
    shipped = board.shipped()
    remaining_days = sum(s.get("estimate_days", 0) for s in remaining)

    # velocity = stories shipped per elapsed sprint. Meaningless before ~1 full
    # sprint has elapsed (tiny denominator -> wild number), so we don't report it
    # or a projection until then (the early number is noise; see notes/01).
    elapsed_sprints = _elapsed_sprints(board, config, today, sprint_weeks)
    if elapsed_sprints < 1.0:
        velocity = None
        projected_sprints_to_finish = None
    else:
        velocity = round(len(shipped) / elapsed_sprints, 2)
        projected_sprints_to_finish = (
            round(len(remaining) / velocity, 1) if velocity else None
        )

    if projected_sprints_to_finish is None:
        verdict = "unknown"
    elif projected_sprints_to_finish <= sprints_left * GREEN_HEADROOM:
        verdict = "green"
    elif projected_sprints_to_finish <= sprints_left * STALL_SPRINTS_AMBER:
        verdict = "amber"
    else:
        verdict = "red"

    # ---- next milestone ------------------------------------------------------
    upcoming = sorted(
        ({"name": m["name"], "date": m["date"]} for m in config.get("milestones", [])
         if _date(m["date"]) >= today),
        key=lambda m: m["date"],
    )
    next_milestone = upcoming[0] if upcoming else None
    if next_milestone:
        next_milestone = {
            **next_milestone,
            "weeks_away": _weeks_between(today, _date(next_milestone["date"])),
        }

    # ---- aging / blocked / allocation ------------------------------------
    aging = [
        {"id": s["id"], "title": s["title"], "phase": s["phase"],
         "days_since_update": (today - _date(s["updated"])).days,
         "assignee": s.get("assignee")}
        for s in remaining
        if (today - _date(s["updated"])).days >= AGING_DAYS
    ]

    shipped_ids = {s["id"] for s in shipped}
    blocked = []
    for s in remaining:
        open_blockers = [b for b in s.get("blocked_by", []) if b not in shipped_ids]
        if open_blockers:
            blocked.append({"id": s["id"], "title": s["title"],
                            "waiting_on": open_blockers, "assignee": s.get("assignee")})

    allocation = _allocation(board, config)

    # ---- stories sitting in QA/Polish with acceptance criteria that have no
    #      recorded evidence — i.e. "done" is being claimed but not shown.
    unproven = []
    for s in board.stories:
        if s["phase"] not in ("QA", "Polish"):
            continue
        acs = s.get("acceptance_criteria", [])
        ev_count = len(s.get("evidence", []))
        if acs and ev_count < len(acs):
            unproven.append({"id": s["id"], "title": s["title"], "phase": s["phase"],
                             "criteria": len(acs), "evidence_items": ev_count,
                             "assignee": s.get("assignee")})

    # ---- phase distribution (a quick "where is everything") ------------
    dist = {p: 0 for p in PHASES}
    for s in board.stories:
        dist[s["phase"]] = dist.get(s["phase"], 0) + 1

    return {
        "as_of": today.isoformat(),
        "project": board.project,
        "current_sprint": board.current_sprint,
        "schedule": {
            "weeks_to_ship": weeks_left,
            "sprints_to_ship": sprints_left,
            "stories_total": len(board.stories),
            "stories_shipped": len(shipped),
            "stories_remaining": len(remaining),
            "person_days_remaining": remaining_days,
            "elapsed_sprints": elapsed_sprints,
            "velocity_stories_per_sprint": velocity,
            "projected_sprints_to_finish": projected_sprints_to_finish,
            "verdict": verdict,
        },
        "next_milestone": next_milestone,
        "phase_distribution": dist,
        "aging_stories": aging,
        "blocked_stories": blocked,
        "unproven_stories": unproven,
        "allocation": allocation,
    }


def _elapsed_sprints(board: Board, config: dict, today: dt.date, sprint_weeks: float) -> float:
    start = _date(config["start_date"])
    return max(round(_weeks_between(start, today) / sprint_weeks, 1), 0.1)


def _allocation(board: Board, config: dict) -> list[dict]:
    """Per-person committed days in the current sprint vs. their stated capacity."""
    caps = {m["name"]: m.get("capacity_days_per_sprint", 8) for m in config.get("team", [])}
    committed = {name: 0 for name in caps}
    for s in board.in_sprint(board.current_sprint):
        if s["phase"] == "Shipped":
            continue
        who = s.get("assignee")
        if who in committed:
            committed[who] += s.get("estimate_days", 0)
    rows = []
    for name, cap in caps.items():
        load = committed.get(name, 0)
        rows.append({
            "member": name,
            "role": next((m["role"] for m in config["team"] if m["name"] == name), ""),
            "committed_days": load,
            "capacity_days": cap,
            "over_by": max(load - cap, 0),
        })
    return sorted(rows, key=lambda r: r["over_by"], reverse=True)
