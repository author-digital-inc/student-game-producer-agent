"""Thin wrapper around the Claude API, plus an offline MOCK mode for the classroom.

Why a wrapper at all: every agent calls Claude the same way (a system prompt +
one user message, no tools), so the call lives in exactly one place. That also
makes it trivial to (a) run the whole pipeline offline with canned responses and
(b) log every prompt so students can see what the agent actually received.

MOCK mode is the default whenever ANTHROPIC_API_KEY is unset. It reads a canned
response from fixtures/sample_project/mock_llm/<agent>.md so `python run.py demo`
works immediately after `pip install`, with no key and no cost.
"""

from __future__ import annotations

import os
import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
MOCK_DIR = REPO_ROOT / "fixtures" / "sample_project" / "mock_llm"

DEFAULT_MODEL = os.environ.get("PRODUCER_MODEL", "claude-opus-5")


def is_live() -> bool:
    """True when we should call the real API. --live on the CLI sets PRODUCER_LIVE=1."""
    forced = os.environ.get("PRODUCER_LIVE") == "1"
    return bool(os.environ.get("ANTHROPIC_API_KEY")) and forced


def _mock(agent: str) -> str:
    path = MOCK_DIR / f"{agent}.md"
    if not path.exists():
        return f"[MOCK mode: no canned response file at {path}]"
    return path.read_text(encoding="utf-8").strip()


def run_agent(agent: str, system_prompt: str, user_content: str, *,
              max_tokens: int = 16000, log_dir: pathlib.Path | None = None) -> str:
    """Send one system prompt + one user message to Claude and return the text.

    `agent` is a short slug ("risk_scanner") used for the MOCK filename and the
    prompt log. Nothing here uses tools — these agents only read and write text.
    """
    if log_dir is not None:
        log_dir.mkdir(parents=True, exist_ok=True)
        (log_dir / f"{agent}.prompt.md").write_text(
            f"# system\n\n{system_prompt}\n\n# user\n\n{user_content}\n",
            encoding="utf-8",
        )

    if not is_live():
        reason = "no ANTHROPIC_API_KEY" if not os.environ.get("ANTHROPIC_API_KEY") else "no --live flag"
        print(f"  [{agent}] MOCK response ({reason})", file=sys.stderr)
        return _mock(agent)

    # --- real call --------------------------------------------------------
    from anthropic import Anthropic  # imported lazily so MOCK runs need no install

    client = Anthropic()
    kwargs = dict(
        model=DEFAULT_MODEL,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_content}],
    )
    # Adaptive thinking + effort are the current API (Opus 5 / Sonnet 5). Older
    # anthropic packages reject these kwargs — fall back so a stale install still
    # runs instead of crashing a student mid-demo.
    try:
        resp = client.messages.create(
            thinking={"type": "adaptive"},
            output_config={"effort": "high"},
            **kwargs,
        )
    except TypeError:
        print(f"  [{agent}] note: anthropic SDK too old for adaptive thinking; "
              f"calling without it. `pip install -U anthropic` to fix.", file=sys.stderr)
        resp = client.messages.create(**kwargs)

    return "".join(b.text for b in resp.content if getattr(b, "type", None) == "text").strip()
