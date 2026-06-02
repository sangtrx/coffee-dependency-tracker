from __future__ import annotations

import re
import unittest

from coffee_dependency_tracker import __version__


class VersionTests(unittest.TestCase):
    def test_version_is_semver_like(self) -> None:
        self.assertIsInstance(__version__, str)
        self.assertRegex(__version__, r"^\d+\.\d+\.\d+$")
