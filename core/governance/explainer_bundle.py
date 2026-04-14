"""规则解释输出打包器。

Phase 1.9: 将解释信息真正组织成运行时可用的输出包，
而不修改核心决策链（GateResult / matcher / engine）。
"""

from dataclasses import dataclass
from typing import List

from core.governance.explainer import RuleExplanation, explain_matched_rules
from core.governance.models import GovernanceRule


@dataclass(frozen=True)
class ExplanationBundle:
    """完整的规则解释输出包。

    外围 helper，不修改任何核心结构。
    使用场景：
    - 调试输出
    - 日志记录
    - 外部工具展示
    - 未来扩展到 Memory/管理台
    """
    decision: str
    matched_rule_ids: List[str]
    explanations: List[RuleExplanation]
    readable_summary: str
    suggestions: List[str]
    risk_summary: str


def bundle_explanations(
    decision: str,
    matched_rule_ids: List[str],
    schema_rules_lookup: dict[str, GovernanceRule],
    suggestions: List[str] | None = None,
) -> ExplanationBundle:
    """打包完整的解释输出。

    Args:
        decision: 决策结果（来自 GateResult.decision）
        matched_rule_ids: 匹配的规则 ID 列表（来自 GateResult.matched_rules）
        schema_rules_lookup: 完整的规则查找表
        suggestions: 建议列表（来自 GateResult.suggestions），可选

    Returns:
        完整的解释输出包
    """
    suggestions = suggestions or []

    # 1. 从 lookup 表中获取完整的 GovernanceRule 列表
    matched_rules = []
    for rule_id in matched_rule_ids:
        rule = schema_rules_lookup.get(rule_id)
        if rule:
            matched_rules.append(rule)
        # 如果 rule_id 不存在，直接忽略（降级处理）

    # 2. 生成结构化解释
    explanations = explain_matched_rules(matched_rules, schema_rules_lookup)

    # 3. 生成可读摘要
    readable_summary = _build_readable_summary(decision, explanations)

    # 4. 生成风险摘要
    risk_summary = _build_risk_summary(explanations)

    return ExplanationBundle(
        decision=decision,
        matched_rule_ids=matched_rule_ids,
        explanations=explanations,
        readable_summary=readable_summary,
        suggestions=suggestions,
        risk_summary=risk_summary,
    )


def _build_readable_summary(
    decision: str,
    explanations: List[RuleExplanation],
) -> str:
    """构建可读摘要。

    规则：
    - 无匹配：未触发治理规则
    - 单规则：触发{decision}（{risk_level}/{category}）：{rationale}
    - 多规则：触发{decision}（{最高风险}，{数量}条规则）：{categories}
    """
    if not explanations:
        return "未触发治理规则"

    if len(explanations) == 1:
        exp = explanations[0]
        decision_text = _decision_to_text(decision)
        return f"触发{decision_text}（{exp.risk_level}/{exp.category}）：{exp.rationale}"

    # 多规则：合并分类，取最高风险
    categories = " / ".join(sorted(set(exp.category for exp in explanations)))
    highest_risk = _get_highest_risk([exp.risk_level for exp in explanations])
    decision_text = _decision_to_text(decision)
    return f"触发{decision_text}（{highest_risk}，{len(explanations)}条规则）：{categories}"


def _build_risk_summary(explanations: List[RuleExplanation]) -> str:
    """构建风险摘要。

    规则：
    - 有 high → 高风险规则触发
    - 否则有 medium → 中风险规则触发
    - 否则有 low → 低风险规则触发
    - 无匹配 → 未触发风险规则
    """
    if not explanations:
        return "未触发风险规则"

    risks = [exp.risk_level for exp in explanations]
    highest = _get_highest_risk(risks)

    risk_map = {
        "high": "高风险规则触发",
        "medium": "中风险规则触发",
        "low": "低风险规则触发",
    }
    return risk_map.get(highest, "未知风险规则触发")


def _get_highest_risk(risks: List[str]) -> str:
    """获取最高风险等级。

    优先级：high > medium > low
    """
    if "high" in risks:
        return "high"
    if "medium" in risks:
        return "medium"
    if "low" in risks:
        return "low"
    return "unknown"


def _decision_to_text(decision: str) -> str:
    """将决策类型转换为可读文本。"""
    decision_map = {
        "Block": "阻断",
        "Escalate": "升级",
        "Review Required": "审查",
        "Allow": "放行",
    }
    return decision_map.get(decision, decision)
