"""FileEvidenceStore 测试。"""

from __future__ import annotations

import uuid

from stores.file.evidence.store import FileEvidenceStore
from stores.protocols import Evidence


def _make_evidence(session_id: str = "sess-001", ev_type: str = "block") -> Evidence:
    return Evidence(
        id=str(uuid.uuid4()),
        type=ev_type,
        assertion="test assertion",
        source_ref="event-001",
        timestamp="2026-04-13T10:00:00Z",
        confidence=1.0,
        applicable_scope={"session_id": session_id},
    )


class TestFileEvidenceStore:
    def test_record_and_get(self, tmp_path):
        store = FileEvidenceStore(tmp_path / "evidence")
        ev = _make_evidence()
        ev_id = store.record(ev)

        retrieved = store.get(ev_id)
        assert retrieved is not None
        assert retrieved.id == ev_id
        assert retrieved.type == "block"

    def test_record_creates_jsonl(self, tmp_path):
        store = FileEvidenceStore(tmp_path / "evidence")
        ev = _make_evidence(session_id="test-session")
        store.record(ev)

        jsonl_path = tmp_path / "evidence" / "test-session.jsonl"
        assert jsonl_path.exists()
        lines = jsonl_path.read_text().strip().splitlines()
        assert len(lines) == 1

    def test_batch_record(self, tmp_path):
        store = FileEvidenceStore(tmp_path / "evidence")
        evs = [_make_evidence() for _ in range(3)]
        ids = store.batch_record(evs)

        assert len(ids) == 3
        for ev_id in ids:
            assert store.get(ev_id) is not None

    def test_query_by_session(self, tmp_path):
        store = FileEvidenceStore(tmp_path / "evidence")
        store.record(_make_evidence(session_id="s1"))
        store.record(_make_evidence(session_id="s1"))
        store.record(_make_evidence(session_id="s2"))

        results = store.query({"session_id": "s1"})
        assert len(results) == 2

    def test_query_by_type(self, tmp_path):
        store = FileEvidenceStore(tmp_path / "evidence")
        store.record(_make_evidence(ev_type="block"))
        store.record(_make_evidence(ev_type="review"))

        results = store.query({"type": "block"})
        assert len(results) == 1
        assert results[0].type == "block"

    def test_query_by_confidence_gte(self, tmp_path):
        store = FileEvidenceStore(tmp_path / "evidence")
        store.record(_make_evidence(ev_type="block"))  # confidence=1.0
        store.record(Evidence(
            id=str(uuid.uuid4()),
            type="review",
            assertion="low conf",
            source_ref="e1",
            timestamp="2026-04-13T10:00:00Z",
            confidence=0.5,
            applicable_scope={"session_id": "sess-001"},
        ))

        results = store.query({"confidence_gte": 1.0})
        assert len(results) == 1
        assert results[0].confidence == 1.0

    def test_get_missing_returns_none(self, tmp_path):
        store = FileEvidenceStore(tmp_path / "evidence")
        assert store.get("nonexistent-id") is None

    def test_default_session_for_no_scope(self, tmp_path):
        ev = Evidence(
            id=str(uuid.uuid4()),
            type="test",
            assertion="",
            source_ref="e1",
            timestamp="2026-04-13T10:00:00Z",
            confidence=1.0,
            applicable_scope=None,
        )
        store = FileEvidenceStore(tmp_path / "evidence")
        store.record(ev)

        default_path = tmp_path / "evidence" / "_default.jsonl"
        assert default_path.exists()
