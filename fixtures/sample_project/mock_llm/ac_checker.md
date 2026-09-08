**ST-7 Camera follow with look-ahead and room bounds — PASS**

- Smoothed look-ahead — PR #34 (merged) implements it; playtest 10-10 confirms feel.
- Never shows outside room bounds — clip in #playtest showing the clamp; 3 players
  on the 10-10 build reported no out-of-bounds views.
- No visible jitter at 60fps on the target laptop — playtest 10-10, 3 players, on
  the target machine, none reported jitter.

**ST-9 Enemy pathfinding around static obstacles — NEEDS WORK**

- "Navigates around walls to reach the player" — PR #38 is basic A* only; no
  recorded playtest or clip showing an enemy routing around a wall to the player.
  *To close:* a build link or clip of a grunt pathing around an L-shaped wall to
  the player, plus the Tech Lead's sign-off (Priya's review flagged this).
- "No pathing hitches with 6 enemies active" — no performance test recorded.
  *To close:* a build with 6+ active grunts and a frame-time capture staying under
  16ms on the target laptop.
- "Enemies do not clip through thin platforms" — no evidence.
  *To close:* a playtest note or clip on a level with thin platforms.

**ST-12 Save and load (single slot) — NEEDS WORK**

- "Game state round-trips through save then load" — met: build 0.3.0, happy path
  verified.
- "Corrupt or missing save file falls back to a new game without crashing" — not
  implemented (owner confirms). *To close:* a test that deletes / truncates the
  save file and shows the game starting a new run without an exception.

**1 of 3 stories pass the gate.** ST-9 and ST-12 should not move to Shipped this
week. ST-9 in particular is mislabelled as QA-ready.
