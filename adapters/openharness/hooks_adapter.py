"""OpenHarness HTTP Hook 适配器 — 最小可执行版本。

对接 OpenHarness HTTP Hook 机制：
- OpenHarness 配置 HTTP Hook，当 pre_tool_use 等事件触发时 POST 到远程 URL
- SaucyClaw 作为 HTTP 端点接收事件，执行治理检查，返回响应
- block_on_failure: true 时，SaucyClaw 返回非 2xx 即可阻断 OpenHarness 操作

本适配器提供两个方向的能力：
1. OpenHarnessHookReceiver — 接收 OpenHarness hook POST 请求，执行治理，返回响应
2. OpenHarnessHookProbe — 模拟 OpenHarness 发送 hook POST，用于本地验证

M12 — OpenHarness First Executable Path
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Protocol

from stores.protocols import GateResult


# ─── 结果结构 ───


@dataclass(frozen=True)
class OpenHarnessHookResult:
    """OpenHarness hook 处理结果。"""
    success: bool
    blocked: bool
    error: str | None = None
    status_code: int | None = None
    event_type: str | None = None


# ─── OpenHarness Hook Payload 契约 ───


def build_openharness_hook_response(
    gate_result: GateResult,
    status_code: int = 200,
) -> tuple[dict[str, Any], OpenHarnessHookResult]:
    """从 GateResult 构建 OpenHarness hook 响应。

    OpenHarness HTTP Hook 的响应逻辑：
    - 2xx 响应 → hook 成功，继续执行（除非 block_on_failure 且响应非 success）
    - 非 2xx 响应 → hook 失败，若 block_on_failure=true 则阻断

    治理阻断策略：
    - Block 决策 → 返回 403 + 阻止标记
    - Allow 决策 → 返回 200 + 通过标记
    """
    is_block = gate_result.decision == "Block"

    if is_block:
        status_code = 403
        response_body = {
            "blocked": True,
            "reason": gate_result.reason,
            "matched_rules": gate_result.matched_rules,
        }
    else:
        status_code = 200
        response_body = {
            "blocked": False,
            "reason": gate_result.reason,
        }

    result = OpenHarnessHookResult(
        success=not is_block,
        blocked=is_block,
        status_code=status_code,
    )

    return response_body, result


def parse_openharness_hook_payload(raw: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """解析 OpenHarness HTTP Hook 发送的 payload。

    OpenHarness 发送的格式：
    {"event": "pre_tool_use", "payload": {...工具名和参数...}}
    """
    event_type = raw.get("event", "unknown")
    payload = raw.get("payload", {})
    return event_type, payload


# ─── Receiver（治理端点） ───


class GovernanceCheckFn(Protocol):
    """治理检查函数接口。"""
    def __call__(self, event_type: str, payload: dict[str, Any]) -> GateResult: ...


class OpenHarnessHookReceiver:
    """接收 OpenHarness hook 请求，执行治理检查，返回响应。

    用法：
        def my_check(event_type, payload) -> GateResult:
            ...

        receiver = OpenHarnessHookReceiver(governance_check=my_check)
        response_body, result = receiver.handle_hook_request(hook_payload)
    """

    def __init__(self, governance_check: GovernanceCheckFn) -> None:
        self._governance_check = governance_check
        self._log: list[tuple[dict[str, Any], OpenHarnessHookResult]] = []

    def handle_hook_request(
        self,
        raw_payload: dict[str, Any],
    ) -> tuple[dict[str, Any], OpenHarnessHookResult]:
        """处理 OpenHarness hook POST 请求。

        返回 (response_body, result)，调用方负责设置 HTTP status_code。
        """
        event_type, payload = parse_openharness_hook_payload(raw_payload)
        gate_result = self._governance_check(event_type, payload)
        response_body, result = build_openharness_hook_response(gate_result)

        self._log.append((raw_payload, result))
        return response_body, result

    @property
    def log(self) -> list[tuple[dict[str, Any], OpenHarnessHookResult]]:
        return list(self._log)


# ─── Probe（本地验证端） ───


class OpenHarnessHookProbe:
    """模拟 OpenHarness 发送 hook POST，用于本地验证。

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
        self._log: list[tuple[dict[str, Any], OpenHarnessHookResult]] = []

    def send_hook_event(
        self,
        event_type: str,
        payload: dict[str, Any],
    ) -> OpenHarnessHookResult:
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

                result = OpenHarnessHookResult(
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

            result = OpenHarnessHookResult(
                success=False,
                blocked=blocked,
                error=f"HTTP {exc.code}: {body_text}",
                status_code=exc.code,
                event_type=event_type,
            )
        except error.URLError as exc:
            result = OpenHarnessHookResult(
                success=False,
                blocked=False,
                error=str(exc.reason),
                event_type=event_type,
            )
        except TimeoutError:
            result = OpenHarnessHookResult(
                success=False,
                blocked=False,
                error="Request timed out",
                event_type=event_type,
            )

        self._log.append((hook_payload, result))
        return result

    @property
    def log(self) -> list[tuple[dict[str, Any], OpenHarnessHookResult]]:
        return list(self._log)
