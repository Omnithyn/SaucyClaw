"""本体核心 Schema 定义。

N1 — Ontology Core Foundation

定义本体类型：
- EventType：事件类型（如 ToolInvocation、TaskAssignment）
- ContextType：上下文类型（如 SessionContext、WorkspaceContext）
- FactType：事实类型（如 ReviewRequirement、PermissionGrant）
- EvidenceRef：证据引用结构
- PolicyBinding：策略绑定结构

复用现有 meta_model 的 EntityType、RelationType。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class EventType:
    """事件类型定义。

    事件是本体中发生的"动作"或"状态变化"。
    如：ToolInvocation、TaskAssignment、ReviewRequest。
    """

    id: str
    name: str
    description: str
    subject_type: str  # 事件主体类型（如 "agent-role"）
    object_type: str | None = None  # 事件客体类型（可选）
    properties: list[str] = field(default_factory=list)  # 事件属性名列表

    # 时间戳字段名（默认为 "timestamp"）
    timestamp_field: str = "timestamp"


@dataclass(frozen=True)
class ContextType:
    """上下文类型定义。

    上下文是事件发生时的"环境"或"状态快照"。
    如：SessionContext、WorkspaceContext、ExecutionContext。
    """

    id: str
    name: str
    description: str
    properties: list[str] = field(default_factory=list)

    # 上下文的生命周期
    lifecycle: str = "ephemeral"  # ephemeral（瞬态）| persistent（持久）


@dataclass(frozen=True)
class FactType:
    """事实类型定义。

    事实是本体中"已发生"或"已建立"的关系或状态。
    如：ReviewRequirement、PermissionGrant、RoleAssignment。

    事实可以被证据引用，形成证据链。
    """

    id: str
    name: str
    description: str

    # 事实的主体和客体类型
    subject_type: str
    object_type: str | None = None

    # 事实的成立条件（本体语义层）
    establishment_condition: str | None = None

    # 事实是否可被证据引用
    evidence_binding: bool = True


@dataclass(frozen=True)
class EvidenceRef:
    """证据引用结构。

    将治理证据绑定到本体事实，而非仅作为治理附属信息。

    结构：
    - evidence_id：证据唯一标识（指向 stores/evidence 中的证据）
    - fact_type：所绑定的事实类型
    - fact_id：所绑定的事实实例 ID
    - binding_type：绑定方式（direct | inferred | aggregated）
    """

    evidence_id: str
    fact_type: str
    fact_id: str
    binding_type: str = "direct"  # direct | inferred | aggregated

    # 证据在本体中的语义角色
    semantic_role: str = "supports"  # supports | contradicts | neutral


@dataclass(frozen=True)
class PolicyBinding:
    """策略绑定结构。

    将规则绑定到本体语义层（对象/关系/事件/上下文/事实），
    而非仅绑定到字段判断。

    绑定层级：
    - entity_type：绑定到对象类型
    - relation_type：绑定到关系类型
    - event_type：绑定到事件类型
    - context_type：绑定到上下文类型
    - fact_type：绑定到事实类型

    策略判断将从"字段判断"走向"本体判断"。
    """

    policy_id: str  # 策略唯一标识（对应 GovernanceRule）
    policy_name: str

    # 绑定目标（至少一个）
    binds_to_entity_type: str | None = None
    binds_to_relation_type: str | None = None
    binds_to_event_type: str | None = None
    binds_to_context_type: str | None = None
    binds_to_fact_type: str | None = None

    # 本体判断条件（语义层）
    ontology_condition: str | None = None

    # 判断模式
    judgment_mode: str = "ontology"  # ontology | field | hybrid


@dataclass(frozen=True)
class OntologySchema:
    """完整本体 Schema。

    包含所有类型定义：
    - EntityTypes（复用 meta_model）
    - RelationTypes（复用 meta_model）
    - EventTypes
    - ContextTypes
    - FactTypes
    """

    event_types: list[EventType] = field(default_factory=list)
    context_types: list[ContextType] = field(default_factory=list)
    fact_types: list[FactType] = field(default_factory=list)

    def get_event_type(self, type_id: str) -> EventType | None:
        """获取事件类型。"""
        for et in self.event_types:
            if et.id == type_id:
                return et
        return None

    def get_context_type(self, type_id: str) -> ContextType | None:
        """获取上下文类型。"""
        for ct in self.context_types:
            if ct.id == type_id:
                return ct
        return None

    def get_fact_type(self, type_id: str) -> FactType | None:
        """获取事实类型。"""
        for ft in self.fact_types:
            if ft.id == type_id:
                return ft
        return None


# ─── Helper Functions ───


def build_event_type_from_dict(data: dict[str, Any]) -> EventType:
    """从 dict 构建 EventType。"""
    return EventType(
        id=data["id"],
        name=data["name"],
        description=data.get("description", ""),
        subject_type=data["subject_type"],
        object_type=data.get("object_type"),
        properties=data.get("properties", []),
        timestamp_field=data.get("timestamp_field", "timestamp"),
    )


def build_context_type_from_dict(data: dict[str, Any]) -> ContextType:
    """从 dict 构建 ContextType。"""
    return ContextType(
        id=data["id"],
        name=data["name"],
        description=data.get("description", ""),
        properties=data.get("properties", []),
        lifecycle=data.get("lifecycle", "ephemeral"),
    )


def build_fact_type_from_dict(data: dict[str, Any]) -> FactType:
    """从 dict 构建 FactType。"""
    return FactType(
        id=data["id"],
        name=data["name"],
        description=data.get("description", ""),
        subject_type=data["subject_type"],
        object_type=data.get("object_type"),
        establishment_condition=data.get("establishment_condition"),
        evidence_binding=data.get("evidence_binding", True),
    )


def build_policy_binding_from_dict(data: dict[str, Any]) -> PolicyBinding:
    """从 dict 构建 PolicyBinding。"""
    return PolicyBinding(
        policy_id=data["policy_id"],
        policy_name=data["policy_name"],
        binds_to_entity_type=data.get("binds_to_entity_type"),
        binds_to_relation_type=data.get("binds_to_relation_type"),
        binds_to_event_type=data.get("binds_to_event_type"),
        binds_to_context_type=data.get("binds_to_context_type"),
        binds_to_fact_type=data.get("binds_to_fact_type"),
        ontology_condition=data.get("ontology_condition"),
        judgment_mode=data.get("judgment_mode", "ontology"),
    )
