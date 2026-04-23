"""事件映射器。

N2 — Ontology Governance Loop
N2.1 — RuntimePackage-Driven Governance Realignment

把 raw runtime event 映射为：
- EventInstance
- EntityInstance
- ContextSnapshot

N2.1 新增：
- map_raw_event_with_package() Package-driven 映射
- Schema 驱动的 event_type 识别
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ontology.authoring_package import RuntimePackage
from ontology.schema import OntologySchema, EventType
from ontology.instances import (
    EntityInstance,
    EventInstance,
    ContextSnapshot,
    build_entity_instance,
    build_event_instance,
    build_context_snapshot,
)


class EventMappingError(Exception):
    """事件映射失败。"""


@dataclass(frozen=True)
class EventMappingResult:
    """事件映射结果。

    包含：
    - event_instance：映射的事件实例
    - entity_instances：映射的实体实例列表
    - context_snapshot：映射的上下文快照（可选）
    """

    event_instance: EventInstance
    entity_instances: list[EntityInstance]
    context_snapshot: ContextSnapshot | None = None


# ─── 映射器 ───


def map_raw_event_to_ontology(
    raw_event: dict[str, Any],
    ontology_schema: OntologySchema,
) -> EventMappingResult:
    """将 raw runtime event 映射到本体实例。

    最小映射逻辑：
    1. 从 raw_event 识别 event_type（如 "pre_tool_use" → "tool-invocation"）
    2. 构建 EventInstance
    3. 构建 subject EntityInstance
    4. 构建 ContextSnapshot（如有上下文信息）

    返回 EventMappingResult。
    """
    # 识别 event_type
    event_type_id = _detect_event_type(raw_event)
    event_type = ontology_schema.get_event_type(event_type_id)

    if event_type is None:
        # fallback 到默认 tool-invocation
        event_type_id = "tool-invocation"
        event_type = ontology_schema.get_event_type(event_type_id)
        if event_type is None:
            raise EventMappingError(f"EventType {event_type_id!r} not found")

    # 构建主体 EntityInstance
    subject_entity = _build_subject_entity(raw_event, event_type)

    # 构建 EventInstance
    event_data = _extract_event_data(raw_event, event_type)
    event_instance = build_event_instance(
        event_type=event_type_id,
        subject_instance_id=subject_entity.instance_id,
        event_data=event_data,
        object_instance_id=None,  # 最小映射暂不处理客体
    )

    # 构建 ContextSnapshot（可选）
    context_snapshot = _build_context_snapshot(raw_event)

    return EventMappingResult(
        event_instance=event_instance,
        entity_instances=[subject_entity],
        context_snapshot=context_snapshot,
    )


def _detect_event_type(raw_event: dict[str, Any]) -> str:
    """检测 event_type。

    最小映射规则：
    - "pre_tool_use" → "tool-invocation"
    - "task_assignment" → "task-assignment"
    - 其他 → "tool-invocation"
    """
    # 从 raw_event 的 event 字段识别
    raw_event_type = raw_event.get("event", "unknown")

    # 映射规则
    mapping = {
        "pre_tool_use": "tool-invocation",
        "post_tool_use": "tool-invocation",
        "task_assignment": "task-assignment",
        "review_request": "review-request",
    }

    return mapping.get(raw_event_type, "tool-invocation")


def _build_subject_entity(
    raw_event: dict[str, Any],
    event_type: EventType,
) -> EntityInstance:
    """构建主体 EntityInstance。

    从 raw_event 的 payload 中提取 subject 信息。
    如：assignee → AgentRole
    """
    payload = raw_event.get("payload", {})

    # 提取主体名称
    subject_name = payload.get("assignee", payload.get("agent", "unknown"))

    # 提取主体属性
    properties: dict[str, Any] = {}
    if "capabilities" in payload:
        properties["capabilities"] = payload["capabilities"]
    if "permissions" in payload:
        properties["permissions"] = payload["permissions"]

    return build_entity_instance(
        entity_type=event_type.subject_type,
        name=subject_name,
        properties=properties,
        source="runtime",
    )


def _extract_event_data(
    raw_event: dict[str, Any],
    event_type: EventType,
) -> dict[str, Any]:
    """提取事件数据。

    从 raw_event payload 中提取 event_type.properties 定义的字段。
    """
    payload = raw_event.get("payload", {})

    event_data: dict[str, Any] = {}

    # 提取定义的属性
    for prop_name in event_type.properties:
        if prop_name in payload:
            event_data[prop_name] = payload[prop_name]

    # 补充额外字段
    if "tool_name" in payload:
        event_data["tool_name"] = payload["tool_name"]
    if "tool_args" in payload:
        event_data["tool_args"] = payload["tool_args"]

    return event_data


def _build_context_snapshot(
    raw_event: dict[str, Any],
) -> ContextSnapshot | None:
    """构建 ContextSnapshot（可选）。

    从 raw_event 提取上下文信息。
    """
    payload = raw_event.get("payload", {})

    context_data: dict[str, Any] = {}

    # 提取上下文字段
    if "session_id" in payload:
        context_data["session_id"] = payload["session_id"]
    if "workspace" in payload:
        context_data["workspace_path"] = payload["workspace"]
    if "timestamp" in raw_event:
        context_data["timestamp"] = raw_event["timestamp"]

    if not context_data:
        return None

    return build_context_snapshot(
        context_type="session-context",
        snapshot=context_data,
    )


# ─── N2.1 Package-Driven Mapping ───


def map_raw_event_with_package(
    raw_event: dict[str, Any],
    runtime_package: RuntimePackage,
) -> EventMappingResult:
    """Package-driven 事件映射（N2.1 正式入口）。

    Schema 驱动的 event_type 识别：
    1. 从 runtime_package.ontology_schema.event_types 动态匹配
    2. Fallback 到默认映射表

    Args:
        raw_event: 原始运行时事件
        runtime_package: 编译后的运行时包

    Returns:
        EventMappingResult
    """
    ontology_schema = runtime_package.ontology_schema

    # Schema-driven 识别 event_type
    event_type_id = _schema_driven_detect_event_type(raw_event, ontology_schema)

    event_type = ontology_schema.get_event_type(event_type_id)
    if event_type is None:
        # Fallback 到默认 tool-invocation
        event_type_id = "tool-invocation"
        event_type = ontology_schema.get_event_type(event_type_id)
        if event_type is None:
            # 创建默认 EventType（当 schema 为空时）
            event_type = EventType(
                id="tool-invocation",
                name="Tool Invocation",
                description="默认工具调用事件",
                subject_type="agent-role",
                properties=["tool_name", "tool_args"],
            )

    # 构建主体 EntityInstance（Schema-driven）
    subject_entity = _schema_driven_build_subject_entity(raw_event, event_type)

    # 构建 EventInstance
    event_data = _extract_event_data(raw_event, event_type)
    event_instance = build_event_instance(
        event_type=event_type_id,
        subject_instance_id=subject_entity.instance_id,
        event_data=event_data,
        object_instance_id=None,
    )

    # 构建 ContextSnapshot
    context_snapshot = _build_context_snapshot(raw_event)

    return EventMappingResult(
        event_instance=event_instance,
        entity_instances=[subject_entity],
        context_snapshot=context_snapshot,
    )


def _schema_driven_detect_event_type(
    raw_event: dict[str, Any],
    ontology_schema: OntologySchema,
) -> str:
    """Schema-driven 检测 event_type。

    从 ontology_schema.event_types 动态匹配：
    - 检查 raw_event.event 是否匹配任何 event_type.id
    - 检查 raw_event.event 是否匹配任何 event_type.name
    - Fallback 到默认映射表

    Args:
        raw_event: 原始事件
        ontology_schema: Schema

    Returns:
        event_type_id
    """
    raw_event_type = raw_event.get("event", "unknown")

    # 1. 检查是否直接匹配 event_type.id
    for et in ontology_schema.event_types:
        if et.id == raw_event_type:
            return et.id
        # 检查去除前缀的匹配（如 "tool-invocation" 匹配 "event-tool-invocation"）
        if f"event-{et.id}" == raw_event_type:
            return et.id

    # 2. 检查是否匹配 event_type.name
    for et in ontology_schema.event_types:
        if et.name.lower().replace(" ", "-") == raw_event_type.lower():
            return et.id

    # 3. Fallback 到默认映射表
    fallback_mapping = {
        "pre_tool_use": "tool-invocation",
        "post_tool_use": "tool-invocation",
        "task_assignment": "task-assignment",
        "review_request": "review-request",
    }

    return fallback_mapping.get(raw_event_type, "tool-invocation")


def _schema_driven_build_subject_entity(
    raw_event: dict[str, Any],
    event_type: EventType,
) -> EntityInstance:
    """Schema-driven 构建主体 EntityInstance。

    从 event_type.subject_type 推导 entity_type。
    从 payload 提取属性（基于 event_type.properties）。

    Args:
        raw_event: 原始事件
        event_type: 事件类型定义

    Returns:
        EntityInstance
    """
    payload = raw_event.get("payload", {})

    # 从 subject_type 推导 entity_type
    entity_type = event_type.subject_type

    # 提取主体名称
    subject_name = payload.get("assignee", payload.get("agent", payload.get("user", "unknown")))

    # 根据 event_type.properties 提取属性
    properties: dict[str, Any] = {}
    for prop_name in event_type.properties:
        if prop_name in payload:
            properties[prop_name] = payload[prop_name]

    # 补充额外属性
    if "capabilities" in payload:
        properties["capabilities"] = payload["capabilities"]
    if "permissions" in payload:
        properties["permissions"] = payload["permissions"]

    return build_entity_instance(
        entity_type=entity_type,
        name=subject_name,
        properties=properties,
        source="runtime",
    )
