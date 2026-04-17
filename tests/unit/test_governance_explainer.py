"""规则解释器单元测试。"""

from pathlib import Path

from core.governance.explainer import explain_matched_rules, RuleExplanation
from core.governance.loader import load_governance
from core.governance.matcher import match_rules

SCHEMAS_DIR = Path(__file__).parent.parent.parent / "schemas" / "governance"


def test_explain_single_matched_rule():
    """验证单条匹配规则能正确转换为解释。"""
    schema = load_governance(SCHEMAS_DIR)

    # 模拟触发 rule-reviewer-must-differ 的输入（同时避免触发其他规则）
    input_data = {
        "task_type": "C",
        "assignee": "reviewer",
        "reviewer": "reviewer",
        "conflict": "false",  # 避免触发 rule-escalate-on-conflict
    }

    matched = match_rules(schema.rules, input_data)
    assert len(matched) >= 1
    assert any(r.id == "rule-reviewer-must-differ" for r in matched)

    explanations = explain_matched_rules(matched, {r.id: r for r in schema.rules})

    assert len(explanations) == len(matched)
    exp = [e for e in explanations if e.rule_id == "rule-reviewer-must-differ"][0]
    assert exp.category == "separation_of_duties"
    assert exp.risk_level == "high"
    assert exp.source == "ORCHESTRATION.md"
    assert "审查者与执行者" in exp.rationale


def test_explain_multiple_matched_rules():
    """验证多条匹配规则能正确转换为解释列表。"""
    schema = load_governance(SCHEMAS_DIR)

    # 模拟同时触发多条规则的输入
    input_data = {
        "task_type": "D",
        "assignee": "specialist",
        "handoff": "false",
        "direct_output": "false",
        "reviewer": "reviewer",  # 避免 reviewer-must-differ 条件错误
    }

    matched = match_rules(schema.rules, input_data)
    assert len(matched) >= 1

    explanations = explain_matched_rules(matched, {r.id: r for r in schema.rules})

    assert len(explanations) == len(matched)
    for exp in explanations:
        assert isinstance(exp, RuleExplanation)
        assert exp.rule_id != ""
        assert exp.category in [
            "separation_of_duties",
            "routing",
            "handoff",
            "escalation",
        ]
        assert exp.risk_level in ["low", "medium", "high"]
        assert exp.source != ""
        assert exp.rationale != ""


def test_explain_no_matched_rules():
    """验证无匹配规则时返回空列表。"""
    schema = load_governance(SCHEMAS_DIR)

    # 合规输入，不应触发任何规则
    input_data = {
        "task_type": "C",
        "assignee": "specialist",
        "reviewer": "manager",
        "direct_output": "false",
        "conflict": "false",
    }

    matched = match_rules(schema.rules, input_data)
    assert len(matched) == 0

    explanations = explain_matched_rules(matched)

    assert explanations == []


def test_explain_without_lookup():
    """验证不提供 lookup 表时，直接使用 matched_rules 自带的元数据。"""
    schema = load_governance(SCHEMAS_DIR)

    input_data = {
        "task_type": "C",
        "assignee": "reviewer",
        "reviewer": "reviewer",
        "conflict": "false",  # 避免触发 rule-escalate-on-conflict
    }

    matched = match_rules(schema.rules, input_data)
    assert len(matched) >= 1

    # 不传 lookup，直接使用 matched_rules 自带的元数据
    explanations = explain_matched_rules(matched)

    assert len(explanations) == len(matched)
    exp = [e for e in explanations if e.rule_id == "rule-reviewer-must-differ"][0]
    assert exp.category == "separation_of_duties"
    assert exp.risk_level == "high"
    assert exp.source == "ORCHESTRATION.md"


def test_explanation_fields_completeness():
    """验证 RuleExplanation 包含所有必需字段。"""
    schema = load_governance(SCHEMAS_DIR)

    input_data = {
        "task_type": "C",
        "assignee": "reviewer",
        "reviewer": "reviewer",
        "conflict": "false",  # 避免触发 rule-escalate-on-conflict
    }

    matched = match_rules(schema.rules, input_data)
    explanations = explain_matched_rules(matched, {r.id: r for r in schema.rules})

    assert len(explanations) == len(matched)
    exp = [e for e in explanations if e.rule_id == "rule-reviewer-must-differ"][0]

    # 检查所有字段都已填充
    assert hasattr(exp, "rule_id")
    assert hasattr(exp, "category")
    assert hasattr(exp, "risk_level")
    assert hasattr(exp, "source")
    assert hasattr(exp, "rationale")

    # 检查字段值非空
    assert exp.rule_id
    assert exp.category
    assert exp.risk_level
    assert exp.source
    assert exp.rationale
