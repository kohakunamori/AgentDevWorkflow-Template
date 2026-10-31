# Setup & enablement checklist

## 1. Create a repository from this template

Choose **Use this template**. Pick a new name and appropriate visibility. Copy files, not old Issues/PRs/labels/secret values. GitHub template duplication doesn't automatically install labels, secrets, environment protections or branch protection rules.

## 2. Local smoke test

- Python >= 3.11 and Git.
- Run `python -m unittest discover -s tests -v`, then `python scripts/check_template.py`.
- `gh auth status` if you want to use bootstrap scripts; never paste auth tokens into Issues or chat.

## 3. Enable GitHub Actions

- Settings → Actions → General: allow chosen trusted actions. If policies restrict actions, approve `openai/codex-action@v1`, `actions/checkout@v4`, `actions/upload-artifact@v4`, `actions/download-artifact@v4`, and `actions/setup-python@v5`.
- Add repository **Actions secret** `OPENAI_API_KEY` with a dedicated API key. Do not paste keys into any source file or Issues.
- Optional repository **variable** `AGENT_AUTOMATION_ENABLED=true`: enables label-triggered triage, review, and scheduled retrospective. Leave unset or false to prevent automatic API spending. Manually dispatched Agent runs still require the secret and authorization.
- Run the **Bootstrap labels** workflow once. It creates `agent:triage`, `agent:review`, `type:bug`, `type:feature` and `status:blocked`. Only users who can apply labels can trigger the event-driven agents.
- Set your budget and API usage alerts in the OpenAI platform separately. The sample does not enforce an API spend cap.

## 4. Protect main (GitHub settings, not replicated in template)

- Settings → Branch rules / Rulesets: require a PR, required CI check, and (preferably) at least one real human approval before merging to `main`.
- Restrict force pushes, branch deletion and bypass rules. Set CODEOWNERS to real people, not a bot, once your repository has maintainers.
- Set default workflow permissions to the minimum your organization allows. Individual jobs request explicit permissions; the Code Publishing job needs contents and pull-requests write.

## 5. Try the demonstration

- Open a `Bug report` Issue using the template.
- Add `agent:triage` after reviewing the report (requires variable enabled) and inspect the comment.
- Actions → **Agent implement** → Run workflow → specify Issue number. The action should produce a Draft PR.
- Let CI run, add `agent:review` to that PR; inspect the AI's independent review.
- Confirm behavior yourself, then merge manually. Run **Release** manually using a semantic version.

## 6. Optional always-on controller

The [24/7 Controller](../server/README.md) is the missing central scheduler for continuous Issue processing. It polls maintainer-approved Issues and dispatches independent GitHub Actions workers. It keeps persistent state, handles retries and limits concurrency; it is **not** needed for manual operation.

## 7. Safety caveats

- External Issue text, PR diffs and Codex-generated patches are untrusted inputs. The sample isolates model jobs from jobs with write tokens; its patch publisher only permits source/tests/docs paths and rejects symlinks and oversized patches. Never relax these guards without a security review.
- The Codex action controls its API proxy and sandbox; always review [upstream security notes](https://github.com/openai/codex-action#safety-strategy).
- A real project must customize build/test commands, provenance checks and environments. Do not run third-party install scripts or privileged deployment inside AI jobs.

## Troubleshooting

- No agent run? Check the Actions workflow was enabled, label exists, maintainer applied it, `AGENT_AUTOMATION_ENABLED` is exactly `true`, and `OPENAI_API_KEY` is set.
- Codex error? Review the failed job logs (avoid posting sensitive details); verify API billing and permissions.
- No PR? Inspect `agent.patch` and the publish job's safety guard. Changes outside allowlisted directories are intentionally rejected. A no-op Codex response also produces no PR.
- Reused template with different language? Update CI and source/tests allowlist before invoking the coding agent.
