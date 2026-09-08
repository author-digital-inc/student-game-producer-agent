"""Decide whether this week's state needs a human — and if so, for what.

This is the piece that makes the workflow worth running unattended. `track.py`
keeps the books automatically and silently. The scheduled review calls
`check()`; if it returns nothing, no person is interrupted. If it returns
triggers, only the agents relevant to those triggers run, and one notification
goes to the producer.

Thresholds live in config/team.yaml under `escalation:` so a team can tune how
noisy it is without touching code.
"""

from __future__ import annotations

from dataclasses import dataclass, field

_VERDICT_RANK = {"green": 0, "unknown": 0, "amber": 1, "red": 2}


@dataclass
class Trigger:
    key: str                       # short id, e.g. "schedule"
    headline: str                  # one line for the notification
    detail: str                    # a sentence of grounding
    agents: list[str] = field(default_factory=list)   # agent sections to include


def check(evidence: dict, last_run: dict | None, config: dict) -> list[Trigger]:
    rules = config.get("escalation", {}) or {}
    sched = evidence["schedule"]
    verdict = sched["verdict"]
    triggers: list[Trigger] = []

    # 1) schedule verdict at or worse than the configured floor
    floor = rules.get("schedule_verdict_at_or_worse_than", "amber")
    if verdict in ("amber", "red") and _VERDICT_RANK[verdict] >= _VERDICT_RANK.get(floor, 1):
        triggers.append(Trigger(
            "schedule",
            f"Schedule verdict is {verdict.upper()}",
            f"Projected {sched['projected_sprints_to_finish']} more sprints to "
            f"finish vs {sched['sprints_to_ship']} of runway "
            f"(velocity {sched['velocity_stories_per_sprint']}).",
            ["risk_scanner", "sprint_planner"],
        ))

    # 2) verdict moved the wrong way since last review
    if rules.get("notify_on_verdict_change", True) and last_run:
        prev = last_run.get("verdict")
        if prev and prev != verdict and _VERDICT_RANK[verdict] > _VERDICT_RANK.get(prev, 0):
            triggers.append(Trigger(
                "verdict_change",
                f"Schedule slipped: {prev.upper()} -> {verdict.upper()} since last review",
                "The trend is the signal here, not the single number.",
                ["risk_scanner"],
            ))

    # 3) someone committed well past their capacity this sprint
    over_days = rules.get("over_allocation_days", 2)
    over = [r for r in evidence["allocation"] if r["over_by"] >= over_days]
    if over:
        who = ", ".join(f"{r['member']} (+{r['over_by']}d)" for r in over)
        triggers.append(Trigger(
            "over_allocation",
            f"Over capacity this sprint: {who}",
            "Committed days exceed stated capacity; work needs re-balancing or cutting.",
            ["sprint_planner"],
        ))

    # 4) a story silently stalled
    age_days = rules.get("aging_story_days", 10)
    aging = [s for s in evidence["aging_stories"] if s["days_since_update"] >= age_days]
    if aging:
        ids = ", ".join(s["id"] for s in aging)
        triggers.append(Trigger(
            "aging",
            f"{len(aging)} story(ies) untouched {age_days}+ days: {ids}",
            "No phase change or update — likely blocked, forgotten, or mis-scoped.",
            ["standup_synthesizer"],
        ))

    # 5) "done" claimed without evidence
    if rules.get("unproven_done", True) and evidence["unproven_stories"]:
        ids = ", ".join(s["id"] for s in evidence["unproven_stories"])
        triggers.append(Trigger(
            "unproven_done",
            f"In QA/Polish without evidence for every acceptance criterion: {ids}",
            "A person should look at the build before these move to Shipped.",
            ["ac_checker"],
        ))

    # 6) a new dependency started blocking work since last review
    if rules.get("new_blocker", True) and last_run:
        prev_blocked = set(last_run.get("blocked_ids", []))
        now_blocked = {s["id"] for s in evidence["blocked_stories"]}
        new = sorted(now_blocked - prev_blocked)
        if new:
            triggers.append(Trigger(
                "new_blocker",
                f"Newly blocked since last review: {', '.join(new)}",
                "A dependency that was fine last week is now holding up work.",
                ["standup_synthesizer"],
            ))

    return triggers


def agents_for(triggers: list[Trigger]) -> list[str]:
    """De-duplicated, in a stable order, so the review runs each agent at most once."""
    order = ["standup_synthesizer", "ac_checker", "risk_scanner", "sprint_planner"]
    needed = {a for t in triggers for a in t.agents}
    return [a for a in order if a in needed]
