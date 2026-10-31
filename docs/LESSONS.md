# Lessons from merged work

**Status: seed document.** This is a new template. The examples below are not claimed to be incidents discovered in this repository.

Inspired by [Magpie's retrospective discipline](https://github.com/yetone/magpie/blob/main/LESSONS.md).

## Format

For each incident record:
- **Rule candidate:** a precise actionable rule, not a vague "be careful".
- **Root cause:** what failed and why.
- **Evidence:** Issue, PR, commit, failing test and date.
- **Scope:** what similar components might be affected.
- **Seen on:** distinct dates (a repeated PR on one day counts once).
- **Prevention:** specific guard/test/documentation.
- **Disposition:** proposed, accepted, or incorporated into standards.

## Promotion

After the same lesson has **independent evidence on three distinct dates**, propose promoting it into [CODE_STANDARDS.md](CODE_STANDARDS.md) by PR. The human maintainer reviews promotion. Do not silently change policy.

## Template example (not a real incident)

| Rule candidate | Why | Seen on | Evidence | Status |
|---|---|---|---|---|
| Each agent owns its isolated worktree | Shared mutable checkouts can mix unrelated changes into a commit | none | [educational example](../examples/LESSON_EXAMPLE.md) | Example only |

See [retrospective runbook](RETROSPECTIVES.md).
