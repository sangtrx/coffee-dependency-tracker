"""Coffee Dependency Tracker — Log coffee consumption and track productivity trends.

A simple CLI tool to track daily coffee consumption and get insights into your
caffeine dependency and productivity patterns.

Core API:
    - CoffeeEntry — Model for a single coffee consumption record
    - load_entries() — Load coffee logs from file
    - save_entries() — Save coffee logs to file
    - daily_totals() — Calculate daily totals
    - filter_entries() — Filter entries by date range

Example:
    >>> from coffee_dependency_tracker import CoffeeEntry, append_entry
    >>> from datetime import datetime
    >>> entry = CoffeeEntry(datetime.now(), cups=2, note="morning")
"""

__version__ = "0.3.1"

from .models import CoffeeEntry
from .stats import (
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
from .storage import append_entry, load_entries, save_entries

__all__ = [
    "CoffeeEntry",
    "append_entry",
    "build_report",
    "compute_streaks",
    "daily_totals",
    "filter_entries",
    "forecast_cups",
    "load_entries",
    "render_daily_totals",
    "sparkline",
    "save_entries",
    "summarize",
    "trend_label",
    "__version__",
]
