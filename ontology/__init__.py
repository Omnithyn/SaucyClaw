"""本体核心模块。

N1 — Ontology Core Foundation
N2 — Ontology Governance Loop
N1.5 — Ontology Platform Architecture & Visual Authoring Foundation

提供 SaucyClaw 的最小本体核心，让对象、关系、事件、上下文、事实、证据和规则
有统一的语义挂点，为后续本体驱动治理做准备。

模块结构：
- schema.py：本体类型定义（EventType、ContextType、FactType、EvidenceRef、PolicyBinding）
- instances.py：本体实例模型（EntityInstance、RelationInstance、
  EventInstance、ContextSnapshot、FactRecord）
- facts.py：事实与证据绑定结构（FactEvidenceBinding、EvidenceChain、
  FactEstablishment）
- policy_binding.py：规则绑定点（OntologyPolicyBinding、PolicyCondition、PolicyJudgment）
- loader.py：本体 YAML 加载器（load_ontology_schema、validate_ontology_schema）
- mapping.py：事件映射器（map_raw_event_to_ontology、EventMappingResult）
- establishment.py：事实建立器（establish_fact_from_event、FactEstablishmentResult）
- governance_loop.py：本体治理循环
  （run_ontology_governance_loop、OntologyGovernanceResult）
- visual_model.py：可视化构建规范模型（N1.5）
- catalog.py：类型注册与索引（N1.5）
- validation.py：一致性校验（N1.5）
- roundtrip.py：三向等价转换（N1.5）

三层架构：
- Schema Layer：类型定义（静态）
- Instance Layer：实例模型（动态）
- Binding Layer：绑定关系（证据链、策略绑定）
- Loop Layer：治理循环（映射 → 建立 → 评估）
- Platform Layer：可视化构建、Catalog、校验、Round-Trip（N1.5）
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

from ontology.loader import (
    OntologyLoadError,
    load_ontology_schema,
    validate_ontology_schema,
    load_default_ontology_schema,
)

from ontology.mapping import (
    EventMappingError,
    EventMappingResult,
    map_raw_event_to_ontology,
)

from ontology.establishment import (
    FactEstablishmentError,
    FactEstablishmentResult,
    establish_fact_from_event,
)

from ontology.governance_loop import (
    OntologyGovernanceError,
    OntologyGovernanceResult,
    run_ontology_governance_loop,
    run_minimal_ontology_governance,
)

# N1.5 — Platform Layer
from ontology.visual_model import (
    VisualNodeType,
    VisualEdgeType,
    VisualNode,
    VisualEdge,
    VisualGraph,
    PropertySchema,
    FormSchema,
    Category,
    Palette,
    build_visual_node_type,
    build_visual_edge_type,
    build_property_schema,
    build_form_schema,
    build_visual_node,
    build_visual_edge,
    build_visual_graph,
    build_palette,
)

from ontology.catalog import (
    OntologyCatalog,
    CatalogIndex,
)

from ontology.validation import (
    ValidationResult,
    validate_schema_references,
    validate_visual_graph,
    validate_catalog_completeness,
    validate_full_ontology,
)

from ontology.roundtrip import (
    RoundTripReport,
    visual_graph_to_schema,
    schema_to_visual_graph,
    yaml_config_to_visual_graph,
    verify_schema_roundtrip,
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
    # Loader
    "OntologyLoadError",
    "load_ontology_schema",
    "validate_ontology_schema",
    "load_default_ontology_schema",
    # Mapping
    "EventMappingError",
    "EventMappingResult",
    "map_raw_event_to_ontology",
    # Establishment
    "FactEstablishmentError",
    "FactEstablishmentResult",
    "establish_fact_from_event",
    # Governance Loop
    "OntologyGovernanceError",
    "OntologyGovernanceResult",
    "run_ontology_governance_loop",
    "run_minimal_ontology_governance",
    # N1.5 — Visual Model
    "VisualNodeType",
    "VisualEdgeType",
    "VisualNode",
    "VisualEdge",
    "VisualGraph",
    "PropertySchema",
    "FormSchema",
    "Category",
    "Palette",
    "build_visual_node_type",
    "build_visual_edge_type",
    "build_property_schema",
    "build_form_schema",
    "build_visual_node",
    "build_visual_edge",
    "build_visual_graph",
    "build_palette",
    # N1.5 — Catalog
    "OntologyCatalog",
    "CatalogIndex",
    # N1.5 — Validation
    "ValidationResult",
    "validate_schema_references",
    "validate_visual_graph",
    "validate_catalog_completeness",
    "validate_full_ontology",
    # N1.5 — Round-Trip
    "RoundTripReport",
    "visual_graph_to_schema",
    "schema_to_visual_graph",
    "yaml_config_to_visual_graph",
    "verify_schema_roundtrip",
]
