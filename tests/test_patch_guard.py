import tempfile
from pathlib import Path
import unittest

from scripts.verify_agent_patch import validate_patch


class PatchGuardTests(unittest.TestCase):
    def patch(self, contents: str) -> Path:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        path = Path(self.temp.name) / "change.patch"
        path.write_text(contents, encoding="utf-8")
        return path

    def test_accepts_known_source(self):
        path = self.patch("diff --git a/src/hello.py b/src/hello.py\n--- a/src/hello.py\n+++ b/src/hello.py\n")
        self.assertEqual(validate_patch(path), ["src/hello.py"])

    def test_rejects_workflow_edit(self):
        path = self.patch("diff --git a/.github/workflows/ci.yml b/.github/workflows/ci.yml\n")
        with self.assertRaises(ValueError):
            validate_patch(path)

    def test_rejects_traversal(self):
        path = self.patch("diff --git a/docs/../../secrets b/docs/../../secrets\n")
        with self.assertRaises(ValueError):
            validate_patch(path)

    def test_rejects_symlink(self):
        path = self.patch("diff --git a/src/x b/src/x\nnew file mode 120000\n")
        with self.assertRaises(ValueError):
            validate_patch(path)
