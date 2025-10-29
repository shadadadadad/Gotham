"""Entity resolution helpers."""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, List

from .dataset import DatasetStore, EntityRecord


class Resolver:
    """Deduplicates records based on matching keys."""

    def __init__(self, store: DatasetStore) -> None:
        self.store = store

    def resolve_by_email(self, dataset_name: str) -> None:
        records = self.store.get_records(dataset_name)
        by_email: Dict[str, List[EntityRecord]] = defaultdict(list)
        for record in records:
            if record.email:
                by_email[record.email.lower()].append(record)

        for duplicates in by_email.values():
            primary = duplicates[0]
            for candidate in duplicates[1:]:
                merged = primary.merge(candidate)
                merged.metadata.setdefault("resolution_notes", "")
                merged.metadata["resolution_notes"] = \
                    f"Merged duplicate {candidate.entity_id} by email"
                self.store.upsert_record(dataset_name, merged)
                primary = merged

    def enrich_affiliations(self, dataset_name: str, knowledge_base: Dict[str, str]) -> None:
        for record in self.store.get_records(dataset_name):
            if record.affiliation and record.affiliation in knowledge_base:
                record.metadata["affiliation_summary"] = knowledge_base[record.affiliation]
                self.store.upsert_record(dataset_name, record)


__all__ = ["Resolver"]
