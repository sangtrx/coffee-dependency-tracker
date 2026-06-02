from __future__ import annotations

from datetime import datetime
import unittest

from coffee_dependency_tracker.models import CoffeeEntry


class CoffeeEntryTests(unittest.TestCase):
    def test_coffee_entry_round_trip(self) -> None:
        entry = CoffeeEntry(
            timestamp=datetime(2026, 6, 2, 8, 30),
            cups=2.5,
            note="launch prep",
            source="home",
        )

        self.assertEqual(
            entry.to_dict(),
            {
                "timestamp": "2026-06-02T08:30:00",
                "cups": 2.5,
                "note": "launch prep",
                "source": "home",
            },
        )

        rebuilt = CoffeeEntry.from_dict(entry.to_dict())
        self.assertEqual(rebuilt, entry)

    def test_from_dict_handles_messy_input_gracefully(self) -> None:
        entry = CoffeeEntry.from_dict(
            {
                "timestamp": "2026-06-02T08:30:00",
                "cups": "",
                "note": None,
                "source": None,
            }
        )

        self.assertEqual(entry.timestamp, datetime(2026, 6, 2, 8, 30))
        self.assertEqual(entry.cups, 0.0)
        self.assertEqual(entry.note, "")
        self.assertEqual(entry.source, "")