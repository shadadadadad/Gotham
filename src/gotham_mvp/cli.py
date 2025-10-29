"""Command-line entry point for the Gotham MVP demo."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

from .core.dataset import DatasetStore
from .core.ingestion import ingest_entities
from .core.ontology import Ontology
from .services.workspace import WorkspaceSession


def load_records(path: Path) -> Iterable:
    return list(ingest_entities(path))


def run_demo(dataset_path: Path) -> None:
    store = DatasetStore()
    ontology = Ontology()
    workspace = WorkspaceSession(dataset_name="investigation", store=store, ontology=ontology)

    workspace.bootstrap_default_ontology()
    workspace.ingest(load_records(dataset_path))
    workspace.resolve_entities()
    workspace.enrich()

    summary = workspace.summarize()
    print("=== Workspace Summary ===")
    for section, lines in summary.items():
        print(f"[{section}]")
        for line in lines:
            print(f"  - {line}")

    print("\n=== Search: 'Axis' ===")
    for record, score in workspace.search("Axis"):
        print(f"{record.name} ({record.entity_type}) score={score:.2f}")

    print("\n=== Timeline ===")
    for ts, record in workspace.timeline():
        formatted = ts.strftime("%Y-%m-%d")
        print(f"{formatted}: {record.name} [{record.entity_type}]")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Gotham MVP investigation demo")
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("data/sample_people.csv"),
        help="Path to the CSV dataset to ingest",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    run_demo(args.dataset)


if __name__ == "__main__":
    main()
