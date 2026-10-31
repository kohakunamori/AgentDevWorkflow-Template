# Setup guide

## Fast path: GitHub-hosted, no server

1. Click **Use this template** on the source repository. Template copies contain code, not its old Issues, labels, secrets, branch rules or runtime credentials.
2. Test locally: `python -m unittest discover -s tests -v`, `python scripts/check_template.py`. Python 3.11+ recommended.
3. Ensure GitHub Actions is enabled. Approve needed actions per your organization rules: `openai/codex-action@v1`, checkout, Python setup, upload/download artifact.
4. Add **Actions secret** `OPENAI_API_KEY`. Use a purpose-specific API key with suitable usage/billing limits, never an Issue text or repository variable.
5. Run **Bootstrap labels** from Actions once. This creates `agent:triage`, `agent:approved`, `agent:review`, `agent:blocked` and task labels.
6. Set repository Actions variable `AGENT_AUTOMATION_ENABLED=true` **only when ready to spend API tokens**. With it off, human `workflow_dispatch` actions can still be used.
7. New trusted-author Issues auto-trigger triage. External reporters need a maintainer-applied `agent:triage`. To start Coding Agent, a maintainer adds `agent:approved` to an open Issue.
8. Watch **Agent implement** jobs: `implement` generates a patch, `verify` tests it without secrets, and `publish` makes a Draft PR if verification succeeded. Normal `pull_request` events from Actions Bot might not trigger; the publisher explicitly dispatches CI on the new PR branch.
9. The independent review workflow comments on eligible PRs/updates and successful agent-created PRs. **Review the actual changes yourself** before merge.
10. Run **Release** manually from the intended verified main branch and inspect published assets. The retrospective workflow generates an artifact for manual LESSONS promotion.

## Recommended manual configuration

Use GitHub Settings → Rulesets / Branch protection to require a PR, required `CI` check(s), and human approval before `main` changes. Restrict pushes, force pushes and bypasses. The template cannot transfer these repository settings.

Set OpenAI platform budget alerts. The feature flag is an on/off switch, **not** a daily token/dollar budget. Keep `OPENAI_API_KEY` in GitHub Actions Secrets; nothing in the optional Controller requires it.

## Learning exercise

Follow [WALKTHROUGH.md](../examples/WALKTHROUGH.md) for a small `count_pending` feature. The demo deliberately avoids third-party package installs, expensive systems and side effects.

## Troubleshooting

- **No AI workflow?** Verify repository Actions are enabled, `AGENT_AUTOMATION_ENABLED` equals `true`, the triggering actor is trusted, the label matches, and the API secret exists. Public nonmember Issues do not auto-spend.
- **Implement is skipped?** Verify the Issue is open, not blocked, and not already represented by an open `agent/issue-N-run-*` PR. The Issue label is a human authorization gate.
- **Verify failed?** Read the exact red test. Nothing is published until the verification job succeeds.
- **No PR?** Inspect the verified patch paths, producer artifact and publisher log. A no-op patch or forbidden workflow edit is rejected.
- **PR generated but no CI?** Search Actions for a `CI` `workflow_dispatch` run on the `agent/issue-N-run-ID` branch. This bypasses GitHub's `GITHUB_TOKEN` event suppression.
- **No independent review?** Fork PRs cannot use the secret in ordinary `pull_request` workflows; manually dispatch **Agent review** from the Actions tab with the PR number. Otherwise enable automation and check that the PR/run matches an eligible trigger. Codex Action enforces actor permissions; the workflow-run review only allowlists `github-actions[bot]`.
- **Private server needed?** No. The [optional Controller](../server/README.md) adds persistent backlog state and quotas but should not be started alongside direct issue-label dispatch for the same Issues.

Refer to [SERVERLESS.md](SERVERLESS.md) for the complete trigger/permission matrix.
