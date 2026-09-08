"""producer — an agentic producer workflow for a 5-person student game team.

Read these in order to understand the system:
  1. producer/board.py       — where the work lives (local JSON or GitHub Issues)
  2. producer/evidence.py    — deterministic metrics computed in plain Python
  3. producer/agents/        — four small agents that turn evidence into judgement
  4. run.py                  — the entry point: `track` (no AI) and `review`
                               (agentic, escalation-gated) tie it together

The design rule the whole repo follows: Python gathers the facts, the agent
interprets them, and a human makes every decision that changes the plan.
"""

__all__ = ["board", "evidence", "llm", "state"]
