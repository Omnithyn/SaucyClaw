"""规则绑定点（本体语义层）。

N1 — Ontology Core Foundation

将规则绑定到本体语义层（对象/关系/事件/上下文/事实），
而非仅绑定到字段判断。

核心结构：
- OntologyPolicyBinding：本体层策略绑定
- PolicyCondition：本体判断条件
- PolicyJudgment：策略判断结果
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from ontology.schema import PolicyBinding  # noqa: E402
from ontology.instances import EntityInstance, FactRecord  # noqa: E402


@dataclass(frozen=True)
class OntologyPolicyBinding:
    """本体层策略绑定。

    将 GovernanceRule 绑定到本体语义层：
    - policy_binding：策略绑定定义（来自 schema）
    - bound_instances：绑定的本体实例列表
    - binding_status：绑定状态（active | inactive | expired）
    """

    binding_id: str
    policy_binding: PolicyBinding

    # 绑定的本体实例（按绑定目标类型）
    bound_entity_instances: list[str] = field(default_factory=list)  # EntityInstance.instance_id
    bound_relation_instances: list[str] = field(default_factory=list)  # RelationInstance.instance_id
    bound_event_instances: list[str] = field(default_factory=list)  # EventInstance.instance_id
    bound_context_snapshots: list[str] = field(default_factory=list)  # ContextSnapshot.snapshot_id
    bound_fact_records: list[str] = field(default_factory=list)  # FactRecord.fact_id

    # 绑定状态
    binding_status: str = "active"  # active | inactive | expired

    # 绑定时间
    bound_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class PolicyCondition:
    """本体判断条件。

    从"字段判断"走向"本体判断"：
    - condition_id：条件唯一标识
    - condition_type：条件类型（entity | relation | event | context | fact）
    - condition_expression：本体语义表达式
    """

    condition_id: str
    condition_type: str  # entity | relation | event | context | fact

    # 本体语义表达式（如 "AgentRole.name == 'CEO'"）
    condition_expression: str

    # 条件的参数（本体实例 ID）
    subject_instance_id: str
    object_instance_id: str | None = None

    # 条件的元数据
    condition_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PolicyJudgment:
    """策略判断结果。

    本体层策略判断的结果：
    - judgment_id：判断唯一标识
    - policy_binding：策略绑定
    - judgment_result：判断结果（pass | fail | review | escalate）
    - matched_conditions：匹配的条件列表
    - ontology_context：本体上下文（判断时的本体状态）
    """

    judgment_id: str
    policy_binding: PolicyBinding

    # 判断结果
    judgment_result: str  # pass | fail | review | escalate
    judgment_reason: str

    # 匹配的条件
    matched_conditions: list[PolicyCondition] = field(default_factory=list)

    # 判断时的本体上下文
    ontology_context: dict[str, Any] = field(default_factory=dict)

    # 判断时间
    judged_at: datetime = field(default_factory=datetime.utcnow)

    # 判断的证据引用
    evidence_refs: list[str] = field(default_factory=list)


# ─── Helper Functions ───


def build_ontology_policy_binding(
    policy_binding: PolicyBinding,
    bound_entity_instances: list[str] | None = None,
    bound_relation_instances: list[str] | None = None,
    bound_event_instances: list[str] | None = None,
    bound_context_snapshots: list[str] | None = None,
    bound_fact_records: list[str] | None = None,
) -> OntologyPolicyBinding:
    """构建本体层策略绑定。"""
    from ontology.instances import generate_instance_id

    return OntologyPolicyBinding(
        binding_id=generate_instance_id("policy-bind"),
        policy_binding=policy_binding,
        bound_entity_instances=bound_entity_instances or [],
        bound_relation_instances=bound_relation_instances or [],
        bound_event_instances=bound_event_instances or [],
        bound_context_snapshots=bound_context_snapshots or [],
        bound_fact_records=bound_fact_records or [],
    )


def build_policy_condition(
    condition_type: str,
    condition_expression: str,
    subject_instance_id: str,
    object_instance_id: str | None = None,
    condition_metadata: dict[str, Any] | None = None,
) -> PolicyCondition:
    """构建本体判断条件。"""
    from ontology.instances import generate_instance_id

    return PolicyCondition(
        condition_id=generate_instance_id("cond"),
        condition_type=condition_type,
        condition_expression=condition_expression,
        subject_instance_id=subject_instance_id,
        object_instance_id=object_instance_id,
        condition_metadata=condition_metadata or {},
    )


def build_policy_judgment(
    policy_binding: PolicyBinding,
    judgment_result: str,
    judgment_reason: str,
    matched_conditions: list[PolicyCondition] | None = None,
    ontology_context: dict[str, Any] | None = None,
    evidence_refs: list[str] | None = None,
) -> PolicyJudgment:
    """构建策略判断结果。"""
    from ontology.instances import generate_instance_id

    return PolicyJudgment(
        judgment_id=generate_instance_id("judg"),
        policy_binding=policy_binding,
        judgment_result=judgment_result,
        judgment_reason=judgment_reason,
        matched_conditions=matched_conditions or [],
        ontology_context=ontology_context or {},
        evidence_refs=evidence_refs or [],
    )


# ─── 本体判断器 ───


def evaluate_entity_condition(
    condition: PolicyCondition,
    entity_instance: EntityInstance,
) -> bool:
    """评估实体条件。

    从"字段判断"走向"本体判断"。
    如：AgentRole.name == 'CEO' → entity_instance.name == 'CEO'
    """
    # 简化版：直接比较属性
    # 未来可扩展为完整的本体查询语言
    expr = condition.condition_expression

    # 解析简单表达式：property == value
    if "==" in expr:
        parts = expr.split("==")
        property_name = parts[0].strip()
        expected_value = parts[1].strip().strip("'\"")

        actual_value = entity_instance.properties.get(property_name) or entity_instance.name
        return str(actual_value) == expected_value

    return False


def evaluate_fact_condition(
    condition: PolicyCondition,
    fact_record: FactRecord,
) -> bool:
    """评估事实条件。

    如：ReviewRequirement.required == true → fact_record.fact_data.get("required") == True
    """
    expr = condition.condition_expression

    if "==" in expr:
        parts = expr.split("==")
        property_name = parts[0].strip()
        expected_value = parts[1].strip().strip("'\"")

        actual_value = fact_record.fact_data.get(property_name)
        return str(actual_value) == expected_value

    return False


def evaluate_policy_on_ontology(
    policy_binding: PolicyBinding,
    ontology_instances: dict[str, Any],
) -> PolicyJudgment:
    """在 ontology 层评估策略。

    ontology_instances 包含：
    - entities: list[EntityInstance]
    - relations: list[RelationInstance]
    - events: list[EventInstance]
    - contexts: list[ContextSnapshot]
    - facts: list[FactRecord]
    """
    matched_conditions: list[PolicyCondition] = []

    # 评估实体条件
    if policy_binding.binds_to_entity_type:
        for entity in ontology_instances.get("entities", []):
            if entity.entity_type == policy_binding.binds_to_entity_type:
                cond = build_policy_condition(
                    condition_type="entity",
                    condition_expression=policy_binding.ontology_condition or "",
                    subject_instance_id=entity.instance_id,
                )
                if evaluate_entity_condition(cond, entity):
                    matched_conditions.append(cond)

    # 评估事实条件
    if policy_binding.binds_to_fact_type:
        for fact in ontology_instances.get("facts", []):
            if fact.fact_type == policy_binding.binds_to_fact_type:
                cond = build_policy_condition(
                    condition_type="fact",
                    condition_expression=policy_binding.ontology_condition or "",
                    subject_instance_id=fact.fact_id,
                )
                if evaluate_fact_condition(cond, fact):
                    matched_conditions.append(cond)

    # 判断结果
    judgment_result = "pass" if not matched_conditions else "review"
    judgment_reason = f"matched {len(matched_conditions)} ontology conditions"

    return build_policy_judgment(
        policy_binding=policy_binding,
        judgment_result=judgment_result,
        judgment_reason=judgment_reason,
        matched_conditions=matched_conditions,
        ontology_context={
            "entity_count": len(ontology_instances.get("entities", [])),
            "fact_count": len(ontology_instances.get("facts", [])),
        },
    )
