from __future__ import annotations

from datetime import date, datetime
import unittest

from coffee_dependency_tracker.models import CoffeeEntry
from coffee_dependency_tracker.stats import (
    build_report,
    compute_streaks,
    daily_totals,
    filter_entries,
    forecast_cups,
    render_daily_totals,
    sparkline,
    summarize,
    trend_label,
)


NOW = datetime(2026, 6, 2, 12, 0)


def sample_entries() -> list[CoffeeEntry]:
    return [
        CoffeeEntry(datetime(2026, 5, 30, 8, 0), 1.0, source="home"),
        CoffeeEntry(datetime(2026, 5, 31, 9, 0), 2.0, note="busy day"),
        CoffeeEntry(datetime(2026, 6, 1, 10, 0), 1.5, source="office"),
        CoffeeEntry(datetime(2026, 6, 2, 11, 0), 1.0, source="office"),
    ]


class StatsTests(unittest.TestCase):
    def test_filter_entries_by_date_range(self) -> None:
        entries = sample_entries()

        filtered = filter_entries(entries, since=date(2026, 5, 31), until=NOW.date())

        self.assertEqual([entry.timestamp.day for entry in filtered], [31, 1, 2])

    def test_daily_totals_and_rendering(self) -> None:
        entries = sample_entries()
        totals = daily_totals(entries, days=4, now=NOW)

        self.assertEqual(
            totals,
            {
                date(2026, 5, 30): 1.0,
                date(2026, 5, 31): 2.0,
                date(2026, 6, 1): 1.5,
                date(2026, 6, 2): 1.0,
            },
        )
        self.assertTrue(render_daily_totals(totals).startswith("Daily totals:"))

    def test_streaks_trend_and_forecast(self) -> None:
        entries = sample_entries()

        self.assertEqual(compute_streaks(entries, now=NOW), (4, 4))
        self.assertEqual(trend_label(entries, now=NOW), "new trend")
        self.assertEqual(forecast_cups(entries, now=NOW), 0.7857142857142857)
        self.assertEqual(sparkline([0.0, 1.0, 2.0, 3.0]), "▁▃▆█")

    def test_summary_and_report_have_expected_content(self) -> None:
        entries = sample_entries()

        summary = summarize(entries, now=NOW)
        report = build_report(entries, now=NOW, days=4, include_chart=True)

        self.assertIn("Total cups logged: 5.5", summary)
        self.assertIn("Productivity forecast: mysteriously calm", summary)
        self.assertIn("Coffee report", report)
        self.assertIn("Trend (last 7 vs previous 7 days): new trend", report)
        self.assertIn("Last 4 days:", report)

    def test_empty_inputs_return_friendly_messages(self) -> None:
        self.assertEqual(summarize([], now=NOW), "No coffee logged yet. Try: python main.py add --cups 1")
        self.assertEqual(build_report([], now=NOW), "No coffee logged yet. Try: python main.py add --cups 1")
        self.assertEqual(compute_streaks([], now=NOW), (0, 0))
        self.assertEqual(trend_label([], now=NOW), "new trend")