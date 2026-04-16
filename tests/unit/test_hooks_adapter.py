"""测试 hooks adapter payload 构造和响应解析。

验证：
- _build_hook_agent_payload 输出字段正确
- message 包含完整治理决策信息
- last_payload 记录发送的 payload
- HooksWakeResult 结构正确
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
import sys
sys.path.insert(0, str(PROJECT_ROOT))

from adapters.openclaw.hooks_adapter import (
    _build_hook_agent_payload,
    OpenClawHooksAdapter,
    HooksWakeResult,
)


class TestBuildHookAgentPayload:
    """测试 payload 构造"""

    def test_required_fields_present(self):
        """必需字段存在"""
        payload = _build_hook_agent_payload(
            decision="Block",
            matched_rules=["rule-1"],
            reason="test reason",
            suggestions=["fix it"],
            explanation_summary="test explanation",
        )

        assert "message" in payload
        assert "name" in payload
        assert "wakeMode" in payload
        assert "channel" in payload
        assert "deliver" in payload

    def test_message_contains_decision(self):
        """message 包含决策"""
        payload = _build_hook_agent_payload(
            decision="Block",
            matched_rules=["rule-1"],
            reason="test reason",
            suggestions=[],
        )

        assert "[governance|Block]" in payload["message"]
        assert "决策: Block" in payload["message"]

    def test_message_contains_rules(self):
        """message 包含规则"""
        payload = _build_hook_agent_payload(
            decision="Block",
            matched_rules=["rule-reviewer-must-differ"],
            reason="触发规则",
            suggestions=[],
        )

        assert "规则: rule-reviewer-must-differ" in payload["message"]

    def test_message_contains_no_rules_for_allow(self):
        """Allow 无规则时 message 包含未触发治理规则"""
        payload = _build_hook_agent_payload(
            decision="Allow",
            matched_rules=[],  # 无规则
            reason="无规则触发",
            suggestions=[],
        )

        assert "未触发治理规则" in payload["message"]

    def test_message_contains_reason(self):
        """message 包含原因"""
        payload = _build_hook_agent_payload(
            decision="Block",
            matched_rules=["rule-1"],
            reason="审查者与执行者相同",
            suggestions=[],
        )

        assert "原因: 审查者与执行者相同" in payload["message"]

    def test_message_contains_suggestions(self):
        """message 包含建议"""
        payload = _build_hook_agent_payload(
            decision="Block",
            matched_rules=["rule-1"],
            reason="test",
            suggestions=["请修改审查者", "检查配置"],
        )

        assert "建议: 请修改审查者; 检查配置" in payload["message"]

    def test_message_contains_explanation(self):
        """message 包含解释"""
        payload = _build_hook_agent_payload(
            decision="Block",
            matched_rules=["rule-1"],
            reason="test",
            suggestions=[],
            explanation_summary="触发阻断（high/separation_of_duties）",
        )

        assert "解释: 触发阻断（high/separation_of_duties）" in payload["message"]

    def test_default_values(self):
        """默认值正确"""
        payload = _build_hook_agent_payload(
            decision="Block",
            matched_rules=["rule-1"],
            reason="test",
            suggestions=[],
        )

        assert payload["wakeMode"] == "now"
        assert payload["deliver"] is True
        assert payload["channel"] == "last"

    def test_custom_hook_name(self):
        """自定义 hook name"""
        payload = _build_hook_agent_payload(
            decision="Block",
            matched_rules=["rule-1"],
            reason="test",
            suggestions=[],
            name="Custom Governance Hook",
        )

        assert payload["name"] == "Custom Governance Hook"


class TestHooksWakeResult:
    """测试 HooksWakeResult 结构"""

    def test_success_result(self):
        """成功结果"""
        result = HooksWakeResult(
            gateway="test-gateway",
            success=True,
            run_id="abc-123",
            status_code=200,
        )

        assert result.success is True
        assert result.run_id == "abc-123"
        assert result.status_code == 200
        assert result.error is None

    def test_failure_result(self):
        """失败结果"""
        result = HooksWakeResult(
            gateway="test-gateway",
            success=False,
            error="HTTP 401",
            status_code=401,
        )

        assert result.success is False
        assert result.error == "HTTP 401"
        assert result.status_code == 401
        assert result.run_id is None


class TestHooksAdapterLastPayload:
    """测试 last_payload 记录"""

    def test_last_payload_records_sent_payload(self):
        """last_payload 记录发送的 payload"""
        adapter = OpenClawHooksAdapter(
            gateway_url="http://test/hooks/agent",
            token="test-token",
        )

        # Mock send
        with patch.object(adapter, "_wake_hooks") as mock_wake:
            mock_wake.return_value = HooksWakeResult(
                gateway="test",
                success=True,
                run_id="test-id",
            )

            from stores.protocols import GateResult
            result = GateResult(
                decision="Block",
                reason="test",
                matched_rules=["rule-1"],
                evidence_ids=[],
                suggestions=[],
            )

            adapter.send_decision(result)

            assert adapter.last_payload is not None
            assert "message" in adapter.last_payload
            assert "[governance|Block]" in adapter.last_payload["message"]

    def test_last_payload_returns_copy(self):
        """last_payload 返回副本"""
        adapter = OpenClawHooksAdapter(
            gateway_url="http://test/hooks/agent",
            token="test-token",
        )

        adapter._last_payload = {"message": "test", "name": "Hook"}

        payload1 = adapter.last_payload
        payload2 = adapter.last_payload

        # 修改副本不影响原数据
        payload1["message"] = "modified"
        assert payload2["message"] == "test"

    def test_last_payload_none_before_send(self):
        """发送前 last_payload 为 None"""
        adapter = OpenClawHooksAdapter(
            gateway_url="http://test/hooks/agent",
            token="test-token",
        )

        assert adapter.last_payload is None


class TestHooksAdapterSendDecision:
    """测试 send_decision 方法"""

    def test_send_decision_calls_wake_hooks(self):
        """send_decision 调用 _wake_hooks"""
        adapter = OpenClawHooksAdapter(
            gateway_url="http://test/hooks/agent",
            token="test-token",
        )

        with patch.object(adapter, "_wake_hooks") as mock_wake:
            mock_wake.return_value = HooksWakeResult(
                gateway="test",
                success=True,
                run_id="test-id",
            )

            from stores.protocols import GateResult
            result = GateResult(
                decision="Allow",
                reason="test",
                matched_rules=[],
                evidence_ids=[],
                suggestions=[],
            )

            wake_result = adapter.send_decision(result)

            assert mock_wake.called
            assert wake_result.success is True

    def test_send_decision_with_explanation(self):
        """send_decision 包含解释"""
        adapter = OpenClawHooksAdapter(
            gateway_url="http://test/hooks/agent",
            token="test-token",
        )

        with patch.object(adapter, "_wake_hooks") as mock_wake:
            mock_wake.return_value = HooksWakeResult(
                gateway="test",
                success=True,
                run_id="test-id",
            )

            from stores.protocols import GateResult
            result = GateResult(
                decision="Block",
                reason="test",
                matched_rules=["rule-1"],
                evidence_ids=[],
                suggestions=["fix it"],
            )

            adapter.send_decision(
                result,
                explanation_summary="触发阻断规则",
            )

            payload = adapter.last_payload
            assert "解释: 触发阻断规则" in payload["message"]