"""测试本体 Schema 定义。

N1 — Ontology Core Foundation
验证 EventType、ContextType、FactType、EvidenceRef、PolicyBinding 的定义与构建。
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ontology.schema import (  # noqa: E402
    EventType,
    ContextType,
    FactType,
    EvidenceRef,
    PolicyBinding,
    OntologySchema,
    build_event_type_from_dict,
    build_context_type_from_dict,
    build_fact_type_from_dict,
    build_policy_binding_from_dict,
)


class TestEventType:
    """测试 EventType 定义。"""

    def test_event_type_minimal(self):
        """最小事件类型定义。"""
        event_type = EventType(
            id="tool-invocation",
            name="工具调用",
            description="Agent 调用工具",
            subject_type="agent-role",
        )

        assert event_type.id == "tool-invocation"
        assert event_type.subject_type == "agent-role"
        assert event_type.object_type is None
        assert event_type.timestamp_field == "timestamp"

    def test_event_type_with_object(self):
        """带客体的事件类型。"""
        event_type = EventType(
            id="task-assignment",
            name="任务分配",
            description="任务分配给 Agent",
            subject_type="agent-role",
            object_type="task-type",
        )

        assert event_type.object_type == "task-type"

    def test_build_event_type_from_dict(self):
        """从 dict 构建 EventType。"""
        data = {
            "id": "review-request",
            "name": "审查请求",
            "description": "请求审查",
            "subject_type": "agent-role",
            "object_type": "task-type",
            "properties": ["review_type", "reviewer_role"],
        }

        event_type = build_event_type_from_dict(data)

        assert event_type.id == "review-request"
        assert event_type.properties == ["review_type", "reviewer_role"]


class TestContextType:
    """测试 ContextType 定义。"""

    def test_context_type_ephemeral(self):
        """瞬态上下文类型。"""
        context_type = ContextType(
            id="session-context",
            name="会话上下文",
            description="Agent 会话环境",
            lifecycle="ephemeral",
        )

        assert context_type.lifecycle == "ephemeral"

    def test_context_type_persistent(self):
        """持久上下文类型。"""
        context_type = ContextType(
            id="workspace-context",
            name="工作空间上下文",
            description="工作空间状态",
            lifecycle="persistent",
        )

        assert context_type.lifecycle == "persistent"

    def test_build_context_type_from_dict(self):
        """从 dict 构建 ContextType。"""
        data = {
            "id": "execution-context",
            "name": "执行上下文",
            "description": "执行环境",
            "properties": ["operation_id", "tool_name"],
            "lifecycle": "ephemeral",
        }

        context_type = build_context_type_from_dict(data)

        assert context_type.id == "execution-context"
        assert context_type.properties == ["operation_id", "tool_name"]


class TestFactType:
    """测试 FactType 定义。"""

    def test_fact_type_minimal(self):
        """最小事实类型定义。"""
        fact_type = FactType(
            id="review-requirement",
            name="审查要求",
            description="任务需要审查",
            subject_type="agent-role",
        )

        assert fact_type.id == "review-requirement"
        assert fact_type.evidence_binding is True

    def test_fact_type_with_object(self):
        """带客体的事实类型。"""
        fact_type = FactType(
            id="permission-grant",
            name="权限授予",
            description="权限授予事实",
            subject_type="agent-role",
            object_type="permission",
            establishment_condition="Role.has_permission == True",
        )

        assert fact_type.object_type == "permission"
        assert fact_type.establishment_condition is not None

    def test_build_fact_type_from_dict(self):
        """从 dict 构建 FactType。"""
        data = {
            "id": "role-assignment",
            "name": "角色分配",
            "description": "角色分配事实",
            "subject_type": "agent-role",
            "object_type": "agent-role",
            "evidence_binding": True,
        }

        fact_type = build_fact_type_from_dict(data)

        assert fact_type.id == "role-assignment"
        assert fact_type.object_type == "agent-role"


class TestEvidenceRef:
    """测试 EvidenceRef 定义。"""

    def test_evidence_ref_direct(self):
        """直接证据引用。"""
        evidence_ref = EvidenceRef(
            evidence_id="ev-123",
            fact_type="review-requirement",
            fact_id="fact-456",
            binding_type="direct",
        )

        assert evidence_ref.evidence_id == "ev-123"
        assert evidence_ref.binding_type == "direct"
        assert evidence_ref.semantic_role == "supports"

    def test_evidence_ref_inferred(self):
        """推断证据引用。"""
        evidence_ref = EvidenceRef(
            evidence_id="ev-789",
            fact_type="permission-grant",
            fact_id="fact-012",
            binding_type="inferred",
            semantic_role="contradicts",
        )

        assert evidence_ref.binding_type == "inferred"
        assert evidence_ref.semantic_role == "contradicts"


class TestPolicyBinding:
    """测试 PolicyBinding 定义。"""

    def test_policy_binding_to_entity(self):
        """绑定到实体类型的策略。"""
        binding = PolicyBinding(
            policy_id="policy-001",
            policy_name="CEO 审查策略",
            binds_to_entity_type="agent-role",
            ontology_condition="name == 'CEO'",
            judgment_mode="ontology",
        )

        assert binding.binds_to_entity_type == "agent-role"
        assert binding.binds_to_fact_type is None
        assert binding.judgment_mode == "ontology"

    def test_policy_binding_to_fact(self):
        """绑定到事实类型的策略。"""
        binding = PolicyBinding(
            policy_id="policy-002",
            policy_name="审查要求策略",
            binds_to_fact_type="review-requirement",
            ontology_condition="required == True",
            judgment_mode="ontology",
        )

        assert binding.binds_to_fact_type == "review-requirement"

    def test_policy_binding_hybrid(self):
        """混合判断模式策略。"""
        binding = PolicyBinding(
            policy_id="policy-003",
            policy_name="混合策略",
            binds_to_event_type="tool-invocation",
            binds_to_fact_type="review-requirement",
            ontology_condition="tool_name == 'Write'",
            judgment_mode="hybrid",
        )

        assert binding.binds_to_event_type == "tool-invocation"
        assert binding.judgment_mode == "hybrid"

    def test_build_policy_binding_from_dict(self):
        """从 dict 构建 PolicyBinding。"""
        data = {
            "policy_id": "policy-004",
            "policy_name": "测试策略",
            "binds_to_entity_type": "agent-role",
            "ontology_condition": "capabilities contains 'review'",
            "judgment_mode": "ontology",
        }

        binding = build_policy_binding_from_dict(data)

        assert binding.policy_id == "policy-004"
        assert binding.binds_to_entity_type == "agent-role"


class TestOntologySchema:
    """测试 OntologySchema 组合。"""

    def test_ontology_schema_empty(self):
        """空本体 Schema。"""
        schema = OntologySchema()

        assert schema.event_types == []
        assert schema.context_types == []
        assert schema.fact_types == []

    def test_ontology_schema_with_types(self):
        """带类型的本体 Schema。"""
        event_type = EventType(
            id="tool-invocation",
            name="工具调用",
            description="Agent 调用工具",
            subject_type="agent-role",
        )
        context_type = ContextType(
            id="session-context",
            name="会话上下文",
            description="Agent 会话环境",
        )
        fact_type = FactType(
            id="review-requirement",
            name="审查要求",
            description="任务需要审查",
            subject_type="agent-role",
        )

        schema = OntologySchema(
            event_types=[event_type],
            context_types=[context_type],
            fact_types=[fact_type],
        )

        assert len(schema.event_types) == 1
        assert schema.get_event_type("tool-invocation") == event_type
        assert schema.get_context_type("session-context") == context_type
        assert schema.get_fact_type("review-requirement") == fact_type
        assert schema.get_event_type("unknown") is None
