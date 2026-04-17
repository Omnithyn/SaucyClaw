"""Debug Render 单元测试。

Phase 2.6: 验证调试输出渲染器的正确性。
"""

from __future__ import annotations

from pathlib import Path

from adapters.openclaw.adapter import OpenClawHostAdapter
from adapters.openclaw.explain_bridge import ExplainBridge
from adapters.openclaw.debug_render import render_shadow_run
from adapters.openclaw.runtime_trace import build_runtime_trace
from adapters.openclaw.shadow_runtime import ShadowRuntime
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


class TestRenderBlockScenario:
    """Block 场景输出包含关键信息。"""

    def test_render_block(self, tmp_path):
        runtime, adapter, bridge = _make_full_stack(tmp_path, bridge_enable=True)
        fixture = _load_fixture("block_input.yaml")

        run_result = runtime.process_and_write(fixture)
        trace = build_runtime_trace(run_result, bridge=bridge)
        output = render_shadow_run(run_result, trace)

        # 断言关键信息
        assert "决策: Block" in output
        assert "Shadow Mode: ON" in output
        assert "风险: high" in output
        assert "rule-reviewer-must-differ" in output
        assert "触发阻断" in output
        assert "风险等级: high" in output
        assert "── Shadow Run " in output
        assert "── Explanation " in output
        assert "── Write Back " in output


class TestRenderAllowScenario:
    """Allow 场景输出包含关键信息。"""

    def test_render_allow(self, tmp_path):
        runtime, adapter, bridge = _make_full_stack(tmp_path, bridge_enable=True)
        fixture = _load_fixture("allow_input.yaml")

        run_result = runtime.process_and_write(fixture)
        trace = build_runtime_trace(run_result, bridge=bridge)
        output = render_shadow_run(run_result, trace)

        # 断言关键信息
        assert "决策: Allow" in output
        assert "no-rules" in output
        assert "未触发治理规则" in output
        assert "── Shadow Run " in output
        # Allow 场景无解释项，应显示降级信息
        assert "no triggered rule explanations" in output


class TestRenderWithoutBridge:
    """无 bridge 时输出包含 shadow_mode=OFF / explanation-unavailable。"""

    def test_render_no_bridge(self, tmp_path):
        runtime, adapter = _make_runtime_no_bridge(tmp_path)
        fixture = _load_fixture("block_input.yaml")

        run_result = runtime.process_and_write(fixture)
        trace = build_runtime_trace(run_result, bridge=None)
        output = render_shadow_run(run_result, trace)

        # 断言关键信息
        assert "Shadow Mode: OFF" in output
        assert "explanation-unavailable" in output
        assert "风险: 无" in output
        assert "决策: Block" in output
