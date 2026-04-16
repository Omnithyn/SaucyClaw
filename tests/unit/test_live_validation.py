"""测试 live validation evidence 结构和保存逻辑。

验证：
- LiveValidationEvidence 字段正确
- save_evidence 生成 payload 和 evidence 文件
- build_evidence 正确构造 evidence
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
import sys
sys.path.insert(0, str(PROJECT_ROOT))

# 导入 live_validation 模块中的 helper 函数
from experiments.openclaw_poc.live_validation import (
    LiveValidationEvidence,
    build_evidence,
    save_evidence,
)
from adapters.openclaw.hooks_adapter import HooksWakeResult


class TestLiveValidationEvidence:
    """测试 LiveValidationEvidence 结构"""

    def test_required_fields(self):
        """必需字段存在"""
        evidence = LiveValidationEvidence(
            scenario="test-scenario",
            gateway_url="http://test/hooks/agent",
            timestamp="2026-04-16T00:00:00Z",
            payload={"message": "test"},
            gateway="test-gateway",
            success=True,
            run_id="test-run-id",
            status_code=200,
            mode="live",
        )

        assert evidence.scenario == "test-scenario"
        assert evidence.gateway_url == "http://test/hooks/agent"
        assert evidence.success is True
        assert evidence.mode == "live"

    def test_success_evidence(self):
        """成功 evidence"""
        evidence = LiveValidationEvidence(
            scenario="block_test",
            gateway_url="http://test",
            timestamp="2026-04-16T00:00:00Z",
            payload={"message": "Block decision"},
            gateway="hooks",
            success=True,
            run_id="abc-123",
            status_code=200,
        )

        assert evidence.success is True
        assert evidence.run_id == "abc-123"
        assert evidence.error is None

    def test_failure_evidence(self):
        """失败 evidence"""
        evidence = LiveValidationEvidence(
            scenario="failure_test",
            gateway_url="http://test",
            timestamp="2026-04-16T00:00:00Z",
            payload=None,
            gateway="hooks",
            success=False,
            error="HTTP 401: Unauthorized",
            status_code=401,
        )

        assert evidence.success is False
        assert evidence.error == "HTTP 401: Unauthorized"
        assert evidence.payload is None

    def test_mode_is_live(self):
        """mode 默认为 live"""
        evidence = LiveValidationEvidence(
            scenario="test",
            gateway_url="http://test",
            timestamp="2026-04-16T00:00:00Z",
            payload={},
            gateway="hooks",
            success=True,
        )

        assert evidence.mode == "live"

    def test_evidence_is_frozen(self):
        """evidence 是不可变的"""
        evidence = LiveValidationEvidence(
            scenario="test",
            gateway_url="http://test",
            timestamp="2026-04-16T00:00:00Z",
            payload={},
            gateway="hooks",
            success=True,
        )

        # dataclass(frozen=True) 应阻止修改
        with pytest.raises(Exception):
            evidence.success = False  # type: ignore


class TestBuildEvidence:
    """测试 build_evidence 函数"""

    def test_build_evidence_from_success_result(self):
        """从成功结果构建 evidence"""
        wake_result = HooksWakeResult(
            gateway="hooks-gateway",
            success=True,
            run_id="run-abc-123",
            status_code=200,
        )

        evidence = build_evidence(
            scenario="block_test",
            gateway_url="http://test/hooks/agent",
            payload={"message": "Block"},
            wake_result=wake_result,
        )

        assert evidence.scenario == "block_test"
        assert evidence.success is True
        assert evidence.run_id == "run-abc-123"
        assert evidence.status_code == 200
        assert evidence.gateway == "hooks-gateway"

    def test_build_evidence_from_failure_result(self):
        """从失败结果构建 evidence"""
        wake_result = HooksWakeResult(
            gateway="hooks-gateway",
            success=False,
            error="HTTP 401",
            status_code=401,
        )

        evidence = build_evidence(
            scenario="failure_test",
            gateway_url="http://test/hooks/agent",
            payload={"message": "test"},
            wake_result=wake_result,
        )

        assert evidence.success is False
        assert evidence.error == "HTTP 401"
        assert evidence.status_code == 401

    def test_build_evidence_includes_payload(self):
        """evidence 包含 payload"""
        wake_result = HooksWakeResult(
            gateway="hooks",
            success=True,
            run_id="id",
        )

        payload = {
            "message": "[governance|Block]\n决策: Block",
            "name": "SaucyClaw Governance",
            "wakeMode": "now",
            "channel": "last",
        }

        evidence = build_evidence(
            scenario="test",
            gateway_url="http://test",
            payload=payload,
            wake_result=wake_result,
        )

        assert evidence.payload == payload


class TestSaveEvidence:
    """测试 save_evidence 函数"""

    def test_save_evidence_creates_payload_file(self):
        """保存 payload 文件"""
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)

            evidence = LiveValidationEvidence(
                scenario="test_scenario",
                gateway_url="http://test",
                timestamp="2026-04-16T00:00:00Z",
                payload={"message": "test", "name": "Hook"},
                gateway="hooks",
                success=True,
                run_id="run-id",
            )

            save_evidence(evidence, output_dir)

            payload_file = output_dir / "test_scenario_payload.json"
            assert payload_file.exists()

            with open(payload_file) as f:
                saved_payload = json.load(f)
            assert saved_payload["message"] == "test"

    def test_save_evidence_creates_evidence_file(self):
        """保存 evidence 文件"""
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)

            evidence = LiveValidationEvidence(
                scenario="test_scenario",
                gateway_url="http://test",
                timestamp="2026-04-16T00:00:00Z",
                payload={"message": "test"},
                gateway="hooks",
                success=True,
                run_id="run-id",
                status_code=200,
            )

            save_evidence(evidence, output_dir)

            evidence_file = output_dir / "test_scenario_evidence.json"
            assert evidence_file.exists()

            with open(evidence_file) as f:
                saved_evidence = json.load(f)
            assert saved_evidence["scenario"] == "test_scenario"
            assert saved_evidence["success"] is True
            assert saved_evidence["run_id"] == "run-id"

    def test_save_evidence_without_payload(self):
        """无 payload 时只保存 evidence"""
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)

            evidence = LiveValidationEvidence(
                scenario="no_payload_test",
                gateway_url="http://test",
                timestamp="2026-04-16T00:00:00Z",
                payload=None,  # 无 payload
                gateway="hooks",
                success=False,
                error="Decision mismatch",
            )

            save_evidence(evidence, output_dir)

            evidence_file = output_dir / "no_payload_test_evidence.json"
            assert evidence_file.exists()

            # 无 payload 文件
            payload_file = output_dir / "no_payload_test_payload.json"
            assert not payload_file.exists()

    def test_evidence_contains_mode(self):
        """evidence 包含 mode 字段"""
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)

            evidence = LiveValidationEvidence(
                scenario="test",
                gateway_url="http://test",
                timestamp="2026-04-16T00:00:00Z",
                payload={"message": "test"},
                gateway="hooks",
                success=True,
            )

            save_evidence(evidence, output_dir)

            evidence_file = output_dir / "test_evidence.json"
            with open(evidence_file) as f:
                saved = json.load(f)

            assert saved["mode"] == "live"