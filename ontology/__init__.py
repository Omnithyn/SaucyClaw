"""本体核心模块。

N1 — Ontology Core Foundation

提供 SaucyClaw 的最小本体核心，让对象、关系、事件、上下文、事实、证据和规则
有统一的语义挂点，为后续本体驱动治理做准备。

模块结构：
- schema.py：本体类型定义（EventType、ContextType、FactType、EvidenceRef、PolicyBinding）
- instances.py：本体实例模型（EntityInstance、RelationInstance、EventInstance、ContextSnapshot、FactRecord）
- facts.py：事实与证据绑定结构（FactEvidenceBinding、EvidenceChain、FactEstablishment）
- policy_binding.py：规则绑定点（OntologyPolicyBinding、PolicyCondition、PolicyJudgment）

三层架构：
- Schema Layer：类型定义（静态）
- Instance Layer：实例模型（动态）
- Binding Layer：绑定关系（证据链、策略绑定）
"""

from __future__ import annotations

from ontology.schema import (
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

from ontology.instances import (
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

from ontology.facts import (
    FactEvidenceBinding,
    EvidenceChain,
    FactEstablishment,
    build_fact_evidence_binding,
    build_evidence_chain,
    build_fact_establishment,
)

from ontology.policy_binding import (
    OntologyPolicyBinding,
    PolicyCondition,
    PolicyJudgment,
    build_ontology_policy_binding,
    build_policy_condition,
    build_policy_judgment,
    evaluate_entity_condition,
    evaluate_fact_condition,
    evaluate_policy_on_ontology,
)


__all__ = [
    # Schema
    "EventType",
    "ContextType",
    "FactType",
    "EvidenceRef",
    "PolicyBinding",
    "OntologySchema",
    "build_event_type_from_dict",
    "build_context_type_from_dict",
    "build_fact_type_from_dict",
    "build_policy_binding_from_dict",
    # Instances
    "EntityInstance",
    "RelationInstance",
    "EventInstance",
    "ContextSnapshot",
    "FactRecord",
    "generate_instance_id",
    "build_entity_instance",
    "build_relation_instance",
    "build_event_instance",
    "build_context_snapshot",
    "build_fact_record",
    # Facts
    "FactEvidenceBinding",
    "EvidenceChain",
    "FactEstablishment",
    "build_fact_evidence_binding",
    "build_evidence_chain",
    "build_fact_establishment",
    # Policy Binding
    "OntologyPolicyBinding",
    "PolicyCondition",
    "PolicyJudgment",
    "build_ontology_policy_binding",
    "build_policy_condition",
    "build_policy_judgment",
    "evaluate_entity_condition",
    "evaluate_fact_condition",
    "evaluate_policy_on_ontology",
]
