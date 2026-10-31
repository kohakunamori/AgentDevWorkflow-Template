# Code standards

These are rules for both the implementer and the independent reviewer.

## Change design
- One Issue and one behavior change per PR. No unrelated refactoring or dependency updates hidden inside a bug fix.
- Reproduce the reporter's actual inputs and surface. Mark assumptions as assumptions.
- Follow input → logic → persisted state → output. Examine every sibling call site for the same bug class.
- The implementation and its documentation must agree; changed contracts require updated docs.
- A failed config read means unknown/error, never "empty" or "allowed". Preserve explicit user values.

## Testing
- Every bug fix gets a regression test that fails on the old behavior and passes on the corrected code; a compile failure or skipped test is not sufficient.
- Test observable outcomes, not only internal method calls. Include malformed, boundary, empty, interrupted and repeated inputs as relevant.
- Tests use controlled fixtures, isolate side effects, clean up resources and avoid live credentials/network services.
- Run project-wide checks after relevant targeted tests. Do not silently excuse a red test because it also fails on main.
- The test summary records **command, exit code, exact SHA, platform, PASS/FAIL/NOT_RUN/BLOCKED**. Never report unexecuted validation as success.

## Security
- Never run untrusted PR code with secrets or deployment/merge permissions.
- Never add secret-bearing logs, API keys, release credentials, unknown binaries or obfuscated blobs.
- CI, permissions, dependencies, installers, external endpoints and publishing code need a dedicated maintainer review.
- The default must not change a user's explicitly chosen configuration.

## Review
- Inspect whole diff, run tests and reproduce at the reviewed SHA.
- Revert the fix or mutate the behavior safely to check the test really catches it.
- On an updated PR head, previous AI/human evidence is stale; re-run/inspect.
- Release is separate from tagging; check actual published artifacts and user-visible behavior.
