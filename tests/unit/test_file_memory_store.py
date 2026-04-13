"""FileMemoryStore 测试。"""

from __future__ import annotations

import uuid

from stores.file.memory.store import FileMemoryStore
from stores.protocols import MemoryRecord


def _make_record(
    record_id: str | None = None,
    tags: list[str] | None = None,
    record_type: str = "governance_rule",
) -> MemoryRecord:
    return MemoryRecord(
        id=record_id or str(uuid.uuid4()),
        type=record_type,
        summary="test summary",
        tags=tags or ["test"],
        source_evidences=["ev-1"],
        created_at="2026-04-13T10:00:00Z",
    )


class TestFileMemoryStore:
    def test_write_and_search_by_tag(self, tmp_path):
        store = FileMemoryStore(tmp_path / "memory")
        rec = _make_record(tags=["governance", "block"])
        store.write(rec)

        results = store.search({"tags": ["governance"]})
        assert len(results) == 1
        assert results[0].id == rec.id

    def test_search_by_type(self, tmp_path):
        store = FileMemoryStore(tmp_path / "memory")
        store.write(_make_record(record_type="rule_hit"))
        store.write(_make_record(record_type="rule_miss"))

        results = store.search({"type": "rule_hit"})
        assert len(results) == 1
        assert results[0].type == "rule_hit"

    def test_search_with_no_match(self, tmp_path):
        store = FileMemoryStore(tmp_path / "memory")
        store.write(_make_record(tags=["alpha"]))

        results = store.search({"tags": ["beta"]})
        assert results == []

    def test_search_limit(self, tmp_path):
        store = FileMemoryStore(tmp_path / "memory")
        for i in range(5):
            store.write(_make_record(tags=["common"]))

        results = store.search({"tags": ["common"]}, limit=2)
        assert len(results) <= 2

    def test_search_no_filter_returns_all(self, tmp_path):
        store = FileMemoryStore(tmp_path / "memory")
        for i in range(3):
            store.write(_make_record(tags=[f"tag-{i}"]))

        results = store.search({}, limit=10)
        assert len(results) == 3

    def test_decay_is_noop(self, tmp_path):
        store = FileMemoryStore(tmp_path / "memory")
        store.write(_make_record())
        store.decay()  # 不应报错
        results = store.search({})
        assert len(results) == 1

    def test_write_creates_json_file(self, tmp_path):
        rec_id = str(uuid.uuid4())
        store = FileMemoryStore(tmp_path / "memory")
        store.write(_make_record(record_id=rec_id))

        json_path = tmp_path / "memory" / f"{rec_id}.json"
        assert json_path.exists()
