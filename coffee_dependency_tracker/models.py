"""Data models for coffee consumption tracking."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class CoffeeEntry:
    """Represents a single coffee consumption entry.
    
    Attributes:
        timestamp: When the coffee was consumed
        cups: Number of cups consumed
        note: Optional note about the entry
        source: Optional source of the coffee (e.g., "office", "home")
    """
    timestamp: datetime
    cups: float
    note: str = ""
    source: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> "CoffeeEntry":
        """Create a CoffeeEntry from a dictionary (deserialization).
        
        Args:
            data: Dictionary with entry data
            
        Returns:
            CoffeeEntry instance
        """
        raw_ts = data.get("timestamp")
        try:
            timestamp = datetime.fromisoformat(str(raw_ts)) if raw_ts else datetime.now()
        except ValueError:
            timestamp = datetime.now()
        try:
            cups = float(data.get("cups", 0) or 0)
        except (TypeError, ValueError):
            cups = 0.0
        note = str(data.get("note") or "")
        source = str(data.get("source") or "")
        return cls(timestamp=timestamp, cups=cups, note=note, source=source)

    def to_dict(self) -> dict:
        """Convert CoffeeEntry to a dictionary for serialization.
        
        Returns:
            Dictionary representation of the entry
        """
        return {
            "timestamp": self.timestamp.isoformat(timespec="seconds"),
            "cups": self.cups,
            "note": self.note,
            "source": self.source,
        }
