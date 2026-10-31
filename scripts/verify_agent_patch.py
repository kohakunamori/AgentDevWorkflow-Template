#!/usr/bin/env python3
"""Conservative validator for an AI-authored git diff.

Run BEFORE git apply. After applying, the publisher also validates the staged
paths with Git and refuses symlinks. This is a guardrail, not a sandbox.
"""
from __future__ import annotations

import os
from pathlib import Path
import re
import subprocess
import sys

ALLOWED_PREFIXES = ("src/", "tests/", "docs/", "examples/")
MAX_BYTES = 250_000
PATH_RE = re.compile(r"^diff --git a/([^\n]+) b/([^\n]+)$")


def validate_patch(path: Path) -> list[str]:
    if path.stat().st_size == 0:
        raise ValueError("patch is empty")
    if path.stat().st_size > MAX_BYTES:
        raise ValueError(f"patch exceeds {MAX_BYTES} bytes")
    contents = path.read_text(encoding="utf-8")
    if "GIT binary patch" in contents or "\x00" in contents:
        raise ValueError("binary patches are forbidden")
    if "new file mode 120000" in contents or "new mode 120000" in contents:
        raise ValueError("symlink patches are forbidden")
    if "rename from " in contents or "copy from " in contents:
        raise ValueError("renames and copies are outside this example's scope")
    paths: list[str] = []
    for line in contents.splitlines():
        if not line.startswith("diff --git "):
            continue
        match = PATH_RE.fullmatch(line)
        if not match:
            raise ValueError("unrecognized diff path encoding")
        left, right = match.groups()
        if left != right:
            raise ValueError("renames are forbidden")
        if any(bad in right for bad in ("\\", '"', "\r")):
            raise ValueError("unusual path encoding is forbidden")
        parts = Path(right).parts
        if right.startswith("/") or ".." in parts or not right.startswith(ALLOWED_PREFIXES):
            raise ValueError(f"disallowed path: {right}")
        paths.append(right)
    if not paths:
        raise ValueError("patch contains no recognized file changes")
    return paths


def verify_staged() -> None:
    files = subprocess.check_output(["git", "diff", "--cached", "--name-only", "-z"])
    for raw in filter(None, files.split(b"\0")):
        name = os.fsdecode(raw)
        if not name.startswith(ALLOWED_PREFIXES) or ".." in Path(name).parts:
            raise ValueError(f"disallowed staged path: {name}")
        mode = subprocess.check_output(
            ["git", "ls-files", "--stage", "--", name], text=True
        ).split(maxsplit=1)[0]
        if mode == "120000":
            raise ValueError(f"symlink staged: {name}")


if __name__ == "__main__":
    try:
        if len(sys.argv) == 3 and sys.argv[1] == "--staged":
            verify_staged()
        elif len(sys.argv) == 2:
            changed = validate_patch(Path(sys.argv[1]))
            print("Allowed paths:", *changed, sep="\n  ")
        else:
            raise ValueError("usage: verify_agent_patch.py PATCH | --staged ignore")
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(f"Rejected unsafe patch: {exc}", file=sys.stderr)
        raise SystemExit(1)
