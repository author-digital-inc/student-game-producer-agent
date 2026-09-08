"""The board: the single source of truth for what the team is building.

Two backends, same shape:
  * LocalBoard  — a JSON file. This is the default. It is what makes the repo
                  runnable on day one with no accounts. It is also completely
                  fine to use for a real 20-week project if the team keeps it
                  updated (commit it, review it in stand-up).
  * GitHubBoard — reads open/closed Issues from a real repo and maps labels to
                  story phases. Use this once the team already runs on GitHub
                  Issues and does not want a second list to maintain.

A "story" is one unit of player-facing work. Canonical fields:

    id                 "ST-012"
    title              "Enemy pathfinding around static obstacles"
    phase              one of PHASES below
    estimate_days      integer, rough person-days of work
    assignee           team member name (matches config/team.yaml), or null
    sprint             sprint id this story is committed to, e.g. "S3", or null
    acceptance_criteria list[str] — the checklist that defines "done"
    evidence           list[str] — PRs, playtest notes, build numbers proving AC
    blocked_by         list[str] — story ids that must ship first
    updated            "YYYY-MM-DD" — last time the phase or status changed
    history            list[{phase, date}] — phase transitions, oldest first
"""

from __future__ import annotations

import json
import os
import pathlib

# The pipeline a story moves through. Order matters: index = progress.
PHASES = [
    "Conception",
    "Design Review",
    "Implementation",
    "QA",
    "Polish",
    "Shipped",
]


class Board:
    def __init__(self, project: str, sprints: list[dict], current_sprint: str,
                 stories: list[dict]):
        self.project = project
        self.sprints = sprints
        self.current_sprint = current_sprint
        self.stories = stories

    # -- convenience views the evidence + agents use --------------------------
    def story(self, story_id: str) -> dict | None:
        return next((s for s in self.stories if s["id"] == story_id), None)

    def in_sprint(self, sprint_id: str) -> list[dict]:
        return [s for s in self.stories if s.get("sprint") == sprint_id]

    def not_shipped(self) -> list[dict]:
        return [s for s in self.stories if s["phase"] != "Shipped"]

    def shipped(self) -> list[dict]:
        return [s for s in self.stories if s["phase"] == "Shipped"]

    def to_dict(self) -> dict:
        return {
            "project": self.project,
            "sprints": self.sprints,
            "current_sprint": self.current_sprint,
            "stories": self.stories,
        }


class LocalBoard(Board):
    """Backed by a single JSON file."""

    def __init__(self, path: str | pathlib.Path):
        self.path = pathlib.Path(path)
        data = json.loads(self.path.read_text(encoding="utf-8"))
        super().__init__(
            project=data["project"],
            sprints=data.get("sprints", []),
            current_sprint=data.get("current_sprint", ""),
            stories=data.get("stories", []),
        )

    def save(self) -> None:
        self.path.write_text(json.dumps(self.to_dict(), indent=2) + "\n", encoding="utf-8")


class GitHubBoard(Board):
    """Backed by GitHub Issues on GITHUB_REPO.

    Mapping convention (all optional — missing labels just mean "no signal"):
      label "phase:implementation"  -> phase   (matched case-insensitively to PHASES)
      label "sprint:S3"             -> sprint
      label "est:5"                 -> estimate_days
      "Blocked by #41" in the body  -> blocked_by (["ST-41"])
      task list "- [x] ..." lines   -> acceptance_criteria (checked = has evidence)
    A closed issue is treated as phase "Shipped" regardless of labels.
    """

    def __init__(self, repo: str | None = None, token: str | None = None):
        import requests

        repo = repo or os.environ["GITHUB_REPO"]
        token = token or os.environ["GITHUB_TOKEN"]
        headers = {"Authorization": f"Bearer {token}",
                   "Accept": "application/vnd.github+json"}

        issues: list[dict] = []
        page = 1
        while True:
            r = requests.get(
                f"https://api.github.com/repos/{repo}/issues",
                headers=headers,
                params={"state": "all", "per_page": 100, "page": page},
                timeout=30,
            )
            r.raise_for_status()
            batch = [i for i in r.json() if "pull_request" not in i]
            issues.extend(batch)
            if len(batch) < 100:
                break
            page += 1

        stories = [self._issue_to_story(i) for i in issues]
        super().__init__(project=repo, sprints=[], current_sprint="", stories=stories)

    @staticmethod
    def _issue_to_story(issue: dict) -> dict:
        labels = [l["name"].lower() for l in issue.get("labels", [])]
        phase = "Conception"
        sprint = None
        estimate = 3
        for name in labels:
            if name.startswith("phase:"):
                want = name.split(":", 1)[1].replace("-", " ").strip()
                phase = next((p for p in PHASES if p.lower() == want), phase)
            elif name.startswith("sprint:"):
                sprint = name.split(":", 1)[1].upper()
            elif name.startswith("est:"):
                try:
                    estimate = int(name.split(":", 1)[1])
                except ValueError:
                    pass
        if issue["state"] == "closed":
            phase = "Shipped"

        body = issue.get("body") or ""
        ac, evidence = [], []
        for line in body.splitlines():
            s = line.strip()
            if s.startswith("- [x] "):
                ac.append(s[6:].strip())
                evidence.append("checked in issue task list")
            elif s.startswith("- [ ] "):
                ac.append(s[6:].strip())

        blocked_by = []
        for token in body.replace("\n", " ").split():
            if token.startswith("#") and token[1:].isdigit():
                blocked_by.append(f"ST-{token[1:]}")

        assignee = (issue.get("assignee") or {}).get("login")
        return {
            "id": f"ST-{issue['number']}",
            "title": issue["title"],
            "phase": phase,
            "estimate_days": estimate,
            "assignee": assignee,
            "sprint": sprint,
            "acceptance_criteria": ac,
            "evidence": evidence,
            "blocked_by": blocked_by,
            "updated": issue["updated_at"][:10],
            "history": [],
        }


def load_board(kind: str, local_path: str | pathlib.Path) -> Board:
    if kind == "local":
        return LocalBoard(local_path)
    if kind == "github":
        return GitHubBoard()
    raise ValueError(f"unknown board kind: {kind!r} (use 'local' or 'github')")
