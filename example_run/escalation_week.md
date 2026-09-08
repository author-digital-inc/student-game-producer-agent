# Example: a week where a human is needed

Same tool, same command, a project in trouble. This is what
`python run.py demo --auto` produces out of the box (MOCK responses — no API key,
no cost). The sample team "Starfall" is at week 6 of 20, one week before First
Playable, and several things have quietly gone wrong at once.

## Console

```
tracked: 16 stories, 3 shipped / 13 left; 35 commits/7d from 5 people; snapshot -> state\snapshots\2026-09-08.json

=== Week 6 - Starfall ===
{
  "weeks_to_ship": 15.0,
  "sprints_to_ship": 7.5,
  "stories_total": 16,
  "stories_shipped": 3,
  "stories_remaining": 13,
  "person_days_remaining": 49,
  "elapsed_sprints": 2.5,
  "velocity_stories_per_sprint": 1.2,
  "projected_sprints_to_finish": 10.8,
  "verdict": "red"
}
escalation: 4 trigger(s): schedule, over_allocation, aging, unproven_done
running standup_synthesizer ...
running ac_checker ...
running risk_scanner ...
running sprint_planner ...

wrote reports\week6.md
```

Four thresholds tripped, so four agents ran and a report was written. With
`--post`, the GitHub Action would now open **one** issue titled
_"Producer: 4 things need you — week 6"_ and `cc` the producer.

## The top of reports/week6.md

```markdown
# Producer review — Week 6 (Starfall)
_Generated 2026-10-13 · sprint S3_

## Schedule at a glance

- **Status:** 🔴 RED
- Shipped 3 / 16 · 13 remaining (49 person-days)
- Velocity 1.2/sprint -> projected 10.8 more sprints vs 7.5 of runway
- Next milestone: **First Playable** in 1.0 weeks (2026-10-20)

## Why you're getting this

The tracker flagged the following for a human. Everything else is being kept
up to date automatically.

- **Schedule verdict is RED** — Projected 10.8 more sprints to finish vs 7.5
  of runway (velocity 1.2).
- **Over capacity this sprint: Jules (+4d)** — Committed days exceed stated
  capacity; work needs re-balancing or cutting.
- **4 stories untouched 10+ days: ST-16, ST-22, ST-28, ST-30** — No phase
  change or update — likely blocked, forgotten, or mis-scoped.
- **In QA/Polish without evidence for every acceptance criterion: ST-9** —
  A person should look at the build before it moves to Shipped.
```

Below that, the report has the full **weekly status** (each acceptance criterion
marked met / claimed-unverified / not-met, with the evidence cited), the
**acceptance-criteria gate** (1 of 3 stories pass), the **risk register** (8
ranked rows, each tied to a computed figure), and a **draft next sprint** that
cuts scope to make First Playable reachable.

It ends with what the tool did *not* decide — which features to cut, the final
sprint commitment, "done" disputes, and tone. Those go to the team.

> Run `python run.py demo` (without `--auto`) to write the whole report to
> `reports/week6.md` and read it in full.

## The point

The same run, on a healthy week, produces
[`silent_week.md`](silent_week.md) — one line, no issue, no interruption. The tool
scales its noise to how much trouble the project is actually in.
