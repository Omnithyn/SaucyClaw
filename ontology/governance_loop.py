"""本体治理循环。

N2 — Ontology Governance Loop

输入：raw event + loaded ontology schema + policy binding
流程：映射实例 → 建立事实 → 评估 policy binding → 输出 judgment
输出：OntologyGovernanceResult

不要求直接改写现有 core governance engine，
但要能给出一个清晰的 ontology-driven judgment。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ontology.schema import OntologySchema, PolicyBinding
from ontology.loader import load_ontology_schema  # noqa: E402
from ontology.mapping import map_raw_event_to_ontology, EventMappingResult, EventMappingError  # noqa: E402
from ontology.establishment import establish_fact_from_event, FactEstablishmentResult  # noqa: E402
from ontology.policy_binding import (
    PolicyJudgment,
    evaluate_policy_on_ontology,
)


class OntologyGovernanceError(Exception):
    """本体治理失败。"""


@dataclass(frozen=True)
class OntologyGovernanceResult:
    """本体治理结果。

    包含：
    - mapping_result：事件映射结果
    - establishment_result：事实建立结果（可选）
    - judgment：策略判断结果（可选）
    - governance_status：治理状态（mapped | established | judged | skipped）
    """

    mapping_result: EventMappingResult
    establishment_result: FactEstablishmentResult | None = None
    judgment: PolicyJudgment | None = None
    governance_status: str = "mapped"  # mapped | established | judged | skipped

    # 治理摘要
    summary: str = ""


# ─── 治理循环 ───


def run_ontology_governance_loop(
    raw_event: dict[str, Any],
    ontology_schema: OntologySchema,
    policy_bindings: list[PolicyBinding],
) -> OntologyGovernanceResult:
    """运行本体治理循环。

    流程：
    1. map_raw_event_to_ontology → EventMappingResult
    2. establish_fact_from_event → FactEstablishmentResult（可选）
    3. evaluate_policy_on_ontology → PolicyJudgment（可选）
    4. 返回 OntologyGovernanceResult
    """
    # Step 1: 映射事件
    try:
        mapping_result = map_raw_event_to_ontology(raw_event, ontology_schema)
    except EventMappingError as exc:
        raise OntologyGovernanceError(f"事件映射失败: {exc}")

    governance_status = "mapped"
    summary = f"事件已映射: {mapping_result.event_instance.event_type}"

    # Step 2: 建立事实（可选）
    establishment_result = None
    try:
        establishment_result = establish_fact_from_event(
            mapping_result.event_instance,
            mapping_result.entity_instances,
            ontology_schema,
        )
        if establishment_result:
            governance_status = "established"
            summary += f" → 事实已建立: {establishment_result.fact_record.fact_type}"
    except Exception:  # noqa: E722
        # 事实建立失败不阻断循环
        pass

    # Step 3: 评估策略（可选）
    judgment = None
    if policy_bindings and establishment_result:
        # 构建 ontology_instances
        ontology_instances = {
            "entities": mapping_result.entity_instances,
            "events": [mapping_result.event_instance],
            "contexts": [mapping_result.context_snapshot] if mapping_result.context_snapshot else [],
            "facts": [establishment_result.fact_record],
        }

        # 评估所有 policy bindings
        for policy_binding in policy_bindings:
            judgment = evaluate_policy_on_ontology(policy_binding, ontology_instances)
            if judgment.judgment_result != "pass":
                # 非 pass 结果，记录并停止
                governance_status = "judged"
                summary += f" → 策略判断: {judgment.judgment_result}"
                break

        if judgment and judgment.judgment_result == "pass":
            governance_status = "judged"
            summary += " → 策略判断: pass"

    return OntologyGovernanceResult(
        mapping_result=mapping_result,
        establishment_result=establishment_result,
        judgment=judgment,
        governance_status=governance_status,
        summary=summary,
    )


# ─── Convenience Runner ───


def run_minimal_ontology_governance(
    raw_event: dict[str, Any],
    policy_bindings: list[PolicyBinding] | None = None,
    schema_dir: str | None = None,
) -> OntologyGovernanceResult:
    """运行最小本体治理（使用默认 Schema）。

    便捷函数：
    - 加载默认 ontology_schema
    - 运行 governance loop
    """
    if schema_dir is None:
        from ontology.loader import SCHEMA_DIR
        schema_dir = SCHEMA_DIR

    ontology_schema = load_ontology_schema(schema_dir)

    if policy_bindings is None:
        policy_bindings = []

    return run_ontology_governance_loop(raw_event, ontology_schema, policy_bindings)
