# System design and lifecycle

The goal is **engineering leverage with auditability**, not unlimited autonomous authority.

## States

`NEW → TRIAGED → APPROVED → IMPLEMENTING → DRAFT_PR → CI_GREEN → REVIEWED → HUMAN_APPROVED → MERGED → RELEASED`.

A failure routes to `BLOCKED` with an Issue, reproduction evidence and an owner, not a fictitious green test. Every transition has an observable artifact: Issue comment, patch, PR, CI log, review, tag, or release.

## Components

| Component | Actor | Input | Artifact | Permission |
|---|---|---|---|---|
| Intake | Human / Issues | Bug / request | Issue | Issues write |
| Triage | Codex Agent | Issue JSON | Triage comment | Read-only AI job; write-only post job |
| Implementation | Codex Agent | Approved Issue | Workspace diff | Read-only GitHub token |
| Patch publisher | GitHub Actions | Validated patch | Draft PR | Contents + PR write |
| CI | Deterministic tests | PR commit | Pass / fail | Read-only |
| Independent review | Codex Agent | PR patch and base | Review comment | Read-only AI job |
| Merge | Human | CI + review | Merge commit | Human |
| Release | Human + Actions | Version and tested main | GitHub Release | Contents write |
| Retrospective | Codex Agent | Git history, PR titles | Lessons proposal | Read-only AI job |

## Isolation and provenance

One agent session per worktree. Do not let two agents commit from a single checkout, as changes may be attributed to the wrong task. Evidence must match exact tree and revision. For bug fixes, tests should fail before and pass after; reviewers should break the fix deliberately in an isolated sandbox.

The implementation job cannot push because credentials are read-only and checkout does not persist credentials. Its output is a patch. A distinct publishing job with a GitHub write token performs structural checks then opens a **Draft** PR. AI review similarly separates generation from posting.

## Human checkpoints

Humans authorize coding, CI/policy changes, secrets, protected files, dependencies, merges, and releases. Reducing privileges and using GitHub rulesets matters more than how many agents are running. See [security policy](REVIEW_POLICY.md).

## Retrospective rules

The nightly agent reviews recent commits and regressions, then creates a **proposal** with evidence links. No agent is allowed to rewrite standards based on a single incident. After three *separate dates* of a documented failure pattern, propose updating standards through a reviewed PR. See [lessons](LESSONS.md).
