"""共享 HTTP Inbound Hook Adapter 骨架。

M18 — Shared Inbound HTTP Hook Adapter Base

提供 OpenHarness/Hermes 共享的 HTTP inbound hook 实现骨架：
- Probe HTTP POST 发送 + 错误处理
- Receiver 模板方法（parse → check → build → log）

runtime-specific 部分（由各 runtime 实现）：
- parse_hook_payload(raw) → (event_type, payload)
- build_hook_response(gate_result) → (dict, InboundHookResult)

复用公共基座：
- InboundHookResult — 直接使用
"""

from __future__ import annotations

import json
from typing import Any, Callable

from adapters.inbound_hook_protocols import InboundHookResult
from stores.protocols import GateResult


# ─── 共享 Probe 骨架 ───


class InboundHttpHookProbeBase:
    """共享 HTTP inbound hook probe 骨架。

    M18: 提供 HTTP POST 发送 + 错误处理的共享实现。

    提供：
    - HTTP POST 发送
    - 错误处理（HTTPError/URLError/TimeoutError）
    - log 结构

    runtime-specific 部分（子类可覆盖）：
    - build_hook_payload(event_type, payload) → dict

    用法：
        # 直接继承（默认行为正确）
        class OpenHarnessHookProbe(InboundHttpHookProbeBase):
            pass

        # 或覆盖 build_hook_payload（如 payload 格式不同）
        class CustomHookProbe(InboundHttpHookProbeBase):
            def build_hook_payload(self, event_type, payload):
                return {"type": event_type, "data": payload}  # 自定义格式
    """

    def __init__(
        self,
        target_url: str,
        timeout_ms: int = 5000,
    ) -> None:
        self.target_url = target_url
        self.timeout_ms = timeout_ms
        self._log: list[tuple[dict[str, Any], InboundHookResult]] = []

    def build_hook_payload(self, event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        """构造 hook payload（子类可覆盖）。

        默认格式：{"event": event_type, "payload": payload}
        OpenHarness/Hermes 都使用此格式，无需覆盖。
        """
        return {
            "event": event_type,
            "payload": payload,
        }

    def send_hook_event(
        self,
        event_type: str,
        payload: dict[str, Any],
    ) -> InboundHookResult:
        """发送 hook 事件（共享实现）。

        流程：
        1. 构造 hook_payload（调用 build_hook_payload）
        2. 创建 HTTP Request
        3. POST 到 target_url
        4. 处理响应/错误
        5. 记录 log
        6. 返回 InboundHookResult
        """
        from urllib import request, error

        hook_payload = self.build_hook_payload(event_type, payload)

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
        """获取发送历史记录。"""
        return list(self._log)


# ─── 共享 Receiver 骨架 ───


class InboundHttpHookReceiverBase:
    """共享 HTTP inbound hook receiver 骨架。

    M18: 提供 handle_hook_request 模板方法的共享实现。

    提供：
    - handle_hook_request 模板方法（parse → check → build → log）
    - log 结构

    runtime-specific 部分（注入）：
    - parse_hook_payload(raw) → (event_type, payload)
    - build_hook_response(gate_result) → (dict, InboundHookResult)

    用法：
        class OpenHarnessHookReceiver(InboundHttpHookReceiverBase):
            def __init__(self, governance_check):
                super().__init__(
                    governance_check=governance_check,
                    parse_hook_payload=parse_openharness_hook_payload,
                    build_hook_response=build_openharness_hook_response,
                )
    """

    def __init__(
        self,
        governance_check: Callable[[str, dict[str, Any]], GateResult],
        parse_hook_payload: Callable[[dict[str, Any]], tuple[str, dict[str, Any]]],
        build_hook_response: Callable[[GateResult], tuple[dict[str, Any], InboundHookResult]],
    ) -> None:
        self._governance_check = governance_check
        self._parse_hook_payload = parse_hook_payload
        self._build_hook_response = build_hook_response
        self._log: list[tuple[dict[str, Any], InboundHookResult]] = []

    def handle_hook_request(
        self,
        raw_payload: dict[str, Any],
    ) -> tuple[dict[str, Any], InboundHookResult]:
        """处理 hook 请求（共享模板方法）。

        流程：
        1. parse_hook_payload(raw_payload) → (event_type, payload)
        2. governance_check(event_type, payload) → GateResult
        3. build_hook_response(gate_result) → (response_body, result)
        4. log.append((raw_payload, result))
        5. return (response_body, result)
        """
        event_type, payload = self._parse_hook_payload(raw_payload)
        gate_result = self._governance_check(event_type, payload)
        response_body, result = self._build_hook_response(gate_result)

        self._log.append((raw_payload, result))
        return response_body, result

    @property
    def log(self) -> list[tuple[dict[str, Any], InboundHookResult]]:
        """获取处理历史记录。"""
        return list(self._log)
