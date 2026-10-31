import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class WorkflowContractTests(unittest.TestCase):
    def read(self, filename):
        return (ROOT / ".github" / "workflows" / filename).read_text(encoding="utf-8")

    def test_issue_and_pr_events_are_present(self):
        triage = self.read("agent-triage.yml")
        implement = self.read("agent-implement.yml")
        review = self.read("agent-review.yml")
        self.assertIn("types: [opened, reopened, labeled]", triage)
        self.assertIn("types: [labeled]", implement)
        self.assertIn("github.event.label.name == 'agent:approved'", implement)
        self.assertIn("types: [opened, reopened, synchronize, ready_for_review, labeled]", review)
        self.assertIn("github.event.pull_request.head.repo.full_name == github.repository", review)

    def test_secret_bearing_jobs_cannot_publish(self):
        implement = self.read("agent-implement.yml")
        sections = {
            label: implement.split(f"  {label}:\n", 1)[1].split("\n  ", 1)[0]
            for label in ("implement", "verify", "publish")
        }
        self.assertIn("openai-api-key:", sections["implement"])
        self.assertNotIn("contents: write", sections["implement"])
        self.assertNotIn("openai-api-key:", sections["verify"])
        self.assertIn("contents: read", sections["verify"])
        self.assertNotIn("openai-api-key:", sections["publish"])
        self.assertIn("contents: write", sections["publish"])
        self.assertIn("gh workflow run ci.yml", sections["publish"])

    def test_no_privileged_external_pr_checkout(self):
        for path in (ROOT / ".github" / "workflows").glob("*.yml"):
            content = path.read_text(encoding="utf-8")
            self.assertNotIn("pull_request_target:", content, path.name)
            self.assertNotIn("gh pr merge", content, path.name)


if __name__ == "__main__":
    unittest.main()
