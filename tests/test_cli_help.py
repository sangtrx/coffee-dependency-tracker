from __future__ import annotations

import unittest
from contextlib import redirect_stdout
from io import StringIO

from coffee_dependency_tracker.cli import main


class CliHelpTests(unittest.TestCase):
    def test_help_exits_with_zero_and_prints_usage(self) -> None:
        buf = StringIO()
        with redirect_stdout(buf), self.assertRaises(SystemExit) as ctx:
            main(["--help"])

        self.assertEqual(ctx.exception.code, 0)
        self.assertIn("usage:", buf.getvalue().lower())
