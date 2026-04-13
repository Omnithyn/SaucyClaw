"""证据生成器。

根据治理规则评估结果生成 Evidence 记录。
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from core.governance.models import GovernanceRule
from stores.protocols import Evidence, NormalizedEvent


# 决策 → 证据类型映射
_DECISION_TYPE_MAP: dict[str, str] = {
    "Allow": "allowance",
    "Review Required": "review",
    "Block": "block",
    "Escalate": "escalation",
}

# 决策 → 置信度映射
_DECISION_CONFIDENCE_MAP: dict[str, float] = {
    "Allow": 1.0,
    "Review Required": 0.5,
    "Block": 1.0,
    "Escalate": 0.5,
}


class EvidenceGenerator:
    """从治理规则评估结果生成证据。"""

    def generate(
        self,
        rule: GovernanceRule,
        event: NormalizedEvent,
        input_data: dict,
    ) -> Evidence:
        """为单次规则评估生成证据。

        Args:
            rule: 触发（或评估过）的治理规则。
            event: 关联的标准化事件。
            input_data: 用于规则评估的输入数据。

        Returns:
            Evidence 实例。
        """
        evidence_type = _DECISION_TYPE_MAP.get(rule.on_hit, "observation")
        confidence = _DECISION_CONFIDENCE_MAP.get(rule.on_hit, 0.0)

        assertion = (
            f"规则 {rule.id} 触发: {rule.description} "
            f"(severity={rule.severity}, on_hit={rule.on_hit})"
        )

        return Evidence(
            id=str(uuid.uuid4()),
            type=evidence_type,
            assertion=assertion,
            source_ref=event.id,
            timestamp=event.timestamp,
            confidence=confidence,
            governance_version=rule.task_type,
            applicable_scope={"session_id": event.session_id},
        )

    def generate_batch(
        self,
        rules: list[GovernanceRule],
        event: NormalizedEvent,
        input_data: dict,
    ) -> list[Evidence]:
        """为多条规则批量生成证据。"""
        return [self.generate(rule, event, input_data) for rule in rules]


def summarize_governance_action(
    rules: list[GovernanceRule],
) -> tuple[str, str, list[str]]:
    """根据触发的规则列表生成治理摘要。

    Returns:
        (decision, reason, matched_rule_ids)
        decision 取最高 severity 规则对应的 on_hit 值。
    """
    if not rules:
        return ("Allow", "无规则触发", [])

    # 按 severity 排序取最高（block > review > warn > info）
    severity_order = {"block": 0, "warn": 1, "review": 2, "info": 3}
    sorted_rules = sorted(
        rules, key=lambda r: severity_order.get(r.severity, 99)
    )
    top_rule = sorted_rules[0]

    matched_ids = [r.id for r in rules]
    reason = f"触发 {len(rules)} 条规则，最高 severity: {top_rule.severity}"
    return (top_rule.on_hit, reason, matched_ids)
