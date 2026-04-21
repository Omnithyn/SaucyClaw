"""Hermes Hook 适配器 — 最小可执行版本。

对接 Hermes Hook 脚本发现机制：
- Hermes 从 ~/.hermes/hooks/ 目录发现脚本
- agent:step 事件触发时执行脚本
- 脚本通过 stdin 接收事件数据，POST 到 SaucyClaw 端点
- 脚本返回非 0 值阻断 Hermes 操作

本适配器提供两个方向的能力：
1. HermesHookReceiver — 接收 Hermes hook POST 请求，执行治理，返回响应
2. HermesHookProbe — 模拟 Hermes 发送 hook POST，用于本地验证

M17 — Hermes First Executable Path on Inbound Base
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

# HermesHookResult 与 InboundHookResult 字段完全一致
# 直接复用公共基座，无需重复定义
HermesHookResult = InboundHookResult


# ─── Hermes Hook Payload 契约（runtime-specific）───


def build_hermes_hook_response(
    gate_result: GateResult,
    status_code: int = 200,
) -> tuple[dict[str, Any], HermesHookResult]:
    """从 GateResult 构建 Hermes hook 响应。

    runtime-specific: 转换为 Hermes 特定的 dict 格式。

    M17: 桥接公共基座 build_gatekeeping_response_from_gate_result
    """
    # 使用公共基座构建 GatekeepingResponse
    base_response = build_gatekeeping_response_from_gate_result(gate_result)

    # 转换为 Hermes 特定的 dict 格式
    response_body = {
        "blocked": base_response.blocked,
        "reason": base_response.reason,
    }

    if base_response.blocked:
        response_body["matched_rules"] = base_response.matched_rules

    result = HermesHookResult(
        success=base_response.success,
        blocked=base_response.blocked,
        status_code=base_response.status_code,
    )

    return response_body, result


def parse_hermes_hook_payload(raw: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """解析 Hermes Hook 脚本发送的 payload。

    runtime-specific: Hermes payload 格式 {"event": "agent:step", "payload": {...}}

    M17: 桥接公共基座 parse_inbound_hook_event_minimal
    """
    event = parse_inbound_hook_event_minimal(raw, event_key="event", payload_key="payload")
    return event.event_type, event.payload


# ─── Receiver（使用共享骨架）───


class GovernanceCheckFn(Protocol):
    """治理检查函数接口。"""

    def __call__(self, event_type: str, payload: dict[str, Any]) -> GateResult:
        """治理检查函数。"""
        ...


class HermesHookReceiver(InboundHttpHookReceiverBase):
    """接收 Hermes hook 请求，执行治理检查，返回响应。

    M18: 继承共享骨架 InboundHttpHookReceiverBase

    用法：
        def my_check(event_type, payload) -> GateResult:
            ...

        receiver = HermesHookReceiver(governance_check=my_check)
        response_body, result = receiver.handle_hook_request(hook_payload)
    """

    def __init__(self, governance_check: GovernanceCheckFn) -> None:
        super().__init__(
            governance_check=governance_check,
            parse_hook_payload=parse_hermes_hook_payload,
            build_hook_response=build_hermes_hook_response,
        )


# ─── Probe（使用共享骨架）───


class HermesHookProbe(InboundHttpHookProbeBase):
    """模拟 Hermes 发送 hook POST，用于本地验证。

    M18: 继承共享骨架 InboundHttpHookProbeBase

    用法：
        probe = HermesHookProbe(target_url="http://localhost:18990/governance")
        result = probe.send_hook_event("agent:step", {"tool_name": "Write"})
    """

    pass  # 默认 build_hook_payload 格式正确，无需覆盖
