# Hooks — where the automatic tracking plugs in

The idea: the mechanical parts of tracking a project happen **on their own**, at
the moments work actually changes, without anyone remembering to run anything. A
person is pulled in only when there is a judgement call.

## Two places things fire

### 1. Local git hooks — after every commit and merge (no AI, instant)

`post-commit` and `post-merge` run `python run.py track`, which:

- tallies commits per teammate for the last 7 days → `state/commit_activity.json`
- saves a dated snapshot of the board → `state/snapshots/<date>.json`

That's it. No model call, no network, and `|| true` means a problem here can
never block a commit. This is the "busy work" — the running tally of who did what
and where the board stood each day — done for free.

**Install** (run from this folder, pointing at your *game* repo):

```bash
sh hooks/install.sh /path/to/your/game/repo
# Windows:
./hooks/install.ps1 -GameRepo C:\path\to\your\game\repo
```

It rewrites `__PRODUCER_DIR__` to this folder's path and drops the scripts into
your game repo's `.git/hooks/`. An existing hook of the same name is backed up to
`*.pre-producer.bak`.

> Git hooks are per-clone and are **not** committed, so each teammate runs the
> installer once. If you'd rather do it repo-wide, commit these two files to a
> `githooks/` folder in your game repo and set
> `git config core.hooksPath githooks`.

### 2. GitHub Actions — the weekly judgement pass (AI, but only speaks up when needed)

`deploy/producer-review.yml` (copy it into your game repo at
`.github/workflows/`) runs `python run.py review --auto --post`:

- **on a schedule** (Monday morning), and
- **when a story issue is closed** (a shipped story can change the picture).

`--auto` runs `producer/escalation.py` first. If nothing crosses a threshold in
`config/team.yaml`, the job writes a one-line "all clear" and stops — nobody is
pinged. If something does cross (schedule slipped, someone over capacity, a story
stalled, "done" without evidence, a new blocker), it runs only the relevant
agents and opens **one** GitHub issue that `cc`s the producer.

Set two repo secrets on your game repo: `ANTHROPIC_API_KEY` and (optional)
`DISCORD_WEBHOOK_URL`. `GITHUB_TOKEN` is provided automatically by Actions.

## The split, in one line

| | Runs | Calls AI | Interrupts a human |
|---|---|---|---|
| `run.py track` | every commit / merge | no | never |
| `run.py review --auto` | weekly + on issue close | only if a threshold trips | only if a threshold trips |
| `run.py review` (no `--auto`) | when you want the full picture | yes | it's a report you chose to read |
