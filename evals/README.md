# Evals

These test `producer/evidence.py` — the deterministic layer — not the LLM.

The LLM's wording changes run to run; asserting on it is a losing game. But every
number the agents are told to cite is computed here, so if the arithmetic is
right and the prompts demand citations, the agent output is anchored to something
checkable. That is what we test.

```bash
python evals/run_evals.py
```

## Adding a case

Make a folder under `cases/` with two files:

**`board.json`** — a hand-built board (same shape as
`fixtures/sample_project/board.json`) that isolates one situation.

**`expected.yaml`** —

```yaml
description: what this case is about
as_of: "2026-11-10"          # the date evidence is computed against

expect:                       # exact-match on dotted paths into the evidence dict
  schedule.verdict: red
  schedule.stories_remaining: 6

include_ids:                  # these ids MUST appear in the named list
  aging_stories: [ST-104]
  blocked_stories: [ST-9]

overallocated_members: [Jules]   # each must have over_by > 0 in allocation
```

All three sections are optional. `expect` is strict equality, so if you assert a
float like `velocity_stories_per_sprint: 0.44` it has to match the rounding in
`build_evidence` exactly — run the case once and copy the real value in.

## Why this belongs in a production course

An agentic workflow you cannot test is one you cannot trust in front of a
stakeholder. The habit worth building: whatever the model is told to rely on,
compute it yourself and put a test around it.
