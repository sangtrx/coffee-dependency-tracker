"""Statistics and analytics for coffee consumption."""

from __future__ import annotations

from datetime import date, datetime, timedelta

from .models import CoffeeEntry

EMPTY_LOG_MESSAGE = "No coffee logged yet. Try: python main.py add --cups 1"


def filter_entries(
    entries: list[CoffeeEntry],
    since: date | None = None,
    until: date | None = None,
) -> list[CoffeeEntry]:
    """Filter coffee entries by date range.
    
    Args:
        entries: List of coffee entries to filter
        since: Start date (inclusive)
        until: End date (inclusive)
        
    Returns:
        Filtered list of entries within the date range
    """
    if since is None and until is None:
        return list(entries)
    filtered: list[CoffeeEntry] = []
    for entry in entries:
        day = entry.timestamp.date()
        if since and day < since:
            continue
        if until and day > until:
            continue
        filtered.append(entry)
    return filtered


def daily_totals(
    entries: list[CoffeeEntry],
    days: int = 7,
    now: datetime | None = None,
) -> dict[date, float]:
    """Calculate daily coffee consumption totals.
    
    Args:
        entries: List of coffee entries
        days: Number of days to include in the calculation
        now: Reference datetime (defaults to current time)
        
    Returns:
        Dictionary mapping dates to total cups consumed
    """
    now = now or datetime.now()
    days = max(1, days)
    start = now.date() - timedelta(days=days - 1)
    totals = {start + timedelta(days=i): 0.0 for i in range(days)}
    for entry in entries:
        day = entry.timestamp.date()
        if day in totals:
            totals[day] += entry.cups
    return totals


def render_daily_totals(totals: dict[date, float]) -> str:
    """Format daily totals for display.
    
    Args:
        totals: Dictionary of date to cups mapping
        
    Returns:
        Formatted string showing daily totals
    """
    lines = ["Daily totals:"]
    for day in sorted(totals.keys()):
        lines.append(f"- {day.isoformat()}: {totals[day]:.1f} cup(s)")
    return "\n".join(lines)


def sparkline(values: list[float]) -> str:
    """Create a text sparkline visualization of values.
    
    Args:
        values: List of numeric values to visualize
        
    Returns:
        Sparkline string using Unicode block characters
    """
    if not values:
        return ""
    blocks = "▁▂▃▄▅▆▇█"
    min_value = min(values)
    max_value = max(values)
    if max_value == min_value:
        return blocks[0] * len(values)
    span = max_value - min_value
    result = []
    for value in values:
        index = int(round((value - min_value) / span * (len(blocks) - 1)))
        result.append(blocks[index])
    return "".join(result)


def compute_streaks(
    entries: list[CoffeeEntry], now: datetime | None = None
) -> tuple[int, int]:
    """Calculate coffee consumption streaks.
    
    Args:
        entries: List of coffee entries
        now: Reference datetime (defaults to current time)
        
    Returns:
        Tuple of (current_streak, longest_streak) in days
    """
    now = now or datetime.now()
    days = sorted({entry.timestamp.date() for entry in entries})
    if not days:
        return 0, 0

    longest = 1
    current = 1
    for index in range(1, len(days)):
        if days[index] == days[index - 1] + timedelta(days=1):
            current += 1
        else:
            longest = max(longest, current)
            current = 1
    longest = max(longest, current)

    current_streak = 0
    day_cursor = now.date()
    day_set = set(days)
    while day_cursor in day_set:
        current_streak += 1
        day_cursor = day_cursor - timedelta(days=1)
    return current_streak, longest


def trend_label(entries: list[CoffeeEntry], now: datetime | None = None) -> str:
    """Analyze coffee consumption trend over the last 14 days.
    
    Args:
        entries: List of coffee entries
        now: Reference datetime (defaults to current time)
        
    Returns:
        Trend label: "rising", "falling", "steady", or "new trend"
    """
    if not entries:
        return "new trend"

    totals = daily_totals(entries, days=14, now=now)
    values = [totals[day] for day in sorted(totals.keys())]
    previous = sum(values[:7])
    recent = sum(values[7:])
    if previous == 0:
        return "new trend"
    ratio = recent / previous
    if ratio >= 1.15:
        return "rising"
    if ratio <= 0.85:
        return "falling"
    return "steady"


def forecast_cups(entries: list[CoffeeEntry], now: datetime | None = None) -> float:
    """Forecast coffee consumption for the next day.
    
    Uses average from last 7 days as forecast.
    
    Args:
        entries: List of coffee entries
        now: Reference datetime (defaults to current time)
        
    Returns:
        Forecasted number of cups for next day
    """
    totals = daily_totals(entries, days=7, now=now)
    return sum(totals.values()) / 7


def build_report(
    entries: list[CoffeeEntry],
    now: datetime | None = None,
    days: int = 14,
    include_chart: bool = True,
) -> str:
    """Build a comprehensive coffee consumption report.
    
    Args:
        entries: List of coffee entries
        now: Reference datetime (defaults to current time)
        days: Number of days to include in chart
        include_chart: Whether to include sparkline chart
        
    Returns:
        Formatted report string
    """
    if not entries:
        return EMPTY_LOG_MESSAGE

    now = now or datetime.now()
    summary_lines = summarize(entries, now=now).splitlines()
    totals = daily_totals(entries, days=days, now=now)
    current_streak, longest_streak = compute_streaks(entries, now=now)
    trend = trend_label(entries, now=now)
    forecast = forecast_cups(entries, now=now)

    lines = ["Coffee report"]
    lines.extend(summary_lines)
    lines.append("")
    lines.append(f"Trend (last 7 vs previous 7 days): {trend}")
    lines.append(f"Current streak: {current_streak} day(s)")
    lines.append(f"Longest streak: {longest_streak} day(s)")
    lines.append(f"Forecast (next day): {forecast:.2f} cup(s)")

    if include_chart:
        values = [totals[day] for day in sorted(totals.keys())]
        chart = sparkline(values)
        lines.append("")
        lines.append(f"Last {days} days: {chart}")
    lines.append("")
    lines.append(render_daily_totals(totals))
    return "\n".join(lines)


def summarize(entries: list[CoffeeEntry], now: datetime | None = None) -> str:
    """Create a text summary of coffee consumption statistics.
    
    Args:
        entries: List of coffee entries
        now: Reference datetime (defaults to current time)
        
    Returns:
        Formatted summary string
    """
    if not entries:
        return EMPTY_LOG_MESSAGE

    now = now or datetime.now()
    total = sum(entry.cups for entry in entries)
    first_ts = min(entry.timestamp for entry in entries)
    last_ts = max(entry.timestamp for entry in entries)
    days = max(1, (last_ts.date() - first_ts.date()).days + 1)
    avg_all = total / days

    start_7 = now.date() - timedelta(days=6)
    daily_7 = {start_7 + timedelta(days=i): 0.0 for i in range(7)}
    for entry in entries:
        day = entry.timestamp.date()
        if day in daily_7:
            daily_7[day] += entry.cups
    avg_7 = sum(daily_7.values()) / 7

    prediction = "steady"
    if avg_7 >= 3:
        prediction = "high-octane"
    elif avg_7 >= 1.5:
        prediction = "healthy hum"
    elif avg_7 < 0.8:
        prediction = "mysteriously calm"

    lines = [
        f"Total cups logged: {total:.1f}",
        f"Average per day (all time): {avg_all:.2f}",
        f"Average per day (last 7): {avg_7:.2f}",
        f"Most recent cup: {last_ts.strftime('%Y-%m-%d %H:%M')}",
        f"Productivity forecast: {prediction}",
    ]
    return "\n".join(lines)
