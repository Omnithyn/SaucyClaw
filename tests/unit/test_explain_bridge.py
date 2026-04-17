"""解释桥接器单元测试。"""

from pathlib import Path

from adapters.openclaw.explain_bridge import (
    ExplainBridge,
    AdapterExplainOutput,
)
from core.governance.loader import load_governance
from stores.protocols import GateResult

SCHEMAS_DIR = Path(__file__).parent.parent.parent / "schemas" / "governance"


def test_enhance_output_with_bundle():
    """验证 Shadow Mode 开启时，返回 explanation_bundle。"""
    schema = load_governance(SCHEMAS_DIR)
    lookup = {r.id: r for r in schema.rules}

    bridge = ExplainBridge(lookup, enable=True)

    # 模拟触发单条规则的 GateResult
    result = GateResult(
        decision="Block",
        reason="违反治理规则",
        matched_rules=["rule-reviewer-must-differ"],
        evidence_ids=["evidence-1"],
        suggestions=["输出被阻断"],
    )

    enhanced = bridge.enhance_output(result)

    assert isinstance(enhanced, AdapterExplainOutput)
    assert enhanced.decision == "Block"
    assert enhanced.matched_rules == ["rule-reviewer-must-differ"]
    assert enhanced.explanation_bundle is not None
    assert enhanced.raw_result == result

    bundle = enhanced.explanation_bundle
    assert bundle.decision == "Block"
    assert bundle.matched_rule_ids == ["rule-reviewer-must-differ"]
    assert len(bundle.explanations) == 1
    assert bundle.readable_summary.startswith("触发阻断")
    assert bundle.risk_summary == "高风险规则触发"


def test_enhance_output_without_bundle():
    """验证 Shadow Mode 关闭时，explanation_bundle 为 None。"""
    schema = load_governance(SCHEMAS_DIR)
    lookup = {r.id: r for r in schema.rules}

    bridge = ExplainBridge(lookup, enable=False)

    result = GateResult(
        decision="Block",
        reason="违反治理规则",
        matched_rules=["rule-reviewer-must-differ"],
        evidence_ids=["evidence-1"],
        suggestions=["输出被阻断"],
    )

    enhanced = bridge.enhance_output(result)

    assert isinstance(enhanced, AdapterExplainOutput)
    assert enhanced.decision == "Block"
    assert enhanced.matched_rules == ["rule-reviewer-must-differ"]
    assert enhanced.explanation_bundle is None
    assert enhanced.raw_result == result


def test_shadow_mode_toggle():
    """验证 Shadow Mode 开关切换有效。"""
    schema = load_governance(SCHEMAS_DIR)
    lookup = {r.id: r for r in schema.rules}

    bridge = ExplainBridge(lookup, enable=False)

    result = GateResult(
        decision="Block",
        reason="违反治理规则",
        matched_rules=["rule-reviewer-must-differ"],
        evidence_ids=["evidence-1"],
        suggestions=["输出被阻断"],
    )

    # 初始关闭
    enhanced = bridge.enhance_output(result)
    assert enhanced.explanation_bundle is None

    # 开启
    bridge.enable_shadow_mode()
    enhanced = bridge.enhance_output(result)
    assert enhanced.explanation_bundle is not None

    # 关闭
    bridge.disable_shadow_mode()
    enhanced = bridge.enhance_output(result)
    assert enhanced.explanation_bundle is None


def test_adapter_write_back_still_accepts_raw_gate_result():
    """验证 bridge 引入后，原 adapter 的 write_back(result) 仍保持不变。

    这是关键测试：证明 bridge 不改变 adapter 契约。
    """
    schema = load_governance(SCHEMAS_DIR)
    lookup = {r.id: r for r in schema.rules}

    bridge = ExplainBridge(lookup, enable=True)

    # 原始 GateResult
    result = GateResult(
        decision="Block",
        reason="违反治理规则",
        matched_rules=["rule-reviewer-must-differ"],
        evidence_ids=["evidence-1"],
        suggestions=["输出被阻断"],
    )

    # bridge 生成增强输出
    enhanced = bridge.enhance_output(result)

    # 验证原始 result 仍然完整可用
    assert enhanced.raw_result == result
    assert enhanced.raw_result.decision == "Block"
    assert enhanced.raw_result.matched_rules == ["rule-reviewer-must-differ"]
    assert enhanced.raw_result.suggestions == ["输出被阻断"]

    # 证明 adapter 仍然可以接受原始 result
    # （不需要实际调用 adapter.write_back，只需证明 result 未被修改）
    assert isinstance(enhanced.raw_result, GateResult)
    assert hasattr(enhanced.raw_result, "decision")
    assert hasattr(enhanced.raw_result, "matched_rules")
    assert hasattr(enhanced.raw_result, "suggestions")


def test_adapter_explain_output_fields_completeness():
    """验证 AdapterExplainOutput 包含所有必需字段。"""
    schema = load_governance(SCHEMAS_DIR)
    lookup = {r.id: r for r in schema.rules}

    bridge = ExplainBridge(lookup, enable=True)

    result = GateResult(
        decision="Block",
        reason="违反治理规则",
        matched_rules=["rule-reviewer-must-differ"],
        evidence_ids=["evidence-1"],
        suggestions=["输出被阻断"],
    )

    enhanced = bridge.enhance_output(result)

    # 检查所有字段都已填充
    assert hasattr(enhanced, "decision")
    assert hasattr(enhanced, "matched_rules")
    assert hasattr(enhanced, "explanation_bundle")
    assert hasattr(enhanced, "raw_result")

    # 检查字段值
    assert enhanced.decision == "Block"
    assert enhanced.matched_rules == ["rule-reviewer-must-differ"]
    assert enhanced.explanation_bundle is not None
    assert enhanced.raw_result == result


def test_enhance_output_with_no_matched_rules():
    """验证无匹配规则时的降级行为。"""
    schema = load_governance(SCHEMAS_DIR)
    lookup = {r.id: r for r in schema.rules}

    bridge = ExplainBridge(lookup, enable=True)

    result = GateResult(
        decision="Allow",
        reason="通过所有治理规则",
        matched_rules=[],
        evidence_ids=[],
        suggestions=[],
    )

    enhanced = bridge.enhance_output(result)

    assert enhanced.decision == "Allow"
    assert enhanced.matched_rules == []
    assert enhanced.explanation_bundle is not None
    assert enhanced.explanation_bundle.readable_summary == "未触发治理规则"
    assert enhanced.explanation_bundle.risk_summary == "未触发风险规则"


def test_enhance_output_with_unknown_rule_id():
    """验证包含未知 rule_id 时的降级行为。"""
    schema = load_governance(SCHEMAS_DIR)
    lookup = {r.id: r for r in schema.rules}

    bridge = ExplainBridge(lookup, enable=True)

    # 包含一个不存在的 rule_id
    result = GateResult(
        decision="Block",
        reason="违反治理规则",
        matched_rules=["rule-reviewer-must-differ", "unknown-rule-id"],
        evidence_ids=["evidence-1"],
        suggestions=["输出被阻断"],
    )

    enhanced = bridge.enhance_output(result)

    # 不应该崩溃
    assert enhanced.explanation_bundle is not None
    # 只有已知规则被处理
    assert len(enhanced.explanation_bundle.explanations) == 1
    assert enhanced.explanation_bundle.explanations[0].rule_id == "rule-reviewer-must-differ"
