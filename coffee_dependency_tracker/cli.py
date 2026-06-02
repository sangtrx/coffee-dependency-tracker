from __future__ import annotations

import argparse
from datetime import date, datetime
from pathlib import Path
 
APP_NAME = "coffee-dependency-tracker"

from .models import CoffeeEntry
from .stats import build_report, daily_totals, filter_entries, render_daily_totals, summarize
from .storage import DEFAULT_LOG_PATH, append_entry, load_entries, save_entries


def parse_date(value: str) -> date:
    try:
        return datetime.fromisoformat(value).date()
    except ValueError as exc:
        """Parse a YYYY-MM-DD date string into a date object.

        Raises argparse.ArgumentTypeError when parsing fails so argparse can
        present a helpful message to the user.
        """
        raise argparse.ArgumentTypeError("Date must be YYYY-MM-DD") from exc


def parse_datetime(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value)
    except ValueError as exc:
        """Parse an ISO-format datetime string into a datetime object.

        Raises argparse.ArgumentTypeError when parsing fails so argparse can
        present a helpful message to the user.
        """
        raise argparse.ArgumentTypeError("Datetime must be ISO format") from exc


def parse_positive_float(value: str) -> float:
    try:
        cups = float(value)
    except ValueError as exc:
        """Parse a numeric string into a positive float.

        Used for the `--cups` argument. Raises argparse.ArgumentTypeError for
        invalid or non-positive inputs.
        """
        raise argparse.ArgumentTypeError("Cups must be a number") from exc
    if cups <= 0:
        raise argparse.ArgumentTypeError("Cups must be greater than 0")
    return cups


def parse_positive_int(value: str) -> int:
    try:
        n = int(value)
    except ValueError as exc:
        """Parse a numeric string into a positive integer.

        Used for `--days` and `--limit`. Raises argparse.ArgumentTypeError for
        invalid or non-positive inputs.
        """
        raise argparse.ArgumentTypeError("Value must be an integer") from exc
    if n <= 0:
        raise argparse.ArgumentTypeError("Value must be greater than 0")
    return n


def validate_not_future(timestamp: datetime) -> None:
    if timestamp > datetime.now():
        raise ValueError("Timestamp cannot be in the future")


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
    add_parser.add_argument("--cups", type=parse_positive_float, default=1.0, help="How many cups")
    add_parser.add_argument("--note", help="Optional note")
    add_parser.add_argument("--source", help="Brew type or source label")
    add_parser.add_argument("--at", type=parse_datetime, help="Timestamp (ISO format)")

    stats_parser = subparsers.add_parser("stats", help="Show stats")
    stats_parser.add_argument("--since", type=parse_date, help="Start date (YYYY-MM-DD)")
    stats_parser.add_argument("--until", type=parse_date, help="End date (YYYY-MM-DD)")
    stats_parser.add_argument("--daily", action="store_true", help="Include daily totals")
    stats_parser.add_argument("--days", type=parse_positive_int, default=7, help="Days for daily totals")

    report_parser = subparsers.add_parser("report", help="Generate a detailed report")
    report_parser.add_argument("--since", type=parse_date, help="Start date (YYYY-MM-DD)")
    report_parser.add_argument("--until", type=parse_date, help="End date (YYYY-MM-DD)")
    report_parser.add_argument("--days", type=parse_positive_int, default=14, help="Days to chart")
    report_parser.add_argument("--no-chart", action="store_true", help="Skip sparkline")

    list_parser = subparsers.add_parser("list", help="List logged entries")
    list_parser.add_argument("--since", type=parse_date, help="Start date (YYYY-MM-DD)")
    list_parser.add_argument("--until", type=parse_date, help="End date (YYYY-MM-DD)")
    list_parser.add_argument("--limit", type=parse_positive_int, default=10, help="Max entries to show")

    export_parser = subparsers.add_parser("export", help="Export entries")
    export_parser.add_argument("--out", type=Path, required=True, help="Output path")
    export_parser.add_argument("--since", type=parse_date, help="Start date (YYYY-MM-DD)")
    export_parser.add_argument("--until", type=parse_date, help="End date (YYYY-MM-DD)")
    export_parser.add_argument("--force", action="store_true", help="Overwrite an existing file")

    import_parser = subparsers.add_parser("import", help="Import entries (replaces current log)")
    import_parser.add_argument("path", type=Path, help="Path to JSON/CSV file")

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "add":
        timestamp = args.at or datetime.now()
        try:
            validate_not_future(timestamp)
        except ValueError as exc:
            parser.error(str(exc))
        entry = CoffeeEntry(
            timestamp=timestamp,
            cups=args.cups,
            note=args.note or "",
            source=args.source or "",
        )
        append_entry(entry, args.data)
        print(f"Logged {args.cups} cup(s) at {entry.timestamp.isoformat(timespec='seconds')}")
        return

    entries = load_entries(args.data)
    # Validate common argument constraints
    # --since must be <= --until when both provided
    if getattr(args, "since", None) and getattr(args, "until", None):
        if args.since > args.until:
            parser.error("--since must be on or before --until")

    if args.command == "stats":
        filtered = filter_entries(entries, args.since, args.until)
        print(summarize(filtered))
        if args.daily:
            totals = daily_totals(filtered, days=args.days, now=datetime.now())
            print(render_daily_totals(totals))
        return

    if args.command == "report":
        filtered = filter_entries(entries, args.since, args.until)
        print(
            build_report(
                filtered,
                now=datetime.now(),
                days=args.days,
                include_chart=not args.no_chart,
            )
        )
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
        if args.out.exists() and not args.force:
            parser.error(f"Output file already exists: {args.out} (use --force to overwrite)")
        save_entries(filtered, args.out)
        print(f"Exported {len(filtered)} entries to {args.out}")
        return

    if args.command == "import":
        imported = load_entries(args.path)
        save_entries(imported, args.data)
        print(f"Imported {len(imported)} entries into {args.data}")
        return
