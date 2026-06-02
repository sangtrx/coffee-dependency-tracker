from __future__ import annotations

import argparse
from datetime import datetime

from .models import CoffeeEntry
from .stats import summarize
from .storage import load_entries, save_entries


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Track coffee consumption with tiny stats.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Log a coffee")
    add_parser.add_argument("--cups", type=float, default=1.0, help="How many cups")
    add_parser.add_argument("--note", help="Optional note")

    subparsers.add_parser("stats", help="Show stats")
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    entries = load_entries()

    if args.command == "add":
        entry = CoffeeEntry(timestamp=datetime.now(), cups=args.cups, note=args.note or "")
        entries.append(entry)
        save_entries(entries)
        print(f"Logged {args.cups} cup(s) at {entry.timestamp.isoformat(timespec='seconds')}")
        return

    if args.command == "stats":
        print(summarize(entries))
        return
