"""OpenClaw 宿主适配器（Phase 0-1 mock 实现）。

模拟 OpenClaw 宿主行为，用于端到端验证治理引擎流程。
Phase 0-1 不依赖真实 OpenClaw 运行时。
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from stores.protocols import (
    GateResult,
    HostAdapter,
    NormalizedEvent,
    SessionContext,
)


class OpenClawHostAdapter:
    """OpenClaw 宿主适配器 mock。

    模拟行为：
    - connect: 从 context dict 中提取 session_id 和 source
    - collect_event: 将 raw_event 包装为 NormalizedEvent
    - intercept_output: 占位，实际拦截由 GovernanceEngine 完成
    - write_back: 将 GateResult 写入内部日志
    - get_capabilities: 返回模拟能力集
    """

    def __init__(self) -> None:
        self._write_back_log: list[GateResult] = []

    def connect(self, context: dict) -> SessionContext:
        session_id = context.get("session_id", str(uuid.uuid4()))
        source = context.get("source", "openclaw-mock")
        metadata = {k: v for k, v in context.items() if k not in ("session_id", "source")}
        return SessionContext(
            session_id=session_id,
            source=source,
            metadata=metadata,
        )

    def collect_event(self, raw_event: dict) -> NormalizedEvent:
        event_type = raw_event.get("event_type") or raw_event.get("type", "unknown")
        source = raw_event.get("source", "openclaw-mock")
        session_id = raw_event.get("session_id", "")
        timestamp = raw_event.get("timestamp") or datetime.now(timezone.utc).isoformat()

        _meta_keys = {"event_type", "type", "source", "session_id", "timestamp"}
        payload = {k: v for k, v in raw_event.items() if k not in _meta_keys}
        if "payload" in raw_event:
            payload = raw_event["payload"]

        return NormalizedEvent(
            id=str(uuid.uuid4()),
            event_type=str(event_type),
            source=str(source),
            session_id=str(session_id),
            timestamp=timestamp,
            payload=payload,
        )

    def intercept_output(self, result: dict) -> GateResult:
        """Phase 0-1: 占位实现。

        实际拦截逻辑由 GovernanceEngine.process_event 完成。
        此方法仅返回一个默认的 Allow 结果。
        """
        return GateResult(
            decision="Allow",
            reason="mock: 实际拦截由 GovernanceEngine 处理",
            matched_rules=[],
            evidence_ids=[],
            suggestions=[],
        )

    def write_back(self, gate_result: GateResult) -> None:
        """记录 GateResult 到内部日志。"""
        self._write_back_log.append(gate_result)

    def get_capabilities(self) -> dict:
        return {
            "hooks": ["output_intercept", "task_assign", "review_request"],
            "supports_streaming": False,
            "supports_context_injection": True,
            "version": "mock-0.1",
        }

    @property
    def write_back_log(self) -> list[GateResult]:
        return list(self._write_back_log)
