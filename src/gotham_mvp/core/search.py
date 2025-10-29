"""Full-text search utilities for the Gotham MVP."""

from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from typing import Dict, Iterable, List, Tuple

from .dataset import DatasetStore, EntityRecord

TOKEN_RE = re.compile(r"[A-Za-z0-9_]+")


def tokenize(text: str | None) -> List[str]:
    if not text:
        return []
    return [token.lower() for token in TOKEN_RE.findall(text)]


def build_inverted_index(records: Iterable[EntityRecord]) -> Dict[str, Counter]:
    index: Dict[str, Counter] = defaultdict(Counter)
    for record in records:
        tokens = tokenize(" ".join(filter(None, [record.name, record.notes, record.affiliation])))
        for token in tokens:
            index[token][record.entity_id] += 1
    return index


def search(store: DatasetStore, dataset_name: str, query: str, limit: int = 5) -> List[Tuple[EntityRecord, float]]:
    records = store.get_records(dataset_name)
    index = build_inverted_index(records)
    query_tokens = tokenize(query)
    scores: Dict[str, float] = defaultdict(float)
    doc_lengths: Dict[str, int] = defaultdict(int)

    for token in query_tokens:
        postings = index.get(token)
        if not postings:
            continue
        idf = math.log(1 + len(records) / (1 + len(postings)))
        for entity_id, term_freq in postings.items():
            scores[entity_id] += term_freq * idf
            doc_lengths[entity_id] += term_freq

    ranked = sorted(
        ((store_entity(store, dataset_name, entity_id), score / doc_lengths[entity_id])
         for entity_id, score in scores.items()),
        key=lambda pair: pair[1],
        reverse=True,
    )
    return ranked[:limit]


def store_entity(store: DatasetStore, dataset_name: str, entity_id: str) -> EntityRecord:
    for record in store.get_records(dataset_name):
        if record.entity_id == entity_id:
            return record
    raise KeyError(f"Entity {entity_id} not found in dataset {dataset_name}")


__all__ = ["search"]
