"""OpenClaw 通知适配器单元测试。"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from stores.protocols import GateResult
from adapters.openclaw.notification_adapter import (
    OpenClawNotificationAdapter,
    WakeResult,
    _build_openclaw_payload,
)
from experiments.openclaw_poc.mock_gateway import (
    start_mock_server_in_background,
    stop_mock_server,
    clear_received,
    received_payloads,
)


MOCK_PORT = 18791


def _make_block_result() -> GateResult:
    return GateResult(
        decision="Block",
        reason="triggered rule-reviewer-must-differ",
        matched_rules=["rule-reviewer-must-differ"],
        evidence_ids=["ev-001"],
        suggestions=["reviewer should differ from assignee"],
    )


def _make_allow_result() -> GateResult:
    return GateResult(
        decision="Allow",
        reason="no rules triggered",
        matched_rules=[],
        evidence_ids=[],
        suggestions=[],
    )


class TestBuildOpenClawPayload:
    """测试 payload 构建函数。"""

    def test_block_payload_structure(self) -> None:
        result = _make_block_result()
        payload = _build_openclaw_payload(
            decision=result.decision,
            matched_rules=result.matched_rules,
            reason=result.reason,
            suggestions=result.suggestions,
        )

        assert payload["event"] == "governance-decision"
        assert payload["timestamp"] is not None
        assert "context" in payload
        assert payload["context"]["sessionId"] == ""

    def test_instruction_contains_decision(self) -> None:
        result = _make_block_result()
        payload = _build_openclaw_payload(
            decision=result.decision,
            matched_rules=result.matched_rules,
            reason=result.reason,
            suggestions=result.suggestions,
        )

        assert "[governance|Block]" in payload["instruction"]
        assert "rule-reviewer-must-differ" in payload["instruction"]

    def test_allow_instruction(self) -> None:
        result = _make_allow_result()
        payload = _build_openclaw_payload(
            decision=result.decision,
            matched_rules=result.matched_rules,
            reason=result.reason,
            suggestions=result.suggestions,
        )

        assert "[governance|Allow]" in payload["instruction"]
        assert "未触发治理规则" in payload["instruction"]

    def test_with_explanation_summary(self) -> None:
        result = _make_block_result()
        payload = _build_openclaw_payload(
            decision=result.decision,
            matched_rules=result.matched_rules,
            reason=result.reason,
            suggestions=result.suggestions,
            explanation_summary="test explanation",
        )

        assert "解释: test explanation" in payload["instruction"]

    def test_with_session_context(self) -> None:
        result = _make_block_result()
        ctx = {
            "session_id": "ses-001",
            "project_path": "/tmp/project",
            "project_name": "TestProject",
            "tmux_session": "main",
        }
        payload = _build_openclaw_payload(
            decision=result.decision,
            matched_rules=result.matched_rules,
            reason=result.reason,
            suggestions=result.suggestions,
            session_context=ctx,
        )

        assert payload["sessionId"] == "ses-001"
        assert payload["projectPath"] == "/tmp/project"
        assert payload["projectName"] == "TestProject"
        assert payload["context"]["sessionId"] == "ses-001"


class TestOpenClawNotificationAdapter:
    """测试 HTTP gateway 适配器。"""

    def setup_method(self) -> None:
        self.server, self.thread = start_mock_server_in_background(port=MOCK_PORT)

    def teardown_method(self) -> None:
        stop_mock_server(self.server)

    def test_send_block_decision(self) -> None:
        clear_received()
        adapter = OpenClawNotificationAdapter(
            gateway_url=f"http://127.0.0.1:{MOCK_PORT}",
            gateway_name="mock",
        )

        result = _make_block_result()
        wake = adapter.send_decision(result)

        assert wake.success is True
        assert wake.gateway == "mock"
        assert len(received_payloads) == 1
        assert received_payloads[0]["event"] == "governance-decision"

    def test_send_allow_decision(self) -> None:
        clear_received()
        adapter = OpenClawNotificationAdapter(
            gateway_url=f"http://127.0.0.1:{MOCK_PORT}",
            gateway_name="mock",
        )

        result = _make_allow_result()
        wake = adapter.send_decision(result)

        assert wake.success is True
        assert len(received_payloads) == 1

    def test_unreachable_gateway(self) -> None:
        adapter = OpenClawNotificationAdapter(
            gateway_url="http://127.0.0.1:19999",
            gateway_name="unreachable",
            timeout_ms=1_000,
        )

        result = _make_block_result()
        wake = adapter.send_decision(result)

        assert wake.success is False
        assert wake.error is not None

    def test_log_records_decisions(self) -> None:
        clear_received()
        adapter = OpenClawNotificationAdapter(
            gateway_url=f"http://127.0.0.1:{MOCK_PORT}",
            gateway_name="mock",
        )

        adapter.send_decision(_make_block_result())
        adapter.send_decision(_make_allow_result())

        assert len(adapter.log) == 2
        assert adapter.log[0][0].decision == "Block"
        assert adapter.log[1][0].decision == "Allow"

    def test_log_is_immutable_copy(self) -> None:
        adapter = OpenClawNotificationAdapter(
            gateway_url=f"http://127.0.0.1:{MOCK_PORT}",
            gateway_name="mock",
        )
        adapter.send_decision(_make_block_result())

        log1 = adapter.log
        log2 = adapter.log

        assert log1 is not log2


class TestWakeResult:
    """测试 WakeResult 数据结构。"""

    def test_success_result(self) -> None:
        wr = WakeResult(gateway="test", success=True, status_code=200)
        assert wr.success is True
        assert wr.status_code == 200
        assert wr.error is None

    def test_failure_result(self) -> None:
        wr = WakeResult(gateway="test", success=False, error="timeout")
        assert wr.success is False
        assert wr.error == "timeout"

    def test_is_immutable(self) -> None:
        wr = WakeResult(gateway="test", success=True)
        with pytest.raises(Exception):
            wr.gateway = "modified"  # type: ignore[misc]
