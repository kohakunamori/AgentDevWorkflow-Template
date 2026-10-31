# Example retrospective entry (fictional)

**Rule candidate:** Verify a bug fix with a regression test that fails on the old implementation.

**Mechanism:** An implementation agent wrote a test that passed before the repair; it could not prove the defect was corrected.

**Evidence:** Not applicable — this is a teaching example, not a claim of a real PR or incident.

**Observed on distinct dates:** zero.

**Prevention:** In a clean worktree, run the new test on the parent commit; capture its behavioral failure, apply the fix, and run it again.

**Disposition:** Example only. Never promote this example to an incident without actual evidence.
