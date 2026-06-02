from __future__ import annotations

import csv
import json
from pathlib import Path

from .models import CoffeeEntry

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOG_PATH = REPO_ROOT / "coffee_log.json"


def load_entries(path: Path = DEFAULT_LOG_PATH) -> list[CoffeeEntry]:
    if not path.exists():
        return []
    if path.suffix.lower() == ".csv":
        return _load_entries_csv(path)
    return _load_entries_json(path)


def save_entries(entries: list[CoffeeEntry], path: Path = DEFAULT_LOG_PATH) -> None:
    if path.suffix.lower() == ".csv":
        _save_entries_csv(entries, path)
        return
    _save_entries_json(entries, path)


def _load_entries_json(path: Path) -> list[CoffeeEntry]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return [CoffeeEntry.from_dict(item) for item in data if isinstance(item, dict)]
    except json.JSONDecodeError:
        return []
    return []


def _save_entries_json(entries: list[CoffeeEntry], path: Path) -> None:
    payload = [entry.to_dict() for entry in entries]
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _load_entries_csv(path: Path) -> list[CoffeeEntry]:
    entries: list[CoffeeEntry] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            entries.append(CoffeeEntry.from_dict(row))
    return entries


def _save_entries_csv(entries: list[CoffeeEntry], path: Path) -> None:
    fieldnames = ["timestamp", "cups", "note", "source"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for entry in entries:
            writer.writerow(entry.to_dict())
