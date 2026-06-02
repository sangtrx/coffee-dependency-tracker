from __future__ import annotations

import unittest
from pathlib import Path

from coffee_dependency_tracker.cli import build_parser
from coffee_dependency_tracker.storage import DEFAULT_LOG_PATH


class ParserDefaultsTests(unittest.TestCase):
    def test_default_data_path_is_default_log_path(self) -> None:
        parser = build_parser()
        ns = parser.parse_args(["stats"])  # no --data provided
        self.assertEqual(ns.data, DEFAULT_LOG_PATH)
