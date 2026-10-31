#!/usr/bin/env python3
"""Persistent, single-instance, conservative GitHub Issue -> Actions dispatcher.

The controller is *not* a code execution environment. It watches approved
issues and dispatches an isolated GitHub-hosted Agent workflow for each one.
All state is stored in SQLite to survive restarts. No third-party dependencies.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path
import re
import sqlite3
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen
from uuid import uuid4

REPO_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
INFLIGHT = ("dispatching", "running", "uncertain")
DONE = ("pr-created", "failed", "cancelled")
API = "https://api.github.com"


def log(event: str, **details: object) -> None:
    print(json.dumps({"time": datetime.now(timezone.utc).isoformat(),
                      "event": event, **details}, sort_keys=True), flush=True)


@dataclass(frozen=True)
class Config:
    repository: str
    database: str = "/data/controller.sqlite3"
    label: str = "agent:approved"
    poll_seconds: int = 90
    max_parallel: int = 2
    max_daily: int = 10
    max_attempts: int = 2
    retry_seconds: int = 900
    enabled: bool = False
    workflow: str = "agent-implement.yml"

    def __post_init__(self) -> None:
        if not REPO_PATTERN.fullmatch(self.repository):
            raise ValueError("GITHUB_REPOSITORY must be owner/repository")
        if not 15 <= self.poll_seconds <= 3600:
            raise ValueError("poll_seconds must be between 15 and 3600")
        if not 1 <= self.max_parallel <= 12:
            raise ValueError("max_parallel must be 1..12")
        if not 1 <= self.max_daily <= 100:
            raise ValueError("max_daily must be 1..100")
        if not 1 <= self.max_attempts <= 5:
            raise ValueError("max_attempts must be 1..5")
        if not 60 <= self.retry_seconds <= 86400:
            raise ValueError("retry_seconds must be 60..86400")

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            repository=os.environ["GITHUB_REPOSITORY"],
            database=os.getenv("CONTROLLER_DATABASE", "/data/controller.sqlite3"),
            label=os.getenv("CONTROLLER_APPROVAL_LABEL", "agent:approved"),
            poll_seconds=int(os.getenv("CONTROLLER_POLL_SECONDS", "90")),
            max_parallel=int(os.getenv("CONTROLLER_MAX_PARALLEL", "2")),
            max_daily=int(os.getenv("CONTROLLER_MAX_DAILY", "10")),
            max_attempts=int(os.getenv("CONTROLLER_MAX_ATTEMPTS", "2")),
            retry_seconds=int(os.getenv("CONTROLLER_RETRY_SECONDS", "900")),
            enabled=os.getenv("CONTROLLER_DISPATCH_ENABLED", "false").lower() == "true",
        )


class GitHubError(Exception):
    pass


class GitHubAPI:
    def __init__(self, token: str, repository: str):
        if not token:
            raise ValueError("GH_TOKEN is required")
        if not REPO_PATTERN.fullmatch(repository):
            raise ValueError("invalid repository")
        self.repository = repository
        self.prefix = "/repos/" + repository
        self.token = token

    def request(self, method: str, path: str, data: object | None = None) -> object:
        # All paths are internal constants and validated numeric IDs.
        payload = None if data is None else json.dumps(data).encode("utf-8")
        req = Request(API + path, data=payload, method=method, headers={
            "Accept": "application/vnd.github+json",
            "Authorization": "Bearer " + self.token,
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "AgentDevWorkflow-Controller/1",
            "Content-Type": "application/json",
        })
        try:
            with urlopen(req, timeout=25) as response:
                body = response.read()
                return json.loads(body) if body else {}
        except HTTPError as exc:
            # Never log request bodies or authentication headers.
            raise GitHubError(f"GitHub {method} failed (HTTP {exc.code})") from exc
        except (URLError, TimeoutError, OSError) as exc:
            raise GitHubError(f"GitHub {method} transport error: {type(exc).__name__}") from exc

    def approved_issues(self, label: str) -> list[int]:
        found: list[int] = []
        for page in range(1, 11):
            query = urlencode({"state": "open", "labels": label, "per_page": 100,
                               "page": page, "sort": "created", "direction": "asc"})
            data = self.request("GET", self.prefix + "/issues?" + query)
            if not isinstance(data, list):
                raise GitHubError("invalid issue listing")
            for item in data:
                if not isinstance(item, dict) or "pull_request" in item:
                    continue
                labels = {x.get("name") for x in item.get("labels", []) if isinstance(x, dict)}
                number = item.get("number")
                if isinstance(number, int) and label in labels and "agent:blocked" not in labels:
                    found.append(number)
            if len(data) < 100:
                break
        return found

    def dispatch(self, number: int, request_id: str) -> int | None:
        # The workflow must be on the repository default branch.
        data = self.request(
            "POST",
            self.prefix + "/actions/workflows/agent-implement.yml/dispatches",
            {"ref": "main", "inputs": {"issue_number": str(number),
                                      "request_id": request_id}},
        )
        if not isinstance(data, dict):
            raise GitHubError("invalid dispatch response")
        run_id = data.get("workflow_run_id")
        return run_id if isinstance(run_id, int) else None

    def find_run(self, request_id: str) -> int | None:
        query = urlencode({"event": "workflow_dispatch", "per_page": 100})
        data = self.request("GET", self.prefix +
                            "/actions/workflows/agent-implement.yml/runs?" + query)
        if not isinstance(data, dict):
            raise GitHubError("invalid workflow run list")
        for run in data.get("workflow_runs", []):
            if "[req:" + request_id + "]" in run.get("display_title", ""):
                return int(run["id"])
        return None

    def run(self, run_id: int) -> dict:
        data = self.request("GET", self.prefix + "/actions/runs/" + str(run_id))
        if not isinstance(data, dict):
            raise GitHubError("invalid workflow run response")
        return data


class Store:
    def __init__(self, path: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                issue_number INTEGER PRIMARY KEY,
                status TEXT NOT NULL,
                attempts INTEGER NOT NULL DEFAULT 0,
                request_id TEXT,
                run_id INTEGER,
                changed_at REAL NOT NULL,
                eligible_after REAL NOT NULL DEFAULT 0
            )
        """)
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS dispatches (
                request_id TEXT PRIMARY KEY,
                issue_number INTEGER NOT NULL,
                created_at REAL NOT NULL
            )
        """)
        self.db.commit()

    def get(self, number: int) -> dict | None:
        row = self.db.execute("SELECT * FROM tasks WHERE issue_number=?", (number,)).fetchone()
        return dict(row) if row else None

    def states(self, *states: str) -> list[dict]:
        if not states:
            return []
        placeholders = ",".join("?" for _ in states)
        return [dict(row) for row in self.db.execute(
            "SELECT * FROM tasks WHERE status IN (" + placeholders + ")", states
        )]

    def in_flight(self) -> int:
        return len(self.states(*INFLIGHT))

    def daily_count(self, now: float) -> int:
        today = datetime.fromtimestamp(now, timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        ).timestamp()
        return int(self.db.execute(
            "SELECT COUNT(*) FROM dispatches WHERE created_at>=?", (today,)
        ).fetchone()[0])

    def reserve(self, number: int, request_id: str, now: float) -> None:
        with self.db:
            self.db.execute("""
                INSERT INTO tasks(issue_number,status,attempts,request_id,run_id,changed_at,eligible_after)
                VALUES(?, 'dispatching', 1, ?, NULL, ?, 0)
                ON CONFLICT(issue_number) DO UPDATE SET
                    status='dispatching', attempts=tasks.attempts+1,
                    request_id=excluded.request_id, run_id=NULL,
                    changed_at=excluded.changed_at, eligible_after=0
            """, (number, request_id, now))
            self.db.execute(
                "INSERT INTO dispatches(request_id,issue_number,created_at) VALUES(?,?,?)",
                (request_id, number, now),
            )

    def update(self, number: int, status: str, now: float,
               run_id: int | None = None, eligible_after: float = 0) -> None:
        with self.db:
            self.db.execute(
                "UPDATE tasks SET status=?, changed_at=?, run_id=COALESCE(?,run_id),"
                " eligible_after=? WHERE issue_number=?",
                (status, now, run_id, eligible_after, number),
            )

    def reset(self, number: int) -> None:
        with self.db:
            self.db.execute("DELETE FROM tasks WHERE issue_number=?", (number,))

    def close(self) -> None:
        self.db.close()


def tick(config: Config, api: GitHubAPI, store: Store, now: float) -> None:
    # First reconcile all work. A dispatch with uncertain outcome is never
    # blindly retried: it could have succeeded before a connection failed.
    for task in store.states("dispatching", "running"):
        number = task["issue_number"]
        if not task["run_id"]:
            run_id = api.find_run(task["request_id"])
            if run_id:
                store.update(number, "running", now, run_id=run_id)
                task["run_id"] = run_id
            elif now - task["changed_at"] > 600:
                store.update(number, "uncertain", now)
                log("requires_manual_reconciliation", issue=number)
                continue
            else:
                continue
        run = api.run(task["run_id"])
        if run.get("status") != "completed":
            continue
        if run.get("conclusion") == "success":
            store.update(number, "pr-created", now)
            log("finished", issue=number, status="pr-created", run_id=task["run_id"])
        elif task["attempts"] < config.max_attempts:
            store.update(number, "retry-wait", now,
                         eligible_after=now + config.retry_seconds)
            log("retry_scheduled", issue=number, attempt=task["attempts"])
        else:
            store.update(number, "failed", now)
            log("failed", issue=number, run_id=task["run_id"])

    active = store.in_flight()
    daily = store.daily_count(now)
    for number in api.approved_issues(config.label):
        current = store.get(number)
        if current and current["status"] not in ("retry-wait",):
            continue
        if current and current["eligible_after"] > now:
            continue
        if active >= config.max_parallel or daily >= config.max_daily:
            break
        if not config.enabled:
            log("dry_run_candidate", issue=number)
            continue
        request_id = uuid4().hex
        store.reserve(number, request_id, now)
        active += 1
        daily += 1
        try:
            run_id = api.dispatch(number, request_id)
        except GitHubError:
            # Explicit error and ambiguous network errors are both kept for
            # human reconciliation to prevent duplicate expensive runs.
            store.update(number, "uncertain", now)
            log("dispatch_uncertain", issue=number)
            continue
        if run_id:
            store.update(number, "running", now, run_id=run_id)
        log("dispatched", issue=number, run_id=run_id or "pending", attempt=1 if not current else current["attempts"] + 1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--once", action="store_true", help="Poll and exit")
    parser.add_argument("--health", action="store_true", help="Check SQLite availability")
    parser.add_argument("--status", action="store_true", help="Print local scheduler tasks")
    parser.add_argument("--reset-issue", type=int, metavar="NUMBER",
                        help="Allow an Issue to be dispatched again after manual reconciliation")
    args = parser.parse_args()
    config = Config.from_env()
    store = Store(config.database)
    if args.health:
        store.db.execute("SELECT 1")
        return 0
    if args.status:
        for row in store.db.execute("SELECT * FROM tasks ORDER BY issue_number"):
            print(json.dumps(dict(row), sort_keys=True))
        return 0
    if args.reset_issue:
        store.reset(args.reset_issue)
        log("manually_reset", issue=args.reset_issue)
        return 0
    api = GitHubAPI(os.environ["GH_TOKEN"], config.repository)

    # Single-host single-writer. Docker Compose starts one controller; do not
    # deploy multiple controllers against one database on different hosts.
    lock_path = config.database + ".lock"
    with open(lock_path, "a", encoding="utf-8") as lockfile:
        try:
            fcntl.flock(lockfile.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            log("another_controller_running")
            return 2
        log("controller_started", repository=config.repository,
            dispatch_enabled=config.enabled, max_parallel=config.max_parallel)
        while True:
            try:
                tick(config, api, store, time.time())
            except (GitHubError, sqlite3.Error) as exc:
                log("tick_error", error_type=type(exc).__name__)
            if args.once:
                break
            time.sleep(config.poll_seconds)
    return 0


if __name__ == "__main__":
    sys.exit(main())
