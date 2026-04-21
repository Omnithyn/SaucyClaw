"""测试共享 HTTP inbound hook 骨架。

M18 — Shared Inbound HTTP Hook Adapter Base
验证 InboundHttpHookProbeBase 和 InboundHttpHookReceiverBase 的共享实现。
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from stores.protocols import GateResult  # noqa: E402
from adapters.inbound_hook_protocols import InboundHookResult  # noqa: E402


class TestInboundHttpHookProbeBase:
    """测试共享 Probe 骨架。"""

    def test_probe_has_send_hook_event_method(self):
        """共享骨架有 send_hook_event 方法。"""
        from adapters.inbound_http_hook_base import InboundHttpHookProbeBase

        probe = InboundHttpHookProbeBase(target_url="http://127.0.0.1:9999/governance")
        assert hasattr(probe, "send_hook_event")
        assert callable(probe.send_hook_event)

    def test_probe_has_build_hook_payload_method(self):
        """共享骨架有 build_hook_payload 方法。"""
        from adapters.inbound_http_hook_base import InboundHttpHookProbeBase

        probe = InboundHttpHookProbeBase(target_url="http://127.0.0.1:9999/governance")
        assert hasattr(probe, "build_hook_payload")
        assert callable(probe.build_hook_payload)

    def test_default_build_hook_payload_format(self):
        """默认 build_hook_payload 格式正确。"""
        from adapters.inbound_http_hook_base import InboundHttpHookProbeBase

        probe = InboundHttpHookProbeBase(target_url="http://127.0.0.1:9999/governance")
        payload = probe.build_hook_payload("pre_tool_use", {"tool_name": "Write"})

        assert payload["event"] == "pre_tool_use"
        assert payload["payload"]["tool_name"] == "Write"

    def test_probe_has_log_property(self):
        """共享骨架有 log property。"""
        from adapters.inbound_http_hook_base import InboundHttpHookProbeBase

        probe = InboundHttpHookProbeBase(target_url="http://127.0.0.1:9999/governance")
        assert hasattr(probe, "log")
        assert probe.log == []

    def test_probe_returns_inbound_hook_result(self):
        """Probe 返回 InboundHookResult。"""
        from adapters.inbound_http_hook_base import InboundHttpHookProbeBase
        from adapters.inbound_hook_protocols import InboundHookResult

        probe = InboundHttpHookProbeBase(
            target_url="http://127.0.0.1:19999/governance",
            timeout_ms=1000,
        )
        result = probe.send_hook_event("pre_tool_use", {"tool_name": "Read"})

        assert isinstance(result, InboundHookResult)
        assert result.success is False  # 连接失败

    def test_probe_log_records_request(self):
        """Probe log 记录请求。"""
        from adapters.inbound_http_hook_base import InboundHttpHookProbeBase
        from adapters.inbound_hook_protocols import InboundHookResult

        probe = InboundHttpHookProbeBase(
            target_url="http://127.0.0.1:19999/governance",
            timeout_ms=1000,
        )
        probe.send_hook_event("pre_tool_use", {"tool_name": "Read"})

        log = probe.log
        assert len(log) == 1

        hook_payload, result = log[0]
        assert isinstance(result, InboundHookResult)
        assert hook_payload["event"] == "pre_tool_use"


class TestInboundHttpHookReceiverBase:
    """测试共享 Receiver 骨架。"""

    def _dummy_check(self, event_type: str, payload: dict) -> GateResult:
        return GateResult(
            decision="Allow",
            reason="test",
            matched_rules=[],
            evidence_ids=[],
            suggestions=[],
        )

    def _dummy_parse(self, raw: dict) -> tuple[str, dict]:
        return raw.get("event", "unknown"), raw.get("payload", {})

    def _dummy_build(self, gate_result: GateResult) -> tuple[dict, InboundHookResult]:
        response_body = {"blocked": False, "reason": gate_result.reason}
        result = InboundHookResult(
            success=True,
            blocked=False,
            status_code=200,
        )
        return response_body, result

    def test_receiver_has_handle_hook_request_method(self):
        """共享骨架有 handle_hook_request 方法。"""
        from adapters.inbound_http_hook_base import InboundHttpHookReceiverBase

        receiver = InboundHttpHookReceiverBase(
            governance_check=self._dummy_check,
            parse_hook_payload=self._dummy_parse,
            build_hook_response=self._dummy_build,
        )

        assert hasattr(receiver, "handle_hook_request")
        assert callable(receiver.handle_hook_request)

    def test_receiver_has_log_property(self):
        """共享骨架有 log property。"""
        from adapters.inbound_http_hook_base import InboundHttpHookReceiverBase

        receiver = InboundHttpHookReceiverBase(
            governance_check=self._dummy_check,
            parse_hook_payload=self._dummy_parse,
            build_hook_response=self._dummy_build,
        )

        assert hasattr(receiver, "log")
        assert receiver.log == []

    def test_receiver_returns_tuple(self):
        """Receiver 返回 (dict, InboundHookResult) tuple。"""
        from adapters.inbound_http_hook_base import InboundHttpHookReceiverBase
        from adapters.inbound_hook_protocols import InboundHookResult

        receiver = InboundHttpHookReceiverBase(
            governance_check=self._dummy_check,
            parse_hook_payload=self._dummy_parse,
            build_hook_response=self._dummy_build,
        )

        response_body, result = receiver.handle_hook_request({
            "event": "pre_tool_use",
            "payload": {"tool_name": "Read"},
        })

        assert isinstance(response_body, dict)
        assert isinstance(result, InboundHookResult)
        assert result.success is True

    def test_receiver_log_records_request(self):
        """Receiver log 记录请求。"""
        from adapters.inbound_http_hook_base import InboundHttpHookReceiverBase
        from adapters.inbound_hook_protocols import InboundHookResult

        receiver = InboundHttpHookReceiverBase(
            governance_check=self._dummy_check,
            parse_hook_payload=self._dummy_parse,
            build_hook_response=self._dummy_build,
        )

        receiver.handle_hook_request({
            "event": "pre_tool_use",
            "payload": {"tool_name": "Read"},
        })

        log = receiver.log
        assert len(log) == 1

        raw_payload, result = log[0]
        assert isinstance(result, InboundHookResult)
        assert raw_payload["event"] == "pre_tool_use"


class TestSharedSkeletonInheritance:
    """测试 OpenHarness/Hermes 继承共享骨架。"""

    def test_openharness_probe_inherits_shared_skeleton(self):
        """OpenHarnessHookProbe 继承共享骨架。"""
        from adapters.openharness.hooks_adapter import OpenHarnessHookProbe
        from adapters.inbound_http_hook_base import InboundHttpHookProbeBase

        probe = OpenHarnessHookProbe(target_url="http://127.0.0.1:9999/governance")

        assert isinstance(probe, InboundHttpHookProbeBase)
        assert hasattr(probe, "send_hook_event")
        assert hasattr(probe, "log")

    def test_hermes_probe_inherits_shared_skeleton(self):
        """HermesHookProbe 继承共享骨架。"""
        from adapters.hermes.hooks_adapter import HermesHookProbe
        from adapters.inbound_http_hook_base import InboundHttpHookProbeBase

        probe = HermesHookProbe(target_url="http://127.0.0.1:9999/governance")

        assert isinstance(probe, InboundHttpHookProbeBase)
        assert hasattr(probe, "send_hook_event")
        assert hasattr(probe, "log")

    def test_openharness_receiver_inherits_shared_skeleton(self):
        """OpenHarnessHookReceiver 继承共享骨架。"""
        from adapters.openharness.hooks_adapter import OpenHarnessHookReceiver
        from adapters.inbound_http_hook_base import InboundHttpHookReceiverBase

        def dummy_check(event_type: str, payload: dict) -> GateResult:
            return GateResult(
                decision="Allow",
                reason="test",
                matched_rules=[],
                evidence_ids=[],
                suggestions=[],
            )

        receiver = OpenHarnessHookReceiver(governance_check=dummy_check)

        assert isinstance(receiver, InboundHttpHookReceiverBase)
        assert hasattr(receiver, "handle_hook_request")
        assert hasattr(receiver, "log")

    def test_hermes_receiver_inherits_shared_skeleton(self):
        """HermesHookReceiver 继承共享骨架。"""
        from adapters.hermes.hooks_adapter import HermesHookReceiver
        from adapters.inbound_http_hook_base import InboundHttpHookReceiverBase

        def dummy_check(event_type: str, payload: dict) -> GateResult:
            return GateResult(
                decision="Allow",
                reason="test",
                matched_rules=[],
                evidence_ids=[],
                suggestions=[],
            )

        receiver = HermesHookReceiver(governance_check=dummy_check)

        assert isinstance(receiver, InboundHttpHookReceiverBase)
        assert hasattr(receiver, "handle_hook_request")
        assert hasattr(receiver, "log")


class TestSharedSkeletonBehavior:
    """测试共享骨架行为正确。"""

    def test_openharness_probe_using_shared_send(self):
        """OpenHarness Probe 使用共享 send_hook_event。"""
        from adapters.openharness.hooks_adapter import OpenHarnessHookProbe
        from adapters.inbound_hook_protocols import InboundHookResult

        probe = OpenHarnessHookProbe(
            target_url="http://127.0.0.1:19999/governance",
            timeout_ms=1000,
        )
        result = probe.send_hook_event("pre_tool_use", {"tool_name": "Read"})

        # 验证使用共享骨架的 send_hook_event
        assert isinstance(result, InboundHookResult)
        assert result.success is False  # 连接失败
        assert probe.log[0][0]["event"] == "pre_tool_use"

    def test_hermes_probe_using_shared_send(self):
        """Hermes Probe 使用共享 send_hook_event。"""
        from adapters.hermes.hooks_adapter import HermesHookProbe
        from adapters.inbound_hook_protocols import InboundHookResult

        probe = HermesHookProbe(
            target_url="http://127.0.0.1:19999/governance",
            timeout_ms=1000,
        )
        result = probe.send_hook_event("agent:step", {"tool_name": "Read"})

        # 验证使用共享骨架的 send_hook_event
        assert isinstance(result, InboundHookResult)
        assert result.success is False
        assert probe.log[0][0]["event"] == "agent:step"

    def test_openharness_receiver_using_shared_template(self):
        """OpenHarness Receiver 使用共享模板方法。"""
        from adapters.openharness.hooks_adapter import OpenHarnessHookReceiver
        from adapters.inbound_hook_protocols import InboundHookResult

        def dummy_check(event_type: str, payload: dict) -> GateResult:
            return GateResult(
                decision="Allow",
                reason="test",
                matched_rules=[],
                evidence_ids=[],
                suggestions=[],
            )

        receiver = OpenHarnessHookReceiver(governance_check=dummy_check)
        response_body, result = receiver.handle_hook_request({
            "event": "pre_tool_use",
            "payload": {"tool_name": "Read"},
        })

        # 验证使用共享骨架的模板方法
        assert isinstance(result, InboundHookResult)
        assert receiver.log[0][0]["event"] == "pre_tool_use"

    def test_hermes_receiver_using_shared_template(self):
        """Hermes Receiver 使用共享模板方法。"""
        from adapters.hermes.hooks_adapter import HermesHookReceiver
        from adapters.inbound_hook_protocols import InboundHookResult

        def dummy_check(event_type: str, payload: dict) -> GateResult:
            return GateResult(
                decision="Allow",
                reason="test",
                matched_rules=[],
                evidence_ids=[],
                suggestions=[],
            )

        receiver = HermesHookReceiver(governance_check=dummy_check)
        response_body, result = receiver.handle_hook_request({
            "event": "agent:step",
            "payload": {"tool_name": "Read"},
        })

        # 验证使用共享骨架的模板方法
        assert isinstance(result, InboundHookResult)
        assert receiver.log[0][0]["event"] == "agent:step"
