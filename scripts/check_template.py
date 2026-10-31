#!/usr/bin/env python3
"""Lightweight template integrity check using only Python's standard library."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "README.md",
    "docs/SERVERLESS.md",
    "scripts/validate_agent_issue.py",
    "scripts/check_existing_pr.py",
    "tests/test_agent_policy.py",
    "server/controller.py",
    "server/Dockerfile",
    "server/compose.yml",
    "server/README.md",
    "AGENTS.md",
    "docs/SETUP.md",
    "docs/WORKFLOW.md",
    "docs/CODE_STANDARDS.md",
    "docs/LESSONS.md",
    "docs/REVIEW_POLICY.md",
    ".github/workflows/ci.yml",
    ".github/workflows/agent-triage.yml",
    ".github/workflows/agent-implement.yml",
    ".github/workflows/agent-review.yml",
    ".github/workflows/nightly-retrospective.yml",
    ".github/workflows/bootstrap-labels.yml",
    ".github/workflows/release.yml",
    "agents/TRIAGE.md",
    "agents/IMPLEMENT.md",
    "agents/REVIEW.md",
    "agents/RETROSPECTIVE.md",
    "src/demo_tasks.py",
    "tests/test_demo_tasks.py",
)


def main() -> int:
    missing = [path for path in REQUIRED if not (ROOT / path).is_file()]
    for path in missing:
        print("MISSING:", path, file=sys.stderr)
    if missing:
        return 1
    print(f"Template integrity: PASS ({len(REQUIRED)} required files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
