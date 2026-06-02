"""Storage backends for coffee entries (JSON, CSV, and SQLite)."""

from __future__ import annotations

import csv
import json
import sqlite3
from pathlib import Path

from .models import CoffeeEntry

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOG_PATH = REPO_ROOT / "coffee_log.json"


def _ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _is_sqlite_path(path: Path) -> bool:
    """Check if a path points to a SQLite database."""
    return path.suffix.lower() in {".db", ".sqlite", ".sqlite3"}


def _connect(path: Path) -> sqlite3.Connection:
    _ensure_parent_dir(path)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


def _init_db(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            cups REAL NOT NULL,
            note TEXT NOT NULL,
            source TEXT NOT NULL
        );
        """
    )
    connection.commit()


def load_entries(path: Path = DEFAULT_LOG_PATH) -> list[CoffeeEntry]:
    """Load coffee entries from a file (JSON, CSV, or SQLite).
    
    Args:
        path: Path to the storage file
        
    Returns:
        List of CoffeeEntry objects
    """
    if not path.exists():
        return []
    if _is_sqlite_path(path):
        return _load_entries_sqlite(path)
    if path.suffix.lower() == ".csv":
        return _load_entries_csv(path)
    return _load_entries_json(path)


def save_entries(entries: list[CoffeeEntry], path: Path = DEFAULT_LOG_PATH) -> None:
    """Save coffee entries to a file (JSON, CSV, or SQLite).
    
    Args:
        entries: List of CoffeeEntry objects to save
        path: Path to the storage file
    """
    if _is_sqlite_path(path):
        _replace_entries_sqlite(entries, path)
        return
    if path.suffix.lower() == ".csv":
        _save_entries_csv(entries, path)
        return
    _save_entries_json(entries, path)


def append_entry(entry: CoffeeEntry, path: Path = DEFAULT_LOG_PATH) -> None:
    """Append a single coffee entry to the log.
    
    Args:
        entry: CoffeeEntry to append
        path: Path to the storage file
    """
    if _is_sqlite_path(path):
        _append_entry_sqlite(entry, path)
        return
    entries = load_entries(path)
    entries.append(entry)
    save_entries(entries, path)


def _load_entries_json(path: Path) -> list[CoffeeEntry]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return [CoffeeEntry.from_dict(item) for item in data if isinstance(item, dict)]
    except json.JSONDecodeError:
        return []
    return []


def _save_entries_json(entries: list[CoffeeEntry], path: Path) -> None:
    _ensure_parent_dir(path)
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
    _ensure_parent_dir(path)
    fieldnames = ["timestamp", "cups", "note", "source"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for entry in entries:
            writer.writerow(entry.to_dict())


def _load_entries_sqlite(path: Path) -> list[CoffeeEntry]:
    with _connect(path) as connection:
        _init_db(connection)
        rows = connection.execute("SELECT * FROM entries ORDER BY timestamp").fetchall()
    return [
        CoffeeEntry.from_dict(
            {
                "timestamp": row["timestamp"],
                "cups": row["cups"],
                "note": row["note"],
                "source": row["source"],
            }
        )
        for row in rows
    ]


def _append_entry_sqlite(entry: CoffeeEntry, path: Path) -> None:
    with _connect(path) as connection:
        _init_db(connection)
        connection.execute(
            """
            INSERT INTO entries (timestamp, cups, note, source)
            VALUES (?, ?, ?, ?)
            """,
            (
                entry.timestamp.isoformat(timespec="seconds"),
                entry.cups,
                entry.note,
                entry.source,
            ),
        )
        connection.commit()


def _replace_entries_sqlite(entries: list[CoffeeEntry], path: Path) -> None:
    with _connect(path) as connection:
        _init_db(connection)
        connection.execute("DELETE FROM entries")
        connection.executemany(
            """
            INSERT INTO entries (timestamp, cups, note, source)
            VALUES (?, ?, ?, ?)
            """,
            [
                (
                    entry.timestamp.isoformat(timespec="seconds"),
                    entry.cups,
                    entry.note,
                    entry.source,
                )
                for entry in entries
            ],
        )
        connection.commit()
