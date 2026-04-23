"""事实建立器。

N2 — Ontology Governance Loop
N2.1 — RuntimePackage-Driven Governance Realignment

从 EventInstance 推导 FactRecord + FactEstablishment + EvidenceChain。

N2.1 新增：
- establish_fact_with_package() Package-driven 建立
- Schema 騱动的 fact_type 推导
- establishment_condition 条件表达式解析
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ontology.authoring_package import RuntimePackage
from ontology.schema import OntologySchema, FactType, EventType
from ontology.instances import (
    EventInstance,
    EntityInstance,
    FactRecord,
    build_fact_record,
)
from ontology.facts import (
    FactEstablishment,
    EvidenceChain,
    build_fact_establishment,
)


class FactEstablishmentError(Exception):
    """事实建立失败。"""


@dataclass(frozen=True)
class FactEstablishmentResult:
    """事实建立结果。

    包含：
    - fact_record：建立的事实记录
    - fact_establishment：事实建立过程
    - evidence_chain：证据链（可选）
    """

    fact_record: FactRecord
    fact_establishment: FactEstablishment
    evidence_chain: EvidenceChain | None = None


# ─── 建立器 ───


def establish_fact_from_event(
    event_instance: EventInstance,
    entity_instances: list[EntityInstance],
    ontology_schema: OntologySchema,
) -> FactEstablishmentResult | None:
    """从 EventInstance 推导 FactRecord。

    最小推导规则：
    - tool-invocation + tool_name == "Write" → review-requirement

    返回 FactEstablishmentResult 或 None（无事实可建立）。
    """
    # 获取 event_type
    event_type = ontology_schema.get_event_type(event_instance.event_type)
    if event_type is None:
        return None

    # 尝试推导事实
    fact_type_id = _derive_fact_type(event_instance, event_type, ontology_schema)
    if fact_type_id is None:
        return None

    fact_type = ontology_schema.get_fact_type(fact_type_id)
    if fact_type is None:
        return None

    # 构建主体 EntityInstance
    subject_entity = _find_subject_entity(event_instance, entity_instances)

    # 构建事实数据
    fact_data = _build_fact_data(event_instance, fact_type)

    # 构建 FactRecord
    fact_record = build_fact_record(
        fact_type=fact_type_id,
        subject_instance_id=subject_entity.instance_id if subject_entity else "unknown",
        fact_data=fact_data,
    )

    # 构建 FactEstablishment
    fact_establishment = build_fact_establishment(
        fact_record=fact_record,
        establishing_event_id=event_instance.instance_id,
        establishment_type="inferred",  # 从事件推导
    )

    return FactEstablishmentResult(
        fact_record=fact_record,
        fact_establishment=fact_establishment,
        evidence_chain=None,  # 最小建立暂无证据链
    )


def _derive_fact_type(
    event_instance: EventInstance,
    event_type: EventType,
    ontology_schema: OntologySchema,
) -> str | None:
    """推导事实类型。

    最小推导规则：
    - tool-invocation + tool_name == "Write" → review-requirement
    """
    # 检查 event_type
    if event_instance.event_type != "tool-invocation":
        return None

    # 检查 tool_name
    tool_name = event_instance.event_data.get("tool_name", "")
    if tool_name != "Write":
        return None

    # 推导为 review-requirement
    return "review-requirement"


def _find_subject_entity(
    event_instance: EventInstance,
    entity_instances: list[EntityInstance],
) -> EntityInstance | None:
    """查找主体 EntityInstance。

    从 entity_instances 中找到 event_instance.subject_instance_id 对应的实例。
    """
    for entity in entity_instances:
        if entity.instance_id == event_instance.subject_instance_id:
            return entity
    return None


def _build_fact_data(
    event_instance: EventInstance,
    fact_type: FactType,
) -> dict[str, Any]:
    """构建事实数据。

    从 event_instance.event_data 提取事实所需数据。
    """
    fact_data: dict[str, Any] = {}

    # 最小规则：tool_name == "Write" → required = True
    if event_instance.event_data.get("tool_name") == "Write":
        fact_data["required"] = True
        fact_data["review_type"] = "code_review"

    return fact_data


# ─── N2.1 Package-Driven Establishment ───


def establish_fact_with_package(
    event_instance: EventInstance,
    entity_instances: list[EntityInstance],
    runtime_package: RuntimePackage,
) -> FactEstablishmentResult | None:
    """Package-driven 建立事实（N2.1 正式入口）。

    Schema 骱动的 fact_type 推导：
    1. 从 runtime_package.ontology_schema.fact_types 查找匹配条件
    2. 解析 establishment_condition 表达式
    3. 构建 FactRecord

    Args:
        event_instance: 事件实例
        entity_instances: 实体实例列表
        runtime_package: 编译后的运行时包

    Returns:
        FactEstablishmentResult 或 None
    """
    ontology_schema = runtime_package.ontology_schema

    # Schema-driven 推导 fact_type
    fact_type_id = _schema_driven_derive_fact_type(
        event_instance,
        ontology_schema,
    )

    if fact_type_id is None:
        return None

    fact_type = ontology_schema.get_fact_type(fact_type_id)
    if fact_type is None:
        return None

    # 构建主体 EntityInstance
    subject_entity = _find_subject_entity(event_instance, entity_instances)

    # 构建事实数据（Schema-driven）
    fact_data = _schema_driven_build_fact_data(event_instance, fact_type)

    # 构建 FactRecord
    fact_record = build_fact_record(
        fact_type=fact_type_id,
        subject_instance_id=subject_entity.instance_id if subject_entity else "unknown",
        fact_data=fact_data,
    )

    # 构建 FactEstablishment
    fact_establishment = build_fact_establishment(
        fact_record=fact_record,
        establishing_event_id=event_instance.instance_id,
        establishment_type="inferred",
    )

    return FactEstablishmentResult(
        fact_record=fact_record,
        fact_establishment=fact_establishment,
        evidence_chain=None,
    )


def _schema_driven_derive_fact_type(
    event_instance: EventInstance,
    ontology_schema: OntologySchema,
) -> str | None:
    """Schema-driven 推导事实类型。

    从 ontology_schema.fact_types 查找：
    - 检查每个 fact_type.establishment_condition
    - 解析条件表达式（如 "tool_name == 'Write'"）
    - 返回第一个匹配的 fact_type.id

    Args:
        event_instance: 事件实例
        ontology_schema: Schema

    Returns:
        fact_type_id 或 None
    """
    for fact_type in ontology_schema.fact_types:
        condition = fact_type.establishment_condition
        if condition is None:
            continue

        # 尝试解析条件表达式
        if _evaluate_condition(condition, event_instance):
            return fact_type.id

    # Fallback 到最小样例（保留兼容）
    if event_instance.event_type == "tool-invocation":
        tool_name = event_instance.event_data.get("tool_name", "")
        if tool_name == "Write":
            return "review-requirement"

    return None


def _evaluate_condition(
    condition: str,
    event_instance: EventInstance,
) -> bool:
    """解析条件表达式。

    最小解析器（支持 == 和 !=）：
    - "tool_name == 'Write'" → event_data["tool_name"] == "Write"
    - "tool_name != 'Read'" → event_data["tool_name"] != "Read"

    Args:
        condition: 条件表达式字符串
        event_instance: 事件实例

    Returns:
        True/False
    """
    # 解析 "=="
    if "==" in condition:
        parts = condition.split("==")
        if len(parts) == 2:
            field_name = parts[0].strip()
            expected_value = parts[1].strip().strip("'\"")

            actual_value = event_instance.event_data.get(field_name)
            if actual_value is not None:
                return str(actual_value) == expected_value

    # 解析 "!="
    if "!=" in condition:
        parts = condition.split("!=")
        if len(parts) == 2:
            field_name = parts[0].strip()
            expected_value = parts[1].strip().strip("'\"")

            actual_value = event_instance.event_data.get(field_name)
            if actual_value is not None:
                return str(actual_value) != expected_value

    return False


def _schema_driven_build_fact_data(
    event_instance: EventInstance,
    fact_type: FactType,
) -> dict[str, Any]:
    """Schema-driven 构建事实数据。

    从 fact_type 的定义推导事实数据：
    - 如果 establishment_condition 包含 tool_name
    - 推导相关字段

    Args:
        event_instance: 事件实例
        fact_type: 事实类型定义

    Returns:
        fact_data dict
    """
    fact_data: dict[str, Any] = {}

    # 从 event_data 复制相关字段
    if fact_type.establishment_condition:
        # 解析条件中提到的字段
        condition = fact_type.establishment_condition
        if "tool_name" in condition:
            fact_data["tool_name"] = event_instance.event_data.get("tool_name")
            # 推导 required
            if event_instance.event_data.get("tool_name") == "Write":
                fact_data["required"] = True

    # 补充 subject/object 信息
    if fact_type.subject_type:
        fact_data["subject_type"] = fact_type.subject_type
    if fact_type.object_type:
        fact_data["object_type"] = fact_type.object_type

    return fact_data
