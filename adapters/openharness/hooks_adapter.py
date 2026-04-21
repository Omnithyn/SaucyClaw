"""OpenHarness HTTP Hook 适配器 — 最小可执行版本。

对接 OpenHarness HTTP Hook 机制：
- OpenHarness 配置 HTTP Hook，当 pre_tool_use 等事件触发时 POST 到远程 URL
- SaucyClaw 作为 HTTP 端点接收事件，执行治理检查，返回响应
- block_on_failure: true 时，SaucyClaw 返回非 2xx 即可阻断 OpenHarness 操作

本适配器提供两个方向的能力：
1. OpenHarnessHookReceiver — 接收 OpenHarness hook POST 请求，执行治理，返回响应
2. OpenHarnessHookProbe — 模拟 OpenHarness 发送 hook POST，用于本地验证

M12 — OpenHarness First Executable Path
M16 — Inbound Base Adoption（真正复用公共基座）
M18 — Shared HTTP Hook Adapter Base（复用共享骨架）

复用层次：
- 公共协议：inbound_hook_protocols.py（InboundHookResult + Helper）
- 共享骨架：inbound_http_hook_base.py（Probe/Receiver 基类）
- runtime-specific：本文件（parse + build 函数）
"""

from __future__ import annotations

from typing import Any, Protocol

from adapters.inbound_http_hook_base import (
    InboundHttpHookProbeBase,
    InboundHttpHookReceiverBase,
)
from adapters.inbound_hook_protocols import (
    InboundHookResult,
    build_gatekeeping_response_from_gate_result,
    parse_inbound_hook_event_minimal,
)
from stores.protocols import GateResult


# ─── 结果结构（直接复用公共基座）───

# OpenHarnessHookResult 与 InboundHookResult 字段完全一致
# 直接复用公共基座，无需重复定义
OpenHarnessHookResult = InboundHookResult


# ─── OpenHarness Hook Payload 契约（runtime-specific）───


def build_openharness_hook_response(
    gate_result: GateResult,
    status_code: int = 200,
) -> tuple[dict[str, Any], OpenHarnessHookResult]:
    """从 GateResult 构建 OpenHarness hook 响应。

    runtime-specific: 转换为 OpenHarness 特定的 dict 格式。

    M16: 桥接公共基座 build_gatekeeping_response_from_gate_result
    """
    # 使用公共基座构建 GatekeepingResponse
    base_response = build_gatekeeping_response_from_gate_result(gate_result)

    # 转换为 OpenHarness 特定的 dict 格式
    response_body = {
        "blocked": base_response.blocked,
        "reason": base_response.reason,
    }

    if base_response.blocked:
        response_body["matched_rules"] = base_response.matched_rules

    result = OpenHarnessHookResult(
        success=base_response.success,
        blocked=base_response.blocked,
        status_code=base_response.status_code,
    )

    return response_body, result


def parse_openharness_hook_payload(raw: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """解析 OpenHarness HTTP Hook 发送的 payload。

    runtime-specific: OpenHarness payload 格式 {"event": ..., "payload": ...}

    M16: 桥接公共基座 parse_inbound_hook_event_minimal
    """
    event = parse_inbound_hook_event_minimal(raw, event_key="event", payload_key="payload")
    return event.event_type, event.payload


# ─── Receiver（使用共享骨架）───


class GovernanceCheckFn(Protocol):
    """治理检查函数接口。"""

    def __call__(self, event_type: str, payload: dict[str, Any]) -> GateResult:
        """治理检查函数。"""
        ...


class OpenHarnessHookReceiver(InboundHttpHookReceiverBase):
    """接收 OpenHarness hook 请求，执行治理检查，返回响应。

    M18: 继承共享骨架 InboundHttpHookReceiverBase

    用法：
        def my_check(event_type, payload) -> GateResult:
            ...

        receiver = OpenHarnessHookReceiver(governance_check=my_check)
        response_body, result = receiver.handle_hook_request(hook_payload)
    """

    def __init__(self, governance_check: GovernanceCheckFn) -> None:
        super().__init__(
            governance_check=governance_check,
            parse_hook_payload=parse_openharness_hook_payload,
            build_hook_response=build_openharness_hook_response,
        )


# ─── Probe（使用共享骨架）───


class OpenHarnessHookProbe(InboundHttpHookProbeBase):
    """模拟 OpenHarness 发送 hook POST，用于本地验证。

    M18: 继承共享骨架 InboundHttpHookProbeBase

    用法：
        probe = OpenHarnessHookProbe(target_url="http://localhost:9988/governance")
        result = probe.send_hook_event("pre_tool_use", {"tool_name": "Write"})
    """

    pass  # 默认 build_hook_payload 格式正确，无需覆盖
