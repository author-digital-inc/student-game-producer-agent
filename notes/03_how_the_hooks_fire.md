# Note 3 — How the automation fires, and how it stays quiet

Two mechanisms, deliberately kept apart.

## The always-on part: git hooks

A **git hook** is a script git runs automatically at a certain moment. This repo
ships two:

- `hooks/post-commit` — runs right after you `git commit`
- `hooks/post-merge` — runs right after a `git pull` / merge brings in changes

Both do the same thing: `python run.py track`. That reads the commit log and the
board, updates `state/commit_activity.json`, and saves a board snapshot. No AI, no
network, and it ends in `|| true` so if it ever errors it can't block your commit.

You install them once per clone with `hooks/install.sh` (or `install.ps1`). They
are not committed to the repo — git deliberately doesn't let a repo run arbitrary
scripts on your machine without you opting in.

## The weekly part: a GitHub Action with an escalation gate

`deploy/producer-review.yml` (which you copy into your game repo at
`.github/workflows/`) runs `run.py review --auto` on a schedule and whenever a
story issue is closed.

`--auto` is the important flag. It runs `producer/escalation.py` *before* doing
any AI work. `escalation.check()` compares the computed evidence against the
thresholds in `config/team.yaml`:

```yaml
escalation:
  schedule_verdict_at_or_worse_than: amber
  notify_on_verdict_change: true
  over_allocation_days: 2
  aging_story_days: 10
  unproven_done: true
  new_blocker: true
```

- **Nothing trips** → the job writes a one-line "all clear", updates the tracking
  data, and exits. No issue, no ping. Most weeks, near the start of a project,
  look like this.
- **Something trips** → only the agents relevant to *that* trigger run (a
  schedule problem runs the risk + planning agents; an "unproven done" runs the
  acceptance-criteria checker), and **one** GitHub issue opens, tagged to the
  producer, headed "N things need you — week X".

So the cost — in dollars and in interruptions — scales with how much trouble the
project is actually in. A healthy week is free and silent.

## Tuning it

If the team feels nagged, loosen the thresholds (`over_allocation_days: 4`,
`schedule_verdict_at_or_worse_than: red`). Near a milestone, tighten them. It's
just a YAML file; no code change.
