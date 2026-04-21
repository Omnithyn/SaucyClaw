"""测试 Hermes hooks adapter。

M17 — Hermes First Executable Path on Inbound Base
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from stores.protocols import GateResult  # noqa: E402


class TestParseHermesHookPayload:
    """测试 parse_hermes_hook_payload。"""

    def test_parse_valid_payload(self):
        """解析 Hermes payload。"""
        from adapters.hermes.hooks_adapter import parse_hermes_hook_payload

        event_type, payload = parse_hermes_hook_payload({
            "event": "agent:step",
            "payload": {"tool_name": "Write", "session_id": "abc123"},
        })
        assert event_type == "agent:step"
        assert payload["tool_name"] == "Write"
        assert payload["session_id"] == "abc123"

    def test_parse_empty_payload(self):
        """空 payload 返回 unknown。"""
        from adapters.hermes.hooks_adapter import parse_hermes_hook_payload

        event_type, payload = parse_hermes_hook_payload({})
        assert event_type == "unknown"
        assert payload == {}

    def test_parse_nested_payload(self):
        """解析嵌套 payload。"""
        from adapters.hermes.hooks_adapter import parse_hermes_hook_payload

        event_type, payload = parse_hermes_hook_payload({
            "event": "agent:step",
            "payload": {"tool_name": "Bash", "tool_input": {"command": "ls"}, "session_id": "xyz"},
        })
        assert event_type == "agent:step"
        assert payload["tool_input"]["command"] == "ls"


class TestBuildHermesHookResponse:
    """测试 build_hermes_hook_response。"""

    def test_block_response(self):
        """Block 响应。"""
        from adapters.hermes.hooks_adapter import build_hermes_hook_response

        gate = GateResult(
            decision="Block",
            reason="违规操作",
            matched_rules=["rule-1"],
            evidence_ids=[],
            suggestions=[],
        )
        response_body, result = build_hermes_hook_response(gate)

        assert result.blocked is True
        assert result.success is False
        assert result.status_code == 403
        assert response_body["blocked"] is True
        assert response_body["reason"] == "违规操作"
        assert response_body["matched_rules"] == ["rule-1"]

    def test_allow_response(self):
        """Allow 响应。"""
        from adapters.hermes.hooks_adapter import build_hermes_hook_response

        gate = GateResult(
            decision="Allow",
            reason="合规操作",
            matched_rules=[],
            evidence_ids=[],
            suggestions=[],
        )
        response_body, result = build_hermes_hook_response(gate)

        assert result.blocked is False
        assert result.success is True
        assert result.status_code == 200
        assert response_body["blocked"] is False
        assert response_body["reason"] == "合规操作"


class TestHermesHookResult:
    """测试 HermesHookResult。"""

    def test_result_is_inbound_hook_result(self):
        """HermesHookResult 应是 InboundHookResult 的别名。"""
        from adapters.hermes.hooks_adapter import HermesHookResult
        from adapters.inbound_hook_protocols import InboundHookResult

        assert HermesHookResult is InboundHookResult

    def test_result_is_frozen(self):
        """Result 是 frozen 的。"""
        from adapters.hermes.hooks_adapter import HermesHookResult

        result = HermesHookResult(success=True, blocked=False)
        with pytest.raises(Exception):
            result.success = False  # type: ignore


class TestHermesHookReceiver:
    """测试 HermesHookReceiver。"""

    def _dummy_check(self, event_type: str, payload: dict) -> GateResult:
        return GateResult(
            decision="Allow",
            reason="test",
            matched_rules=[],
            evidence_ids=[],
            suggestions=[],
        )

    def test_handle_hook_request(self):
        """处理 hook 请求。"""
        from adapters.hermes.hooks_adapter import HermesHookReceiver

        receiver = HermesHookReceiver(governance_check=self._dummy_check)
        response_body, result = receiver.handle_hook_request({
            "event": "agent:step",
            "payload": {"tool_name": "Read"},
        })

        assert result.blocked is False
        assert result.success is True
        assert len(receiver.log) == 1

    def test_handle_block_request(self):
        """处理 Block 请求。"""
        from adapters.hermes.hooks_adapter import HermesHookReceiver

        def block_check(event_type: str, payload: dict) -> GateResult:
            return GateResult(
                decision="Block",
                reason="blocked",
                matched_rules=["rule-1"],
                evidence_ids=[],
                suggestions=[],
            )

        receiver = HermesHookReceiver(governance_check=block_check)
        response_body, result = receiver.handle_hook_request({
            "event": "agent:step",
            "payload": {"tool_name": "Write"},
        })

        assert result.blocked is True
        assert result.status_code == 403
        assert response_body["blocked"] is True


class TestHermesHookProbe:
    """测试 HermesHookProbe。"""

    def test_probe_has_send_hook_event_method(self):
        """Probe 有 send_hook_event 方法。"""
        from adapters.hermes.hooks_adapter import HermesHookProbe

        probe = HermesHookProbe(target_url="http://127.0.0.1:9999/governance")
        assert hasattr(probe, "send_hook_event")
        assert callable(probe.send_hook_event)

    def test_probe_returns_inbound_hook_result(self):
        """Probe 返回 InboundHookResult。"""
        from adapters.hermes.hooks_adapter import HermesHookProbe
        from adapters.inbound_hook_protocols import InboundHookResult

        probe = HermesHookProbe(
            target_url="http://127.0.0.1:19999/governance",
            timeout_ms=1000,
        )
        result = probe.send_hook_event("agent:step", {"tool_name": "Read"})

        assert isinstance(result, InboundHookResult)
        assert result.success is False  # 连接失败
