"""规则解释打包器单元测试。"""

from pathlib import Path

from core.governance.explainer_bundle import (
    bundle_explanations,
    ExplanationBundle,
)
from core.governance.loader import load_governance

SCHEMAS_DIR = Path(__file__).parent.parent.parent / "schemas" / "governance"


def test_bundle_single_rule():
    """验证单规则打包。"""
    schema = load_governance(SCHEMAS_DIR)
    lookup = {r.id: r for r in schema.rules}

    bundle = bundle_explanations(
        decision="Block",
        matched_rule_ids=["rule-reviewer-must-differ"],
        schema_rules_lookup=lookup,
        suggestions=["输出被阻断"],
    )

    assert isinstance(bundle, ExplanationBundle)
    assert bundle.decision == "Block"
    assert bundle.matched_rule_ids == ["rule-reviewer-must-differ"]
    assert len(bundle.explanations) == 1
    assert bundle.explanations[0].rule_id == "rule-reviewer-must-differ"
    assert bundle.explanations[0].category == "separation_of_duties"
    assert bundle.explanations[0].risk_level == "high"
    assert bundle.readable_summary == (
        "触发阻断（high/separation_of_duties）："
        "防止审查者与执行者同一人，确保独立审查"
    )
    assert bundle.suggestions == ["输出被阻断"]
    assert bundle.risk_summary == "高风险规则触发"


def test_bundle_multiple_rules():
    """验证多规则打包。"""
    schema = load_governance(SCHEMAS_DIR)
    lookup = {r.id: r for r in schema.rules}

    bundle = bundle_explanations(
        decision="Block",
        matched_rule_ids=[
            "rule-reviewer-must-differ",
            "rule-handoff-required",
        ],
        schema_rules_lookup=lookup,
        suggestions=["输出被阻断", "需要手動交接"],
    )

    assert isinstance(bundle, ExplanationBundle)
    assert len(bundle.explanations) == 2
    assert bundle.readable_summary.startswith("触发阻断（high，2条规则）：")
    assert "separation_of_duties" in bundle.readable_summary
    assert "handoff" in bundle.readable_summary
    assert bundle.risk_summary == "高风险规则触发"
    assert len(bundle.suggestions) == 2


def test_bundle_no_matched_rules():
    """验证无匹配规则时的降级。"""
    schema = load_governance(SCHEMAS_DIR)
    lookup = {r.id: r for r in schema.rules}

    bundle = bundle_explanations(
        decision="Allow",
        matched_rule_ids=[],
        schema_rules_lookup=lookup,
        suggestions=[],
    )

    assert isinstance(bundle, ExplanationBundle)
    assert bundle.decision == "Allow"
    assert bundle.matched_rule_ids == []
    assert bundle.explanations == []
    assert bundle.readable_summary == "未触发治理规则"
    assert bundle.suggestions == []
    assert bundle.risk_summary == "未触发风险规则"


def test_risk_summary_computation():
    """验证风险摘要计算（取最高风险）。"""
    schema = load_governance(SCHEMAS_DIR)
    lookup = {r.id: r for r in schema.rules}

    # 高 + 中 → 高
    bundle = bundle_explanations(
        decision="Block",
        matched_rule_ids=[
            "rule-reviewer-must-differ",  # high
            "rule-handoff-required",  # medium
        ],
        schema_rules_lookup=lookup,
    )
    assert bundle.risk_summary == "高风险规则触发"

    # 中 + 低 → 中
    bundle = bundle_explanations(
        decision="Block",
        matched_rule_ids=[
            "rule-handoff-required",  # medium
            "rule-restricted-routing",  # medium
        ],
        schema_rules_lookup=lookup,
    )
    assert bundle.risk_summary == "中风险规则触发"

    # 只有低 → 低
    # 注：当前规则集中没有 low 风险规则，此测试可选


def test_unknown_rule_id_degradation():
    """验证未知 rule_id 的降级行为。"""
    schema = load_governance(SCHEMAS_DIR)
    lookup = {r.id: r for r in schema.rules}

    # 包含一个不存在的 rule_id
    bundle = bundle_explanations(
        decision="Block",
        matched_rule_ids=[
            "rule-reviewer-must-differ",
            "unknown-rule-id",
        ],
        schema_rules_lookup=lookup,
        suggestions=["输出被阻断"],
    )

    # 不应该崩溃
    assert isinstance(bundle, ExplanationBundle)
    # 只有已知规则被处理
    assert len(bundle.explanations) == 1
    assert bundle.explanations[0].rule_id == "rule-reviewer-must-differ"
    assert bundle.readable_summary == (
        "触发阻断（high/separation_of_duties）："
        "防止审查者与执行者同一人，确保独立审查"
    )
    assert bundle.risk_summary == "高风险规则触发"


def test_explanation_bundle_fields_completeness():
    """验证 ExplanationBundle 包含所有必需字段。"""
    schema = load_governance(SCHEMAS_DIR)
    lookup = {r.id: r for r in schema.rules}

    bundle = bundle_explanations(
        decision="Block",
        matched_rule_ids=["rule-reviewer-must-differ"],
        schema_rules_lookup=lookup,
    )

    # 检查所有字段都已填充
    assert hasattr(bundle, "decision")
    assert hasattr(bundle, "matched_rule_ids")
    assert hasattr(bundle, "explanations")
    assert hasattr(bundle, "readable_summary")
    assert hasattr(bundle, "suggestions")
    assert hasattr(bundle, "risk_summary")

    # 检查字段值非空（除 suggestions 可能为空）
    assert bundle.decision
    assert isinstance(bundle.matched_rule_ids, list)
    assert isinstance(bundle.explanations, list)
    assert bundle.readable_summary
    assert isinstance(bundle.suggestions, list)
    assert bundle.risk_summary


def test_bundle_with_escalate_decision():
    """验证 Escalate 决策的打包。"""
    schema = load_governance(SCHEMAS_DIR)
    lookup = {r.id: r for r in schema.rules}

    bundle = bundle_explanations(
        decision="Escalate",
        matched_rule_ids=["rule-escalate-on-conflict"],
        schema_rules_lookup=lookup,
    )

    assert bundle.decision == "Escalate"
    assert bundle.readable_summary.startswith("触发升级（")
    assert bundle.risk_summary == "高风险规则触发"


def test_decision_text_mapping():
    """验证决策类型到可读文本的映射。"""
    schema = load_governance(SCHEMAS_DIR)
    lookup = {r.id: r for r in schema.rules}

    # Block
    bundle = bundle_explanations(
        decision="Block",
        matched_rule_ids=["rule-reviewer-must-differ"],
        schema_rules_lookup=lookup,
    )
    assert "阻断" in bundle.readable_summary

    # Review Required
    bundle = bundle_explanations(
        decision="Review Required",
        matched_rule_ids=["rule-reviewer-must-differ"],
        schema_rules_lookup=lookup,
    )
    assert "审查" in bundle.readable_summary

    # Escalate
    bundle = bundle_explanations(
        decision="Escalate",
        matched_rule_ids=["rule-escalate-on-conflict"],
        schema_rules_lookup=lookup,
    )
    assert "升级" in bundle.readable_summary
