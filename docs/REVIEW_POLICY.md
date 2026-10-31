# Review policy and security gates

The AI reviewer is an *independent source of findings*, **not** a substitute for responsible human merge approval.

## First: harm scan (before executing code)

Stop and ask the maintainer if a PR modifies CI, build/release scripts, dependencies, external network calls, secrets or permission scopes; introduces remote execution, opaque blobs, credential reads, telemetry or destructive commands; or touches hardware/cloud infrastructure.

Never execute untrusted PR code in an environment that exposes API keys or elevated network permissions.

## Then: evidence-driven review

1. Check Issue intent and latest comments; compare **all** changed paths to the stated scope.
2. Inspect upstream assumptions, data flow, failure paths and sibling code.
3. Verify the specific regression fails before and passes after in a safe environment.
4. Run broader tests on a current base; record which commands really ran.
5. Review interfaces, backward compatibility, rollback and documentation.
6. Comment with SHA, risks, evidence, missing checks and a decision suggestion.
7. Let a human maintainer decide merge, policy exceptions and release.

## Trust boundary in Actions

AI model jobs have `contents:read` and no write-capable repository token. A separate job receives narrowly scoped `issues:write` / `pull-requests:write` to post already generated text; implementation uses a patch artifact and an allowlist before a privileged publisher can create a draft PR.

These are layered mitigations, not a proof of perfect security. Treat all AI output as untrusted, and configure branch rulesets independently.

## Contributor credit

Credit externally reported root causes, fixtures and patches where used. Agents may recommend human review of spam or suspicious submissions, but should not automatically blacklist people.
