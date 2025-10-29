"""Smoke tests for the Gotham MVP workspace service."""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest import TestCase

from gotham_mvp.core.dataset import DatasetStore
from gotham_mvp.core.ingestion import ingest_entities
from gotham_mvp.core.ontology import Ontology
from gotham_mvp.services.workspace import WorkspaceSession


class WorkspaceTestCase(TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.dataset_path = Path(self.tmpdir.name) / "sample.csv"
        self.dataset_path.write_text(
            """entity_id,entity_type,name,email,affiliation,last_seen,notes\n"""
            "1,Person,Alice,a@example.com,Axis Corp,2024-05-20,Met Bob\n"
            "2,Person,Alice,a@example.com,Axis Corp,2024-05-21,Follow up\n"
            "3,Interaction,Project,,Axis Corp,2024-05-18,Referenced in memo\n"
        )
        store = DatasetStore()
        ontology = Ontology()
        self.workspace = WorkspaceSession("test", store, ontology)
        self.workspace.bootstrap_default_ontology()
        self.workspace.ingest(list(ingest_entities(self.dataset_path)))

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_resolution_merges_duplicates(self) -> None:
        self.workspace.resolve_entities()
        records = self.workspace.store.get_records("test")
        emails = {record.email for record in records if record.entity_type == "Person"}
        self.assertEqual(emails, {"a@example.com"})

    def test_search_returns_ranked_results(self) -> None:
        self.workspace.resolve_entities()
        self.workspace.enrich()
        results = self.workspace.search("Axis")
        self.assertTrue(results)
        record, score = results[0]
        self.assertIn("Axis", record.affiliation or "")
        self.assertGreater(score, 0)

    def test_timeline_orders_events(self) -> None:
        timeline = self.workspace.timeline()
        self.assertTrue(timeline)
        self.assertGreaterEqual(timeline[0][0], timeline[-1][0])
