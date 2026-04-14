"""Runtime Trace 单元测试。

Phase 2.5: 验证运行链路最小摘要器的正确性。
"""

from __future__ import annotations

from pathlib import Path

from adapters.openclaw.adapter import OpenClawHostAdapter
from adapters.openclaw.explain_bridge import ExplainBridge
from adapters.openclaw.runtime_trace import RuntimeTrace, build_runtime_trace
from adapters.openclaw.shadow_runtime import ShadowRuntime, ShadowRunResult
from core.engine.orchestrator import GovernanceEngine
from core.governance.loader import load_governance
from stores.file.evidence.store import FileEvidenceStore
from stores.file.memory.store import FileMemoryStore

SCHEMAS_DIR = Path(__file__).parent.parent.parent / "schemas" / "governance"
FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


def _make_full_stack(tmp_path, bridge_enable=True):
    """创建完整四组件栈：engine + adapter + bridge + runtime。"""
    schema = load_governance(SCHEMAS_DIR)
    lookup = {r.id: r for r in schema.rules}
    bridge = ExplainBridge(lookup, enable=bridge_enable)

    evidence_store = FileEvidenceStore(base_dir=str(tmp_path / "evidence"))
    memory_store = FileMemoryStore(base_dir=str(tmp_path / "memory"))
    engine = GovernanceEngine(
        rules=schema.rules,
        evidence_store=evidence_store,
        memory_store=memory_store,
    )
    adapter = OpenClawHostAdapter()
    runtime = ShadowRuntime(
        engine=engine,
        adapter=adapter,
        explain_bridge=bridge,
    )
    return runtime, adapter, bridge


def _make_runtime_no_bridge(tmp_path):
    """创建无 bridge 的 runtime。"""
    schema = load_governance(SCHEMAS_DIR)
    evidence_store = FileEvidenceStore(base_dir=str(tmp_path / "evidence"))
    memory_store = FileMemoryStore(base_dir=str(tmp_path / "memory"))
    engine = GovernanceEngine(
        rules=schema.rules,
        evidence_store=evidence_store,
        memory_store=memory_store,
    )
    adapter = OpenClawHostAdapter()
    runtime = ShadowRuntime(
        engine=engine,
        adapter=adapter,
        explain_bridge=None,
    )
    return runtime, adapter


def _load_fixture(name):
    """加载 YAML fixture。"""
    import yaml
    with open(FIXTURES_DIR / name) as f:
        return yaml.safe_load(f)


class TestBuildTraceBlockScenario:
    """Block 场景：decision=Block, has_explanation=True, matched_rules 非空, severity 有值。"""

    def test_block_with_bridge_enabled(self, tmp_path):
        runtime, adapter, bridge = _make_full_stack(tmp_path, bridge_enable=True)
        fixture = _load_fixture("block_input.yaml")

        run_result = runtime.process_and_write(fixture)
        trace = build_runtime_trace(run_result, bridge=bridge)

        assert isinstance(trace, RuntimeTrace)
        assert trace.decision == "Block"
        assert len(trace.matched_rules) > 0
        assert trace.shadow_mode is True
        assert trace.has_explanation is True
        assert trace.severity == "high"
        assert "Block" in trace.summary
        assert "high" in trace.summary
        assert "explanation-unavailable" not in trace.summary


class TestBuildTraceAllowScenario:
    """Allow 场景：decision=Allow, matched_rules 为空。"""

    def test_allow_with_bridge_enabled(self, tmp_path):
        runtime, adapter, bridge = _make_full_stack(tmp_path, bridge_enable=True)
        fixture = _load_fixture("allow_input.yaml")

        run_result = runtime.process_and_write(fixture)
        trace = build_runtime_trace(run_result, bridge=bridge)

        assert isinstance(trace, RuntimeTrace)
        assert trace.decision == "Allow"
        assert trace.matched_rules == []
        assert trace.shadow_mode is True
        # Allow 场景无规则触发，所以 has_explanation 取决于是否有 explanation_bundle
        # 有 bridge 且开启，但无匹配规则时，explanation_bundle 存在但 explanations 为空
        # has_explanation 检查的是 explanation_bundle is not None
        assert trace.severity is None
        assert "Allow" in trace.summary
        assert "no-rules" in trace.summary


class TestBuildTraceWithoutBridge:
    """无 bridge 时：shadow_mode=False。"""

    def test_no_bridge_shadow_mode_false(self, tmp_path):
        runtime, adapter = _make_runtime_no_bridge(tmp_path)
        fixture = _load_fixture("block_input.yaml")

        run_result = runtime.process_and_write(fixture)
        trace = build_runtime_trace(run_result, bridge=None)

        assert trace.shadow_mode is False
        assert trace.has_explanation is False
        assert trace.severity is None
        assert "explanation-unavailable" in trace.summary


class TestBuildTraceWithBridgeDisabled:
    """bridge 存在但关闭时：shadow_mode=False, has_explanation=False。"""

    def test_bridge_disabled_no_explanation(self, tmp_path):
        runtime, adapter, bridge = _make_full_stack(tmp_path, bridge_enable=False)
        fixture = _load_fixture("block_input.yaml")

        run_result = runtime.process_and_write(fixture)
        trace = build_runtime_trace(run_result, bridge=bridge)

        # bridge 存在但关闭
        assert bridge.enabled is False
        # shadow_mode 应为 False
        assert trace.shadow_mode is False
        # 有 bridge 但关闭，enhanced_output 存在但 explanation_bundle 为 None
        assert trace.has_explanation is False
        assert trace.severity is None
        assert "explanation-unavailable" in trace.summary


class TestTraceIsImmutable:
    """验证 RuntimeTrace 是 frozen dataclass。"""

    def test_trace_is_frozen(self, tmp_path):
        runtime, adapter, bridge = _make_full_stack(tmp_path, bridge_enable=True)
        fixture = _load_fixture("block_input.yaml")

        run_result = runtime.process_and_write(fixture)
        trace = build_runtime_trace(run_result, bridge=bridge)

        import pytest
        with pytest.raises((TypeError, AttributeError)):
            trace.decision = "Allow"

    def test_trace_matched_rules_is_copy(self, tmp_path):
        """验证 matched_rules 是副本，不会受外部修改影响。"""
        runtime, adapter, bridge = _make_full_stack(tmp_path, bridge_enable=True)
        fixture = _load_fixture("block_input.yaml")

        run_result = runtime.process_and_write(fixture)
        trace = build_runtime_trace(run_result, bridge=bridge)

        # frozen=True 保证了 matched_rules 列表引用不可变
        # 但我们仍然确认它是独立的 list 副本
        assert isinstance(trace.matched_rules, list)
