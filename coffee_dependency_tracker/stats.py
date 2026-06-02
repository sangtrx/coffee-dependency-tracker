from __future__ import annotations

from datetime import datetime, timedelta

from .models import CoffeeEntry


def summarize(entries: list[CoffeeEntry], now: datetime | None = None) -> str:
    if not entries:
        return "No coffee logged yet. Try: python main.py add --cups 1"

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
