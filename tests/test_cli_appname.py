from __future__ import annotations

import unittest

from coffee_dependency_tracker.cli import build_parser, APP_NAME


class AppNameTests(unittest.TestCase):
    def test_parser_description_includes_app_name(self) -> None:
        parser = build_parser()
        self.assertTrue(parser.description.startswith(APP_NAME))
