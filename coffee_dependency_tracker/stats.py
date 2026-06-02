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
    if since is None and until is None:
        return list(entries)

    filtered: list[CoffeeEntry] = []
    for entry in entries:
        day = entry.timestamp.date()
        if since is not None and day < since:
            continue
        if until is not None and day > until:
            continue
        filtered.append(entry)
    return filtered


def daily_totals(
    entries: list[CoffeeEntry],
    days: int = 7,
    now: datetime | None = None,
) -> dict[date, float]:
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
    lines = ["Daily totals:"]
    for day in sorted(totals.keys()):
        lines.append(f"- {day.isoformat()}: {totals[day]:.1f} cup(s)")
    return "\n".join(lines)


def sparkline(values: list[float]) -> str:
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
    totals = daily_totals(entries, days=7, now=now)
    return sum(totals.values()) / 7


def build_report(
    entries: list[CoffeeEntry],
    now: datetime | None = None,
    days: int = 14,
    include_chart: bool = True,
) -> str:
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
        lines.append("")
        lines.append(f"Last {days} days: {sparkline(values)}")

    lines.append("")
    lines.append(render_daily_totals(totals))
    return "\n".join(lines)


def summarize(entries: list[CoffeeEntry], now: datetime | None = None) -> str:
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
