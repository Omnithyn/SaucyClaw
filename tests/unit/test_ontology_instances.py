"""测试本体实例模型。

N1 — Ontology Core Foundation
验证 EntityInstance、RelationInstance、EventInstance、ContextSnapshot、FactRecord 的构建。
"""

from __future__ import annotations

import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ontology.instances import (  # noqa: E402
    EntityInstance,
    RelationInstance,
    EventInstance,
    ContextSnapshot,
    FactRecord,
    generate_instance_id,
    build_entity_instance,
    build_relation_instance,
    build_event_instance,
    build_context_snapshot,
    build_fact_record,
)


class TestGenerateInstanceId:
    """测试实例 ID 生成。"""

    def test_generate_unique_ids(self):
        """生成唯一 ID。"""
        id1 = generate_instance_id("entity")
        id2 = generate_instance_id("entity")

        assert id1.startswith("entity-")
        assert id2.startswith("entity-")
        assert id1 != id2


class TestEntityInstance:
    """测试 EntityInstance。"""

    def test_entity_instance_minimal(self):
        """最小实体实例。"""
        entity = EntityInstance(
            instance_id="inst-001",
            entity_type="agent-role",
            name="CEO",
        )

        assert entity.instance_id == "inst-001"
        assert entity.entity_type == "agent-role"
        assert entity.name == "CEO"
        assert entity.properties == {}

    def test_entity_instance_with_properties(self):
        """带属性的实体实例。"""
        entity = EntityInstance(
            instance_id="inst-002",
            entity_type="agent-role",
            name="Reviewer",
            properties={"capabilities": ["review", "approve"]},
        )

        assert entity.properties["capabilities"] == ["review", "approve"]

    def test_build_entity_instance(self):
        """构建实体实例。"""
        entity = build_entity_instance(
            entity_type="agent-role",
            name="CEO",
            properties={"permissions": {"write": False}},
            source="config",
        )

        assert entity.entity_type == "agent-role"
        assert entity.name == "CEO"
        assert entity.source == "config"

    def test_entity_instance_is_frozen(self):
        """实体实例不可变。"""
        entity = EntityInstance(
            instance_id="inst-003",
            entity_type="agent-role",
            name="CEO",
        )

        # 尝试修改应抛出异常
        try:
            entity.name = "NewCEO"
            assert False, "Should not allow mutation"
        except AttributeError:
            pass  # 预期行为


class TestRelationInstance:
    """测试 RelationInstance。"""

    def test_relation_instance_minimal(self):
        """最小关系实例。"""
        relation = RelationInstance(
            instance_id="rel-001",
            relation_type="role-handoff",
            source_instance_id="inst-001",
            target_instance_id="inst-002",
        )

        assert relation.relation_type == "role-handoff"
        assert relation.source_instance_id == "inst-001"

    def test_build_relation_instance(self):
        """构建关系实例。"""
        relation = build_relation_instance(
            relation_type="role-handoff",
            source_instance_id="inst-001",
            target_instance_id="inst-002",
            properties={"context": "review"},
        )

        assert relation.relation_type == "role-handoff"
        assert relation.properties["context"] == "review"


class TestEventInstance:
    """测试 EventInstance。"""

    def test_event_instance_minimal(self):
        """最小事件实例。"""
        event = EventInstance(
            instance_id="event-001",
            event_type="tool-invocation",
            subject_instance_id="inst-001",
        )

        assert event.event_type == "tool-invocation"
        assert event.object_instance_id is None

    def test_event_instance_with_data(self):
        """带数据的事件实例。"""
        event = EventInstance(
            instance_id="event-002",
            event_type="tool-invocation",
            subject_instance_id="inst-001",
            event_data={"tool_name": "Write", "tool_args": {"file": "test.py"}},
        )

        assert event.event_data["tool_name"] == "Write"

    def test_build_event_instance(self):
        """构建事件实例。"""
        event = build_event_instance(
            event_type="review-request",
            subject_instance_id="inst-001",
            event_data={"review_type": "code_review"},
            object_instance_id="task-001",
        )

        assert event.event_type == "review-request"
        assert event.object_instance_id == "task-001"


class TestContextSnapshot:
    """测试 ContextSnapshot。"""

    def test_context_snapshot_minimal(self):
        """最小上下文快照。"""
        snapshot = ContextSnapshot(
            snapshot_id="ctx-001",
            context_type="session-context",
            snapshot={"session_id": "abc123"},
        )

        assert snapshot.context_type == "session-context"
        assert snapshot.snapshot["session_id"] == "abc123"

    def test_context_snapshot_with_expiry(self):
        """带过期时间的快照。"""
        expires = datetime(2026, 4, 22, 12, 0, 0)
        snapshot = ContextSnapshot(
            snapshot_id="ctx-002",
            context_type="execution-context",
            snapshot={"operation_id": "op-001"},
            expires_at=expires,
        )

        assert snapshot.expires_at is not None

    def test_build_context_snapshot(self):
        """构建上下文快照。"""
        snapshot = build_context_snapshot(
            context_type="session-context",
            snapshot={"session_id": "xyz", "workspace": "/path"},
        )

        assert snapshot.context_type == "session-context"


class TestFactRecord:
    """测试 FactRecord。"""

    def test_fact_record_minimal(self):
        """最小事实记录。"""
        fact = FactRecord(
            fact_id="fact-001",
            fact_type="review-requirement",
            subject_instance_id="inst-001",
        )

        assert fact.fact_type == "review-requirement"
        assert fact.evidence_refs == []
        assert fact.validity == "valid"

    def test_fact_record_with_evidence(self):
        """带证据引用的事实记录。"""
        fact = FactRecord(
            fact_id="fact-002",
            fact_type="review-requirement",
            subject_instance_id="inst-001",
            evidence_refs=["ev-001", "ev-002"],
        )

        assert len(fact.evidence_refs) == 2

    def test_build_fact_record(self):
        """构建事实记录。"""
        fact = build_fact_record(
            fact_type="review-requirement",
            subject_instance_id="inst-001",
            fact_data={"required": True, "reviewer": "CEO"},
            evidence_refs=["ev-001"],
        )

        assert fact.fact_type == "review-requirement"
        assert fact.fact_data["required"] is True

    def test_fact_record_validity_states(self):
        """事实有效性状态。"""
        valid_fact = FactRecord(
            fact_id="fact-003",
            fact_type="review-requirement",
            subject_instance_id="inst-001",
            validity="valid",
        )

        disputed_fact = FactRecord(
            fact_id="fact-004",
            fact_type="review-requirement",
            subject_instance_id="inst-001",
            validity="disputed",
        )

        assert valid_fact.validity == "valid"
        assert disputed_fact.validity == "disputed"
