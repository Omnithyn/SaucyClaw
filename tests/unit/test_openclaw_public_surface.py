"""测试 OpenClaw 公开导出面可用性。

验证外部调用方能从统一入口导入所有公开模块。

M9-R2 — OpenClaw 接入面 Hard Closure
"""

from __future__ import annotations

from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
import sys
sys.path.insert(0, str(PROJECT_ROOT))


class TestOpenClawPublicSurface:
    """验证 adapters.openclaw 公开导出面。"""

    def test_import_hooks_adapter(self):
        """能导入 OpenClawHooksAdapter。"""
        from adapters.openclaw import OpenClawHooksAdapter
        assert OpenClawHooksAdapter is not None

    def test_import_hooks_wake_result(self):
        """能导入 HooksWakeResult。"""
        from adapters.openclaw import HooksWakeResult
        assert HooksWakeResult is not None

    def test_import_notification_adapter(self):
        """能导入 OpenClawNotificationAdapter。"""
        from adapters.openclaw import OpenClawNotificationAdapter
        assert OpenClawNotificationAdapter is not None

    def test_import_wake_result(self):
        """能导入 WakeResult。"""
        from adapters.openclaw import WakeResult
        assert WakeResult is not None

    def test_import_shadow_runtime(self):
        """能导入 ShadowRuntime。"""
        from adapters.openclaw import ShadowRuntime
        assert ShadowRuntime is not None

    def test_import_shadow_run_result(self):
        """能导入 ShadowRunResult。"""
        from adapters.openclaw import ShadowRunResult
        assert ShadowRunResult is not None

    def test_import_host_adapter(self):
        """能导入 OpenClawHostAdapter。"""
        from adapters.openclaw import OpenClawHostAdapter
        assert OpenClawHostAdapter is not None

    def test_import_explain_bridge(self):
        """能导入 ExplainBridge。"""
        from adapters.openclaw import ExplainBridge
        assert ExplainBridge is not None

    def test_import_adapter_explain_output(self):
        """能导入 AdapterExplainOutput。"""
        from adapters.openclaw import AdapterExplainOutput
        assert AdapterExplainOutput is not None

    def test_all_exports_in__all__(self):
        """__all__ 包含所有公开导出。"""
        from adapters.openclaw import __all__

        required_exports = [
            # Shadow Mode
            "OpenClawHostAdapter",
            "ExplainBridge",
            "AdapterExplainOutput",
            "ShadowRuntime",
            "ShadowRunResult",
            # Notification Mode
            "WakeResult",
            "OpenClawNotificationAdapter",
            # Hooks-Live Mode
            "HooksWakeResult",
            "OpenClawHooksAdapter",
        ]

        for export in required_exports:
            assert export in __all__, f"{export} not in __all__"

    def test_hooks_wake_result_structure(self):
        """HooksWakeResult 结构正确。"""
        from adapters.openclaw import HooksWakeResult

        # 成功结果
        success = HooksWakeResult(
            gateway="test",
            success=True,
            run_id="abc-123",
            status_code=200,
        )
        assert success.success is True
        assert success.run_id == "abc-123"
        assert success.error is None

        # 失败结果
        failure = HooksWakeResult(
            gateway="test",
            success=False,
            error="HTTP 401",
            status_code=401,
        )
        assert failure.success is False
        assert failure.error == "HTTP 401"
        assert failure.run_id is None

    def test_wake_result_structure(self):
        """WakeResult 结构正确。"""
        from adapters.openclaw import WakeResult

        success = WakeResult(
            gateway="test",
            success=True,
            status_code=200,
        )
        assert success.success is True
        assert success.error is None

        failure = WakeResult(
            gateway="test",
            success=False,
            error="Connection failed",
        )
        assert failure.success is False
        assert failure.error == "Connection failed"

    def test_shadow_run_result_structure(self):
        """ShadowRunResult 结构正确。"""
        from adapters.openclaw import ShadowRunResult
        from stores.protocols import GateResult

        gate_result = GateResult(
            decision="Block",
            reason="test",
            matched_rules=["rule-1"],
            evidence_ids=[],
            suggestions=[],
        )

        result = ShadowRunResult(
            gate_result=gate_result,
            enhanced_output=None,
        )
        assert result.gate_result.decision == "Block"
        assert result.enhanced_output is None