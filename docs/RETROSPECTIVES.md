# Retrospective loop

1. Review the last 24 hours of merged commits, CI failures, PR follow-up fixes and released versions.
2. Identify cases requiring a second fix, missing a real test, shipping against stale head, or introducing unrelated code.
3. Confirm evidence before making causal claims. Ask which rule would have prevented the problem.
4. Group duplicates by **distinct dates**, not commits, and record an explicit "no evidence" when applicable.
5. Draft a Markdown summary proposing new lessons. The automated job **uploads an artifact only**; it does not rewrite the repo.
6. A maintainer opens an Issue/PR to update [LESSONS.md](LESSONS.md). After three separate dates, review promotion into [CODE_STANDARDS.md](CODE_STANDARDS.md).

The scheduled job runs only with `AGENT_AUTOMATION_ENABLED=true` and an API key. You can also launch it using `workflow_dispatch`.
