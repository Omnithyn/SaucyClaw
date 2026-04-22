"""事实与证据绑定结构。

N1 — Ontology Core Foundation

让 evidence 不再只是治理附属信息，
而是能明确挂到某个本体事实上。

核心结构：
- FactEvidenceBinding：事实与证据的绑定关系
- EvidenceChain：证据链（多个 EvidenceRef 的聚合）
- FactEstablishment：事实的建立过程
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from ontology.schema import EvidenceRef  # noqa: E402
from ontology.instances import FactRecord


@dataclass(frozen=True)
class FactEvidenceBinding:
    """事实与证据的绑定关系。

    将治理证据绑定到本体事实：
    - fact_id：本体事实实例 ID
    - evidence_ref：证据引用（指向 stores/evidence）
    - binding_type：绑定方式
    - semantic_role：证据在本体中的语义角色
    """

    binding_id: str
    fact_id: str  # FactRecord.fact_id
    evidence_ref: EvidenceRef

    # 绑定时间
    bound_at: datetime = field(default_factory=datetime.utcnow)

    # 绑定的置信度
    confidence: float = 1.0  # 0.0 ~ 1.0

    # 绑定的元数据
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EvidenceChain:
    """证据链。

    多个 EvidenceRef 的聚合，形成完整的证据链：
    - chain_id：证据链唯一标识
    - evidence_refs：证据引用列表
    - chain_type：证据链类型（linear | branching | aggregated）
    """

    chain_id: str
    evidence_refs: list[EvidenceRef]

    # 证据链类型
    chain_type: str = "linear"  # linear | branching | aggregated

    # 证据链的起点事实
    root_fact_id: str | None = None

    # 证据链的终点结论
    conclusion_fact_id: str | None = None

    # 证据链的置信度（综合）
    chain_confidence: float = 1.0


@dataclass(frozen=True)
class FactEstablishment:
    """事实的建立过程。

    记录一个本体事实如何被建立：
    - fact_record：被建立的事实记录
    - establishing_event：建立该事实的事件实例 ID
    - evidence_chain：支持该事实的证据链
    - establishment_type：建立方式（asserted | inferred | observed）
    """

    establishment_id: str
    fact_record: FactRecord

    # 建立该事实的事件
    establishing_event_id: str | None = None

    # 支持该事实的证据链
    evidence_chain: EvidenceChain | None = None

    # 建立方式
    establishment_type: str = "asserted"  # asserted | inferred | observed

    # 建立时间
    established_at: datetime = field(default_factory=datetime.utcnow)

    # 建立的置信度
    confidence: float = 1.0


# ─── Helper Functions ───


def build_fact_evidence_binding(
    fact_id: str,
    evidence_ref: EvidenceRef,
    confidence: float = 1.0,
    metadata: dict[str, Any] | None = None,
) -> FactEvidenceBinding:
    """构建事实与证据绑定。"""
    from ontology.instances import generate_instance_id

    return FactEvidenceBinding(
        binding_id=generate_instance_id("binding"),
        fact_id=fact_id,
        evidence_ref=evidence_ref,
        confidence=confidence,
        metadata=metadata or {},
    )


def build_evidence_chain(
    evidence_refs: list[EvidenceRef],
    chain_type: str = "linear",
    root_fact_id: str | None = None,
    conclusion_fact_id: str | None = None,
) -> EvidenceChain:
    """构建证据链。"""
    from ontology.instances import generate_instance_id

    # 综合置信度（取平均值）
    support_count = sum(er.semantic_role == "supports" for er in evidence_refs)
    chain_confidence = support_count / len(evidence_refs) if evidence_refs else 1.0

    return EvidenceChain(
        chain_id=generate_instance_id("chain"),
        evidence_refs=evidence_refs,
        chain_type=chain_type,
        root_fact_id=root_fact_id,
        conclusion_fact_id=conclusion_fact_id,
        chain_confidence=chain_confidence,
    )


def build_fact_establishment(
    fact_record: FactRecord,
    establishing_event_id: str | None = None,
    evidence_chain: EvidenceChain | None = None,
    establishment_type: str = "asserted",
) -> FactEstablishment:
    """构建事实建立过程。"""
    from ontology.instances import generate_instance_id

    confidence = evidence_chain.chain_confidence if evidence_chain else 1.0

    return FactEstablishment(
        establishment_id=generate_instance_id("est"),
        fact_record=fact_record,
        establishing_event_id=establishing_event_id,
        evidence_chain=evidence_chain,
        establishment_type=establishment_type,
        confidence=confidence,
    )
