# 24/7 Issue Controller (optional)

This is the **always-on missing layer** in the template. It is a small Python service, deployable to Linux NAS/VPS with Docker Compose. No Python dependencies, no webhook public port, no exposed HTTP endpoint.

## Real architecture

`GitHub Issue + agent:approved` → persistent SQLite queue → Controller dispatches `agent-implement.yml` → each GitHub-hosted runner uses its own isolated filesystem, Codex invocation and per-run branch → guarded Draft PR → CI → optional independent Agent review → **human merge**.

The Controller does **not** run Codex locally or clone untrusted code. It is a dispatcher. Workers run in **GitHub-hosted ephemeral Actions VMs**, not as shared processes on your NAS. That offers isolation without running Docker-in-Docker or exposing the NAS Git credential to LLM processes.

## Quick start (Linux)

1. Copy `server/.env.example` to `server/.env`, set `GITHUB_REPOSITORY` and `GH_TOKEN`. Restrict permissions with `chmod 600 server/.env`.
2. Use a **fine-grained GitHub token scoped to exactly one repository**, with **Issues: read, Actions: write**, plus implicit metadata read. For 24/7 production, prefer renewable GitHub App installation credentials; this educational version uses a token you provision and rotate.
3. Make sure the target repo has the `Agent implement` workflow on `main`, and configure `OPENAI_API_KEY` in GitHub **Actions Secrets**. The server **never** needs that OpenAI secret.
4. Run `docker compose --env-file server/.env -f server/compose.yml up -d --build`.
5. Observe `docker compose --env-file server/.env -f server/compose.yml logs -f`. With `CONTROLLER_DISPATCH_ENABLED=false` (default), it only prints `dry_run_candidate`; no paid runs.
6. After reviewing logs, change `CONTROLLER_DISPATCH_ENABLED=true`, restart the Compose service, and add the `agent:approved` label to an approved open Issue.
7. Inspect the Draft PR; GitHub Actions runs tests and can trigger review if the optional automation variable is set. Merge only after human validation.

## Operational commands

```bash
docker compose --env-file server/.env -f server/compose.yml ps
docker compose --env-file server/.env -f server/compose.yml logs --tail=100
docker compose --env-file server/.env -f server/compose.yml exec controller python -m server.controller --status
# Only after checking no run is active and inspecting GitHub history:
docker compose --env-file server/.env -f server/compose.yml exec controller python -m server.controller --reset-issue 123
```

The controller polls every 90 seconds. SQLite survives Docker restarts via a named volume. It limits concurrent Issues, total dispatches per UTC day, and per-Issue attempts; failed Actions receive delayed retry. Successful Agent implementation marks the Issue as `pr-created`; **it does not assert that the PR was merged or that its CI passed**. It never retries an ambiguous dispatch automatically.

## Trigger details

- **Manual approval is the production gate:** Issues with `agent:approved` are eligible. Removing the label stops new scheduling, not an already-running workflow (cancel it from Actions).
- **Deduplication:** one task record per Issue, unique request ID for every dispatch; each workflow run has a request ID in its display title to allow reconciliation.
- **Isolation:** GitHub Actions creates fresh execution environments and the implementation workflow creates an Issue/run-specific branch. Unlike sharing a folder on one server, workers do not share checkout or package state.
- **Human merge:** no auto-merge or unattended production release.
- **Idempotency after restarts:** the queue is persistent. The Controller reconnects to known run IDs; for old 204-style dispatch responses it searches workflow run titles.
- **Uncertainty:** if GitHub accepted a dispatch but the Controller lost its response, it marks the Issue uncertain instead of paying for a potentially duplicate run. Operators must reconcile and reset manually.
- **Usage budget:** `CONTROLLER_MAX_DAILY` limits dispatched workflows, not OpenAI token cost. Set actual API budget alerts in the OpenAI platform.

## Security

- Controller only needs GitHub Issues read and Actions write; keep your OpenAI API key in GitHub Actions, **never** in this server.
- Docker has no published ports, runs non-root, a read-only root filesystem and a persistent SQLite volume.
- Do not run multiple replicas against the same DB. The Linux flock is single-host coordination, not distributed consensus.
- GitHub Issue contents are untrusted. A human adding `agent:approved` authorizes model spending, not arbitrary access to secrets or CI modifications.
- The template provides best-effort safety checks, not perfect isolation guarantees. For third-party PRs, the reviewer never checks out and executes the PR head.
- SQLite records can contain operational metadata; back up the volume as needed and avoid making it publicly accessible.

## Known scope limits

This is a **polling controller + remote workers**, not a full local Kubernetes/container agent cluster. GitHub workflow output success means "draft PR proposed"; the final human approval and release remain separate. GitHub itself runs event-triggered jobs without any always-on server; use the Controller only when you need central queue limits, persistent status or consistent 24/7 scheduling.

Future enhancement: a signed GitHub App webhook → controller queue (lower latency) and optional isolated container workers on the NAS, with network/storage quotas and renewable credentials. These are deliberately not enabled or claimed implemented in v1.
