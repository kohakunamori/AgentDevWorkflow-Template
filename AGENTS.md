# Instructions for coding agents

This repository demonstrates a **supervised, evidence-driven, multi-agent software development process**.

Read, in order: [current architecture and project goals](docs/WORKFLOW.md), [code standards](docs/CODE_STANDARDS.md), [lessons](docs/LESSONS.md), [security/review policy](docs/REVIEW_POLICY.md), then the relevant source and tests. Never assume another repository copied from this template uses the demo app as its product.

## Authority boundaries

- The maintainer owns product priorities, architecture decisions, credentials, release criteria, budgets and approvals.
- Agents may investigate Issues, propose plans, implement scoped code, add tests, independently review and prepare Draft PRs.
- Do not merge PRs, publish releases, add secrets, change CI permissions, rewrite policies, add dependencies, or invoke destructive infrastructure/hardware commands without explicit human authorization.
- Agent output is a proposal, not proof. Report real commands, exact SHA, results and untested cases. Do not fabricate verifications.
- When a request is ambiguous, use existing Issue context and project contracts; escalate genuine high-risk scope changes.

## Task workflow

1. Read the full Issue and comments, check duplicates, define acceptance and constraints.
2. Work in a separate branch/worktree; never share mutable working directories across agents.
3. Reproduce reported behavior before changing it. For a bug fix, write a regression that fails on the old implementation and passes after.
4. Make the minimal changes; examine other call sites and boundary cases; update applicable docs.
5. Run the project's actual checks. Separate NOT_RUN and BLOCKED from PASS.
6. Prepare a PR with objective, implementation notes, test evidence, risks, rollback and exact SHA.
7. Invite an independent reviewer. Re-review after updates. Human approval is mandatory for merge/release.
8. Record actionable follow-up Lessons with links to real evidence.

## Model-specific roles

- [Triage](agents/TRIAGE.md)
- [Implement](agents/IMPLEMENT.md)
- [Review](agents/REVIEW.md)
- [Retrospective](agents/RETROSPECTIVE.md)
- [Release](agents/RELEASE.md)

## Do not mistake a sample for a framework

`src/demo_tasks.py` is deliberately small so the workflows can be tested. In a derived repository, update commands, architecture, acceptance conditions and project-specific safety policies before using the template for production code.
