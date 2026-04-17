"""测试 run_poc.py 的决策不匹配失败分支证据保存

验证：
- 决策不匹配时也能保存 evidence
- 所有失败分支都落盘 evidence
"""
import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch


PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from experiments.openclaw_poc.run_poc import run_scenario  # noqa: E402


class TestDecisionMismatchBranch:
    """决策不匹配失败分支测试"""

    def test_decision_mismatch_saves_evidence(self):
        """验证决策不匹配时保存 evidence"""
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)

            # Mock load_fixture 返回最小 fixture
            with patch("experiments.openclaw_poc.run_poc.load_fixture") as mock_load:
                mock_load.return_value = {
                    "assignee": "user1",
                    "reviewer": "user1",
                    "expected": {"decision": "Block"},
                }

                # Mock engine 返回错误决策
                mock_engine = MagicMock()
                mock_engine.process_event.return_value = MagicMock(
                    decision="Allow",  # 返回 Allow，但期望 Block
                    matched_rules=[],
                    reason="test mismatch",
                    evidence_ids=[],
                    suggestions=[],
                )

                # Mock bridge
                mock_bridge = MagicMock()
                mock_bridge.enhance_output.return_value = MagicMock(
                    explanation_bundle=None
                )

                # Mock adapter
                mock_adapter = MagicMock()
                mock_adapter.gateway_url = "http://localhost:18790"

                # 运行场景，期望 Block 但实际返回 Allow
                success, payload, result = run_scenario(
                    engine=mock_engine,
                    bridge=mock_bridge,
                    adapter=mock_adapter,
                    fixture_name="test_decision_mismatch",
                    expected_decision="Block",
                    output_dir=output_dir,
                )

                # 断言失败
                assert success is False
                assert payload is None
                assert result is None

                # 断言 evidence 文件已生成
                evidence_file = output_dir / "test_decision_mismatch_evidence.json"
                assert evidence_file.exists(), "决策不匹配时应保存 evidence 文件"

                # 验证 evidence 内容
                with open(evidence_file) as f:
                    evidence = json.load(f)

                assert evidence["scenario"] == "test_decision_mismatch"
                assert evidence["success"] is False
                assert evidence["payload"] is None  # 还未发送，payload 为 None
                assert "Decision mismatch" in evidence["error"]
                assert "expected Block" in evidence["error"]
                assert "got Allow" in evidence["error"]

    def test_decision_mismatch_evidence_structure(self):
        """验证决策不匹配 evidence 结构完整"""
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)

            # Mock load_fixture
            with patch("experiments.openclaw_poc.run_poc.load_fixture") as mock_load:
                mock_load.return_value = {
                    "assignee": "user2",
                    "reviewer": "user3",
                    "expected": {"decision": "Allow"},
                }

                # Mock engine 返回错误决策
                mock_engine = MagicMock()
                mock_engine.process_event.return_value = MagicMock(
                    decision="Block",
                    matched_rules=["test-rule"],
                    reason="test",
                    evidence_ids=[],
                    suggestions=[],
                )

                mock_bridge = MagicMock()
                mock_bridge.enhance_output.return_value = MagicMock(explanation_bundle=None)

                mock_adapter = MagicMock()
                mock_adapter.gateway_url = "http://localhost:18790"

                # 期望 Allow 但实际返回 Block
                success, _, _ = run_scenario(
                    engine=mock_engine,
                    bridge=mock_bridge,
                    adapter=mock_adapter,
                    fixture_name="test_structure",
                    expected_decision="Allow",
                    output_dir=output_dir,
                )

                assert success is False

                evidence_file = output_dir / "test_structure_evidence.json"
                with open(evidence_file) as f:
                    evidence = json.load(f)

                # 验证所有必需字段都存在
                required_fields = [
                    "scenario", "mode", "gateway_url", "timestamp",
                    "payload", "gateway", "success", "error", "status_code"
                ]
                for field in required_fields:
                    assert field in evidence, f"evidence 缺少必需字段: {field}"

                # 验证字段语义正确
                assert evidence["mode"] in ["mock", "real"]
                assert evidence["gateway_url"] == ""  # 还未发送
                assert evidence["gateway"] == ""  # 还未发送
                assert evidence["success"] is False
                assert evidence["status_code"] is None
