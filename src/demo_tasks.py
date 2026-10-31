"""Tiny dependency-free demo for the Issue -> Agent -> PR -> CI workflow."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True, slots=True)
class Task:
    title: str
    completed: bool = False


def add_task(tasks: Iterable[Task], title: str) -> list[Task]:
    """Return a new list with a non-blank task appended."""
    cleaned = title.strip()
    if not cleaned:
        raise ValueError("task title must not be blank")
    return [*tasks, Task(title=cleaned)]


def complete_task(tasks: Iterable[Task], title: str) -> list[Task]:
    """Mark matching tasks complete without mutating existing tasks."""
    result: list[Task] = []
    for task in tasks:
        if task.title == title:
            result.append(Task(title=task.title, completed=True))
        else:
            result.append(task)
    return result


def list_tasks(tasks: Iterable[Task], *, include_completed: bool = True) -> list[Task]:
    """Return tasks in original order, optionally filtering completed entries."""
    return [task for task in tasks if include_completed or not task.completed]


# Teaching exercise: implement count_pending(tasks) via an Issue.
