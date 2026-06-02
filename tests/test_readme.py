from __future__ import annotations

import unittest
from pathlib import Path


class ReadmeTests(unittest.TestCase):
    def test_readme_mentions_import_behavior(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        text = (repo_root / "README.md").read_text(encoding="utf-8")
        self.assertIn("Import behavior:", text)
