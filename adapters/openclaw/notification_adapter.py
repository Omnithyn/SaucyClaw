"""OpenClaw 通知适配器 — 通过 HTTP/Command gateway 发送治理决策通知。

与 mock adapter（OpenClawHostAdapter）不同，本适配器面向真实 OpenClaw gateway，
将 SaucyClaw 治理决策通过 HTTP POST 或 shell command 发送为通知。

设计依据：
- OpenClaw OpenClawPayload 结构（src/openclaw/types.ts）
- OpenClaw wakeGateway 实现（src/openclaw/dispatcher.ts）
- 差距分析结论（docs/integration/openclaw_real_runtime_gap_analysis.md）
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from urllib import request, error

from stores.protocols import GateResult


@dataclass(frozen=True)
class WakeResult:
    """OpenClaw wake 调用结果。"""
    gateway: str
    success: bool
    error: str | None = None
    status_code: int | None = None


def _build_openclaw_payload(
    decision: str,
    matched_rules: list[str],
    reason: str,
    suggestions: list[str],
    explanation_summary: str | None = None,
    session_context: dict[str, str] | None = None,
) -> dict[str, Any]:
    """构建对齐 OpenClaw OpenClawPayload 的通知 payload。

    对齐 TypeScript 定义（src/openclaw/types.ts）：
    interface OpenClawPayload {
        event: string;
        instruction: string;
        text: string;
        timestamp: string;
        sessionId?: string;
        projectPath?: string;
        projectName?: string;
        tmuxSession?: string;
        context: OpenClawContext;
    }
    """
    ctx = session_context or {}
    now = datetime.now(timezone.utc).isoformat()

    # 构建 instruction 文本（对齐 OpenClaw 的 interpolateInstruction 模板风格）
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

    instruction = "\n".join(lines)

    context = {
        "sessionId": ctx.get("session_id", ""),
        "projectPath": ctx.get("project_path", ""),
        "projectName": ctx.get("project_name", ""),
        "tmuxSession": ctx.get("tmux_session", ""),
    }

    return {
        "event": "governance-decision",
        "instruction": instruction,
        "text": f"治理决策: {decision} — {reason}",
        "timestamp": now,
        "sessionId": ctx.get("session_id"),
        "projectPath": ctx.get("project_path"),
        "projectName": ctx.get("project_name"),
        "tmuxSession": ctx.get("tmux_session"),
        "context": context,
    }


class OpenClawNotificationAdapter:
    """通过 OpenClaw gateway 发送治理决策通知。

    支持两种 gateway 类型：
    - http: HTTP POST JSON payload 到指定 URL
    - command: 执行 shell command（通过 subprocess）

    用法：
        adapter = OpenClawNotificationAdapter(
            gateway_url="http://127.0.0.1:18789/hooks/agent",
            gateway_name="local",
        )
        result = adapter.send_decision(gate_result, session_context)
    """

    def __init__(
        self,
        gateway_url: str,
        gateway_name: str = "saucyclaw",
        headers: dict[str, str] | None = None,
        timeout_ms: int = 10_000,
    ) -> None:
        self.gateway_url = gateway_url
        self.gateway_name = gateway_name
        self.headers = headers or {"Content-Type": "application/json"}
        self.timeout_ms = timeout_ms
        self._log: list[tuple[GateResult, WakeResult]] = []
        self._last_payload: dict[str, Any] | None = None

    def send_decision(
        self,
        result: GateResult,
        session_context: dict[str, str] | None = None,
        explanation_summary: str | None = None,
    ) -> WakeResult:
        """构建 OpenClawPayload 并通过 HTTP POST 发送到 gateway。"""
        payload = _build_openclaw_payload(
            decision=result.decision,
            matched_rules=result.matched_rules,
            reason=result.reason,
            suggestions=result.suggestions,
            explanation_summary=explanation_summary,
            session_context=session_context,
        )

        self._last_payload = payload
        wake_result = self._wake_gateway(payload)
        self._log.append((result, wake_result))
        return wake_result

    @property
    def last_payload(self) -> dict[str, Any] | None:
        """返回最近一次发送的 payload 副本（用于验证证据保存）。"""
        if self._last_payload is None:
            return None
        return dict(self._last_payload)

    def _wake_gateway(self, payload: dict[str, Any]) -> WakeResult:
        """发送 payload 到 HTTP gateway。"""
        timeout_sec = self.timeout_ms / 1000.0
        data = json.dumps(payload).encode("utf-8")

        req = request.Request(
            self.gateway_url,
            data=data,
            headers=self.headers,
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=timeout_sec) as response:
                status_code = response.getcode()
                if status_code >= 400:
                    return WakeResult(
                        gateway=self.gateway_name,
                        success=False,
                        error=f"HTTP {status_code}",
                        status_code=status_code,
                    )
                return WakeResult(
                    gateway=self.gateway_name,
                    success=True,
                    status_code=status_code,
                )
        except error.HTTPError as exc:
            return WakeResult(
                gateway=self.gateway_name,
                success=False,
                error=f"HTTP {exc.code}",
                status_code=exc.code,
            )
        except error.URLError as exc:
            return WakeResult(
                gateway=self.gateway_name,
                success=False,
                error=str(exc.reason),
            )
        except TimeoutError:
            return WakeResult(
                gateway=self.gateway_name,
                success=False,
                error="Request timed out",
            )

    @property
    def log(self) -> list[tuple[GateResult, WakeResult]]:
        """返回发送日志（结果不可变副本）。"""
        return list(self._log)


class OpenClawCommandNotificationAdapter:
    """通过 shell command 发送治理决策通知。

    对应 OpenClaw 的 command gateway 类型。

    用法：
        adapter = OpenClawCommandNotificationAdapter(
            command="echo '{{instruction}}' | nc 127.0.0.1 18789",
            gateway_name="local-cmd",
        )
        result = adapter.send_decision(gate_result, session_context)
    """

    def __init__(
        self,
        command: str,
        gateway_name: str = "saucyclaw-cmd",
        timeout_ms: int = 5_000,
    ) -> None:
        self.command = command
        self.gateway_name = gateway_name
        self.timeout_ms = timeout_ms
        self._log: list[tuple[GateResult, WakeResult]] = []

    def send_decision(
        self,
        result: GateResult,
        session_context: dict[str, str] | None = None,
        explanation_summary: str | None = None,
    ) -> WakeResult:
        """构建变量并执行插值后的 command。"""
        ctx = session_context or {}
        project_name = ctx.get("project_name", "")
        if not project_name and ctx.get("project_path"):
            import os
            project_name = os.path.basename(ctx["project_path"])

        variables: dict[str, str] = {
            "session_id": ctx.get("session_id", ""),
            "project_path": ctx.get("project_path", ""),
            "project_name": project_name,
            "tmux_session": ctx.get("tmux_session", ""),
            "decision": result.decision,
            "reason": result.reason,
            "matched_rules": ", ".join(result.matched_rules),
            "suggestions": "; ".join(result.suggestions),
        }

        # 对齐 OpenClaw 的 interpolateInstruction
        command = self.command
        for key, value in variables.items():
            command = command.replace(f"{{{{{key}}}}}", value)

        # 添加 instruction 变量（已插值的完整指令）
        rule_info = f"规则: {', '.join(result.matched_rules)}" if result.matched_rules else "未触发治理规则"
        instruction = (
            f"[governance|{result.decision}]\n"
            f"决策: {result.decision}\n"
            f"{rule_info}\n"
            f"原因: {result.reason}"
        )
        if explanation_summary:
            instruction += f"\n解释: {explanation_summary}"

        command = command.replace("{{instruction}}", instruction)

        wake_result = self._execute_command(command)
        self._log.append((result, wake_result))
        return wake_result

    def _execute_command(self, command: str) -> WakeResult:
        """执行 shell command。"""
        timeout_sec = self.timeout_ms / 1000.0
        try:
            proc = subprocess.run(
                ["sh", "-c", command],
                capture_output=True,
                text=True,
                timeout=timeout_sec,
            )
            if proc.returncode != 0:
                return WakeResult(
                    gateway=self.gateway_name,
                    success=False,
                    error=f"Exit code {proc.returncode}: {proc.stderr.strip()}",
                )
            return WakeResult(
                gateway=self.gateway_name,
                success=True,
            )
        except subprocess.TimeoutExpired:
            return WakeResult(
                gateway=self.gateway_name,
                success=False,
                error="Command timed out",
            )
        except OSError as exc:
            return WakeResult(
                gateway=self.gateway_name,
                success=False,
                error=str(exc),
            )

    @property
    def log(self) -> list[tuple[GateResult, WakeResult]]:
        return list(self._log)
