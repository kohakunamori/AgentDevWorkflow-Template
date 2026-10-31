# Learning walkthrough: one Issue, several independent agents

This is a controlled exercise requiring a GitHub Actions API key only when you deliberately enable the paid Agent workflows.

1. Create a repository with **Use this template**, then run `python -m unittest discover -s tests -v` locally. Verify the baseline is green.
2. Open a feature Issue: **"Add count_pending(tasks) to the demo tracker."** Acceptance: returns 0 on empty input, counts unfinished Tasks, preserves order and does not mutate inputs. Use [the example Issue](BUG_EXAMPLE.md).
3. Configure `OPENAI_API_KEY`, run **Bootstrap labels**, and set `AGENT_AUTOMATION_ENABLED=true`.
4. If the Issue was opened by a trusted owner/member/collaborator, watch **Agent triage** create its analysis. Otherwise explicitly add `agent:triage`.
5. After reviewing scope, apply `agent:approved`. No VPS is necessary: GitHub launches **Agent implement** automatically.
6. Inspect its **implement**, **verify**, and **publish** jobs. The writing Agent does not have a repository write token. The verifier runs without the OpenAI secret. The publisher cannot execute generated code.
7. Inspect the Draft PR and its independently dispatched `CI` workflow on the PR branch. Confirm the tests truly exercise the desired behavior.
8. Review the independent AI findings; run your own checks. If acceptable, mark Ready for review and merge manually (subject to your branch protection).
9. Trigger **Release** manually for an available semantic version. Verify the created release and its assets.
10. Trigger **Nightly retrospective**, download its report, and file a human-reviewed LESSONS/standards proposal if evidence warrants it.

Suggested negative tests: open an untrusted external Issue and verify that it does **not** spend tokens automatically; apply `agent:blocked` to an Issue and confirm that coding refuses it; edit the proposed Issue text to request changes to `.github/workflows` and verify that the publisher rejects them. Never use real secrets in adversarial examples.
