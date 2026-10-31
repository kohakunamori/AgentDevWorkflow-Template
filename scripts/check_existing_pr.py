#!/usr/bin/env python3
"""Avoid opening another generated PR while a previous proposal remains open."""
import json
from pathlib import Path
import re
import sys


def existing_agent_prs(prs: list[dict], issue: int) -> list[int]:
    prefix = f"agent/issue-{issue}-run-"
    result = []
    for pr in prs:
        branch = pr.get("headRefName", "")
        if isinstance(branch, str) and branch.startswith(prefix):
            number = pr.get("number")
            if type(number) is int:
                result.append(number)
    return result


def main() -> int:
    try:
        prs = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
        issue = int(sys.argv[2])
        if issue <= 0 or not isinstance(prs, list):
            raise ValueError("invalid inputs")
        found = existing_agent_prs(prs, issue)
    except (ValueError, OSError, IndexError) as exc:
        print(f"Invalid PR query: {exc}", file=sys.stderr)
        return 2
    if found:
        print(f"Existing proposal for Issue #{issue}: PR(s) {found}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
