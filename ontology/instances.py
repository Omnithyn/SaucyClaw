"""本体实例模型定义。

N1 — Ontology Core Foundation

定义本体实例：
- EntityInstance：实体实例（如具体的 AgentRole）
- RelationInstance：关系实例（如具体的 role-handoff）
- EventInstance：事件实例（如具体的 ToolInvocation）
- ContextSnapshot：上下文快照（如 SessionContext）
- FactRecord：事实记录（如具体的 ReviewRequirement）

实例是 Schema 类型的具体化。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import uuid


@dataclass(frozen=True)
class EntityInstance:
    """实体实例。

    实体是本体的"对象"。
    如：AgentRole(name="CEO", capabilities=["review", "approve"])。

    关键：
    - entity_type：指向 EntityType.id
    - properties：实体的具体属性值
    """

    instance_id: str  # 实例唯一标识
    entity_type: str  # 实体类型 ID（如 "agent-role"）
    name: str  # 实例名称（如 "CEO"）

    # 实体属性值
    properties: dict[str, Any] = field(default_factory=dict)

    # 实体的元数据
    created_at: datetime = field(default_factory=datetime.utcnow)
    source: str = "unknown"  # 实例来源（如 "config" | "runtime" | "event"）


@dataclass(frozen=True)
class RelationInstance:
    """关系实例。

    关系是本体中"对象之间的连接"。
    如：role-handoff(source="CEO", target="Reviewer")。

    关键：
    - relation_type：指向 RelationType.id
    - source_instance_id：源实体实例 ID
    - target_instance_id：目标实体实例 ID
    """

    instance_id: str
    relation_type: str  # 关系类型 ID（如 "role-handoff"）

    # 关系的源和目标
    source_instance_id: str
    target_instance_id: str

    # 关系的属性值（可选）
    properties: dict[str, Any] = field(default_factory=dict)

    # 关系的元数据
    established_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class EventInstance:
    """事件实例。

    事件是本体中"发生的动作或状态变化"。
    如：ToolInvocation(subject="CEO", object="Write", timestamp=...)。

    关键：
    - event_type：指向 EventType.id
    - subject_instance_id：主体实例 ID
    - object_instance_id：客体实例 ID（可选）
    """

    instance_id: str
    event_type: str  # 事件类型 ID（如 "tool-invocation"）

    # 事件的主体和客体
    subject_instance_id: str
    object_instance_id: str | None = None

    # 事件的属性值
    event_data: dict[str, Any] = field(default_factory=dict)

    # 事件的时间戳
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # 事件的上下文引用
    context_snapshot_id: str | None = None


@dataclass(frozen=True)
class ContextSnapshot:
    """上下文快照。

    上下文是事件发生时的"环境状态"。
    如：SessionContext(session_id="abc", workspace="/path")。

    关键：
    - context_type：指向 ContextType.id
    - snapshot：上下文的状态值
    """

    snapshot_id: str
    context_type: str  # 上下文类型 ID（如 "session-context"）

    # 上下文状态值
    snapshot: dict[str, Any] = field(default_factory=dict)

    # 快照时间
    captured_at: datetime = field(default_factory=datetime.utcnow)

    # 快照的生命周期
    expires_at: datetime | None = None


@dataclass(frozen=True)
class FactRecord:
    """事实记录。

    事实是本体中"已发生或已建立的关系或状态"。
    如：ReviewRequirement(subject="CEO", object="code_review", fact_type="review-requirement")。

    关键：
    - fact_type：指向 FactType.id
    - subject_instance_id：事实主体实例 ID
    - object_instance_id：事实客体实例 ID
    - evidence_refs：绑定到本体的证据引用列表
    """

    fact_id: str
    fact_type: str  # 事实类型 ID（如 "review-requirement"）

    # 事实的主体和客体
    subject_instance_id: str
    object_instance_id: str | None = None

    # 事实的属性值
    fact_data: dict[str, Any] = field(default_factory=dict)

    # 绑定的证据引用列表
    evidence_refs: list[str] = field(default_factory=list)  # EvidenceRef.evidence_id 列表

    # 事实的元数据
    established_at: datetime = field(default_factory=datetime.utcnow)
    validity: str = "valid"  # valid | invalid | disputed


# ─── Helper Functions ───


def generate_instance_id(prefix: str = "inst") -> str:
    """生成唯一实例 ID。"""
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def build_entity_instance(
    entity_type: str,
    name: str,
    properties: dict[str, Any],
    source: str = "unknown",
) -> EntityInstance:
    """构建实体实例。"""
    return EntityInstance(
        instance_id=generate_instance_id("entity"),
        entity_type=entity_type,
        name=name,
        properties=properties,
        source=source,
    )


def build_relation_instance(
    relation_type: str,
    source_instance_id: str,
    target_instance_id: str,
    properties: dict[str, Any] | None = None,
) -> RelationInstance:
    """构建关系实例。"""
    return RelationInstance(
        instance_id=generate_instance_id("rel"),
        relation_type=relation_type,
        source_instance_id=source_instance_id,
        target_instance_id=target_instance_id,
        properties=properties or {},
    )


def build_event_instance(
    event_type: str,
    subject_instance_id: str,
    event_data: dict[str, Any],
    object_instance_id: str | None = None,
    context_snapshot_id: str | None = None,
) -> EventInstance:
    """构建事件实例。"""
    return EventInstance(
        instance_id=generate_instance_id("event"),
        event_type=event_type,
        subject_instance_id=subject_instance_id,
        object_instance_id=object_instance_id,
        event_data=event_data,
        context_snapshot_id=context_snapshot_id,
    )


def build_context_snapshot(
    context_type: str,
    snapshot: dict[str, Any],
    expires_at: datetime | None = None,
) -> ContextSnapshot:
    """构建上下文快照。"""
    return ContextSnapshot(
        snapshot_id=generate_instance_id("ctx"),
        context_type=context_type,
        snapshot=snapshot,
        expires_at=expires_at,
    )


def build_fact_record(
    fact_type: str,
    subject_instance_id: str,
    fact_data: dict[str, Any],
    object_instance_id: str | None = None,
    evidence_refs: list[str] | None = None,
) -> FactRecord:
    """构建事实记录。"""
    return FactRecord(
        fact_id=generate_instance_id("fact"),
        fact_type=fact_type,
        subject_instance_id=subject_instance_id,
        object_instance_id=object_instance_id,
        fact_data=fact_data,
        evidence_refs=evidence_refs or [],
    )
