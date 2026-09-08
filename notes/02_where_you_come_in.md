# Note 2 — Where you come in

The tool is built around one line: **the computer watches, you decide.** Here is
what "you decide" actually covers, and why a person is genuinely better at each.

## 1. What to cut

When the review says "projected 10.8 sprints of work, 7.5 of runway", the fix is
almost always to remove scope. The tool will even suggest *categories* of cut
(fewer features vs. simpler versions of each). It will not pick the features,
because that choice is about what your game *is* — the thing your team cares about
and an algorithm has no opinion on. Cutting the boss fight vs. cutting the upgrade
system is a design conversation.

## 2. How to rebalance

The tool can tell you Jules is committed to 13 days of work in a 9-day sprint. It
can't know that Sam is faster at combat code, or that Devon offered to take the
audio task off Jules' plate, or that Marcus is blocked anyway and has spare time.
Moving work between people depends on things that live in the team's heads.

## 3. Whether "done" is really done

The acceptance-criteria gate flags a story as "no evidence recorded". Maybe
there's a build the person forgot to link. Maybe the criterion was written badly.
Maybe it genuinely isn't done. Resolving that means a person looking at the actual
game with the person who built it. The tool's job is to make sure the question
gets asked; answering it is human.

## 4. Tone and fairness

The status write-up names individuals: "2 commits this week, both stubs". That can
be a fair observation or an unfair one depending on context the tool doesn't have
(was that person sick? handed off a huge PR the day before? blocked?). A human
reads the report before it's shared and fixes anything that lands wrong.

## The pattern

In every case, the automation does the part that is *lookup and arithmetic*, and
stops exactly where the next step needs **judgement, context, or
accountability** — three things you don't hand to a script. That boundary isn't a
limitation of this particular tool; it's where the boundary belongs in any
agentic workflow.
