"""集成测试：OpenClaw Adapter + GovernanceEngine 端到端流程。

使用真实 YAML 治理规则定义和 Block/Allow fixtures。
"""

from __future__ import annotations

from pathlib import Path

import yaml

from adapters.openclaw.adapter import OpenClawHostAdapter
from core.engine.orchestrator import GovernanceEngine
from core.governance.loader import load_rules
from core.governance.models import GovernanceRule
from stores.file.evidence.store import FileEvidenceStore
from stores.file.memory.store import FileMemoryStore


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SCHEMAS_DIR = Path(__file__).parent.parent.parent / "schemas" / "governance"
FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


def _make_engine(tmp_path: Path, rules: list[GovernanceRule]) -> tuple[GovernanceEngine, FileEvidenceStore, FileMemoryStore]:
    evidence_store = FileEvidenceStore(tmp_path / "evidence")
    memory_store = FileMemoryStore(tmp_path / "memory")
    engine = GovernanceEngine(
        rules=rules,
        evidence_store=evidence_store,
        memory_store=memory_store,
    )
    return engine, evidence_store, memory_store


# ---------------------------------------------------------------------------
# Block 场景集成测试
# ---------------------------------------------------------------------------

class TestBlockScenarioIntegration:
    def test_block_with_real_yaml_rules(self, tmp_path):
        """使用真实 YAML 规则定义，Block fixture 应被阻断。"""
        rules = load_rules(SCHEMAS_DIR / "rules.yaml")
        engine, _, memory_store = _make_engine(tmp_path, rules)

        fixture_path = FIXTURES_DIR / "block_input.yaml"
        with open(fixture_path) as f:
            fixture = yaml.safe_load(f)

        # 引擎处理
        result = engine.process_event(fixture)

        assert result.decision == "Block", (
            f"期望 Block，实际 {result.decision}: {result.reason}"
        )
        assert "rule-reviewer-must-differ" in result.matched_rules
        assert len(result.evidence_ids) > 0

        # 验证 memory 已写入
        memories = memory_store.search({"type": "violation"})
        assert len(memories) == 1
        assert "task:C" in memories[0].tags
        assert "decision:Block" in memories[0].tags

    def test_block_write_back(self, tmp_path):
        """Block 决策应能通过 write_back 回写宿主。"""
        rules = load_rules(SCHEMAS_DIR / "rules.yaml")
        engine, _, _ = _make_engine(tmp_path, rules)

        fixture_path = FIXTURES_DIR / "block_input.yaml"
        with open(fixture_path) as f:
            fixture = yaml.safe_load(f)

        result = engine.process_event(fixture)

        adapter = OpenClawHostAdapter()
        adapter.write_back(result)

        assert len(adapter.write_back_log) == 1
        assert adapter.write_back_log[0].decision == "Block"


# ---------------------------------------------------------------------------
# Allow 场景集成测试
# ---------------------------------------------------------------------------

class TestAllowScenarioIntegration:
    def test_allow_with_real_yaml_rules(self, tmp_path):
        """使用真实 YAML 规则定义，Allow fixture 应被放行。"""
        rules = load_rules(SCHEMAS_DIR / "rules.yaml")
        engine, _, memory_store = _make_engine(tmp_path, rules)

        fixture_path = FIXTURES_DIR / "allow_input.yaml"
        with open(fixture_path) as f:
            fixture = yaml.safe_load(f)

        result = engine.process_event(fixture)

        assert result.decision == "Allow"
        assert result.matched_rules == []
        assert result.evidence_ids == []

        # 验证 memory 已写入（pass 类型）
        memories = memory_store.search({"type": "pass"})
        assert len(memories) == 1
        assert "task:C" in memories[0].tags
        assert "decision:Allow" in memories[0].tags
        # Allow 不应有 rule: 标签
        assert not any(t.startswith("rule:") for t in memories[0].tags)

    def test_allow_write_back(self, tmp_path):
        """Allow 决策也应能通过 write_back 回写。"""
        rules = load_rules(SCHEMAS_DIR / "rules.yaml")
        engine, _, _ = _make_engine(tmp_path, rules)

        fixture_path = FIXTURES_DIR / "allow_input.yaml"
        with open(fixture_path) as f:
            fixture = yaml.safe_load(f)

        result = engine.process_event(fixture)

        adapter = OpenClawHostAdapter()
        adapter.write_back(result)

        assert len(adapter.write_back_log) == 1
        assert adapter.write_back_log[0].decision == "Allow"


# ---------------------------------------------------------------------------
# Adapter 能力测试
# ---------------------------------------------------------------------------

class TestAdapterCapabilities:
    def test_get_capabilities(self):
        adapter = OpenClawHostAdapter()
        caps = adapter.get_capabilities()

        assert "hooks" in caps
        assert "output_intercept" in caps["hooks"]
        assert caps["version"] == "mock-0.1"

    def test_connect_preserves_metadata(self):
        adapter = OpenClawHostAdapter()
        ctx = adapter.connect({
            "session_id": "s1",
            "source": "test",
            "custom_key": "custom_value",
        })

        assert ctx.session_id == "s1"
        assert ctx.source == "test"
        assert ctx.metadata.get("custom_key") == "custom_value"

    def test_collect_event_produces_normalized_event(self):
        adapter = OpenClawHostAdapter()
        event = adapter.collect_event({
            "type": "task_run",
            "session_id": "s1",
            "assignee": "dev",
        })

        assert event.event_type == "task_run"
        assert event.session_id == "s1"
        assert event.payload.get("assignee") == "dev"
