# student-game-producer-agent

An agentic workflow that does the **bookkeeping half of the producer job** for a
5-person student game team, and pulls a human in only for the calls that need one.

- **Always on, no AI:** git hooks keep a running tally of who did what and a dated
  snapshot of the board, updated on every commit and merge.
- **Weekly, with judgement:** a scheduled job computes the schedule math, and
  **only if something crosses a threshold** does it run the AI agents and open one
  issue for the producer. A healthy week is silent.

New to this? Read [`docs/FOR_STUDENTS.md`](docs/FOR_STUDENTS.md) — it assumes no
background in AI or in production.

---

## Try it in 2 minutes (no API key, no cost)

```bash
pip install -r requirements.txt
python run.py demo
```

Runs against a built-in sample team having a rough week. Then compare the two
example runs:

- [`example_run/silent_week.md`](example_run/silent_week.md) — nothing needs a human
- [`example_run/escalation_week.md`](example_run/escalation_week.md) — four things do

---

## The three verbs

```bash
python run.py track                 # refresh the tally + snapshot. NO AI. git hooks call this.
python run.py review --week 8       # full report — run it when you want the whole picture
python run.py review --auto --post  # scheduled use: silent unless a threshold trips, then notify once
```

| | Runs | Calls AI | Interrupts a human |
|---|---|---|---|
| `track` | every commit / merge | no | never |
| `review --auto` | weekly + on issue close | only if a threshold trips | only if a threshold trips |
| `review` | on demand | yes | it's a report you chose to read |

Thresholds live in `config/team.yaml` under `escalation:` — schedule verdict,
verdict change, over-allocation, aging stories, "done" without evidence, new
blockers. Tune them there; no code change.

---

## How it fits together

```
config/team.yaml ─┐
board (JSON file   ├─▶ producer/evidence.py ──▶ deterministic facts
  or GitHub Issues)┘        velocity · projected finish · runway · aging ·
                            blocked chains · per-person load   (plain Python)
                                   │
                          producer/escalation.py
                       "does any of this need a person?"
                          ╱                        ╲
                    no │                            │ yes
                       ▼                            ▼
             one-line "all clear"      run only the relevant agents
             (no agents, no ping)      (producer/agents/* = prompt + 1 Claude call)
                                                    │
                                                    ▼
                                       reports/week<N>.md  +  ONE GitHub issue
                                       cc the producer
                                                    │
                                       ── the team decides ──
                                  scope cuts · rebalancing · "is it
                                  really done" · tone
```

**The rule:** Python does the lookup and arithmetic; the agent turns that into
readable judgement; a person makes every call that changes the plan or goes on
the record. See [`notes/02_where_you_come_in.md`](notes/02_where_you_come_in.md).

Why the split — models are strong at reading five messy stand-up updates and
weak at arithmetic they weren't handed (where they're wrong *fluently*). So the
schedule math is Python with tests (`evals/`) and the prompts require the agents
to cite it.

---

## Point it at your game

1. Fill in `config/team.yaml` — names, roles, honest capacities, project dates,
   milestones, and the `escalation:` thresholds.
2. Choose the board backend: a committed `board.json` (template in
   `fixtures/sample_project/board.json`) or GitHub Issues with the label
   convention at the top of `producer/board.py` (`--board github`).
3. Install the hooks: `sh hooks/install.sh /path/to/your/game/repo`
   (each teammate, once). See [`hooks/README.md`](hooks/README.md).
4. Copy `deploy/producer-review.yml` into your game repo at
   `.github/workflows/`; add an `ANTHROPIC_API_KEY` secret.
5. Each week, everyone drops 3 sentences in `updates/week<N>.md`.

Full walkthrough: [`docs/FOR_STUDENTS.md`](docs/FOR_STUDENTS.md).

---

## Repo map

| Path | What |
|---|---|
| `run.py` | The entry point. `track`, `review`, `demo`. |
| `config/team.yaml` | The one file you edit. Team, dates, escalation thresholds. |
| `hooks/` | git hooks for the always-on tracking + installer. |
| `deploy/producer-review.yml` | The weekly escalation-gated review — copy into your game repo's `.github/workflows/`. |
| `producer/evidence.py` | All deterministic metrics. The agents may not invent numbers. |
| `producer/escalation.py` | Decides whether — and why — a human is needed. |
| `producer/state.py` | `state/` — commit tally, board snapshots, run history (git-ignored). |
| `producer/agents/` | `standup_synthesizer`, `ac_checker`, `risk_scanner`, `sprint_planner`. |
| `prompts/` | One editable system prompt per agent. |
| `fixtures/sample_project/` | The offline sample: `board.json` (rough week) + `board_healthy.json`. |
| `evals/` | Tests for `evidence.py`. `python evals/run_evals.py`. |
| `example_run/` | Committed silent-week and escalation-week outputs. |
| `notes/` | Three short explainers: what got automated, where you come in, how it fires. |
| `docs/FOR_STUDENTS.md` | Plain-language start guide. |

---

## Cost & model

Agents call `claude-opus-5` by default (`PRODUCER_MODEL` in `.env`), with adaptive
thinking. A week that escalates is ~15–25K tokens (well under $0.50); a healthy
week runs no agents and costs nothing. `PRODUCER_MODEL=claude-sonnet-5` cuts the
escalated-week cost ~5×. `producer/llm.py` degrades gracefully on an older
`anthropic` package (`pip install -U anthropic` to fix).

## Limitations (by design)

- Velocity is noise before ~2 elapsed sprints; the tool reports "not measurable
  yet" until then.
- "Stories" as the projection unit assumes roughly comparable sizes;
  `person_days_remaining` is exposed if you'd rather reproject on effort.
- A stale board produces confident, wrong output. The hooks keep the *snapshot*
  current automatically, but a human still has to move stories to their true
  phase — that's the weekly 15-minute board grooming.
