from __future__ import annotations

from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from coffee_dependency_tracker.models import CoffeeEntry
from coffee_dependency_tracker.storage import append_entry, load_entries, save_entries


ENTRY = CoffeeEntry(datetime(2026, 6, 2, 8, 15), 2.0, note="focus mode", source="home")


class StorageTests(unittest.TestCase):
    def test_json_round_trip_creates_parent_directories(self) -> None:
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "nested" / "coffee.json"

            save_entries([ENTRY], path)
            loaded = load_entries(path)

            self.assertTrue(path.exists())
            self.assertEqual(loaded, [ENTRY])

    def test_csv_round_trip(self) -> None:
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "coffee.csv"

            save_entries([ENTRY], path)

            self.assertEqual(load_entries(path), [ENTRY])

    def test_sqlite_round_trip_via_append_entry(self) -> None:
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "logs" / "coffee.sqlite3"

            append_entry(ENTRY, path)

            self.assertEqual(load_entries(path), [ENTRY])