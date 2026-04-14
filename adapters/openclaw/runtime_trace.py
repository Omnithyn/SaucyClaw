"""运行链路最小摘要器。

Phase 2.5: 为当前外围接入链路提供稳定、轻量、可读的运行摘要。

不是日志系统，不是埋点框架，只是一个 frozen dataclass + 一个纯函数。
用途：debug / CLI 输出 / example 展示 / 后续真实 hook 接入前的链路观察。

保证：
- 零 core 改动
- 零 adapter 契约改动
- 不引入日志/埋点系统
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from adapters.openclaw.explain_bridge import ExplainBridge
    from adapters.openclaw.shadow_runtime import ShadowRunResult


@dataclass(frozen=True)
class RuntimeTrace:
    """运行链路最小摘要。

    Attributes:
        decision: 放行结果（Block / Allow / Escalate）
        matched_rules: 触发规则 ID 列表
        shadow_mode: Shadow Mode 是否开启（bridge 侧状态）
        has_explanation: 本次运行是否生成了真实解释（结果侧状态）
        severity: 最高风险级别（high / medium / low / None）
        summary: 一行可读摘要
    """
    decision: str
    matched_rules: list[str]
    shadow_mode: bool
    has_explanation: bool
    severity: str | None
    summary: str


def build_runtime_trace(
    run_result: ShadowRunResult,
    bridge: ExplainBridge | None = None,
) -> RuntimeTrace:
    """从运行结果构建最小摘要。

    Args:
        run_result: ShadowRuntime.process_and_write 的返回值
        bridge: 解释桥接器（用于读取 shadow_mode 状态）

    Returns:
        运行链路最小摘要
    """
    gate_result = run_result.gate_result

    # shadow_mode: bridge 侧状态
    shadow_mode = bridge.enabled if bridge is not None else False

    # has_explanation: 结果侧是否真的有 explanation
    has_explanation = (
        run_result.enhanced_output is not None
        and run_result.enhanced_output.explanation_bundle is not None
    )

    # severity: 从 explanation_bundle 的 explanations 中推导最高风险级别
    severity = _extract_severity(run_result)

    # summary: 一行可读摘要
    summary = _build_summary(gate_result, run_result, has_explanation, severity)

    return RuntimeTrace(
        decision=gate_result.decision,
        matched_rules=list(gate_result.matched_rules),
        shadow_mode=shadow_mode,
        has_explanation=has_explanation,
        severity=severity,
        summary=summary,
    )


def _extract_severity(run_result: ShadowRunResult) -> str | None:
    """从解释元数据中推导最高风险级别。

    优先级：
    1. enhanced_output.explanation_bundle 存在 → 从 explanations 取最高 risk_level
    2. 无 explanation → None
    """
    bundle = (
        run_result.enhanced_output.explanation_bundle
        if run_result.enhanced_output is not None
        else None
    )
    if bundle is None or not bundle.explanations:
        return None

    risk_levels = [exp.risk_level for exp in bundle.explanations]
    if "high" in risk_levels:
        return "high"
    if "medium" in risk_levels:
        return "medium"
    if "low" in risk_levels:
        return "low"
    return None


def _build_summary(
    gate_result,
    run_result,
    has_explanation: bool,
    severity: str | None,
) -> str:
    """构建一行可读摘要。

    模板：
    - 有 explanation:
      - 有规则: "Block | high | 1 rules | 触发阻断（high/separation_of_duties）：..."
      - 无规则: "Allow | no-rules | 未触发治理规则"
    - 无 explanation:
      - 有规则: "Block | 1 rules | explanation-unavailable"
      - 无规则: "Allow | no-rules | explanation-unavailable"
    """
    decision = gate_result.decision
    rule_count = len(gate_result.matched_rules)

    if not has_explanation:
        rule_text = f"{rule_count} rules" if rule_count > 0 else "no-rules"
        return f"{decision} | {rule_text} | explanation-unavailable"

    # 有 explanation
    if rule_count == 0:
        return f"{decision} | no-rules | 未触发治理规则"

    # 有规则 + 有 explanation：使用 explanation_bundle.readable_summary
    severity_text = severity if severity else "unknown"
    rule_text = f"{rule_count} rule{'s' if rule_count != 1 else ''}"

    bundle = (
        run_result.enhanced_output.explanation_bundle
        if run_result.enhanced_output is not None
        else None
    )
    detail = bundle.readable_summary if bundle is not None else "解释不可用"

    return f"{decision} | {severity_text} | {rule_text} | {detail}"
