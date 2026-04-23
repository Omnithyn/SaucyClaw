"""本体治理循环。

N2 — Ontology Governance Loop
N2.1 — RuntimePackage-Driven Governance Realignment

输入：
- Package-driven: raw_event + RuntimePackage（正式入口）
- Legacy: raw_event + ontology_schema + policy_bindings（兼容入口）

流程：映射实例 → 建立事实 → 评估 policy binding → 输出 judgment
输出：OntologyGovernanceResult

N2.1 新增：
- run_package_driven_governance() 正式入口
- CompilationReport 影响 execute readiness
- ExecuteReadiness 三种模式：full / warning / review
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ontology.authoring_package import RuntimePackage
from ontology.schema import OntologySchema, PolicyBinding
from ontology.loader import load_ontology_schema  # noqa: E402
from ontology.mapping import (
    map_raw_event_to_ontology,
    map_raw_event_with_package,
    EventMappingResult,
    EventMappingError,
)
from ontology.establishment import (
    establish_fact_from_event,
    establish_fact_with_package,
    FactEstablishmentResult,
)
from ontology.policy_binding import (
    PolicyJudgment,
    evaluate_policy_on_ontology,
)
from ontology.runtime_readiness import (
    ExecuteReadiness,
    check_runtime_readiness,
    adapt_readiness_to_judgment_mode,
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
    - execute_readiness：执行就绪状态（N2.1 新增）
    """

    mapping_result: EventMappingResult
    establishment_result: FactEstablishmentResult | None = None
    judgment: PolicyJudgment | None = None
    governance_status: str = "mapped"  # mapped | established | judged | skipped
    execute_readiness: ExecuteReadiness | None = None  # N2.1 新增

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
            "contexts": (
                [mapping_result.context_snapshot]
                if mapping_result.context_snapshot else []
            ),
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


# ─── N2.1 Package-Driven Governance ───


def run_package_driven_governance(
    raw_event: dict[str, Any],
    runtime_package: RuntimePackage,
) -> OntologyGovernanceResult:
    """运行 Package-driven 治理循环（N2.1 正式入口）。

    RuntimePackage 是治理闭环的正式运行时输入。

    流程：
    0. check_runtime_readiness → ExecuteReadiness
    1. map_raw_event_with_package → EventMappingResult
    2. establish_fact_with_package → FactEstablishmentResult（可选）
    3. evaluate_policy_on_ontology → PolicyJudgment（可选）
    4. 返回 OntologyGovernanceResult（包含 execute_readiness）

    Args:
        raw_event: 原始运行时事件
        runtime_package: 编译后的运行时包

    Returns:
        OntologyGovernanceResult
    """
    # Step 0: 检查执行就绪状态
    readiness = check_runtime_readiness(runtime_package)

    # 如果 blocked，直接返回
    if not readiness.can_execute:
        return OntologyGovernanceResult(
            mapping_result=EventMappingResult(
                event_instance=None,  # 需要创建空的
                entity_instances=[],
                context_snapshot=None,
            ),
            governance_status="blocked",
            execute_readiness=readiness,
            summary=f"执行被阻止: {readiness.summary}",
        )

    # Step 1: Package-driven 映射事件
    try:
        mapping_result = map_raw_event_with_package(raw_event, runtime_package)
    except EventMappingError as exc:
        raise OntologyGovernanceError(f"事件映射失败: {exc}")

    governance_status = "mapped"
    summary = f"事件已映射: {mapping_result.event_instance.event_type}"

    # 根据 readiness 添加警告信息
    if readiness.level == "warning":
        summary += f" [Warning: {readiness.summary}]"
    elif readiness.level == "review":
        summary += f" [Review: {readiness.summary}]"

    # Step 2: Package-driven 建立事实
    establishment_result = None
    try:
        establishment_result = establish_fact_with_package(
            mapping_result.event_instance,
            mapping_result.entity_instances,
            runtime_package,
        )
        if establishment_result:
            governance_status = "established"
            summary += f" → 事实已建立: {establishment_result.fact_record.fact_type}"
    except Exception:  # noqa: E722
        pass

    # Step 3: 评估策略（使用 runtime_package.policy_bindings）
    judgment = None
    if runtime_package.policy_bindings and establishment_result:
        ontology_instances = {
            "entities": mapping_result.entity_instances,
            "events": [mapping_result.event_instance],
            "contexts": (
                [mapping_result.context_snapshot]
                if mapping_result.context_snapshot else []
            ),
            "facts": [establishment_result.fact_record],
        }

        # 根据 readiness 调整 judgment mode
        judgment_mode = adapt_readiness_to_judgment_mode(readiness)

        for policy_binding in runtime_package.policy_bindings:
            judgment = evaluate_policy_on_ontology(policy_binding, ontology_instances)

            # review mode: 需人工审核
            if judgment_mode == "review":
                # 强制标记为 review
                from ontology.policy_binding import build_policy_judgment
                if judgment.judgment_result == "pass":
                    judgment = build_policy_judgment(
                        policy_binding=policy_binding,
                        judgment_result="review",
                        judgment_reason="需人工审核（关键字段丢失）",
                        matched_conditions=judgment.matched_conditions,
                    )

            if judgment.judgment_result != "pass":
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
        execute_readiness=readiness,
        summary=summary,
    )
