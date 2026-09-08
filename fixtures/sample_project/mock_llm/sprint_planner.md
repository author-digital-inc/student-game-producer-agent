**Sprint goal (S4):** A First-Playable build that shows the core loop end to
end — move, fight one enemy type, use the HUD, finish a short level — even if
rough. No new systems.

**Committed stories**

| Story | Owner | Est (d) | Target phase by sprint end |
|-------|-------|--------:|----------------------------|
| ST-14 Hit reactions | Jules | 3 (finish) | QA, with a build + clip as evidence |
| ST-9 Pathfinding (descoped: routes around walls, ≤4 enemies) | Jules | 2 | QA passes the gate |
| ST-15 HUD (health/ammo/marker; skip 1440p pass) | Sam | 3 | QA |
| ST-15a HUD anchor points (tiny PR to unblock ST-20) | Sam | 1 | Shipped |
| ST-20 Tutorial (in-world prompts for move/jump/attack) | Marcus | 4 | Implementation, playtested once |
| ST-12 Save/load corrupt-file fallback | Sam | 1 | QA passes the gate |
| ST-7 Camera final polish + sign-off | Priya | 1 | Shipped |
| ST-16 Audio: mixer buses + movement/hit/pickup SFX in a build | Devon | 4 | QA |
| First Playable build packaging + smoke test | Priya | 2 | Shipped |
| Playtest session with 3+ outside players | Devon | 1 | Shipped |

Running totals vs. capacity: Jules 5/9 · Sam 6/9 · Marcus 4/7 · Priya 5/7 ·
Devon 6/8. Deliberately under-booked — this sprint absorbs First Playable
packaging and the fallout from it.

**Explicitly cut from this sprint**

- ST-18 Level 2 blockout — Level 2 is not needed for First Playable; it was also
  blocked on ST-9. Moves to S5.
- ST-24 Upgrade system design, ST-22 Boss 1 design — no design-only work this
  sprint; every hand is on the FP build. To the team: *"We're freezing new
  design for two weeks to land First Playable. Boss and upgrades get decided at
  the Alpha planning meeting, including whether they stay in scope."*
- ST-26 / ST-28 / ST-30 — remain parked pending the scope decision.

**Risks in this plan**

- Jules still owns both remaining combat stories; if ST-14 slips, pathfinding
  slips too. Consider Priya pairing on ST-9 for a day.
- ST-20 depends on ST-15a landing early in the sprint — Sam should do the anchor
  PR on day 1, not day 8.
- Devon has 6 booked days but a 2-commit week behind them; if the audio-mixer
  stall was a hidden blocker, this plan inherits it. Resolve the 1:1 first.
