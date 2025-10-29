"""CSV ingestion pipeline."""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Iterable, Iterator, Mapping

from .dataset import EntityRecord

DATE_FORMATS = [
    "%Y-%m-%d",
    "%Y/%m/%d",
]


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise ValueError(f"Unsupported date format: {value}")


def load_csv(path: str | Path) -> Iterator[Mapping[str, str]]:
    with Path(path).open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            yield {key: value.strip() for key, value in row.items()}


def ingest_entities(path: str | Path) -> Iterable[EntityRecord]:
    for row in load_csv(path):
        record = EntityRecord(
            entity_id=row["entity_id"],
            entity_type=row["entity_type"],
            name=row["name"],
            email=row.get("email") or None,
            affiliation=row.get("affiliation") or None,
            last_seen=parse_datetime(row.get("last_seen")),
            notes=row.get("notes") or None,
        )
        yield record


__all__ = ["ingest_entities"]
