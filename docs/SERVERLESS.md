# Serverless GitHub Actions orchestration

**No private server required.** GitHub events wake isolated ephemeral Actions runners automatically. Nothing has to remain online on your own devices.

## Event-to-Agent routing

| Event | Workflow | Conditions |
|---|---|---|
| `issues.opened` or `issues.reopened` | Agent triage | Automation enabled; Issue author is owner/member/collaborator |
| `issues.labeled: agent:triage` | Agent triage | Automation enabled; a trusted user added the label |
| `issues.labeled: agent:approved` | Agent implement | Automation enabled; Issue open, not blocked; no existing Agent PR |
| `workflow_dispatch` | Agent triage / implement / review | Manually authorized by a user with appropriate repository permissions |
| `pull_request.opened/synchronize/reopened` | Agent review | Automation enabled; trusted same-repository PR (not an untrusted fork) |
| `pull_request.labeled: agent:review` | Agent review | Automation enabled; **same-repository PR only**. For forks, use manual dispatch. |
| `workflow_run.completed` for Agent implement | Agent review | Automation enabled; implementation succeeded |
| `workflow_dispatch` after Draft PR creation | CI | Publisher starts CI on the **actual PR branch** |
| Scheduled daily | Nightly retrospective | Automation enabled; artifact proposal, not direct policy edits |

Public outsiders may report Bugs without being able to spend your API budget. Fork PRs are not automatically reviewed using a secret-bearing `pull_request` workflow; maintainers can use **Actions → Agent review → Run workflow** with the PR number (trusted default-branch checkout, diff as untrusted data). Maintainers can explicitly label and authorize their reports for triage or implementation.

## Standard setup (no VPS)

1. Create repository with **Use this template**.
2. In Settings → Secrets and variables → Actions, set **secret** `OPENAI_API_KEY`.
3. Set Actions repository **variable** `AGENT_AUTOMATION_ENABLED=true` only when you consent to paid model calls.
4. Run the **Bootstrap labels** workflow once.
5. Open a new trusted-author Issue to test automatic triage, or apply `agent:triage` to an existing Issue.
6. Apply `agent:approved` to start the Coding Agent. Each Issue gets a separately queued GitHub-hosted runner.
7. Review its results in **Actions** and the newly opened **Draft PR**.
8. Verify the independently dispatched CI check and AI review. Approve and merge **manually**.

The model runs through `openai/codex-action@v1`, which uses a separate OpenAI API credential. A Codex/ChatGPT/Magpie subscription does not supply API billing for these Actions.

## Isolation and privilege table

| Phase | Token privileges | OpenAI secret | Executes candidate code? |
|---|---|---|---|
| Triage/review analysis | Contents/Issues/PR read | Yes, via restricted Codex proxy | No |
| Implement | Contents/Issues/PR read | Yes, restricted Codex sandbox | Agent may run local tests |
| Verify | Contents read only | **No** | Yes, in a disposable Runner |
| Publish | Contents, PR and Actions write | **No** | **No**, only validates and applies patch |
| CI on generated branch | Contents read only | **No** | Yes, in a disposable Runner |
| Release | Contents write | No | Only after explicit human dispatch |

Patch publication rejects binary/oversized changes, symlinks and changes outside `src/`, `tests/`, `docs/`, and `examples/`. Any workflow, build/publish script, dependency or credential change requires a human-authored and reviewed PR.

### Why explicitly dispatch CI?

Events caused by `GITHUB_TOKEN` generally do not initiate a second workflow run, except for designated exceptions such as `workflow_dispatch` and `repository_dispatch`. A Draft PR created by an Actions token can therefore lack normal `pull_request` CI. Here the publisher invokes `gh workflow run ci.yml --ref <pr-branch>`, so CI actually runs on the proposed head.

### Multiple simultaneous Issues

GitHub provides independent runners and queues. `concurrency` serializes implementation attempts for the same Issue; separate Issue numbers can run concurrently. The implement job also refuses to spend model tokens if an open generated PR already exists for that Issue.

This is **not** a full persistent cross-Issue scheduler. There is no built-in token-budget accounting or guarantee of atomic deduplication across externally triggered controllers. Set OpenAI platform usage budgets/alerts. For persistent queue state and independent retry limits, use the [optional Controller](../server/README.md), and do not enable competing dispatchers simultaneously.

## Cost and safety notes

- A repository-wide opt-in prevents accidental paid model calls, but is not a dollar cap.
- Never grant write/run privileges to untrusted reporters solely for this workflow.
- Codex Action checks trigger actor repository permissions, except for explicitly configured trusted bot actors. AI-generated text, Issue bodies, PR diffs and files are untrusted inputs.
- A GitHub-hosted Runner ends after the workflow; no data is shared through a long-lived mutable worktree.
- Do not assume CI success means the Agent reviewed every possible edge case.
- GitHub schedules run best-effort and can be delayed.

## When would a VPS/NAS be useful?

Only if you need a unified persistent scheduler for large backlogs, cross-repository priority, budgets or per-Issue retries, or want to run your own containerized model workers. The [Docker Controller](../server/README.md) is optional.
