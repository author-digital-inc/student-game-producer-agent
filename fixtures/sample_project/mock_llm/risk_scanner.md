### Headline

Off track. At the current velocity of **1.2 stories/sprint**
(`schedule.velocity_stories_per_sprint`), the 13 remaining stories project to
**10.8 more sprints** (`schedule.projected_sprints_to_finish`) against only
**7.5 sprints of runway** (`schedule.sprints_to_ship`) — roughly a **6–7 week
overrun** toward the 2027-01-26 ship date. First Playable is **1.0 week away**
(`next_milestone.weeks_away`) with 5 stories still in Implementation and only 1 in
Polish (`phase_distribution`).

### Risk register

| # | Risk | Severity | Evidence | Suggested owner | Next action |
|---|------|----------|----------|-----------------|-------------|
| 1 | Scope will not fit the schedule | High | projected 10.8 vs 7.5 sprints; 49 person-days remaining (`schedule`) | Design Lead + team | Bring a cut list to this week's meeting; target dropping ~4–5 stories (see decision below) |
| 2 | First Playable misses next week | High | `next_milestone` 1.0 wk; phase_distribution Implementation=5, QA=2, Polish=1 | Tech Lead | Pick the 3 stories that MUST be in the FP build; defer the rest openly |
| 3 | Jules over-allocated | High | `allocation`: Jules committed 13 days vs 9 capacity (over_by 4); ST-9/ST-14/ST-18 all on Jules | Tech Lead | Move ST-18 off Jules or out of the sprint; ST-18 is blocked by ST-9 anyway |
| 4 | Enemy pathfinding (ST-9) stalled in QA | High | `blocked_stories`: ST-18 waiting on ST-9; AC gate says ST-9 fails its own criteria | Gameplay Builder | Descope ST-9 to "routes around walls, ≤4 enemies" for FP; log the rest |
| 5 | Audio silently stalled | Med | `aging_stories`: ST-16 no update in 18 days; 2 commits this week, both stubs | QA & Audio | 1:1 with Devon — is this blocked, mis-scoped, or a capacity problem elsewhere? |
| 6 | Boss 1 design abandoned | Med | `aging_stories`: ST-22 no update in 23 days; still in Design Review | Design Lead | Decide now: boss in or out for Alpha. If out, say so and stop half-carrying it |
| 7 | Tutorial blocked on HUD | Med | `blocked_stories`: ST-20 waiting on ST-15 | Systems & UI Builder | Ship HUD anchor points as a tiny standalone PR so ST-20 can proceed |
| 8 | Backlog tail unowned | Low | ST-26 / ST-28 / ST-30 in Conception, no assignee, some aging | Producer | Explicitly park these as post-Alpha / cut candidates so they stop reading as "planned" |

### The decision to bring to the team

The math does not close, so the real choice this week is **what Starfall is not
going to be**. Three framings to put in front of the team:

- **Cut breadth:** drop New Game+ (ST-28), accessibility options (ST-30), Level 3
  (ST-26), and the standalone boss (ST-22) — that removes ~15 person-days and
  brings the projection close to the runway. Ship a tight two-level game.
- **Cut depth:** keep the feature list but reduce each to its simplest version
  (ST-9 pathfinding to 4 enemies, one boss phase instead of three, HUD without
  the 1440p pass).
- **Re-negotiate a milestone:** ask the instructor whether First Playable can
  slip one week in exchange for a firmer Alpha.

Recommended starting point: cut breadth now, revisit depth at Alpha. But this is
the team's call to make together, not the producer's to announce.
