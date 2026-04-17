"""测试 OpenHarness hooks adapter。

M12 — OpenHarness First Executable Path
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from stores.protocols import GateResult  # noqa: E402


class TestParseOpenharnessHookPayload:
    """测试 parse_openharness_hook_payload。"""

    def test_parse_valid_payload(self):
        from adapters.openharness.hooks_adapter import parse_openharness_hook_payload

        event_type, payload = parse_openharness_hook_payload({
            "event": "pre_tool_use",
            "payload": {"tool_name": "Write"},
        })
        assert event_type == "pre_tool_use"
        assert payload["tool_name"] == "Write"

    def test_parse_empty_payload(self):
        from adapters.openharness.hooks_adapter import parse_openharness_hook_payload

        event_type, payload = parse_openharness_hook_payload({})
        assert event_type == "unknown"
        assert payload == {}

    def test_parse_nested_payload(self):
        from adapters.openharness.hooks_adapter import parse_openharness_hook_payload

        event_type, payload = parse_openharness_hook_payload({
            "event": "post_tool_use",
            "payload": {"tool_name": "Read", "path": "file.txt", "result": "ok"},
        })
        assert event_type == "post_tool_use"
        assert payload["path"] == "file.txt"


class TestBuildOpenharnessHookResponse:
    """测试 build_openharness_hook_response。"""

    def test_block_response(self):
        from adapters.openharness.hooks_adapter import build_openharness_hook_response
        from stores.protocols import GateResult

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

    def test_allow_response(self):
        from adapters.openharness.hooks_adapter import build_openharness_hook_response
        from stores.protocols import GateResult

        gate = GateResult(
            decision="Allow",
            reason="合规操作",
            matched_rules=[],
            evidence_ids=[],
            suggestions=[],
        )
        response_body, result = build_openharness_hook_response(gate)

        assert result.blocked is False
        assert result.success is True
        assert result.status_code == 200
        assert response_body["blocked"] is False
        assert response_body["reason"] == "合规操作"


class TestOpenHarnessHookResult:
    """测试 OpenHarnessHookResult。"""

    def test_result_is_frozen(self):
        from adapters.openharness.hooks_adapter import OpenHarnessHookResult

        result = OpenHarnessHookResult(success=True, blocked=False)
        with pytest.raises(Exception):
            result.success = False  # type: ignore


class TestOpenHarnessHookReceiver:
    """测试 OpenHarnessHookReceiver。"""

    def _dummy_check(self, event_type: str, payload: dict) -> GateResult:
        return GateResult(
            decision="Allow",
            reason="test",
            matched_rules=[],
            evidence_ids=[],
            suggestions=[],
        )

    def test_handle_hook_request(self):
        from adapters.openharness.hooks_adapter import OpenHarnessHookReceiver

        receiver = OpenHarnessHookReceiver(governance_check=self._dummy_check)
        response_body, result = receiver.handle_hook_request({
            "event": "pre_tool_use",
            "payload": {"tool_name": "Read"},
        })

        assert result.blocked is False
        assert result.success is True
        assert len(receiver.log) == 1

    def test_handle_block_request(self):
        from adapters.openharness.hooks_adapter import OpenHarnessHookReceiver
        from stores.protocols import GateResult

        def block_check(event_type: str, payload: dict) -> GateResult:
            return GateResult(
                decision="Block",
                reason="blocked",
                matched_rules=["rule-1"],
                evidence_ids=[],
                suggestions=[],
            )

        receiver = OpenHarnessHookReceiver(governance_check=block_check)
        response_body, result = receiver.handle_hook_request({
            "event": "pre_tool_use",
            "payload": {"tool_name": "Write"},
        })

        assert result.blocked is True
        assert result.status_code == 403
        assert response_body["blocked"] is True
