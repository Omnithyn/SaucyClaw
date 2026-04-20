"""Inbound Hook Gatekeeping 宿主无关抽象。

本模块定义 inbound_hook_gatekeeping 模式的公共基座：
- 宿主在事件点 POST 到 SaucyClaw 端点
- SaucyClaw 执行治理检查并返回阻断/放行响应

M15 — Inbound Hook Gatekeeping Base Package

设计原则：
- 宿主无关：不依赖具体 runtime（OpenHarness / Hermes）的 payload 格式
- 可复用：OpenHarness 已验证，Hermes 预期可复用
- 与 outbound_hook_push 边界清晰：两个模式各有独立抽象层
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Protocol


# ─── Gatekeeping 决策状态 ───


class GatekeepingDecision(str, Enum):
    """Gatekeeping 响应决策。

    与 GateResult.decision 对应，但这里仅用于响应结构。
    """
    ALLOW = "Allow"
    BLOCK = "Block"


# ─── Inbound Hook 事件结构 ───


@dataclass(frozen=True)
class InboundHookEvent:
    """Inbound hook 事件最小结构。

    宿主发送的 hook 事件至少包含：
    - event_type: 事件类型（如 pre_tool_use）
    - payload: 事件具体内容（由具体 runtime 定义）

    注意：具体 runtime 的 payload 格式由各自 adapter 定义，
    本结构仅提供最小公共抽象。
    """
    event_type: str
    payload: dict[str, Any]


# ─── Gatekeeping 响应结构 ───


@dataclass(frozen=True)
class GatekeepingResponse:
    """Gatekeeping 响应最小结构。

    SaucyClaw 返回给宿主的响应包含：
    - blocked: 是否阻断宿主操作
    - decision: 治理决策（Allow / Block）
    - reason: 阻断/放行原因
    - matched_rules: 匹配的治理规则
    - suggestions: 建议操作

    HTTP 状态码映射：
    - Allow → 200 (is_success)
    - Block → 403 (not is_success)

    宿主的 block_on_failure 逻辑：
    - success = response.is_success (2xx)
    - blocked = hook.block_on_failure and not success
    """
    blocked: bool
    decision: GatekeepingDecision
    reason: str | None = None
    matched_rules: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)

    @property
    def status_code(self) -> int:
        """根据决策返回 HTTP 状态码。

        Allow → 200
        Block → 403
        """
        return 200 if self.decision == GatekeepingDecision.ALLOW else 403

    @property
    def success(self) -> bool:
        """响应是否成功（2xx）。"""
        return self.status_code < 400


# ─── Inbound Hook 结果结构 ───


@dataclass(frozen=True)
class InboundHookResult:
    """Inbound hook 处理结果。

    Probe 发送 hook 请求后收到的结果：
    - success: HTTP 请求是否成功
    - blocked: 是否被治理阻断
    - error: 错误信息（如有）
    - status_code: HTTP 状态码
    - event_type: 事件类型
    """
    success: bool
    blocked: bool
    error: str | None = None
    status_code: int | None = None
    event_type: str | None = None


# ─── Live Validation Evidence 结构 ───


@dataclass(frozen=True)
class InboundHookEvidence:
    """Live validation evidence 最小结构。

    用于记录 inbound hook gatekeeping 的验证证据：
    - scenario: 验证场景名称
    - event_type: 事件类型
    - raw_event: 原始事件 payload
    - response: Gatekeeping 响应
    - timestamp: 时间戳
    - passed: 是否通过验证
    """
    scenario: str
    event_type: str
    raw_event: dict[str, Any]
    response: GatekeepingResponse
    timestamp: str
    passed: bool

    @classmethod
    def create(
        cls,
        scenario: str,
        event_type: str,
        raw_event: dict[str, Any],
        response: GatekeepingResponse,
        passed: bool,
    ) -> InboundHookEvidence:
        """创建 evidence 实例，自动填充 timestamp。"""
        return cls(
            scenario=scenario,
            event_type=event_type,
            raw_event=raw_event,
            response=response,
            timestamp=datetime.now(timezone.utc).isoformat(),
            passed=passed,
        )


# ─── Receiver 协议 ───


class InboundHookReceiver(Protocol):
    """Inbound hook receiver 协议。

    接收宿主发送的 hook 请求，执行治理检查，返回响应。

    具体实现：
    - OpenHarnessHookReceiver（adapters/openharness/hooks_adapter.py）
    - HermesHookReceiver（待实现）

    协议方法：
    - handle_hook_request(raw_event) → (response_body, result)
    """

    def handle_hook_request(
        self,
        raw_event: dict[str, Any],
    ) -> tuple[dict[str, Any], InboundHookResult]:
        """处理 hook 请求并返回响应。"""
        ...


# ─── Probe 协议 ───


class InboundHookProbe(Protocol):
    """Inbound hook probe 协议。

    模拟宿主发送 hook 请求，用于本地验证。

    具体实现：
    - OpenHarnessHookProbe（adapters/openharness/hooks_adapter.py）
    - HermesHookProbe（待实现）

    协议方法：
    - send_hook_event(event_type, payload) → InboundHookResult
    """

    def send_hook_event(
        self,
        event_type: str,
        payload: dict[str, Any],
    ) -> InboundHookResult:
        """发送 hook 事件并返回结果。"""
        ...


# ─── Helper Functions ───


def build_gatekeeping_response_from_gate_result(
    gate_result: Any,  # GateResult，但为避免循环依赖使用 Any
) -> GatekeepingResponse:
    """从 GateResult 构建 GatekeepingResponse。

    治理阻断策略：
    - Block 决策 → blocked=True, decision=Block, status_code=403
    - Allow 决策 → blocked=False, decision=Allow, status_code=200
    """
    is_block = gate_result.decision == "Block"
    decision = GatekeepingDecision.BLOCK if is_block else GatekeepingDecision.ALLOW

    return GatekeepingResponse(
        blocked=is_block,
        decision=decision,
        reason=gate_result.reason,
        matched_rules=gate_result.matched_rules if is_block else [],
        suggestions=gate_result.suggestions if is_block else [],
    )


def parse_inbound_hook_event_minimal(
    raw: dict[str, Any],
    event_key: str = "event",
    payload_key: str = "payload",
) -> InboundHookEvent:
    """解析 inbound hook 事件的最小公共部分。

    大多数 runtime 使用 {event, payload} 格式，
    但具体 key 名称可由参数指定。

    OpenHarness: {"event": ..., "payload": ...}
    Hermes: 预期类似格式（待验证）
    """
    event_type = raw.get(event_key, "unknown")
    payload = raw.get(payload_key, {})
    return InboundHookEvent(event_type=event_type, payload=payload)
