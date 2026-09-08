#!/usr/bin/env python
"""Evals for the deterministic layer.

We do NOT try to assert on the LLM's exact wording — that is not reproducible and
not the interesting part. We assert on producer/evidence.py, because every claim
the agents make is supposed to trace back to it. If the arithmetic is right and
the prompts tell the agent to cite the arithmetic, the agent output is anchored.

Each case is a folder under cases/ with:
    board.json      a hand-built board that exercises one situation
    expected.yaml   the evidence facts that must hold (with `as_of`)

Run:  python evals/run_evals.py
"""

from __future__ import annotations

import json
import pathlib
import sys

import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from producer.board import LocalBoard          # noqa: E402
from producer.evidence import build_evidence   # noqa: E402

CASES = pathlib.Path(__file__).resolve().parent / "cases"


def load_config() -> dict:
    raw = yaml.safe_load((REPO_ROOT / "config" / "team.yaml").read_text(encoding="utf-8"))
    return json.loads(json.dumps(raw, default=str))


def dotted(d: dict, path: str):
    cur = d
    for part in path.split("."):
        cur = cur[part]
    return cur


def check_case(case_dir: pathlib.Path, config: dict) -> list[str]:
    spec = yaml.safe_load((case_dir / "expected.yaml").read_text(encoding="utf-8"))
    board = LocalBoard(case_dir / "board.json")
    ev = build_evidence(board, config, as_of=spec["as_of"])
    fails: list[str] = []

    for path, want in (spec.get("expect") or {}).items():
        got = dotted(ev, path)
        if got != want:
            fails.append(f"    {path}: expected {want!r}, got {got!r}")

    for key, ids in (spec.get("include_ids") or {}).items():
        present = {row["id"] for row in ev[key]}
        missing = [i for i in ids if i not in present]
        if missing:
            fails.append(f"    {key}: missing {missing} (present: {sorted(present)})")

    for member in spec.get("overallocated_members") or []:
        row = next((r for r in ev["allocation"] if r["member"] == member), None)
        if not row or row["over_by"] <= 0:
            fails.append(f"    allocation: expected {member} over capacity, got {row}")

    return fails


def main() -> int:
    config = load_config()
    case_dirs = sorted(p for p in CASES.iterdir() if p.is_dir())
    if not case_dirs:
        print("no cases found under", CASES)
        return 1

    failed = 0
    for case_dir in case_dirs:
        fails = check_case(case_dir, config)
        if fails:
            failed += 1
            print(f"FAIL  {case_dir.name}")
            print("\n".join(fails))
        else:
            print(f"ok    {case_dir.name}")

    print(f"\n{len(case_dirs) - failed}/{len(case_dirs)} cases passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
