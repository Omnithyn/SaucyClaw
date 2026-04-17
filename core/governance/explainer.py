"""规则解释器：将匹配的规则转换为结构化解释。

Phase 1.8: 让规则元数据真正浮出到运行时解释面，
而不只是静态存于 YAML 和 dataclass。
"""

from dataclasses import dataclass
from typing import List

from core.governance.models import GovernanceRule


@dataclass(frozen=True)
class RuleExplanation:
    """单条规则的结构化解释。"""
    rule_id: str
    category: str
    risk_level: str
    source: str
    rationale: str


def explain_matched_rules(
    matched_rules: List[GovernanceRule],
    all_rules_lookup: dict[str, GovernanceRule] | None = None,
) -> List[RuleExplanation]:
    """将匹配的规则列表转换为结构化解释。

    Args:
        matched_rules: match_rules() 返回的违规触发规则列表
        all_rules_lookup: （可选）完整的规则查找表，用于补充额外信息。
                          如果提供，会从这里取元数据；否则直接用 matched_rules 自带的元数据。

    Returns:
        按匹配顺序排列的解释项列表
    """
    explanations = []
    for rule in matched_rules:
        # 优先从 lookup 表取（如需补充信息），否则直接用 rule 自带的
        rule_to_use = all_rules_lookup.get(rule.id, rule) if all_rules_lookup else rule

        explanation = RuleExplanation(
            rule_id=rule_to_use.id,
            category=rule_to_use.category,
            risk_level=rule_to_use.risk_level,
            source=rule_to_use.source,
            rationale=rule_to_use.rationale,
        )
        explanations.append(explanation)

    return explanations
