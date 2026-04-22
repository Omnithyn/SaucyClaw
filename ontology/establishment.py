"""事实建立器。

N2 — Ontology Governance Loop

从 EventInstance 推导 FactRecord + FactEstablishment + EvidenceChain。

最小建立逻辑：
- tool-invocation → review-requirement（当 tool_name == "Write"）
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

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
