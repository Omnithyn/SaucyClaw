"""OpenClaw Hooks 适配器 — 通过 /hooks/agent endpoint 发送治理决策通知。

本适配器专门用于对接 OpenClaw hooks API，使用 HookAgentPayload 格式。

与 OpenClawNotificationAdapter 不同：
- OpenClawNotificationAdapter 使用 OpenClawPayload 格式（event, instruction, text, timestamp）
- OpenClawHooksAdapter 使用 HookAgentPayload 格式（message, name, wakeMode, channel）

OpenClaw hooks API 要求：
- POST /hooks/agent
- Authorization: Bearer <hooks.token>
- Content-Type: application/json
- Body: HookAgentPayload
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from urllib import request, error

from stores.protocols import GateResult


@dataclass(frozen=True)
class HooksWakeResult:
    """OpenClaw hooks wake 调用结果。"""
    gateway: str
    success: bool
    run_id: str | None = None
    error: str | None = None
    status_code: int | None = None


def _build_hook_agent_payload(
    decision: str,
    matched_rules: list[str],
    reason: str,
    suggestions: list[str],
    explanation_summary: str | None = None,
    name: str = "SaucyClaw Governance",
) -> dict[str, Any]:
    """构建 HookAgentPayload 格式的通知 payload。

    HookAgentPayload 结构（根据 OpenClaw 源代码）：
    - message: 必需，消息内容
    - name: 可选，Hook 名称（默认 "Hook"）
    - wakeMode: "now" | "next-heartbeat"，默认 "now"
    - deliver: boolean，默认 true
    - channel: "last" | "discord" | "telegram" | ...，默认 "last"
    """
    # 构建完整的治理决策消息
    rule_info = f"规则: {', '.join(matched_rules)}" if matched_rules else "未触发治理规则"
    suggestion_info = f"建议: {'; '.join(suggestions)}" if suggestions else ""
    explanation_info = f"解释: {explanation_summary}" if explanation_summary else ""

    lines = [
        f"[governance|{decision}]",
        f"决策: {decision}",
        rule_info,
        f"原因: {reason}",
    ]
    if suggestion_info:
        lines.append(suggestion_info)
    if explanation_info:
        lines.append(explanation_info)

    message = "\n".join(lines)

    return {
        "message": message,
        "name": name,
        "wakeMode": "now",
        "deliver": True,
        "channel": "last",
    }


class OpenClawHooksAdapter:
    """通过 OpenClaw /hooks/agent endpoint 发送治理决策通知。

    用法：
        adapter = OpenClawHooksAdapter(
            gateway_url="http://127.0.0.1:26277/hooks/agent",
            token="your-hooks-token",
        )
        result = adapter.send_decision(gate_result)
    """

    def __init__(
        self,
        gateway_url: str,
        token: str,
        gateway_name: str = "openclaw-hooks",
        timeout_ms: int = 10_000,
    ) -> None:
        self.gateway_url = gateway_url
        self.token = token
        self.gateway_name = gateway_name
        self.timeout_ms = timeout_ms
        self._log: list[tuple[GateResult, HooksWakeResult]] = []
        self._last_payload: dict[str, Any] | None = None

    def send_decision(
        self,
        result: GateResult,
        explanation_summary: str | None = None,
        hook_name: str = "SaucyClaw Governance",
    ) -> HooksWakeResult:
        """构建 HookAgentPayload 并通过 /hooks/agent 发送。"""
        payload = _build_hook_agent_payload(
            decision=result.decision,
            matched_rules=result.matched_rules,
            reason=result.reason,
            suggestions=result.suggestions,
            explanation_summary=explanation_summary,
            name=hook_name,
        )

        self._last_payload = payload
        wake_result = self._wake_hooks(payload)
        self._log.append((result, wake_result))
        return wake_result

    @property
    def last_payload(self) -> dict[str, Any] | None:
        """返回最近一次发送的 payload 副本。"""
        if self._last_payload is None:
            return None
        return dict(self._last_payload)

    def _wake_hooks(self, payload: dict[str, Any]) -> HooksWakeResult:
        """发送 payload 到 /hooks/agent endpoint。"""
        timeout_sec = self.timeout_ms / 1000.0
        data = json.dumps(payload).encode("utf-8")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
        }

        req = request.Request(
            self.gateway_url,
            data=data,
            headers=headers,
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=timeout_sec) as response:
                status_code = response.getcode()
                body = response.read().decode("utf-8")
                resp_json = json.loads(body)

                if status_code >= 400:
                    return HooksWakeResult(
                        gateway=self.gateway_name,
                        success=False,
                        error=f"HTTP {status_code}",
                        status_code=status_code,
                    )

                run_id = resp_json.get("runId")
                return HooksWakeResult(
                    gateway=self.gateway_name,
                    success=True,
                    run_id=run_id,
                    status_code=status_code,
                )
        except error.HTTPError as exc:
            body = exc.read().decode("utf-8") if exc.fp else ""
            return HooksWakeResult(
                gateway=self.gateway_name,
                success=False,
                error=f"HTTP {exc.code}: {body}",
                status_code=exc.code,
            )
        except error.URLError as exc:
            return HooksWakeResult(
                gateway=self.gateway_name,
                success=False,
                error=str(exc.reason),
            )
        except TimeoutError:
            return HooksWakeResult(
                gateway=self.gateway_name,
                success=False,
                error="Request timed out",
            )

    @property
    def log(self) -> list[tuple[GateResult, HooksWakeResult]]:
        """返回发送日志。"""
        return list(self._log)