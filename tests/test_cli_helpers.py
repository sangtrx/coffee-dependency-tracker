from __future__ import annotations

import argparse
import unittest

from coffee_dependency_tracker.cli import parse_date, parse_datetime


class CliHelpersTests(unittest.TestCase):
    def test_parse_date_rejects_bad_format(self) -> None:
        with self.assertRaises(argparse.ArgumentTypeError):
            parse_date("06-02-2026")

    def test_parse_datetime_rejects_bad_format(self) -> None:
        with self.assertRaises(argparse.ArgumentTypeError):
            parse_datetime("yesterday")
