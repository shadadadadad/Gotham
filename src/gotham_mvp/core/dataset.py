"""Dataset abstractions and storage for the Gotham MVP."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Iterable, List, Optional


@dataclass(slots=True)
class EntityRecord:
    """Represents a single entity row loaded from a dataset."""

    entity_id: str
    entity_type: str
    name: str
    email: Optional[str] = None
    affiliation: Optional[str] = None
    last_seen: Optional[datetime] = None
    notes: Optional[str] = None
    metadata: Dict[str, str] = field(default_factory=dict)

    def merge(self, other: "EntityRecord") -> "EntityRecord":
        """Merge another record into this one, preferring the most complete values."""

        if self.entity_type != other.entity_type:
            raise ValueError("Cannot merge records of different entity types")

        def choose(current: Optional[str], candidate: Optional[str]) -> Optional[str]:
            return candidate if candidate and not current else current

        merged = EntityRecord(
            entity_id=self.entity_id,
            entity_type=self.entity_type,
            name=self.name if self.name else other.name,
            email=choose(self.email, other.email),
            affiliation=choose(self.affiliation, other.affiliation),
            last_seen=max(filter(None, [self.last_seen, other.last_seen])),
            notes=choose(self.notes, other.notes),
            metadata={**other.metadata, **self.metadata},
        )
        return merged


class DatasetStore:
    """In-memory storage for datasets keyed by dataset name."""

    def __init__(self) -> None:
        self._records: Dict[str, List[EntityRecord]] = {}

    def add_records(self, dataset_name: str, records: Iterable[EntityRecord]) -> None:
        self._records.setdefault(dataset_name, []).extend(records)

    def list_datasets(self) -> List[str]:
        return sorted(self._records)

    def get_records(self, dataset_name: str) -> List[EntityRecord]:
        return list(self._records.get(dataset_name, []))

    def upsert_record(self, dataset_name: str, record: EntityRecord) -> None:
        existing = self._records.setdefault(dataset_name, [])
        for index, current in enumerate(existing):
            if current.entity_id == record.entity_id:
                existing[index] = record
                return
        existing.append(record)


__all__ = ["EntityRecord", "DatasetStore"]
