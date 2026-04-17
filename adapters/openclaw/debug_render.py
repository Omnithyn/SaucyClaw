"""最小调试输出渲染器。

Phase 2.6: 把 Shadow 运行结果渲染为稳定、可读的调试文本。

不做日志框架，不做 formatter 系统，只暴露一个纯函数。
用途：example 展示 / CLI 调试 / 文档输出。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from adapters.openclaw.runtime_trace import RuntimeTrace
    from adapters.openclaw.shadow_runtime import ShadowRunResult


def render_shadow_run(
    run_result: ShadowRunResult,
    trace: RuntimeTrace,
) -> str:
    """渲染一段稳定的调试输出文本。

    所有业务字段均以 RuntimeTrace 为单一真相来源，不重新推导。

    Args:
        run_result: ShadowRuntime.process_and_write 的返回值
        trace: build_runtime_trace 的返回值

    Returns:
        多行调试文本
    """
    lines: list[str] = []

    # ── Header ──
    lines.append("── Shadow Run " + "─" * 40)
    lines.append(f"决策: {trace.decision}")
    rules_text = ", ".join(trace.matched_rules) if trace.matched_rules else "无"
    lines.append(f"规则: {rules_text}")
    lines.append(f"Shadow Mode: {'ON' if trace.shadow_mode else 'OFF'}")
    lines.append(f"解释: {'有' if trace.has_explanation else '无'}")
    severity_text = trace.severity if trace.severity else "无"
    lines.append(f"风险: {severity_text}")
    lines.append("")
    lines.append(f"摘要: {trace.summary}")
    lines.append("")

    # ── Explanation ──
    lines.append("── Explanation " + "─" * 39)
    bundle = (
        run_result.enhanced_output.explanation_bundle
        if run_result.enhanced_output is not None
        else None
    )

    if bundle is not None and bundle.explanations:
        for exp in bundle.explanations:
            lines.append(f"- {exp.rule_id}: {exp.rationale}")
    elif bundle is not None:
        lines.append("- no triggered rule explanations")
    else:
        lines.append("- explanation-unavailable")

    lines.append("")

    # ── Write Back ──
    lines.append("── Write Back " + "─" * 40)
    gate = run_result.gate_result
    rule_count = len(gate.matched_rules)
    risk_text = trace.severity if trace.severity else "无"
    lines.append(f"[{trace.decision}] 触发 {rule_count} 条规则，风险等级: {risk_text}")
    lines.append("─" * 53)

    return "\n".join(lines)
