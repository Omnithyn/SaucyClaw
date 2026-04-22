"""测试本体 Mapping。

N2 — Ontology Governance Loop
验证 map_raw_event_to_ontology 的功能。
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ontology.mapping import (  # noqa: E402
    map_raw_event_to_ontology,
    EventMappingResult,
)
from ontology.loader import load_default_ontology_schema  # noqa: E402


class TestMapRawEventToOntology:
    """测试 map_raw_event_to_ontology。"""

    def test_map_tool_invocation_event(self):
        """映射 tool invocation 事件。"""
        ontology_schema = load_default_ontology_schema()

        raw_event = {
            "event": "pre_tool_use",
            "payload": {
                "tool_name": "Write",
                "assignee": "CEO",
            },
        }

        result = map_raw_event_to_ontology(raw_event, ontology_schema)

        assert isinstance(result, EventMappingResult)
        assert result.event_instance.event_type == "tool-invocation"
        assert result.event_instance.event_data.get("tool_name") == "Write"

    def test_map_entity_instance_from_event(self):
        """从事件映射 EntityInstance。"""
        ontology_schema = load_default_ontology_schema()

        raw_event = {
            "event": "pre_tool_use",
            "payload": {
                "tool_name": "Write",
                "assignee": "CEO",
                "capabilities": ["review", "approve"],
            },
        }

        result = map_raw_event_to_ontology(raw_event, ontology_schema)

        assert len(result.entity_instances) >= 1
        entity = result.entity_instances[0]
        assert entity.name == "CEO"
        assert entity.entity_type == "agent-role"
        assert entity.properties.get("capabilities") == ["review", "approve"]

    def test_map_context_snapshot_from_event(self):
        """从事件映射 ContextSnapshot。"""
        ontology_schema = load_default_ontology_schema()

        raw_event = {
            "event": "pre_tool_use",
            "payload": {
                "tool_name": "Write",
                "session_id": "abc123",
                "workspace": "/path/to/project",
            },
        }

        result = map_raw_event_to_ontology(raw_event, ontology_schema)

        assert result.context_snapshot is not None
        assert result.context_snapshot.context_type == "session-context"
        assert result.context_snapshot.snapshot.get("session_id") == "abc123"

    def test_map_event_without_context(self):
        """映射无上下文的事件。"""
        ontology_schema = load_default_ontology_schema()

        raw_event = {
            "event": "pre_tool_use",
            "payload": {
                "tool_name": "Write",
            },
        }

        result = map_raw_event_to_ontology(raw_event, ontology_schema)

        assert result.context_snapshot is None

    def test_map_unknown_event_type_fallback(self):
        """映射未知事件类型（fallback 到 tool-invocation）。"""
        ontology_schema = load_default_ontology_schema()

        raw_event = {
            "event": "unknown_event",
            "payload": {
                "tool_name": "Read",
            },
        }

        result = map_raw_event_to_ontology(raw_event, ontology_schema)

        # fallback 到 tool-invocation
        assert result.event_instance.event_type == "tool-invocation"

    def test_map_event_with_missing_payload(self):
        """映射缺少 payload 的事件。"""
        ontology_schema = load_default_ontology_schema()

        raw_event = {
            "event": "pre_tool_use",
        }

        result = map_raw_event_to_ontology(raw_event, ontology_schema)

        assert result.event_instance is not None
        assert len(result.entity_instances) >= 1
        # 默认名称为 "unknown"
        assert result.entity_instances[0].name == "unknown"
