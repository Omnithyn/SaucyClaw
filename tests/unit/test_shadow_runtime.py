"""Shadow Runtime 单元测试。"""

from pathlib import Path

from adapters.openclaw.adapter import OpenClawHostAdapter
from adapters.openclaw.explain_bridge import ExplainBridge
from adapters.openclaw.shadow_runtime import ShadowRuntime, ShadowRunResult
from core.engine.orchestrator import GovernanceEngine
from core.governance.loader import load_governance
from stores.file.evidence.store import FileEvidenceStore
from stores.file.memory.store import FileMemoryStore
from stores.protocols import GateResult

SCHEMAS_DIR = Path(__file__).parent.parent.parent / "schemas" / "governance"
FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


def _make_engine(tmp_path):
    """创建测试用引擎。"""
    schema = load_governance(SCHEMAS_DIR)
    evidence_store = FileEvidenceStore(base_dir=str(tmp_path / "evidence"))
    memory_store = FileMemoryStore(base_dir=str(tmp_path / "memory"))
    engine = GovernanceEngine(
        rules=schema.rules,
        evidence_store=evidence_store,
        memory_store=memory_store,
    )
    return engine


class TestShadowRuntimeWithoutBridge:
    def test_process_and_write_without_bridge(self, tmp_path):
        """无 bridge 时 enhanced_output 为 None。"""
        engine = _make_engine(tmp_path)
        adapter = OpenClawHostAdapter()
        runtime = ShadowRuntime(engine=engine, adapter=adapter, explain_bridge=None)

        fixture_path = FIXTURES_DIR / "block_input.yaml"
        import yaml
        with open(fixture_path) as f:
            fixture = yaml.safe_load(f)

        result = runtime.process_and_write(fixture)

        assert isinstance(result, ShadowRunResult)
        assert isinstance(result.gate_result, GateResult)
        assert result.gate_result.decision == "Block"
        assert result.enhanced_output is None
        assert len(adapter.write_back_log) == 1


class TestShadowRuntimeWithBridgeDisabled:
    def test_process_and_write_with_bridge_disabled(self, tmp_path):
        """bridge 存在但关闭时 enhanced_output.explanation_bundle 为 None。"""
        engine = _make_engine(tmp_path)
        adapter = OpenClawHostAdapter()
        schema = load_governance(SCHEMAS_DIR)
        lookup = {r.id: r for r in schema.rules}
        bridge = ExplainBridge(lookup, enable=False)

        runtime = ShadowRuntime(engine=engine, adapter=adapter, explain_bridge=bridge)

        fixture_path = FIXTURES_DIR / "block_input.yaml"
        import yaml
        with open(fixture_path) as f:
            fixture = yaml.safe_load(f)

        result = runtime.process_and_write(fixture)

        assert isinstance(result, ShadowRunResult)
        assert result.gate_result.decision == "Block"
        assert result.enhanced_output is not None
        assert result.enhanced_output.explanation_bundle is None
        assert len(adapter.write_back_log) == 1


class TestShadowRuntimeWithBridgeEnabled:
    def test_process_and_write_with_bridge_enabled(self, tmp_path):
        """bridge 开启时 enhanced_output.explanation_bundle 非 None。"""
        engine = _make_engine(tmp_path)
        adapter = OpenClawHostAdapter()
        schema = load_governance(SCHEMAS_DIR)
        lookup = {r.id: r for r in schema.rules}
        bridge = ExplainBridge(lookup, enable=True)

        runtime = ShadowRuntime(engine=engine, adapter=adapter, explain_bridge=bridge)

        fixture_path = FIXTURES_DIR / "block_input.yaml"
        import yaml
        with open(fixture_path) as f:
            fixture = yaml.safe_load(f)

        result = runtime.process_and_write(fixture)

        assert isinstance(result, ShadowRunResult)
        assert result.gate_result.decision == "Block"
        assert result.enhanced_output is not None
        assert result.enhanced_output.explanation_bundle is not None
        assert result.enhanced_output.explanation_bundle.readable_summary
        assert result.enhanced_output.explanation_bundle.risk_summary
        assert len(adapter.write_back_log) == 1

    def test_write_back_log_records_result(self, tmp_path):
        """验证 adapter.write_back_log 正确记录。"""
        engine = _make_engine(tmp_path)
        adapter = OpenClawHostAdapter()
        schema = load_governance(SCHEMAS_DIR)
        lookup = {r.id: r for r in schema.rules}
        bridge = ExplainBridge(lookup, enable=True)

        runtime = ShadowRuntime(engine=engine, adapter=adapter, explain_bridge=bridge)

        fixture_path = FIXTURES_DIR / "block_input.yaml"
        import yaml
        with open(fixture_path) as f:
            fixture = yaml.safe_load(f)

        result = runtime.process_and_write(fixture)

        # 验证 write_back_log 包含原始结果
        assert len(adapter.write_back_log) == 1
        logged_result = adapter.write_back_log[0]
        assert isinstance(logged_result, GateResult)
        assert logged_result.decision == "Block"
        # 验证与返回结果一致
        assert logged_result == result.gate_result


class TestShadowRuntimeAllowScenario:
    def test_allow_scenario(self, tmp_path):
        """Allow 场景也应正常工作。"""
        engine = _make_engine(tmp_path)
        adapter = OpenClawHostAdapter()
        schema = load_governance(SCHEMAS_DIR)
        lookup = {r.id: r for r in schema.rules}
        bridge = ExplainBridge(lookup, enable=True)

        runtime = ShadowRuntime(engine=engine, adapter=adapter, explain_bridge=bridge)

        fixture_path = FIXTURES_DIR / "allow_input.yaml"
        import yaml
        with open(fixture_path) as f:
            fixture = yaml.safe_load(f)

        result = runtime.process_and_write(fixture)

        assert isinstance(result, ShadowRunResult)
        assert result.gate_result.decision == "Allow"
        assert result.enhanced_output is not None
        assert result.enhanced_output.explanation_bundle is not None
        assert len(adapter.write_back_log) == 1
        assert adapter.write_back_log[0].decision == "Allow"
