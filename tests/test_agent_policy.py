import unittest

from scripts.validate_agent_issue import validate_issue
from scripts.check_existing_pr import existing_agent_prs


class AgentIssuePolicyTests(unittest.TestCase):
    def issue(self, labels=(), state="OPEN"):
        return {
            "state": state,
            "number": 42,
            "labels": [{"name": name} for name in labels],
        }

    def test_approved_issue_is_allowed(self):
        validate_issue(self.issue(["agent:approved"]), True)

    def test_unapproved_issue_is_not_automatically_coded(self):
        with self.assertRaisesRegex(ValueError, "agent:approved"):
            validate_issue(self.issue(), True)
        validate_issue(self.issue(), False)

    def test_blocked_and_closed_issues_are_refused(self):
        for label in ["agent:blocked", "status:blocked"]:
            with self.subTest(label=label), self.assertRaises(ValueError):
                validate_issue(self.issue(["agent:approved", label]), True)
        with self.assertRaises(ValueError):
            validate_issue(self.issue(["agent:approved"], state="CLOSED"), True)

    def test_generated_prs_match_exact_issue_prefix(self):
        prs = [
            {"number": 7, "headRefName": "agent/issue-42-run-100"},
            {"number": 8, "headRefName": "agent/issue-420-run-101"},
            {"number": 9, "headRefName": "feature/other"},
        ]
        self.assertEqual(existing_agent_prs(prs, 42), [7])
        self.assertEqual(existing_agent_prs(prs, 420), [8])


if __name__ == "__main__":
    unittest.main()
