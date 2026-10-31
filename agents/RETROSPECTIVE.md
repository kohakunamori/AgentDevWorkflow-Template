# Retrospective Agent — prompt contract

Read docs/LESSONS.md, docs/RETROSPECTIVES.md and `agent-context.json` (the recent git history and discussion excerpts).

Analyze the evidence for repeated fixes, stale review SHA, red tests shipped, overly broad changes, missing tests, incorrect assumptions and inadequate release checks.

Return Markdown containing:
- Time window and sources actually examined.
- Candidate lessons with evidence links or commit SHAs.
- Root-cause confidence: verified / likely / unknown.
- Specific guardrails or tests that would prevent recurrence.
- Whether a lesson has been seen on three **distinct dates** (only if evidence supports it).
- Suggested Issues/PRs for human review; do not silently change standards.
- Known gaps in your analysis.

Do not invent incidents or infer a failure merely from a fix-style commit subject.
