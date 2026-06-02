from __future__ import annotations

import json
from pathlib import Path

from .models import CoffeeEntry

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOG_PATH = REPO_ROOT / "coffee_log.json"


def load_entries(path: Path = DEFAULT_LOG_PATH) -> list[CoffeeEntry]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return [CoffeeEntry.from_dict(item) for item in data if isinstance(item, dict)]
    except json.JSONDecodeError:
        return []
    return []


def save_entries(entries: list[CoffeeEntry], path: Path = DEFAULT_LOG_PATH) -> None:
    payload = [entry.to_dict() for entry in entries]
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
