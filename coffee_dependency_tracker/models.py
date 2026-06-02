from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class CoffeeEntry:
    timestamp: datetime
    cups: float
    note: str = ""
    source: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> "CoffeeEntry":
        raw_ts = data.get("timestamp")
        try:
            timestamp = datetime.fromisoformat(raw_ts) if raw_ts else datetime.now()
        except ValueError:
            timestamp = datetime.now()
        cups = float(data.get("cups", 0))
        note = str(data.get("note", ""))
        source = str(data.get("source", ""))
        return cls(timestamp=timestamp, cups=cups, note=note, source=source)

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.isoformat(timespec="seconds"),
            "cups": self.cups,
            "note": self.note,
            "source": self.source,
        }
