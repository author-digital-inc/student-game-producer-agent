# Start here — you don't need to know anything about AI

You're on a 5-person game team. One of you is the producer. This tool does the
part of the producer job that is pure bookkeeping, so the human producer can
spend their time on the parts that actually need a person.

## What "the bookkeeping" means

Every week a producer normally has to:

- chase everyone for a status update
- figure out who actually did what (scroll the commits, cross-check the board)
- notice that a task hasn't moved in two weeks
- notice that someone has way too much on their plate
- do the math on whether the remaining work fits the time left
- write all of that up

Most of that is mechanical. This tool does it automatically. What's left — *what
do we cut*, *how do we rebalance*, *is this actually done* — it hands to you.

## The two ways it runs

**All the time, quietly.** Once you install the git hooks (`hooks/README.md`),
every time anyone on the team commits or pulls, the tool updates its running
tally: who committed what this week, and a saved snapshot of where the board
stood. No AI is involved. It takes a fraction of a second and you won't notice
it.

**Once a week, with judgement.** A GitHub Action runs `run.py review --auto`. It
checks a short list of "does a human need to see this?" conditions (in
`config/team.yaml`). If everything's fine, it says "all clear" and that's it. If
something's off — the schedule slipped, a task stalled, someone's overloaded, a
task is marked nearly-done but nothing proves it — it writes a short report and
opens **one** GitHub issue tagging the producer, explaining exactly what needs a
decision.

That's the whole idea: **the computer watches; you decide.**

## Try it right now (2 minutes, no setup, no cost)

```bash
pip install -r requirements.txt
python run.py demo
```

That runs against a made-up sample team ("Starfall") that's having a rough week.
Read `reports/week6.md`. Then read
[`../example_run/escalation_week.md`](../example_run/escalation_week.md) and
[`../example_run/silent_week.md`](../example_run/silent_week.md) — the same tool,
one week where it pings a human and one where it stays quiet.

## Point it at your actual game (about 15 minutes)

1. **Fill in `config/team.yaml`.** Your real names and roles. Your project's
   start date, the final-presentation date, and any milestone dates. For
   `capacity_days_per_sprint`, put how many days each person *actually* spends
   hands-on the game in a two-week stretch, after classes and meetings. Guess
   low.

2. **Pick how the board works:**
   - *Easiest:* keep a `board.json` file (copy `fixtures/sample_project/board.json`
     as a template), edit it in a 15-minute "board grooming" at the start of each
     week, and commit it.
   - *If you already use GitHub Issues:* add the labels described at the top of
     `producer/board.py` (`phase:implementation`, `sprint:S3`, `est:5`, and
     "Blocked by #41" in the issue body) and run with `--board github`.

3. **Install the hooks:** `sh hooks/install.sh /path/to/your/game/repo`
   (each teammate does this once).

4. **Add the weekly Action:** copy `deploy/producer-review.yml` into your game
   repo at `.github/workflows/`, and add an `ANTHROPIC_API_KEY` secret. Done.

5. Each week, everyone drops three sentences in `updates/week<N>.md`. The Monday
   review turns those + the commits + the board into the status, and only bothers
   you if there's a call to make.

## What it will get wrong

It will sometimes misread a messy update, or phrase something unfairly, or be too
confident. The schedule *numbers* are just arithmetic and are reliable; the
*sentences* are written by an AI and need a human eye before you share them. The
report says this at the bottom every time. Treat it like a sharp intern: very
useful, still needs checking.

## What it will never do on its own

Cut a feature. Reassign work. Move a task to "done". Send anything to your
instructor. Those are yours. See
[`../notes/02_where_you_come_in.md`](../notes/02_where_you_come_in.md).
