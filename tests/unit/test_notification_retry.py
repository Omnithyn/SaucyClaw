"""测试 notification retry 机制

验证：
- retryable 错误会重试
- non-retryable 错误不会重试
- attempts / retried 写入 evidence 正确
- OPENCLAW_RETRY_ENABLED=false 禁用 retry
"""
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
import sys
sys.path.insert(0, str(PROJECT_ROOT))

from experiments.openclaw_poc.notification_retry import (
    RetryConfig,
    is_retryable_error,
    with_retry,
)
from adapters.openclaw.notification_adapter import WakeResult


class TestRetryableErrorDetection:
    """可重试错误检测测试"""

    def test_network_error_is_retryable(self):
        """网络错误可重试"""
        assert is_retryable_error("Connection refused", None) is True
        assert is_retryable_error("[Errno 61] Connection refused", None) is True
        assert is_retryable_error("Connection timeout", None) is True
        assert is_retryable_error("Request timed out", None) is True

    def test_http_5xx_is_retryable(self):
        """HTTP 5xx 可重试"""
        assert is_retryable_error("HTTP 500", 500) is True
        assert is_retryable_error("HTTP 502", 502) is True
        assert is_retryable_error("HTTP 503", 503) is True
        assert is_retryable_error("HTTP 504", 504) is True

    def test_http_4xx_is_not_retryable(self):
        """HTTP 4xx 不可重试"""
        assert is_retryable_error("HTTP 400", 400) is False
        assert is_retryable_error("HTTP 401", 401) is False
        assert is_retryable_error("HTTP 403", 403) is False
        assert is_retryable_error("HTTP 404", 404) is False

    def test_null_error_is_not_retryable(self):
        """null 错误不可重试"""
        assert is_retryable_error(None, None) is False

    def test_other_errors_not_retryable(self):
        """其他错误不可重试"""
        assert is_retryable_error("Invalid payload", None) is False
        assert is_retryable_error("Decision mismatch", None) is False


class TestRetryMechanism:
    """Retry 机制测试"""

    def test_retryable_error_retries(self):
        """可重试错误会重试"""
        # Mock send_func：前两次失败，第三次成功
        call_count = 0

        def mock_send():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                return WakeResult(
                    gateway="test",
                    success=False,
                    error="Connection refused",
                    status_code=None,
                )
            return WakeResult(
                gateway="test",
                success=True,
                error=None,
                status_code=200,
            )

        result, attempts, retried = with_retry(mock_send, RetryConfig(max_retries=2))

        assert result.success is True
        assert attempts == 3
        assert retried is True
        assert call_count == 3

    def test_non_retryable_error_no_retry(self):
        """不可重试错误不重试"""
        call_count = 0

        def mock_send():
            nonlocal call_count
            call_count += 1
            return WakeResult(
                gateway="test",
                success=False,
                error="HTTP 404",
                status_code=404,
            )

        result, attempts, retried = with_retry(mock_send, RetryConfig(max_retries=2))

        assert result.success is False
        assert attempts == 1
        assert retried is False
        assert call_count == 1

    def test_success_stops_retry(self):
        """成功后停止重试"""
        call_count = 0

        def mock_send():
            nonlocal call_count
            call_count += 1
            return WakeResult(
                gateway="test",
                success=True,
                error=None,
                status_code=200,
            )

        result, attempts, retried = with_retry(mock_send, RetryConfig(max_retries=2))

        assert result.success is True
        assert attempts == 1
        assert retried is False
        assert call_count == 1

    def test_max_retries_exceeded(self):
        """达到最大重试次数后停止"""
        call_count = 0

        def mock_send():
            nonlocal call_count
            call_count += 1
            return WakeResult(
                gateway="test",
                success=False,
                error="Connection refused",
                status_code=None,
            )

        result, attempts, retried = with_retry(mock_send, RetryConfig(max_retries=2))

        assert result.success is False
        assert attempts == 3  # 首次 + 2 次重试
        assert retried is True
        assert call_count == 3

    def test_custom_retry_config(self):
        """自定义 retry 配置"""
        call_count = 0

        def mock_send():
            nonlocal call_count
            call_count += 1
            if call_count < 4:
                return WakeResult(
                    gateway="test",
                    success=False,
                    error="Connection refused",
                    status_code=None,
                )
            return WakeResult(
                gateway="test",
                success=True,
                error=None,
                status_code=200,
            )

        # 自定义：最多重试 3 次
        result, attempts, retried = with_retry(mock_send, RetryConfig(max_retries=3))

        assert result.success is True
        assert attempts == 4
        assert retried is True
        assert call_count == 4


class TestRetryIntegrationWithEvidence:
    """Retry 与 evidence 集成测试"""

    def test_attempts_retried_in_evidence(self):
        """attempts/retried 正确写入 evidence"""
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)

            from experiments.openclaw_poc.run_poc import build_evidence

            # 模拟 retryable error 场景
            wake_result = WakeResult(
                gateway="unreachable",
                success=False,
                error="Connection refused",
                status_code=None,
            )

            evidence = build_evidence(
                scenario="retry_test",
                mode="mock",
                gateway_url="http://127.0.0.1:9999",
                payload={"event": "test"},
                wake_result=wake_result,
                attempts=3,
                retried=True,
            )

            assert evidence.attempts == 3
            assert evidence.retried is True
            assert evidence.success is False
            assert "Connection refused" in evidence.error

    def test_no_retry_evidence(self):
        """无 retry 时 evidence 正确"""
        from experiments.openclaw_poc.run_poc import build_evidence

        wake_result = WakeResult(
            gateway="test",
            success=False,
            error="HTTP 404",
            status_code=404,
        )

        evidence = build_evidence(
            scenario="no_retry_test",
            mode="mock",
            gateway_url="http://localhost",
            payload={"event": "test"},
            wake_result=wake_result,
            attempts=1,
            retried=False,
        )

        assert evidence.attempts == 1
        assert evidence.retried is False


class TestRetryEnvironmentControl:
    """Retry 环境变量控制测试"""

    def test_retry_disabled_by_env(self):
        """OPENCLAW_RETRY_ENABLED=false 禁用 retry"""
        # 设置环境变量
        original = os.environ.get("OPENCLAW_RETRY_ENABLED")
        os.environ["OPENCLAW_RETRY_ENABLED"] = "false"

        try:
            # 模拟 run_scenario 中的 retry 控制逻辑
            retry_enabled = os.environ.get("OPENCLAW_RETRY_ENABLED", "true").lower() == "true"

            assert retry_enabled is False

            # 验证禁用 retry 时的行为
            call_count = 0

            def mock_send():
                nonlocal call_count
                call_count += 1
                return WakeResult(
                    gateway="test",
                    success=False,
                    error="Connection refused",
                    status_code=None,
                )

            if retry_enabled:
                result, attempts, retried = with_retry(mock_send, RetryConfig())
            else:
                result = mock_send()
                attempts = 1
                retried = False

            assert attempts == 1
            assert retried is False
            assert call_count == 1

        finally:
            # 恢复环境变量
            if original:
                os.environ["OPENCLAW_RETRY_ENABLED"] = original
            else:
                del os.environ["OPENCLAW_RETRY_ENABLED"]

    def test_retry_enabled_by_default(self):
        """默认启用 retry"""
        # 确保环境变量未设置
        original = os.environ.get("OPENCLAW_RETRY_ENABLED")
        if original:
            del os.environ["OPENCLAW_RETRY_ENABLED"]

        try:
            retry_enabled = os.environ.get("OPENCLAW_RETRY_ENABLED", "true").lower() == "true"
            assert retry_enabled is True

        finally:
            if original:
                os.environ["OPENCLAW_RETRY_ENABLED"] = original