# Example Issue — feature for the coding agent

**Title:** Add count_pending(tasks) to the demo task tracker

**Observed:** Users can list tasks but cannot obtain the total unfinished count.

**Expected:** `count_pending` should accept a sequence of Task instances, count only incomplete entries and avoid modifying source input. Return 0 for an empty sequence.

**Acceptance:**
- Empty list returns 0.
- Mixed completed and incomplete entries returns the correct count.
- Does not modify tasks or their order.
- Unit tests pass for all cases.

**Scope:** `src/demo_tasks.py`, `tests/test_demo_tasks.py`. Do not modify workflows or dependencies.

Open this example as a real GitHub Issue in your new repository to exercise Agent implement.
