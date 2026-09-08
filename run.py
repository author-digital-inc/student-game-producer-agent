#!/usr/bin/env python
"""One entry point, three verbs.

    python run.py demo                 # offline tour against the sample project
    python run.py track                # refresh the books — NO AI, safe to run anytime
    python run.py review --week 8      # the weekly pass (writes a full report)
    python run.py review --auto --post # what the scheduled hook runs: silent unless
                                       # something needs a human, then notify once

`track` is the busy-work: it tallies commit activity and snapshots the board so
week-over-week comparison is possible. It never calls an LLM and never posts
anything. Git hooks call it after every commit/merge (see hooks/).

`review` is the judgement pass. With --auto it runs `producer/escalation.py`
first; if nothing crosses a threshold, no person is interrupted.

Nothing is sent anywhere without --post AND (for local runs) a typed confirmation.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pathlib
import subprocess
import sys

import yaml

from producer import escalation, state
from producer.agents import ac_checker, risk_scanner, sprint_planner, standup_synthesizer
from producer.board import load_board
from producer.evidence import build_evidence

REPO_ROOT = pathlib.Path(__file__).resolve().parent
FIXTURE = REPO_ROOT / "fixtures" / "sample_project"
ALL_AGENTS = ["standup_synthesizer", "ac_checker", "risk_scanner", "sprint_planner"]


# ---------------------------------------------------------------- helpers ----
def load_config(path: str) -> dict:
    raw = yaml.safe_load(pathlib.Path(path).read_text(encoding="utf-8"))
    return json.loads(json.dumps(raw, default=str))  # date objects -> "YYYY-MM-DD"


def utf8_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        except Exception:
            pass


def week_from_dates(config: dict) -> int:
    start = dt.date.fromisoformat(config["start_date"])
    return max((dt.date.today() - start).days // 7 + 1, 1)


def as_of_for_week(config: dict, week: int) -> str:
    start = dt.date.fromisoformat(config["start_date"])
    return (start + dt.timedelta(weeks=max(week - 1, 0))).isoformat()


def git_commit_activity(repo_path: str, since_days: int) -> list[dict]:
    """Aggregate `git log` for the game repo into per-author rows. Pure bookkeeping."""
    try:
        out = subprocess.run(
            ["git", "-C", repo_path, "log", f"--since={since_days} days ago",
             "--pretty=%an%x1f%s"],
            capture_output=True, text=True, check=True,
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"  (could not read git log at {repo_path}: {e})", file=sys.stderr)
        return []
    agg: dict[str, dict] = {}
    for line in out.splitlines():
        if "\x1f" not in line:
            continue
        author, subject = line.split("\x1f", 1)
        row = agg.setdefault(author, {"author": author, "count": 0, "last_message": ""})
        row["count"] += 1
        if not row["last_message"]:
            row["last_message"] = subject
    return sorted(agg.values(), key=lambda r: -r["count"])


def read_updates(week: int, board_kind: str) -> str:
    for base in ([REPO_ROOT] if board_kind == "github" else [FIXTURE, REPO_ROOT]):
        p = base / "updates" / f"week{week}.md"
        if p.exists():
            return p.read_text(encoding="utf-8")
    return (f"_No updates/week{week}.md found. Each team member should drop a short "
            f"written update there before the review._")


# ------------------------------------------------------------------ track ----
def cmd_track(args) -> int:
    config = load_config(args.config)
    board = load_board(args.board, args.fixture_board)

    if getattr(args, "fixture_commits", False):
        rows = json.loads((FIXTURE / "commits.json").read_text(encoding="utf-8"))
    else:
        rows = git_commit_activity(args.repo_path, args.since_days)

    state.save_commit_activity(rows)
    snap = state.save_snapshot(board.to_dict(), dt.date.today().isoformat())

    ev = build_evidence(board, config, as_of=dt.date.today().isoformat() if args.board == "github" else None)
    total_commits = sum(r["count"] for r in rows)
    print(f"tracked: {len(board.stories)} stories, "
          f"{ev['schedule']['stories_shipped']} shipped / {ev['schedule']['stories_remaining']} left; "
          f"{total_commits} commits/{args.since_days}d from {len(rows)} people; "
          f"snapshot -> {snap.relative_to(REPO_ROOT)}")
    return 0


# ----------------------------------------------------------------- review ----
def run_agent(name, board, config, updates, commits, last_run, as_of, log_dir):
    if name == "standup_synthesizer":
        return standup_synthesizer.run(board, config, updates, commits, last_run, log_dir=log_dir)
    if name == "ac_checker":
        return ac_checker.run(board, config, log_dir=log_dir)
    if name == "risk_scanner":
        return risk_scanner.run(board, config, as_of=as_of, log_dir=log_dir)
    if name == "sprint_planner":
        return sprint_planner.run(board, config, as_of=as_of, log_dir=log_dir)
    raise ValueError(name)


def schedule_block(ev: dict) -> list[str]:
    s = ev["schedule"]
    icon = {"green": "🟢", "amber": "🟡", "red": "🔴", "unknown": "⚪"}[s["verdict"]]
    out = [f"- **Status:** {icon} {s['verdict'].upper()}",
           f"- Shipped {s['stories_shipped']} / {s['stories_total']} · "
           f"{s['stories_remaining']} remaining ({s['person_days_remaining']} person-days)"]
    if s["velocity_stories_per_sprint"] is None:
        out.append(f"- Velocity: not measurable yet ({s['elapsed_sprints']} sprints elapsed)")
    else:
        out.append(f"- Velocity {s['velocity_stories_per_sprint']}/sprint -> projected "
                   f"{s['projected_sprints_to_finish']} more sprints vs {s['sprints_to_ship']} of runway")
    if ev["next_milestone"]:
        m = ev["next_milestone"]
        out.append(f"- Next milestone: **{m['name']}** in {m['weeks_away']} weeks ({m['date']})")
    return out


def assemble(week, ev, sections, triggers) -> str:
    titles = {
        "standup_synthesizer": "## Weekly status",
        "ac_checker": "## Acceptance-criteria gate",
        "risk_scanner": "## Risk register",
        "sprint_planner": "## Proposed next sprint (DRAFT — the team edits this)",
    }
    L = [f"# Producer review — Week {week} ({ev['project']})",
         f"_Generated {ev['as_of']} · sprint {ev['current_sprint']}_", "",
         "## Schedule at a glance", "", *schedule_block(ev), "", "---", ""]
    if triggers:
        L += ["## Why you're getting this", "",
              "The tracker flagged the following for a human. Everything else is being "
              "kept up to date automatically.", ""]
        for t in triggers:
            L.append(f"- **{t.headline}** — {t.detail}")
        L += ["", "---", ""]
    for key in ALL_AGENTS:
        if key in sections:
            L += [titles[key], "", sections[key].strip(), "", "---", ""]
    L += ["## What the tool did NOT decide",
          "",
          "- **Scope cuts** — *which* features get cut is the team's call.",
          "- **Sprint commitment** — the draft above is a starting point for planning.",
          "- **\"Done\" disputes** — if the AC gate and an owner disagree, a person looks at the build.",
          "- **Tone** — check the status is fair to everyone before sharing it.",
          "",
          "_Schedule numbers are computed. The prose is written by an LLM and can be "
          "wrong — check it against the board._"]
    return "\n".join(L) + "\n"


def notify(text: str, week: int, config: dict, triggers) -> None:
    gh = config.get("github", {}) or {}
    repo = os.environ.get("GITHUB_REPO") or gh.get("repo")
    token = os.environ.get("GITHUB_TOKEN")
    webhook = os.environ.get(config.get("discord_webhook_env", "DISCORD_WEBHOOK_URL"))
    headline = (f"Producer: {len(triggers)} thing(s) need you — week {week}"
                if triggers else f"Producer: all clear — week {week}")

    if webhook:
        import requests
        body = f"**{headline}**\n" + "\n".join(f"- {t.headline}" for t in triggers)
        requests.post(webhook, json={"content": body[:1900]}, timeout=30).raise_for_status()
        print("  notified: Discord")

    if repo and token and triggers:
        import requests
        producer = config.get("producer")
        issue_body = text + (f"\n\ncc @{producer}" if producer else "")
        r = requests.post(
            f"https://api.github.com/repos/{repo}/issues",
            headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"},
            json={"title": headline, "body": issue_body,
                  "labels": ["producer-agent"]},
            timeout=30,
        )
        r.raise_for_status()
        print(f"  notified: opened {repo}#{r.json()['number']}")

    if not webhook and not (repo and token):
        print("  (nothing configured to notify — set DISCORD_WEBHOOK_URL or GITHUB_REPO+GITHUB_TOKEN)")


def cmd_review(args) -> int:
    if args.live:
        os.environ["PRODUCER_LIVE"] = "1"
        if not os.environ.get("ANTHROPIC_API_KEY"):
            print("--live needs ANTHROPIC_API_KEY (copy .env.example to .env).", file=sys.stderr)
            return 2

    config = load_config(args.config)
    week = args.week or week_from_dates(config)
    as_of = None if args.board == "github" else as_of_for_week(config, week)
    board = load_board(args.board, args.fixture_board)

    ev = build_evidence(board, config, as_of=as_of)
    last = state.last_run()
    triggers = escalation.check(ev, last, config)

    print(f"\n=== Week {week} - {board.project} ===")
    print(json.dumps(ev["schedule"], indent=2))
    if args.auto:
        print(f"escalation: {len(triggers)} trigger(s)"
              + (": " + ", ".join(t.key for t in triggers) if triggers else ""))

    # decide which agents to run
    if args.auto:
        wanted = escalation.agents_for(triggers)
    else:
        wanted = ALL_AGENTS

    log_dir = REPO_ROOT / "reports" / f"week{week}_prompts"
    commits = state.load_commit_activity()
    if not commits and getattr(args, "fixture_commits", False):
        commits = json.loads((FIXTURE / "commits.json").read_text(encoding="utf-8"))
    if not commits:
        print("  (no tracked commit activity — run `python run.py track` first)", file=sys.stderr)
    updates = read_updates(week, args.board)

    sections = {}
    for name in wanted:
        print(f"running {name} ...")
        sections[name] = run_agent(name, board, config, updates, commits, last, as_of, log_dir)

    stamp = dt.date.today().isoformat()
    if args.auto and not triggers:
        report = (f"# Producer review — Week {week} ({board.project})\n"
                  f"_Generated {ev['as_of']}_\n\n## All clear\n\n"
                  + "\n".join(schedule_block(ev))
                  + "\n\nNothing crossed an escalation threshold. The board and commit "
                    "activity have been refreshed; no action needed.\n")
        out = REPO_ROOT / "reports" / f"week{week}-allclear.md"
    else:
        report = assemble(week, ev, sections, triggers if args.auto else [])
        out = REPO_ROOT / "reports" / f"week{week}.md"
    out.write_text(report, encoding="utf-8")
    state.record_run(week, ev, str(out.relative_to(REPO_ROOT)),
                     escalated=[t.key for t in triggers])
    print(f"\nwrote {out.relative_to(REPO_ROOT)}")

    if args.auto and not triggers:
        print("nothing needs a human this week.")
        if args.post:
            notify(report, week, config, [])
        return 0

    if args.post:
        if args.auto or args.yes:
            notify(report, week, config, triggers)
        else:
            print("\n" + report)
            if input('\ntype "post" to send this: ').strip().lower() == "post":
                notify(report, week, config, triggers)
            else:
                print("not sent.")
    else:
        print(f"review reports/week{week}.md ; add --post to notify the team")
    return 0


# ------------------------------------------------------------------- demo ----
def cmd_demo(args) -> int:
    print("Running the sample project offline (MOCK responses, no API key, no cost).\n")
    args.config = str(REPO_ROOT / "config" / "team.yaml")
    args.fixture_board = args.fixture_board or str(FIXTURE / "board.json")
    args.board = "local"
    args.live = False
    args.week = args.week or 6
    args.repo_path = "."
    args.since_days = 7
    args.fixture_commits = True   # demo reads fixtures/sample_project/commits.json
    cmd_track(args)
    print()
    return cmd_review(args)


# ------------------------------------------------------------------- main ----
def main() -> int:
    utf8_console()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--config", default=str(REPO_ROOT / "config" / "team.yaml"))
    common.add_argument("--board", choices=["local", "github"], default="local")
    common.add_argument("--board-file", "--fixture-board", dest="fixture_board",
                        default=str(FIXTURE / "board.json"),
                        help="path to your board.json (default: the sample project)")

    p_track = sub.add_parser("track", parents=[common], help="refresh the books (no AI)")
    p_track.add_argument("--repo-path", dest="repo_path", default=".",
                         help="path to the game's git repo (for commit activity)")
    p_track.add_argument("--since-days", dest="since_days", type=int, default=7)

    p_rev = sub.add_parser("review", parents=[common], help="the weekly judgement pass")
    p_rev.add_argument("--week", type=int, help="defaults to weeks since start_date")
    p_rev.add_argument("--auto", action="store_true",
                       help="only involve a human if escalation thresholds are crossed")
    p_rev.add_argument("--post", action="store_true", help="send the notification")
    p_rev.add_argument("--yes", action="store_true", help="skip the typed confirmation")
    p_rev.add_argument("--live", action="store_true", help="call the real Claude API")
    p_rev.add_argument("--repo-path", dest="repo_path", default=".")
    p_rev.add_argument("--since-days", dest="since_days", type=int, default=7)

    p_demo = sub.add_parser("demo", parents=[common], help="offline tour of a full review")
    p_demo.add_argument("--week", type=int)
    p_demo.add_argument("--auto", action="store_true")
    p_demo.add_argument("--post", action="store_true")
    p_demo.add_argument("--yes", action="store_true")
    p_demo.add_argument("--live", action="store_true")

    args = ap.parse_args()
    return {"track": cmd_track, "review": cmd_review, "demo": cmd_demo}[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
