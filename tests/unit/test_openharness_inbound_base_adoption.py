"""测试 OpenHarness inbound base adoption。

M16 — OpenHarness Inbound Base Adoption
验证 OpenHarness 真正代码级复用公共基座：
- OpenHarnessHookResult = InboundHookResult（直接复用）
- Receiver/Probe 符合 InboundHookReceiver/InboundHookProbe Protocol
- helper 函数正确桥接公共基座
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from stores.protocols import GateResult  # noqa: E402


class TestOpenHarnessHookResultIsInboundHookResult:
    """验证 OpenHarnessHookResult 直接复用 InboundHookResult。"""

    def test_openharness_hook_result_is_inbound_hook_result(self):
        """OpenHarnessHookResult 应是 InboundHookResult 的别名。"""
        from adapters.openharness.hooks_adapter import OpenHarnessHookResult
        from adapters.inbound_hook_protocols import InboundHookResult

        # 验证 OpenHarnessHookResult 就是 InboundHookResult
        assert OpenHarnessHookResult is InboundHookResult

    def test_create_result_with_inbound_hook_result(self):
        """使用 InboundHookResult 创建结果，OpenHarness 兼容。"""
        from adapters.inbound_hook_protocols import InboundHookResult
        from adapters.openharness.hooks_adapter import OpenHarnessHookResult

        result = InboundHookResult(
            success=True,
            blocked=False,
            status_code=200,
            event_type="pre_tool_use",
        )

        # 验证类型一致
        assert isinstance(result, OpenHarnessHookResult)
        assert result.success is True


class TestOpenHarnessReceiverConformsToProtocol:
    """验证 OpenHarnessHookReceiver 符合 InboundHookReceiver Protocol。"""

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
        from adapters.openharness.hooks_adapter import OpenHarnessHookReceiver

        receiver = OpenHarnessHookReceiver(governance_check=self._dummy_check)

        # 验证方法存在
        assert hasattr(receiver, "handle_hook_request")

        # 验证 duck typing 符合 Protocol
        # Python Protocol 通过结构匹配，不需要显式继承
        assert callable(receiver.handle_hook_request)

    def test_receiver_returns_inbound_hook_result(self):
        """Receiver 返回 InboundHookResult（而非独立类型）。"""
        from adapters.openharness.hooks_adapter import OpenHarnessHookReceiver
        from adapters.inbound_hook_protocols import InboundHookResult

        receiver = OpenHarnessHookReceiver(governance_check=self._dummy_check)
        response_body, result = receiver.handle_hook_request({
            "event": "pre_tool_use",
            "payload": {"tool_name": "Read"},
        })

        # 验证返回类型
        assert isinstance(result, InboundHookResult)
        assert result.success is True
        assert result.blocked is False

    def test_receiver_log_type_is_correct(self):
        """Receiver log 使用 InboundHookResult。"""
        from adapters.openharness.hooks_adapter import OpenHarnessHookReceiver
        from adapters.inbound_hook_protocols import InboundHookResult

        receiver = OpenHarnessHookReceiver(governance_check=self._dummy_check)
        receiver.handle_hook_request({
            "event": "pre_tool_use",
            "payload": {"tool_name": "Read"},
        })

        log = receiver.log
        assert len(log) == 1

        raw, result = log[0]
        assert isinstance(result, InboundHookResult)


class TestOpenHarnessProbeConformsToProtocol:
    """验证 OpenHarnessHookProbe 符合 InboundHookProbe Protocol。"""

    def test_probe_has_send_hook_event_method(self):
        """Probe 必须有 send_hook_event 方法。"""
        from adapters.openharness.hooks_adapter import OpenHarnessHookProbe

        probe = OpenHarnessHookProbe(target_url="http://127.0.0.1:9999/governance")

        # 验证方法存在
        assert hasattr(probe, "send_hook_event")

        # 验证 duck typing 符合 Protocol
        assert callable(probe.send_hook_event)

    def test_probe_returns_inbound_hook_result(self):
        """Probe 返回 InboundHookResult（而非独立类型）。"""
        from adapters.openharness.hooks_adapter import OpenHarnessHookProbe
        from adapters.inbound_hook_protocols import InboundHookResult

        # 使用不存在的端点，测试失败场景
        probe = OpenHarnessHookProbe(
            target_url="http://127.0.0.1:19999/governance",
            timeout_ms=1000,
        )
        result = probe.send_hook_event("pre_tool_use", {"tool_name": "Read"})

        # 验证返回类型
        assert isinstance(result, InboundHookResult)
        assert result.success is False  # 连接失败

    def test_probe_log_type_is_correct(self):
        """Probe log 使用 InboundHookResult。"""
        from adapters.openharness.hooks_adapter import OpenHarnessHookProbe
        from adapters.inbound_hook_protocols import InboundHookResult

        probe = OpenHarnessHookProbe(
            target_url="http://127.0.0.1:19999/governance",
            timeout_ms=1000,
        )
        probe.send_hook_event("pre_tool_use", {"tool_name": "Read"})

        log = probe.log
        assert len(log) == 1

        raw, result = log[0]
        assert isinstance(result, InboundHookResult)


class TestBuildOpenharnessHookResponseUsesBase:
    """验证 build_openharness_hook_response 桥接公共基座。"""

    def test_allow_response_uses_base_helper(self):
        """Allow 响应使用公共基座构建。"""
        from adapters.openharness.hooks_adapter import build_openharness_hook_response
        from adapters.inbound_hook_protocols import InboundHookResult

        gate_result = GateResult(
            decision="Allow",
            reason="ok",
            matched_rules=[],
            evidence_ids=[],
            suggestions=[],
        )
        response_body, result = build_openharness_hook_response(gate_result)

        # 验证返回类型
        assert isinstance(result, InboundHookResult)
        assert result.success is True
        assert result.blocked is False
        assert result.status_code == 200
        assert response_body["blocked"] is False

    def test_block_response_uses_base_helper(self):
        """Block 响应使用公共基座构建。"""
        from adapters.openharness.hooks_adapter import build_openharness_hook_response
        from adapters.inbound_hook_protocols import InboundHookResult

        gate_result = GateResult(
            decision="Block",
            reason="dangerous",
            matched_rules=["rule-1"],
            evidence_ids=[],
            suggestions=["use alternative"],
        )
        response_body, result = build_openharness_hook_response(gate_result)

        # 验证返回类型
        assert isinstance(result, InboundHookResult)
        assert result.success is False
        assert result.blocked is True
        assert result.status_code == 403
        assert response_body["blocked"] is True
        assert response_body["matched_rules"] == ["rule-1"]


class TestParseOpenharnessHookPayloadUsesBase:
    """验证 parse_openharness_hook_payload 桥接公共基座。"""

    def test_parse_uses_base_helper(self):
        """解析函数使用公共基座。"""
        from adapters.openharness.hooks_adapter import parse_openharness_hook_payload

        raw = {
            "event": "pre_tool_use",
            "payload": {"tool_name": "Write"},
        }
        event_type, payload = parse_openharness_hook_payload(raw)

        # 验证解析结果
        assert event_type == "pre_tool_use"
        assert payload["tool_name"] == "Write"

    def test_parse_with_unknown_event(self):
        """未知 event 返回 unknown。"""
        from adapters.openharness.hooks_adapter import parse_openharness_hook_payload

        raw = {"payload": {"tool_name": "Read"}}
        event_type, payload = parse_openharness_hook_payload(raw)

        assert event_type == "unknown"
        assert payload["tool_name"] == "Read"


class TestExistingTestsStillPass:
    """验证现有 OpenHarness hooks 测试仍通过（兼容性）。"""

    def test_existing_parse_test_compatible(self):
        """现有 parse 测试兼容。"""
        from adapters.openharness.hooks_adapter import parse_openharness_hook_payload

        # 来自 test_openharness_hooks_adapter.py
        event_type, payload = parse_openharness_hook_payload({
            "event": "pre_tool_use",
            "payload": {"tool_name": "Write"},
        })
        assert event_type == "pre_tool_use"
        assert payload["tool_name"] == "Write"

    def test_existing_build_test_compatible(self):
        """现有 build 测试兼容。"""
        from adapters.openharness.hooks_adapter import build_openharness_hook_response

        # 来自 test_openharness_hooks_adapter.py
        gate = GateResult(
            decision="Block",
            reason="违规操作",
            matched_rules=["rule-1"],
            evidence_ids=[],
            suggestions=[],
        )
        response_body, result = build_openharness_hook_response(gate)

        assert result.blocked is True
        assert result.success is False
        assert result.status_code == 403
        assert response_body["blocked"] is True
        assert response_body["reason"] == "违规操作"
        assert response_body["matched_rules"] == ["rule-1"]

    def test_existing_receiver_test_compatible(self):
        """现有 receiver 测试兼容。"""
        from adapters.openharness.hooks_adapter import OpenHarnessHookReceiver

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

        assert result.blocked is False
        assert result.success is True
        assert len(receiver.log) == 1
