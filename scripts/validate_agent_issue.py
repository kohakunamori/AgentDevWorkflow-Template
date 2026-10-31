#!/usr/bin/env python3
"""Validate trusted Issue metadata before spending tokens on coding."""
import argparse
import json
from pathlib import Path
import sys


def validate_issue(data: dict, require_label: bool) -> None:
    if data.get("state") != "OPEN":
        raise ValueError("Issue is not open")
    number = data.get("number")
    if type(number) is not int or number <= 0:
        raise ValueError("Issue number is invalid")
    labels = {
        item.get("name")
        for item in data.get("labels", [])
        if isinstance(item, dict)
    }
    if "agent:blocked" in labels or "status:blocked" in labels:
        raise ValueError("Issue is explicitly blocked")
    if require_label and "agent:approved" not in labels:
        raise ValueError("Event-triggered coding requires agent:approved")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("context", type=Path)
    parser.add_argument("--require-label", action="store_true")
    args = parser.parse_args()
    try:
        validate_issue(
            json.loads(args.context.read_text(encoding="utf-8")),
            args.require_label,
        )
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"Refusing to run: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
