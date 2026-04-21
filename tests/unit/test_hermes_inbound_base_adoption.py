"""测试 Hermes inbound base adoption。

M17 — Hermes First Executable Path on Inbound Base
验证 Hermes 真正代码级复用公共基座：
- HermesHookResult = InboundHookResult（直接复用）
- Receiver/Probe 符合 InboundHookReceiver/InboundHookProbe Protocol
- helper 函数正确桥接公共基座
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from stores.protocols import GateResult  # noqa: E402


class TestHermesHookResultIsInboundHookResult:
    """验证 HermesHookResult 直接复用 InboundHookResult。"""

    def test_hermes_hook_result_is_inbound_hook_result(self):
        """HermesHookResult 应是 InboundHookResult 的别名。"""
        from adapters.hermes.hooks_adapter import HermesHookResult
        from adapters.inbound_hook_protocols import InboundHookResult

        assert HermesHookResult is InboundHookResult

    def test_create_result_with_inbound_hook_result(self):
        """使用 InboundHookResult 创建结果，Hermes 兼容。"""
        from adapters.inbound_hook_protocols import InboundHookResult
        from adapters.hermes.hooks_adapter import HermesHookResult

        result = InboundHookResult(
            success=True,
            blocked=False,
            status_code=200,
            event_type="agent:step",
        )

        assert isinstance(result, HermesHookResult)
        assert result.success is True


class TestHermesReceiverConformsToProtocol:
    """验证 HermesHookReceiver 符合 InboundHookReceiver Protocol。"""

    def _dummy_check(self, event_type: str, payload: dict) -> GateResult:
        return GateResult(
            decision="Allow",
            reason="test",
            matched_rules=[],
            evidence_ids=[],
            suggestions=[],
        )

    def test_receiver_has_handle_hook_request_method(self):
        """Receiver 必须有 handle_hook_request 方法。"""
        from adapters.hermes.hooks_adapter import HermesHookReceiver

        receiver = HermesHookReceiver(governance_check=self._dummy_check)

        assert hasattr(receiver, "handle_hook_request")
        assert callable(receiver.handle_hook_request)

    def test_receiver_returns_inbound_hook_result(self):
        """Receiver 返回 InboundHookResult。"""
        from adapters.hermes.hooks_adapter import HermesHookReceiver
        from adapters.inbound_hook_protocols import InboundHookResult

        receiver = HermesHookReceiver(governance_check=self._dummy_check)
        response_body, result = receiver.handle_hook_request({
            "event": "agent:step",
            "payload": {"tool_name": "Read"},
        })

        assert isinstance(result, InboundHookResult)
        assert result.success is True
        assert result.blocked is False

    def test_receiver_log_type_is_correct(self):
        """Receiver log 使用 InboundHookResult。"""
        from adapters.hermes.hooks_adapter import HermesHookReceiver
        from adapters.inbound_hook_protocols import InboundHookResult

        receiver = HermesHookReceiver(governance_check=self._dummy_check)
        receiver.handle_hook_request({
            "event": "agent:step",
            "payload": {"tool_name": "Read"},
        })

        log = receiver.log
        assert len(log) == 1

        raw, result = log[0]
        assert isinstance(result, InboundHookResult)


class TestHermesProbeConformsToProtocol:
    """验证 HermesHookProbe 符合 InboundHookProbe Protocol。"""

    def test_probe_has_send_hook_event_method(self):
        """Probe 必须有 send_hook_event 方法。"""
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
        assert result.success is False

    def test_probe_log_type_is_correct(self):
        """Probe log 使用 InboundHookResult。"""
        from adapters.hermes.hooks_adapter import HermesHookProbe
        from adapters.inbound_hook_protocols import InboundHookResult

        probe = HermesHookProbe(
            target_url="http://127.0.0.1:19999/governance",
            timeout_ms=1000,
        )
        probe.send_hook_event("agent:step", {"tool_name": "Read"})

        log = probe.log
        assert len(log) == 1

        raw, result = log[0]
        assert isinstance(result, InboundHookResult)


class TestBuildHermesHookResponseUsesBase:
    """验证 build_hermes_hook_response 桥接公共基座。"""

    def test_allow_response_uses_base_helper(self):
        """Allow 响应使用公共基座构建。"""
        from adapters.hermes.hooks_adapter import build_hermes_hook_response
        from adapters.inbound_hook_protocols import InboundHookResult

        gate_result = GateResult(
            decision="Allow",
            reason="ok",
            matched_rules=[],
            evidence_ids=[],
            suggestions=[],
        )
        response_body, result = build_hermes_hook_response(gate_result)

        assert isinstance(result, InboundHookResult)
        assert result.success is True
        assert result.blocked is False
        assert result.status_code == 200
        assert response_body["blocked"] is False

    def test_block_response_uses_base_helper(self):
        """Block 响应使用公共基座构建。"""
        from adapters.hermes.hooks_adapter import build_hermes_hook_response
        from adapters.inbound_hook_protocols import InboundHookResult

        gate_result = GateResult(
            decision="Block",
            reason="dangerous",
            matched_rules=["rule-1"],
            evidence_ids=[],
            suggestions=["use alternative"],
        )
        response_body, result = build_hermes_hook_response(gate_result)

        assert isinstance(result, InboundHookResult)
        assert result.success is False
        assert result.blocked is True
        assert result.status_code == 403
        assert response_body["blocked"] is True
        assert response_body["matched_rules"] == ["rule-1"]


class TestParseHermesHookPayloadUsesBase:
    """验证 parse_hermes_hook_payload 桥接公共基座。"""

    def test_parse_uses_base_helper(self):
        """解析函数使用公共基座。"""
        from adapters.hermes.hooks_adapter import parse_hermes_hook_payload

        raw = {
            "event": "agent:step",
            "payload": {"tool_name": "Write", "session_id": "abc"},
        }
        event_type, payload = parse_hermes_hook_payload(raw)

        assert event_type == "agent:step"
        assert payload["tool_name"] == "Write"

    def test_parse_with_unknown_event(self):
        """未知 event 返回 unknown。"""
        from adapters.hermes.hooks_adapter import parse_hermes_hook_payload

        raw = {"payload": {"tool_name": "Read"}}
        event_type, payload = parse_hermes_hook_payload(raw)

        assert event_type == "unknown"
        assert payload["tool_name"] == "Read"


class TestHermesVsOpenHarnessCompatibility:
    """验证 Hermes 和 OpenHarness 复用相同的公共基座。"""

    def test_both_use_same_inbound_hook_result(self):
        """两者都复用 InboundHookResult。"""
        from adapters.hermes.hooks_adapter import HermesHookResult
        from adapters.openharness.hooks_adapter import OpenHarnessHookResult
        from adapters.inbound_hook_protocols import InboundHookResult

        assert HermesHookResult is InboundHookResult
        assert OpenHarnessHookResult is InboundHookResult
        # Hermes 和 OpenHarness 使用完全相同的 Result 类型

    def test_both_use_same_base_helper(self):
        """两者都使用相同的 base helper。"""
        from adapters.hermes.hooks_adapter import build_hermes_hook_response
        from adapters.openharness.hooks_adapter import build_openharness_hook_response

        gate = GateResult(
            decision="Block",
            reason="test",
            matched_rules=["rule-1"],
            evidence_ids=[],
            suggestions=[],
        )

        # 两个 runtime 都使用公共基座
        hermes_body, hermes_result = build_hermes_hook_response(gate)
        openharness_body, openharness_result = build_openharness_hook_response(gate)

        # 响应结构一致
        assert hermes_result.blocked == openharness_result.blocked
        assert hermes_result.status_code == openharness_result.status_code
        assert hermes_body["blocked"] == openharness_body["blocked"]
