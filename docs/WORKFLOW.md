# Agent-driven engineering workflow

The goal is **auditable engineering throughput with safe boundaries**, not unrestricted autonomy.

## Lifecycle

`ISSUE → TRIAGED → MAINTAINER_APPROVED → AGENT_IMPLEMENT → VERIFIED → DRAFT_PR → CI → INDEPENDENT_REVIEW → HUMAN_MERGE → MANUAL_RELEASE → LESSONS`

- A trusted author's Issue opens: triage may run automatically (opt-in).
- A maintainer marks the Issue `agent:approved`: implementation launches immediately through GitHub Actions.
- Each job gets a fresh GitHub-hosted runner. Coding cannot push; it exports a patch artifact.
- A distinct **read-only verifier** runs tests with the proposed code and without API credentials.
- A distinct **publisher** validates and applies the patch with scoped write permission, then opens a Draft PR and explicitly dispatches PR-head CI.
- A read-only model job independently reviews the PR diff; its comment is not a GitHub approval.
- A human controls merging, releasing, dependency/security policy, and credential changes.
- A scheduled retrospective proposes new lessons based on actual evidence.

The default pipeline is **serverless**: there is no required NAS/VPS. Refer to [SERVERLESS.md](SERVERLESS.md). The [optional SQLite Controller](../server/README.md) adds central queuing, not basic event triggering.

## Agent responsibilities

| Role | Input | Output | Minimum evidence |
|---|---|---|---|
| Triage | Full Issue and comments | Reproduction/plan comment | Reproduction steps and unknowns |
| Implement | Authorized Issue | Candidate patch | Regression and actual executed tests |
| Verify | Patch artifact | Test run log | Passing command/exit code at exact source |
| Publish | Validated patch | Draft PR | Allowed paths, tree and head SHA |
| Review | Trusted base + PR diff | Independent advice | Concrete findings, untested cases |
| Maintainer | CI and review record | Merge/release decision | Real approval and risk acceptance |
| Retrospective | Recent commits/PRs | Lessons proposal | Linked incidents, dates, prevention |

## Isolation and multi-agent consistency

Never share an editable checkout across simultaneous Agents. GitHub runners isolate files, tool processes and branches per Issue; the generated branch is named `agent/issue-<number>-run-<id>`. GitHub Actions `concurrency` serializes duplicate work for one Issue. If a prior generated Draft PR is open, the coding workflow stops before incurring model cost.

Errors and uncertain claims should become actionable Issues, not ignored red checks. When reviewing a bug fix, verify that the proposed regression fails on old code and passes on the candidate code. Tests and docs must correspond to the reviewed SHA.

## Governance

All automatic paid paths require opt-in through `AGENT_AUTOMATION_ENABLED`. New Issues from public outsiders do not directly trigger paid models. Sensitive paths (`.github/`, scripts, dependencies, releases, permissions, infrastructure, secrets) require explicit human involvement. The generated patch validator allows only `src/`, `tests/`, `docs/` and `examples/`.

For [CODE_STANDARDS.md](CODE_STANDARDS.md) updates, record at least three independent dates of the same verified failure pattern in [LESSONS.md](LESSONS.md), then propose a reviewed PR. Do not automatically change engineering rules based on a single AI opinion.
