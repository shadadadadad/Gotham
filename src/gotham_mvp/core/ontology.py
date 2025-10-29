"""Ontology primitives for describing entities and relationships."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass(slots=True)
class PropertyDefinition:
    name: str
    data_type: str
    description: str = ""


@dataclass(slots=True)
class RelationshipDefinition:
    name: str
    source_type: str
    target_type: str
    description: str = ""


@dataclass(slots=True)
class EntityTypeDefinition:
    name: str
    description: str = ""
    properties: Dict[str, PropertyDefinition] = field(default_factory=dict)

    def add_property(self, prop: PropertyDefinition) -> None:
        self.properties[prop.name] = prop


class Ontology:
    """In-memory ontology registry."""

    def __init__(self) -> None:
        self.entity_types: Dict[str, EntityTypeDefinition] = {}
        self.relationships: Dict[str, RelationshipDefinition] = {}

    def register_entity_type(self, entity: EntityTypeDefinition) -> None:
        self.entity_types[entity.name] = entity

    def register_relationship(self, relationship: RelationshipDefinition) -> None:
        key = f"{relationship.source_type}->{relationship.name}->{relationship.target_type}"
        self.relationships[key] = relationship

    def get_entity(self, name: str) -> Optional[EntityTypeDefinition]:
        return self.entity_types.get(name)

    def describe(self) -> List[str]:
        descriptions: List[str] = []
        for entity in self.entity_types.values():
            descriptions.append(f"Entity: {entity.name} - {entity.description}")
            for prop in entity.properties.values():
                descriptions.append(f"  Property: {prop.name} ({prop.data_type}) - {prop.description}")
        for rel in self.relationships.values():
            descriptions.append(
                f"Relationship: {rel.name} ({rel.source_type} -> {rel.target_type}) - {rel.description}"
            )
        return descriptions


__all__ = [
    "PropertyDefinition",
    "RelationshipDefinition",
    "EntityTypeDefinition",
    "Ontology",
]
