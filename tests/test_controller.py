import tempfile
import unittest
from pathlib import Path

from server.controller import Config, GitHubError, Store, tick


class FakeAPI:
    def __init__(self, numbers):
        self.numbers = list(numbers)
        self.sent = []
        self.runs = {}
        self.fail_dispatch = False

    def approved_issues(self, label):
        return self.numbers

    def dispatch(self, number, request_id):
        self.sent.append((number, request_id))
        if self.fail_dispatch:
            raise GitHubError("Simulated lost connection")
        run_id = len(self.sent) + 1000
        self.runs[run_id] = {"status": "in_progress"}
        return run_id

    def run(self, run_id):
        return self.runs[run_id]

    def find_run(self, request_id):
        for i, (_, req) in enumerate(self.sent):
            if request_id == req and not self.fail_dispatch:
                return i + 1001
        return None


class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = Store(str(Path(self.temp.name) / "test.sqlite3"))
        self.addCleanup(self.store.close)
        self.config = Config(repository="owner/example", max_parallel=1, max_daily=3,
                             max_attempts=2, retry_seconds=60, enabled=True)
        self.t0 = 1793500000.0

    def test_dispatch_is_deduplicated_and_parallel_limit_is_enforced(self):
        api = FakeAPI([10, 20])
        tick(self.config, api, self.store, self.t0)
        self.assertEqual([number for number, _ in api.sent], [10])
        tick(self.config, api, self.store, self.t0 + 1)
        self.assertEqual(len(api.sent), 1)
        api.runs[1001] = {"status": "completed", "conclusion": "success"}
        tick(self.config, api, self.store, self.t0 + 2)
        self.assertEqual([number for number, _ in api.sent], [10, 20])
        self.assertEqual(self.store.get(10)["status"], "pr-created")

    def test_failure_retries_after_backoff_and_stops_after_limit(self):
        api = FakeAPI([30])
        tick(self.config, api, self.store, self.t0)
        api.runs[1001] = {"status": "completed", "conclusion": "failure"}
        tick(self.config, api, self.store, self.t0 + 1)
        self.assertEqual(self.store.get(30)["status"], "retry-wait")
        tick(self.config, api, self.store, self.t0 + 20)
        self.assertEqual(len(api.sent), 1)
        tick(self.config, api, self.store, self.t0 + 62)
        self.assertEqual(len(api.sent), 2)
        api.runs[1002] = {"status": "completed", "conclusion": "failure"}
        tick(self.config, api, self.store, self.t0 + 63)
        self.assertEqual(self.store.get(30)["status"], "failed")
        tick(self.config, api, self.store, self.t0 + 500)
        self.assertEqual(len(api.sent), 2)

    def test_dry_run_never_reserves_or_dispatches(self):
        api = FakeAPI([7])
        dry = Config(repository="owner/example", enabled=False)
        tick(dry, api, self.store, self.t0)
        self.assertIsNone(self.store.get(7))
        self.assertFalse(api.sent)

    def test_uncertain_dispatch_wont_duplicate(self):
        api = FakeAPI([4])
        api.fail_dispatch = True
        tick(self.config, api, self.store, self.t0)
        self.assertEqual(self.store.get(4)["status"], "uncertain")
        tick(self.config, api, self.store, self.t0 + 900)
        self.assertEqual(len(api.sent), 1)

    def test_daily_cap(self):
        api = FakeAPI([1, 2, 3])
        cap = Config(repository="owner/example", max_parallel=3, max_daily=2, enabled=True)
        tick(cap, api, self.store, self.t0)
        self.assertEqual(len(api.sent), 2)
        self.assertEqual(self.store.daily_count(self.t0), 2)

    def test_invalid_configuration(self):
        for bad in ("bad", "owner/repo/extra", "bad name/repo"):
            with self.subTest(repo=bad), self.assertRaises(ValueError):
                Config(repository=bad)


if __name__ == "__main__":
    unittest.main()
