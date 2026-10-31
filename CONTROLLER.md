# Controller operations: example status

The standard implementation service is in [server/README.md](server/README.md). An issue becomes executable only after a maintainer adds the `agent:approved` label. The default controller is in dry-run mode. GitHub-hosted runners provide task isolation; no Codex instance is permanently running while idle.

For an all-day **local agent** rather than hosted workflow dispatch, a separate isolated per-task container executor and renewable GitHub App authentication would be needed. This version intentionally avoids sharing mutable checkouts or live credentials between tasks.
