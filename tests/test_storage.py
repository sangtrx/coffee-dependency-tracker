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

    def test_load_malformed_json_returns_empty(self) -> None:
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "bad.json"
            path.write_text("{ not: valid json }", encoding="utf-8")

            self.assertEqual(load_entries(path), [])

    def test_is_sqlite_path_recognizes_extensions(self) -> None:
        from coffee_dependency_tracker.storage import _is_sqlite_path

        self.assertTrue(_is_sqlite_path(Path("db.sqlite3")))
        self.assertTrue(_is_sqlite_path(Path("data.DB")))
        self.assertFalse(_is_sqlite_path(Path("coffee.json")))

    def test_csv_save_creates_parent_directories(self) -> None:
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "nested" / "coffee.csv"
            from coffee_dependency_tracker.storage import save_entries

            save_entries([ENTRY], path)

            self.assertTrue(path.exists())