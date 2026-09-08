"""Local, human-readable memory of what the tool has seen.

  state/history.json        one row per `review` — verdict, counts, blocked ids
  state/commit_activity.json aggregated commits per author (written by track.py)
  state/snapshots/<date>.json  a copy of the board each time track.py runs

All git-ignored: this is run output, not source. A student should be able to open
any of these files and read them.
"""

from __future__ import annotations

import datetime as dt
import json
import pathlib

STATE_DIR = pathlib.Path(__file__).resolve().parent.parent / "state"
HISTORY = STATE_DIR / "history.json"
SNAP_DIR = STATE_DIR / "snapshots"


def _read(path: pathlib.Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def load_history() -> list[dict]:
    return _read(HISTORY, [])


def last_run() -> dict | None:
    hist = load_history()
    return hist[-1] if hist else None


def record_run(week: int, evidence: dict, report_path: str, *,
               escalated: list[str] | None = None) -> None:
    STATE_DIR.mkdir(exist_ok=True)
    hist = load_history()
    sched = evidence["schedule"]
    hist.append({
        "week": week,
        "at": dt.datetime.now().isoformat(timespec="seconds"),
        "as_of": evidence["as_of"],
        "verdict": sched["verdict"],
        "velocity": sched["velocity_stories_per_sprint"],
        "stories_shipped": sched["stories_shipped"],
        "stories_remaining": sched["stories_remaining"],
        "blocked_ids": [s["id"] for s in evidence["blocked_stories"]],
        "escalated": escalated or [],
        "report": report_path,
    })
    HISTORY.write_text(json.dumps(hist, indent=2) + "\n", encoding="utf-8")


def save_snapshot(board_dict: dict, as_of: str) -> pathlib.Path:
    SNAP_DIR.mkdir(parents=True, exist_ok=True)
    path = SNAP_DIR / f"{as_of}.json"
    path.write_text(json.dumps(board_dict, indent=2) + "\n", encoding="utf-8")
    return path


def save_commit_activity(rows: list[dict]) -> pathlib.Path:
    STATE_DIR.mkdir(exist_ok=True)
    path = STATE_DIR / "commit_activity.json"
    path.write_text(json.dumps({
        "updated": dt.datetime.now().isoformat(timespec="seconds"),
        "by_author": rows,
    }, indent=2) + "\n", encoding="utf-8")
    return path


def load_commit_activity() -> list[dict]:
    return _read(STATE_DIR / "commit_activity.json", {}).get("by_author", [])
