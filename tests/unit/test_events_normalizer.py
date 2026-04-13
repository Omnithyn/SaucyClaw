"""事件标准化器测试。"""

from __future__ import annotations

from core.events.normalizer import EventNormalizer


class TestEventNormalizer:
    def test_explicit_fields(self):
        """显式字段格式的事件。"""
        raw = {
            "event_type": "task_assigned",
            "source": "openclaw",
            "session_id": "sess-001",
            "timestamp": "2026-04-13T10:00:00Z",
            "payload": {"task_id": "t-1", "assignee": "developer"},
        }
        normalizer = EventNormalizer()
        event = normalizer.normalize(raw)

        assert event.event_type == "task_assigned"
        assert event.source == "openclaw"
        assert event.session_id == "sess-001"
        assert event.timestamp == "2026-04-13T10:00:00Z"
        assert event.payload == {"task_id": "t-1", "assignee": "developer"}
        assert event.id  # UUID 不为空

    def test_minimal_format(self):
        """极简格式：只包含 type 和 payload。"""
        raw = {
            "type": "code_change",
            "payload": {"files": ["main.py"]},
        }
        normalizer = EventNormalizer()
        event = normalizer.normalize(raw)

        assert event.event_type == "code_change"
        assert event.source == "unknown"
        assert event.session_id == ""
        assert event.payload == {"files": ["main.py"]}

    def test_flat_payload_extraction(self):
        """扁平事件：元字段外的内容提取为 payload。"""
        raw = {
            "event_type": "review_requested",
            "session_id": "sess-002",
            "reviewer": "alice",
            "files_count": 3,
        }
        normalizer = EventNormalizer()
        event = normalizer.normalize(raw)

        assert event.event_type == "review_requested"
        assert event.session_id == "sess-002"
        assert event.payload == {"reviewer": "alice", "files_count": 3}

    def test_nested_payload_preferred(self):
        """如果 raw_event 有嵌套 payload 字段，优先使用。"""
        raw = {
            "event_type": "output_intercept",
            "payload": {"output": "generated_code", "lines": 42},
            "extra_field": "should_be_ignored",
        }
        normalizer = EventNormalizer()
        event = normalizer.normalize(raw)

        assert event.payload == {"output": "generated_code", "lines": 42}

    def test_unknown_type_defaults(self):
        """没有任何 type 字段时默认为 unknown。"""
        raw = {"session_id": "s1"}
        normalizer = EventNormalizer()
        event = normalizer.normalize(raw)

        assert event.event_type == "unknown"
        assert event.source == "unknown"

    def test_generate_timestamp(self):
        """无 timestamp 时自动生成 ISO 时间戳。"""
        raw = {"type": "tick"}
        normalizer = EventNormalizer()
        event = normalizer.normalize(raw)

        assert event.timestamp.endswith("Z") or "+" in event.timestamp

    def test_batch_normalize(self):
        raw_events = [
            {"type": "e1", "session_id": "s1"},
            {"type": "e2", "session_id": "s2"},
            {"event_type": "e3", "source": "test"},
        ]
        normalizer = EventNormalizer()
        events = normalizer.normalize_batch(raw_events)

        assert len(events) == 3
        assert events[0].event_type == "e1"
        assert events[1].event_type == "e2"
        assert events[2].event_type == "e3"

    def test_unique_ids(self):
        """每个事件 ID 应唯一。"""
        raw = {"type": "x"}
        normalizer = EventNormalizer()
        ids = {normalizer.normalize(raw).id for _ in range(10)}
        assert len(ids) == 10
