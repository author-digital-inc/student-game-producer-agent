# Example: a week where the tool stays silent

This is the common case, especially early in a project: the scheduled review
runs, finds nothing that needs a person, and nobody is interrupted.

Reproduce it:

```bash
python run.py review --week 5 --auto \
  --fixture-board fixtures/sample_project/board_healthy.json
```

(`board_healthy.json` is the sample team on a good week — enough shipped, nothing
stalled, nobody overloaded.)

## Console

```
=== Week 5 - Starfall ===
{
  "weeks_to_ship": 16.0,
  "sprints_to_ship": 8.0,
  "stories_total": 14,
  "stories_shipped": 8,
  "stories_remaining": 6,
  "person_days_remaining": 20,
  "elapsed_sprints": 2.0,
  "velocity_stories_per_sprint": 4.0,
  "projected_sprints_to_finish": 1.5,
  "verdict": "green"
}
escalation: 0 trigger(s)

wrote reports\week5-allclear.md
nothing needs a human this week.
```

No agents ran. No API call was made. No issue was opened. In the GitHub Action
this job finishes in a few seconds and posts nothing (or, if a Discord webhook is
set, a single "all clear" line).

## reports/week5-allclear.md

```markdown
# Producer review — Week 5 (Starfall)
_Generated 2026-10-06_

## All clear

- **Status:** 🟢 GREEN
- Shipped 8 / 14 · 6 remaining (20 person-days)
- Velocity 4.0/sprint -> projected 1.5 more sprints vs 8.0 of runway
- Next milestone: **First Playable** in 2.0 weeks (2026-10-20)

Nothing crossed an escalation threshold. The board and commit activity have
been refreshed; no action needed.
```

The tracking still happened — `state/commit_activity.json` and a board snapshot
were updated. The tool just had nothing worth a person's time to say. That is the
design working, not the design doing nothing.
