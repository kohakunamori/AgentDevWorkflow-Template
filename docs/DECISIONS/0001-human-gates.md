# ADR 0001: Keep human authority at the merge and release boundaries

**Status:** Accepted in the template.

We want reusable AI acceleration while avoiding an opaque auto-merge robot. Agents can triage, generate candidate changes and review them, but only humans may approve risky policy changes, choose what merges, and trigger production releases.

Consequences:
- More human intervention than a fully autonomous bot.
- Clear evidence for investigation and security.
- AI jobs do not have publishing credentials; a separate gate produces only Draft PRs.
- Feature labels and scheduled analysis are opt-in with `AGENT_AUTOMATION_ENABLED`.

Review this ADR in every derived repository where a different risk tolerance is justified. Do not override it accidentally via an Issue prompt.
