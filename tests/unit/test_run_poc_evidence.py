"""测试 run_poc.py 的证据保存行为

验证：
- 所有失败分支都能保存 evidence
- timeout mode 跟随运行模式
"""
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


# 添加项目根目录到 sys.path
PROJECT_ROOT = Path(__file__).parent.parent.parent
import sys
sys.path.insert(0, str(PROJECT_ROOT))

from experiments.openclaw_poc.run_poc import (
    ValidationEvidence,
    build_evidence,
    save_validation_bundle,
    run_timeout_test,
)
from adapters.openclaw.notification_adapter import WakeResult


class TestEvidenceSaving:
    """证据保存测试"""

    def test_build_evidence_creates_correct_structure(self):
        """验证 build_evidence 创建正确结构"""
        wake_result = WakeResult(
            gateway="test-gateway",
            success=True,
            error=None,
            status_code=200,
        )

        payload = {"event": "governance-decision", "instruction": "[governance|Block]"}

        evidence = build_evidence(
            scenario="test_scenario",
            mode="mock",
            gateway_url="http://localhost:18790",
            payload=payload,
            wake_result=wake_result,
        )

        assert evidence.scenario == "test_scenario"
        assert evidence.mode == "mock"
        assert evidence.gateway_url == "http://localhost:18790"
        assert evidence.payload == payload
        assert evidence.success is True
        assert evidence.error is None
        assert evidence.status_code == 200

    def test_build_evidence_handles_failure(self):
        """验证 build_evidence 正确处理失败情况"""
        wake_result = WakeResult(
            gateway="unreachable",
            success=False,
            error="Connection refused",
            status_code=None,
        )

        payload = {"event": "governance-decision", "instruction": "[governance|Block]"}

        evidence = build_evidence(
            scenario="timeout",
            mode="mock",
            gateway_url="http://127.0.0.1:9999/nonexistent",
            payload=payload,
            wake_result=wake_result,
        )

        assert evidence.success is False
        assert evidence.error == "Connection refused"
        assert evidence.status_code is None

    def test_save_validation_bundle_creates_files(self):
        """验证 save_validation_bundle 创建文件"""
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)

            wake_result = WakeResult(
                gateway="test-gateway",
                success=True,
                error=None,
                status_code=200,
            )

            payload = {"event": "test", "instruction": "test instruction"}

            evidence = build_evidence(
                scenario="test_save",
                mode="mock",
                gateway_url="http://localhost:18790",
                payload=payload,
                wake_result=wake_result,
            )

            save_validation_bundle(evidence, output_dir)

            # 验证文件存在
            payload_file = output_dir / "test_save_payload.json"
            evidence_file = output_dir / "test_save_evidence.json"

            assert payload_file.exists()
            assert evidence_file.exists()

            # 验证内容
            with open(payload_file) as f:
                saved_payload = json.load(f)
            assert saved_payload == payload

            with open(evidence_file) as f:
                saved_evidence = json.load(f)
            assert saved_evidence["scenario"] == "test_save"
            assert saved_evidence["payload"] == payload

    def test_save_validation_bundle_without_payload(self):
        """验证 payload 为 None 时也能保存 evidence"""
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)

            wake_result = WakeResult(
                gateway="test-gateway",
                success=False,
                error="No payload sent",
                status_code=None,
            )

            evidence = build_evidence(
                scenario="no_payload",
                mode="mock",
                gateway_url="http://localhost:18790",
                payload=None,
                wake_result=wake_result,
            )

            save_validation_bundle(evidence, output_dir)

            # payload 文件不应存在，但 evidence 文件应该存在
            payload_file = output_dir / "no_payload_payload.json"
            evidence_file = output_dir / "no_payload_evidence.json"

            assert not payload_file.exists()
            assert evidence_file.exists()

            # 验证 evidence 内容
            with open(evidence_file) as f:
                saved_evidence = json.load(f)
            assert saved_evidence["payload"] is None


class TestTimeoutModeFollowsEnvironment:
    """timeout mode 跟随环境变量测试"""

    def test_timeout_mode_defaults_to_mock(self):
        """验证 timeout mode 默认为 mock"""
        # 确保环境变量未设置
        original = os.environ.get("OPENCLAW_GATEWAY_TYPE")
        if original:
            del os.environ["OPENCLAW_GATEWAY_TYPE"]

        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)

            # run_timeout_test 内部应该读取环境变量
            # 我们通过检查生成的 evidence.mode 来验证
            # 注意：run_timeout_test 会发送真实请求到不可达地址
            # 我们需要 mock adapter

            with patch("experiments.openclaw_poc.run_poc.OpenClawNotificationAdapter") as mock_adapter_class:
                mock_adapter = MagicMock()
                mock_adapter_class.return_value = mock_adapter
                mock_adapter.gateway_url = "http://127.0.0.1:9999/nonexistent"
                mock_adapter.last_payload = {"event": "test"}

                mock_adapter.send_decision.return_value = WakeResult(
                    gateway="unreachable",
                    success=False,
                    error="Connection refused",
                    status_code=None,
                )

                run_timeout_test(output_dir)

                # 检查生成的 evidence 文件
                evidence_file = output_dir / "timeout_evidence.json"
                assert evidence_file.exists()

                with open(evidence_file) as f:
                    evidence = json.load(f)

                # mode 应该是 mock（默认）
                assert evidence["mode"] == "mock"

    def test_timeout_mode_follows_real_environment(self):
        """验证 timeout mode 跟随 real 环境变量"""
        # 设置环境变量
        original = os.environ.get("OPENCLAW_GATEWAY_TYPE")
        os.environ["OPENCLAW_GATEWAY_TYPE"] = "real"

        try:
            with tempfile.TemporaryDirectory() as tmp:
                output_dir = Path(tmp)

                with patch("experiments.openclaw_poc.run_poc.OpenClawNotificationAdapter") as mock_adapter_class:
                    mock_adapter = MagicMock()
                    mock_adapter_class.return_value = mock_adapter
                    mock_adapter.gateway_url = "http://127.0.0.1:9999/nonexistent"
                    mock_adapter.last_payload = {"event": "test"}

                    mock_adapter.send_decision.return_value = WakeResult(
                        gateway="unreachable",
                        success=False,
                        error="Connection refused",
                        status_code=None,
                    )

                    run_timeout_test(output_dir)

                    # 检查生成的 evidence 文件
                    evidence_file = output_dir / "timeout_evidence.json"
                    assert evidence_file.exists()

                    with open(evidence_file) as f:
                        evidence = json.load(f)

                    # mode 应该是 real（跟随环境变量）
                    assert evidence["mode"] == "real"
        finally:
            # 恢复环境变量
            if original:
                os.environ["OPENCLAW_GATEWAY_TYPE"] = original
            else:
                del os.environ["OPENCLAW_GATEWAY_TYPE"]