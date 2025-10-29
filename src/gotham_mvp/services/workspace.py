"""Workspace service orchestrating Gotham MVP capabilities."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Dict, Iterable, List, Tuple

from ..core.dataset import DatasetStore, EntityRecord
from ..core.ontology import (
    EntityTypeDefinition,
    Ontology,
    PropertyDefinition,
    RelationshipDefinition,
)
from ..core.resolution import Resolver
from ..core.search import search


class WorkspaceSession:
    """High-level API for investigations."""

    def __init__(self, dataset_name: str, store: DatasetStore, ontology: Ontology) -> None:
        self.dataset_name = dataset_name
        self.store = store
        self.ontology = ontology
        self.resolver = Resolver(store)

    def ingest(self, records: Iterable[EntityRecord]) -> None:
        self.store.add_records(self.dataset_name, records)

    def bootstrap_default_ontology(self) -> None:
        person = EntityTypeDefinition(name="Person", description="Individual actors")
        person.add_property(PropertyDefinition("name", "string", "Full name"))
        person.add_property(PropertyDefinition("email", "string", "Email address"))

        organization = EntityTypeDefinition(name="Organization", description="Company or group")
        organization.add_property(PropertyDefinition("name", "string", "Legal name"))
        organization.add_property(PropertyDefinition("sector", "string", "Sector or industry"))

        interaction = EntityTypeDefinition(name="Interaction", description="Events or activities")
        interaction.add_property(PropertyDefinition("name", "string", "Title of the event"))
        interaction.add_property(PropertyDefinition("notes", "string", "Narrative summary"))

        self.ontology.register_entity_type(person)
        self.ontology.register_entity_type(organization)
        self.ontology.register_entity_type(interaction)

        self.ontology.register_relationship(
            RelationshipDefinition(
                name="attended",
                source_type="Person",
                target_type="Interaction",
                description="Person attended the interaction",
            )
        )
        self.ontology.register_relationship(
            RelationshipDefinition(
                name="associated_with",
                source_type="Person",
                target_type="Organization",
                description="Person is associated with an organization",
            )
        )

    def resolve_entities(self) -> None:
        self.resolver.resolve_by_email(self.dataset_name)

    def enrich(self) -> None:
        knowledge_base = {
            "Axis Corp": "Defense contractor expanding satellite operations.",
            "Helios Labs": "Research lab specializing in solar analytics.",
        }
        self.resolver.enrich_affiliations(self.dataset_name, knowledge_base)

    def build_relationships(self) -> Dict[str, List[Tuple[str, str]]]:
        relationships: Dict[str, List[Tuple[str, str]]] = defaultdict(list)
        for record in self.store.get_records(self.dataset_name):
            if record.entity_type == "Person" and record.affiliation:
                relationships["associated_with"].append((record.entity_id, record.affiliation))
            if record.entity_type == "Interaction" and record.notes:
                for other in self.store.get_records(self.dataset_name):
                    if other.entity_type == "Person" and other.notes and record.name in other.notes:
                        relationships["attended"].append((other.entity_id, record.entity_id))
        return relationships

    def search(self, query: str, limit: int = 5) -> List[Tuple[EntityRecord, float]]:
        return search(self.store, self.dataset_name, query, limit=limit)

    def timeline(self) -> List[Tuple[datetime, EntityRecord]]:
        events: List[Tuple[datetime, EntityRecord]] = []
        for record in self.store.get_records(self.dataset_name):
            if record.last_seen:
                events.append((record.last_seen, record))
        return sorted(events, key=lambda item: item[0], reverse=True)

    def summarize(self) -> Dict[str, List[str]]:
        summary: Dict[str, List[str]] = {
            "ontology": self.ontology.describe(),
            "datasets": [f"Dataset '{self.dataset_name}' with {len(self.store.get_records(self.dataset_name))} records"],
            "relationships": [],
        }

        for name, edges in self.build_relationships().items():
            summary["relationships"].append(f"{name}: {len(edges)} edges")
        return summary


__all__ = ["WorkspaceSession"]
