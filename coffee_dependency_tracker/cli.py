from __future__ import annotations

import argparse
from datetime import date, datetime
from pathlib import Path

from .models import CoffeeEntry
from .stats import daily_totals, filter_entries, render_daily_totals, summarize
from .storage import DEFAULT_LOG_PATH, load_entries, save_entries


def parse_date(value: str) -> date:
    try:
        return datetime.fromisoformat(value).date()
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Date must be YYYY-MM-DD") from exc


def parse_datetime(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Datetime must be ISO format") from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Track coffee consumption with tiny stats.")
    parser.add_argument(
        "--data",
        type=Path,
        default=DEFAULT_LOG_PATH,
        help="Path to coffee log (.json or .csv)",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Log a coffee")
    add_parser.add_argument("--cups", type=float, default=1.0, help="How many cups")
    add_parser.add_argument("--note", help="Optional note")
    add_parser.add_argument("--source", help="Brew type or source label")
    add_parser.add_argument("--at", type=parse_datetime, help="Timestamp (ISO format)")

    stats_parser = subparsers.add_parser("stats", help="Show stats")
    stats_parser.add_argument("--since", type=parse_date, help="Start date (YYYY-MM-DD)")
    stats_parser.add_argument("--until", type=parse_date, help="End date (YYYY-MM-DD)")
    stats_parser.add_argument("--daily", action="store_true", help="Include daily totals")
    stats_parser.add_argument("--days", type=int, default=7, help="Days for daily totals")

    list_parser = subparsers.add_parser("list", help="List logged entries")
    list_parser.add_argument("--since", type=parse_date, help="Start date (YYYY-MM-DD)")
    list_parser.add_argument("--until", type=parse_date, help="End date (YYYY-MM-DD)")
    list_parser.add_argument("--limit", type=int, default=10, help="Max entries to show")

    export_parser = subparsers.add_parser("export", help="Export entries")
    export_parser.add_argument("--out", type=Path, required=True, help="Output path")
    export_parser.add_argument("--since", type=parse_date, help="Start date (YYYY-MM-DD)")
    export_parser.add_argument("--until", type=parse_date, help="End date (YYYY-MM-DD)")

    import_parser = subparsers.add_parser("import", help="Import entries (replaces current log)")
    import_parser.add_argument("path", type=Path, help="Path to JSON/CSV file")

    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    entries = load_entries(args.data)

    if args.command == "add":
        timestamp = args.at or datetime.now()
        entry = CoffeeEntry(
            timestamp=timestamp,
            cups=args.cups,
            note=args.note or "",
            source=args.source or "",
        )
        entries.append(entry)
        save_entries(entries, args.data)
        print(f"Logged {args.cups} cup(s) at {entry.timestamp.isoformat(timespec='seconds')}")
        return

    if args.command == "stats":
        filtered = filter_entries(entries, args.since, args.until)
        print(summarize(filtered))
        if args.daily:
            totals = daily_totals(filtered, days=args.days, now=datetime.now())
            print(render_daily_totals(totals))
        return

    if args.command == "list":
        filtered = filter_entries(entries, args.since, args.until)
        ordered = sorted(filtered, key=lambda entry: entry.timestamp, reverse=True)
        for entry in ordered[: args.limit]:
            source = f" ({entry.source})" if entry.source else ""
            note = f" — {entry.note}" if entry.note else ""
            print(
                f"{entry.timestamp.strftime('%Y-%m-%d %H:%M')}: "
                f"{entry.cups:.1f} cup(s){source}{note}"
            )
        return

    if args.command == "export":
        filtered = filter_entries(entries, args.since, args.until)
        save_entries(filtered, args.out)
        print(f"Exported {len(filtered)} entries to {args.out}")
        return

    if args.command == "import":
        imported = load_entries(args.path)
        save_entries(imported, args.data)
        print(f"Imported {len(imported)} entries into {args.data}")
        return
