from __future__ import annotations

import unittest
from pathlib import Path

from coffee_dependency_tracker.storage import DEFAULT_LOG_PATH


class DefaultsTests(unittest.TestCase):
    def test_default_log_path_is_path_and_json(self) -> None:
        self.assertIsInstance(DEFAULT_LOG_PATH, Path)
        self.assertTrue(str(DEFAULT_LOG_PATH).endswith(".json"))
