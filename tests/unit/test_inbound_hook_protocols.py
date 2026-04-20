"""测试 inbound hook gatekeeping 公共基座。

M15 — Inbound Hook Gatekeeping Base Package
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestGatekeepingDecision:
    """测试 GatekeepingDecision 枚举。"""

    def test_allow_exists(self):
        from adapters.inbound_hook_protocols import GatekeepingDecision
        assert GatekeepingDecision.ALLOW.value == "Allow"

    def test_block_exists(self):
        from adapters.inbound_hook_protocols import GatekeepingDecision
        assert GatekeepingDecision.BLOCK.value == "Block"


class TestInboundHookEvent:
    """测试 InboundHookEvent 结构。"""

    def test_event_structure(self):
        from adapters.inbound_hook_protocols import InboundHookEvent

        event = InboundHookEvent(
            event_type="pre_tool_use",
            payload={"tool_name": "Write"},
        )
        assert event.event_type == "pre_tool_use"
        assert event.payload["tool_name"] == "Write"

    def test_event_is_frozen(self):
        from adapters.inbound_hook_protocols import InboundHookEvent

        event = InboundHookEvent(event_type="test", payload={})
        with pytest.raises(Exception):
            event.event_type = "changed"  # type: ignore


class TestGatekeepingResponse:
    """测试 GatekeepingResponse 结构。"""

    def test_allow_response(self):
        from adapters.inbound_hook_protocols import GatekeepingResponse, GatekeepingDecision

        response = GatekeepingResponse(
            blocked=False,
            decision=GatekeepingDecision.ALLOW,
            reason="ok",
        )
        assert response.blocked is False
        assert response.status_code == 200
        assert response.success is True

    def test_block_response(self):
        from adapters.inbound_hook_protocols import GatekeepingResponse, GatekeepingDecision

        response = GatekeepingResponse(
            blocked=True,
            decision=GatekeepingDecision.BLOCK,
            reason="dangerous",
            matched_rules=["rule-1"],
        )
        assert response.blocked is True
        assert response.status_code == 403
        assert response.success is False

    def test_response_is_frozen(self):
        from adapters.inbound_hook_protocols import GatekeepingResponse, GatekeepingDecision

        response = GatekeepingResponse(
            blocked=False,
            decision=GatekeepingDecision.ALLOW,
        )
        with pytest.raises(Exception):
            response.blocked = True  # type: ignore


class TestInboundHookResult:
    """测试 InboundHookResult 结构。"""

    def test_success_result(self):
        from adapters.inbound_hook_protocols import InboundHookResult

        result = InboundHookResult(
            success=True,
            blocked=False,
            status_code=200,
            event_type="pre_tool_use",
        )
        assert result.success is True
        assert result.blocked is False

    def test_failure_result(self):
        from adapters.inbound_hook_protocols import InboundHookResult

        result = InboundHookResult(
            success=False,
            blocked=True,
            error="HTTP 403",
            status_code=403,
        )
        assert result.success is False
        assert result.error == "HTTP 403"


class TestInboundHookEvidence:
    """测试 InboundHookEvidence 结构。"""

    def test_evidence_structure(self):
        from adapters.inbound_hook_protocols import InboundHookEvidence, GatekeepingResponse, GatekeepingDecision

        response = GatekeepingResponse(
            blocked=False,
            decision=GatekeepingDecision.ALLOW,
        )
        evidence = InboundHookEvidence(
            scenario="test",
            event_type="pre_tool_use",
            raw_event={"tool_name": "Read"},
            response=response,
            timestamp="2026-04-20T00:00:00Z",
            passed=True,
        )
        assert evidence.scenario == "test"
        assert evidence.passed is True

    def test_evidence_factory(self):
        from adapters.inbound_hook_protocols import InboundHookEvidence, GatekeepingResponse, GatekeepingDecision

        response = GatekeepingResponse(
            blocked=True,
            decision=GatekeepingDecision.BLOCK,
        )
        evidence = InboundHookEvidence.create(
            scenario="block_test",
            event_type="pre_tool_use",
            raw_event={"tool_name": "Bash"},
            response=response,
            passed=False,
        )
        assert evidence.scenario == "block_test"
        assert evidence.timestamp  # 自动填充


class TestHelperFunctions:
    """测试 helper functions。"""

    def test_build_gatekeeping_response_from_gate_result_allow(self):
        from adapters.inbound_hook_protocols import (
            build_gatekeeping_response_from_gate_result,
            GatekeepingDecision,
        )
        from stores.protocols import GateResult

        gate_result = GateResult(
            decision="Allow",
            reason="ok",
            matched_rules=[],
            evidence_ids=[],
            suggestions=[],
        )
        response = build_gatekeeping_response_from_gate_result(gate_result)
        assert response.blocked is False
        assert response.decision == GatekeepingDecision.ALLOW
        assert response.status_code == 200

    def test_build_gatekeeping_response_from_gate_result_block(self):
        from adapters.inbound_hook_protocols import (
            build_gatekeeping_response_from_gate_result,
            GatekeepingDecision,
        )
        from stores.protocols import GateResult

        gate_result = GateResult(
            decision="Block",
            reason="dangerous",
            matched_rules=["rule-1"],
            evidence_ids=[],
            suggestions=["use alternative"],
        )
        response = build_gatekeeping_response_from_gate_result(gate_result)
        assert response.blocked is True
        assert response.decision == GatekeepingDecision.BLOCK
        assert response.status_code == 403
        assert response.matched_rules == ["rule-1"]

    def test_parse_inbound_hook_event_minimal(self):
        from adapters.inbound_hook_protocols import parse_inbound_hook_event_minimal

        raw = {"event": "pre_tool_use", "payload": {"tool_name": "Write"}}
        event = parse_inbound_hook_event_minimal(raw)
        assert event.event_type == "pre_tool_use"
        assert event.payload["tool_name"] == "Write"


class TestOpenHarnessUsesInboundBase:
    """M15: 验证 OpenHarness 使用 inbound base。"""

    def test_openharness_profile_mentions_inbound_base(self):
        """OpenHarness profile docstring 说明已复用 inbound base。"""
        from adapters.openharness.profile import OpenHarnessProfile

        # 检查 docstring 中包含 M15 说明
        assert "M15" in OpenHarnessProfile.__doc__
        assert "inbound_hook_gatekeeping" in OpenHarnessProfile.__doc__

    def test_hermes_profile_mentions_expected_reuse(self):
        """Hermes profile docstring 说明预期复用 inbound base。"""
        from adapters.hermes.profile import HermesProfile

        # 检查 docstring 中包含 M15 说明
        assert "M15" in HermesProfile.__doc__
        assert "预期复用" in HermesProfile.__doc__


class TestProtocolDefinitions:
    """测试协议定义存在。"""

    def test_inbound_hook_receiver_protocol_exists(self):
        from adapters.inbound_hook_protocols import InboundHookReceiver
        # Protocol 只检查签名，不实例化
        assert InboundHookReceiver is not None

    def test_inbound_hook_probe_protocol_exists(self):
        from adapters.inbound_hook_protocols import InboundHookProbe
        assert InboundHookProbe is not None
