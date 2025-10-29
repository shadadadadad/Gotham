# Gotham MVP

This project provides a minimal, pedagogical clone of Palantir Gotham. It focuses on the
core primitives that underlie data fusion platforms: ingestion, ontology management,
entity resolution, and collaborative analysis workspaces. The code base is intentionally
lightweight so it can serve as a learning tool when exploring system design techniques.

## Features

- **Data ingestion pipeline** for CSV files with basic type inference.
- **Ontology manager** that defines entity types, properties, and relationships.
- **In-memory object store** for datasets and relationship graphs.
- **Workspace session** API that powers investigations through search, filters, and
  timeline views.
- **Command line demo** that loads sample data and runs a scripted investigation.

## Getting Started

1. Install dependencies (Python 3.10+ required):

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```

2. Run the demo CLI:

   ```bash
   python -m gotham_mvp.cli --dataset data/sample_people.csv
   ```

3. Execute the test suite:

   ```bash
   python -m unittest discover
   ```

## Project Structure

```
├── data
│   └── sample_people.csv       # Synthetic dataset used by the demo CLI
├── src/gotham_mvp
│   ├── core
│   │   ├── dataset.py          # Dataset abstractions and in-memory store
│   │   ├── ingestion.py        # CSV ingestion pipeline
│   │   ├── ontology.py         # Ontology and schema management
│   │   ├── resolution.py       # Entity resolution helpers
│   │   └── search.py           # Full-text search utilities
│   ├── services
│   │   └── workspace.py        # Investigation workspace API
│   └── cli.py                  # Entry point for the demo scenario
└── tests
    └── test_workspace.py       # Smoke tests for the workspace service
```

The modules are split between low-level **core** primitives and higher-level
**services** that compose them to create the user-facing experience.

## Sample Investigation

The demo investigation recreates an analyst workflow:

1. Load a dataset of people, organizations, and interactions.
2. Resolve entities by deduplicating records based on email address.
3. Enrich records with metadata extracted from free-form text.
4. Build a relationship graph across entities.
5. Query the dataset for key people of interest using full-text search.
6. Generate a timeline summary of interactions for reporting.

The output is printed to the terminal for clarity, but the same API could power a
web-based UI or integrate with a visualization library.

## Extending the MVP

- Add adapters for more data sources (databases, APIs, JSON, Parquet).
- Store the ontology and datasets in a persistent database.
- Build a FastAPI or GraphQL service to provide remote access.
- Integrate a front-end for rich visualizations and collaborative notes.
- Implement a policy layer for access control and data governance.

These extensions, combined with the core building blocks in this repository, provide a
solid foundation for exploring the architectural choices behind enterprise-scale
intelligence platforms.
