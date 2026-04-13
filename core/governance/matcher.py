"""治理规则条件匹配引擎。"""

from __future__ import annotations

from core.governance.models import Condition, GovernanceRule


class ConditionError(ValueError):
    """条件无法评估。"""


def _resolve_value(field_name: str, condition: Condition, input_data: dict):
    """获取条件比较时使用的值。

    如果条件有 value_from，则从 input_data 中取对应字段的值；
    否则使用 condition.value 的静态值。
    """
    if condition.value_from is not None:
        if condition.value_from not in input_data:
            raise ConditionError(
                f"条件引用字段 {condition.value_from!r} 在输入中不存在"
            )
        return input_data[condition.value_from]
    return condition.value


def _evaluate_field(field_name: str, condition: Condition, input_data: dict) -> bool:
    """评估单个条件。"""
    if field_name not in input_data:
        # 字段不存在：exists 操作符需要特殊处理，其他操作符返回 False
        return condition.op == "exists"

    actual = input_data[field_name]
    expected = _resolve_value(field_name, condition, input_data)

    op = condition.op

    if op == "exists":
        return actual is not None

    if op == "==":
        return actual == expected

    if op == "!=":
        return actual != expected

    if op == "in":
        if not isinstance(expected, list):
            raise ConditionError(
                f"'in' 操作符要求值为列表，实际为 {type(expected).__name__}"
            )
        return actual in expected

    if op == "not_in":
        if not isinstance(expected, list):
            raise ConditionError(
                f"'not_in' 操作符要求值为列表，实际为 {type(expected).__name__}"
            )
        return actual not in expected

    raise ConditionError(f"未知操作符: {op!r}")


def evaluate_rule(rule: GovernanceRule, input_data: dict) -> bool:
    """评估规则的所有条件是否命中。

    Phase 0-1: 单层条件，所有条件为 AND 关系（全部命中 = 规则命中）。
    """
    if not rule.conditions:
        return True

    return all(
        _evaluate_field(cond.field, cond, input_data)
        for cond in rule.conditions
    )


def match_rules(
    rules: list[GovernanceRule], input_data: dict
) -> list[GovernanceRule]:
    """返回所有**违规触发**的规则（条件不满足 = 违规）。

    注意：evaluate_rule 返回 True 表示条件通过（无违规），
    此函数返回的是 evaluate_rule 为 False 的规则（有违规）。
    即：返回需要执行 on_hit 动作的规则列表。

    如需"条件通过的规则"，应直接调用 evaluate_rule。
    """
    return [rule for rule in rules if not evaluate_rule(rule, input_data)]
