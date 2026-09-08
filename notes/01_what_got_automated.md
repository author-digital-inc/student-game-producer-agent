# Note 1 — What got automated

A producer's week is full of small mechanical tasks. Here's which ones this tool
takes over, and how.

| The busy-work task | How the tool does it | Runs when |
|---|---|---|
| "Who actually worked on what this week?" | `run.py track` reads `git log` and tallies commits per person | every commit / merge (git hook) |
| "Where did the board stand on Monday?" | `track` saves a dated copy of the board to `state/snapshots/` | every commit / merge |
| "Is the remaining work going to fit?" | `producer/evidence.py` computes velocity, projected finish, and runway from the board dates | every review |
| "Has anything stalled?" | `evidence.py` lists stories with no update in 10+ days | every review |
| "Is anyone overloaded?" | `evidence.py` adds up each person's committed days vs. their capacity | every review |
| "What's blocking what?" | `evidence.py` walks the `blocked_by` links | every review |
| "Did we do what we said last sprint?" | `agents/standup_synthesizer.py` checks last sprint's acceptance criteria against recorded evidence and the commit log | weekly review |
| "Write it all up" | `run.py` assembles one Markdown report | weekly review |
| "Tell the team" | `run.py review --post` opens one GitHub issue / posts to Discord | only when a human is needed |

None of the first six involve an AI at all — they're arithmetic and file-reading.
The AI only shows up for the "write it up in a way a person can act on" parts, and
even those only run when something is worth a person's attention (Note 3).

## Why bother automating the small stuff

Two reasons it matters more than it looks:

1. **It happens whether or not the producer has time.** The tally and the
   snapshot update on every commit. There's no "I'll catch up on the board
   Friday" — Friday's picture is already saved.
2. **It makes the scary number un-ignorable.** "We have 13 things left and finish
   1.2 per sprint, and 7.5 sprints of runway" is a sentence nobody on a stressed
   team says out loud on their own. The tool says it every week, in writing.
