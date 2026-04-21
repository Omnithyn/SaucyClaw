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

复用公共基座：
- InboundHookResult — 直接复用（字段完全一致）
- build_gatekeeping_response_from_gate_result — 桥接使用
- parse_inbound_hook_event_minimal — 桥接使用
"""

from __future__ import annotations

import json
from typing import Any, Protocol

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


# ─── OpenHarness Hook Payload 契约（桥接公共基座）───


def build_openharness_hook_response(
    gate_result: GateResult,
    status_code: int = 200,
) -> tuple[dict[str, Any], OpenHarnessHookResult]:
    """从 GateResult 构建 OpenHarness hook 响应。

    M16: 桥接公共基座 build_gatekeeping_response_from_gate_result

    OpenHarness HTTP Hook 的响应逻辑：
    - 2xx 响应 → hook 成功，继续执行（除非 block_on_failure 且响应非 success）
    - 非 2xx 响应 → hook 失败，若 block_on_failure=true 则阻断

    治理阻断策略：
    - Block 决策 → 返回 403 + 阻止标记
    - Allow 决策 → 返回 200 + 通过标记
    """
    # 使用公共基座构建 GatekeepingResponse
    base_response = build_gatekeeping_response_from_gate_result(gate_result)

    # 转换为 OpenHarness 特定的 dict 格式
    # OpenHarness 期望 {blocked, reason, matched_rules} 结构
    response_body = {
        "blocked": base_response.blocked,
        "reason": base_response.reason,
    }

    if base_response.blocked:
        response_body["matched_rules"] = base_response.matched_rules

    # 使用公共基座的 InboundHookResult
    result = OpenHarnessHookResult(
        success=base_response.success,
        blocked=base_response.blocked,
        status_code=base_response.status_code,
    )

    return response_body, result


def parse_openharness_hook_payload(raw: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """解析 OpenHarness HTTP Hook 发送的 payload。

    M16: 桥接公共基座 parse_inbound_hook_event_minimal

    OpenHarness 发送的格式：
    {"event": "pre_tool_use", "payload": {...工具名和参数...}}
    """
    # 使用公共基座解析
    event = parse_inbound_hook_event_minimal(raw, event_key="event", payload_key="payload")

    # 返回 tuple 格式（兼容现有调用）
    return event.event_type, event.payload


# ─── Receiver（治理端点）───


class GovernanceCheckFn(Protocol):
    """治理检查函数接口。"""

    def __call__(self, event_type: str, payload: dict[str, Any]) -> GateResult:
        """治理检查函数。"""
        ...


class OpenHarnessHookReceiver:
    """接收 OpenHarness hook 请求，执行治理检查，返回响应。

    M16: 通过复用 InboundHookResult，自动符合 InboundHookReceiver Protocol

    用法：
        def my_check(event_type, payload) -> GateResult:
            ...

        receiver = OpenHarnessHookReceiver(governance_check=my_check)
        response_body, result = receiver.handle_hook_request(hook_payload)
    """

    def __init__(self, governance_check: GovernanceCheckFn) -> None:
        self._governance_check = governance_check
        self._log: list[tuple[dict[str, Any], InboundHookResult]] = []

    def handle_hook_request(
        self,
        raw_payload: dict[str, Any],
    ) -> tuple[dict[str, Any], InboundHookResult]:
        """处理 OpenHarness hook POST 请求。

        返回 (response_body, result)，调用方负责设置 HTTP status_code。
        """
        event_type, payload = parse_openharness_hook_payload(raw_payload)
        gate_result = self._governance_check(event_type, payload)
        response_body, result = build_openharness_hook_response(gate_result)

        self._log.append((raw_payload, result))
        return response_body, result

    @property
    def log(self) -> list[tuple[dict[str, Any], InboundHookResult]]:
        return list(self._log)


# ─── Probe（本地验证端）───


class OpenHarnessHookProbe:
    """模拟 OpenHarness 发送 hook POST，用于本地验证。

    M16: 通过复用 InboundHookResult，自动符合 InboundHookProbe Protocol

    用法：
        probe = OpenHarnessHookProbe(target_url="http://localhost:9988/governance")
        result = probe.send_hook_event("pre_tool_use", {"tool_name": "Write"})
    """

    def __init__(
        self,
        target_url: str,
        timeout_ms: int = 5000,
    ) -> None:
        self.target_url = target_url
        self.timeout_ms = timeout_ms
        self._log: list[tuple[dict[str, Any], InboundHookResult]] = []

    def send_hook_event(
        self,
        event_type: str,
        payload: dict[str, Any],
    ) -> InboundHookResult:
        """发送模拟 hook 事件到目标端点。"""
        from urllib import request, error

        hook_payload = {
            "event": event_type,
            "payload": payload,
        }

        timeout_sec = self.timeout_ms / 1000.0
        data = json.dumps(hook_payload).encode("utf-8")
        headers = {"Content-Type": "application/json"}

        req = request.Request(
            self.target_url,
            data=data,
            headers=headers,
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=timeout_sec) as response:
                status_code = response.getcode()
                body = json.loads(response.read().decode("utf-8"))
                blocked = body.get("blocked", False)

                result = InboundHookResult(
                    success=True,
                    blocked=blocked,
                    status_code=status_code,
                    event_type=event_type,
                )
        except error.HTTPError as exc:
            body_text = exc.read().decode("utf-8") if exc.fp else ""
            try:
                body = json.loads(body_text)
                blocked = body.get("blocked", False)
            except (json.JSONDecodeError, ValueError):
                blocked = True

            result = InboundHookResult(
                success=False,
                blocked=blocked,
                error=f"HTTP {exc.code}: {body_text}",
                status_code=exc.code,
                event_type=event_type,
            )
        except error.URLError as exc:
            result = InboundHookResult(
                success=False,
                blocked=False,
                error=str(exc.reason),
                event_type=event_type,
            )
        except TimeoutError:
            result = InboundHookResult(
                success=False,
                blocked=False,
                error="Request timed out",
                event_type=event_type,
            )

        self._log.append((hook_payload, result))
        return result

    @property
    def log(self) -> list[tuple[dict[str, Any], InboundHookResult]]:
        return list(self._log)
