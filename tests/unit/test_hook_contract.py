"""Hook Contract 契约级验证。

Phase 2.3: 验证外部接入契约的正确性和稳定性。

测试分类：
a. Protocol shape test — 验证 Protocol 方法签名与实际类一致
b. Example smoke test — runpy 跑通 example 文件的最小链路
c. Compatibility check — ShadowRuntime + ExplainBridge + adapter.write_back 组合验证
"""

from __future__ import annotations

import inspect
import runpy
from pathlib import Path

# ---------------------------------------------------------------------------
# a. Protocol shape tests — 验证 Protocol 签名与实际类一致
# ---------------------------------------------------------------------------


class TestProtocolShapes:
    """验证 hook_contract.py 中定义的 Protocol 方法签名与实际实现一致。"""

    def test_host_output_sink_write_back_signature(self):
        """HostOutputSink.write_back 应与 OpenClawHostAdapter.write_back 签名兼容。"""
        from adapters.openclaw.adapter import OpenClawHostAdapter
        from adapters.openclaw.hook_contract import HostOutputSink

        # 验证实际方法在 Protocol 中声明
        assert hasattr(HostOutputSink, "write_back")
        assert hasattr(HostOutputSink, "write_back_log")

        # 验证实际类实现了 Protocol 方法
        adapter = OpenClawHostAdapter()
        assert hasattr(adapter, "write_back")
        assert hasattr(adapter, "write_back_log")

        # 验证 write_back 参数签名兼容（接受 GateResult）
        sig = inspect.signature(adapter.write_back)
        params = list(sig.parameters.keys())
        assert "gate_result" in params

    def test_explain_payload_enhance_output_signature(self):
        """ExplainPayload.enhance_output 应与 ExplainBridge.enhance_output 签名兼容。"""
        from adapters.openclaw.explain_bridge import ExplainBridge
        from adapters.openclaw.hook_contract import ExplainPayload

        assert hasattr(ExplainPayload, "enhance_output")
        assert hasattr(ExplainPayload, "enabled")

        # 验证实际类有对应方法和属性
        bridge = ExplainBridge(schema_rules_lookup={}, enable=False)
        assert hasattr(bridge, "enhance_output")
        assert hasattr(bridge, "_enabled")  # 内部实现，对应 Protocol 的 enabled 属性

        sig = inspect.signature(bridge.enhance_output)
        params = list(sig.parameters.keys())
        assert "result" in params

    def test_governance_processor_signature(self):
        """GovernanceProcessor.process_event 应与 GovernanceEngine.process_event 签名兼容。"""
        from adapters.openclaw.hook_contract import GovernanceProcessor
        from core.engine.orchestrator import GovernanceEngine

        assert hasattr(GovernanceProcessor, "process_event")

        # 验证实际类有该方法
        assert hasattr(GovernanceEngine, "process_event")

        sig = inspect.signature(GovernanceEngine.process_event)
        params = list(sig.parameters.keys())
        assert "raw_event" in params

    def test_shadow_output_signature(self):
        """ShadowOutput.process_and_write 应与 ShadowRuntime.process_and_write 签名兼容。"""
        from adapters.openclaw.hook_contract import ShadowOutput
        from adapters.openclaw.shadow_runtime import ShadowRuntime

        assert hasattr(ShadowOutput, "process_and_write")

        assert hasattr(ShadowRuntime, "process_and_write")

        sig = inspect.signature(ShadowRuntime.process_and_write)
        params = list(sig.parameters.keys())
        assert "raw_event" in params


# ---------------------------------------------------------------------------
# b. Example smoke test — runpy 跑通 example 文件
# ---------------------------------------------------------------------------


class TestExampleSmoke:
    """验证 example 文件可执行且最小链路跑通。"""

    def test_example_runs(self, tmp_path, monkeypatch):
        """runpy 执行 example 文件，验证无异常退出。"""
        example_path = Path(__file__).parent.parent.parent / "examples" / "openclaw_shadow_runtime_example.py"
        assert example_path.exists(), f"Example file not found: {example_path}"

        # 使用 runpy 执行示例
        import sys

        # 确保项目根目录在路径中
        project_root = example_path.parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        # runpy 执行，不应抛出异常
        result = runpy.run_path(str(example_path), run_name="__main__")
        assert result is not None


# ---------------------------------------------------------------------------
# c. Compatibility check — 三组件组合契约验证
# ---------------------------------------------------------------------------


class TestComponentCompatibility:
    """验证 ShadowRuntime + ExplainBridge + adapter.write_back 组合契约未漂移。"""

    def _make_engine(self, tmp_path):
        """创建测试用治理引擎。"""
        from core.engine.orchestrator import GovernanceEngine
        from core.governance.loader import load_governance
        from stores.file.evidence.store import FileEvidenceStore
        from stores.file.memory.store import FileMemoryStore

        schemas_dir = Path(__file__).parent.parent.parent / "schemas" / "governance"
        schema = load_governance(schemas_dir)
        evidence_store = FileEvidenceStore(base_dir=str(tmp_path / "evidence"))
        memory_store = FileMemoryStore(base_dir=str(tmp_path / "memory"))
        return GovernanceEngine(
            rules=schema.rules,
            evidence_store=evidence_store,
            memory_store=memory_store,
        )

    def test_shadow_runtime_with_all_components(self, tmp_path):
        """验证三组件组合：engine → bridge → adapter 完整链路可运行。"""
        from adapters.openclaw.adapter import OpenClawHostAdapter
        from adapters.openclaw.explain_bridge import ExplainBridge
        from adapters.openclaw.shadow_runtime import ShadowRuntime
        from core.governance.loader import load_governance

        engine = self._make_engine(tmp_path)
        adapter = OpenClawHostAdapter()

        schemas_dir = Path(__file__).parent.parent.parent / "schemas" / "governance"
        schema = load_governance(schemas_dir)
        lookup = {r.id: r for r in schema.rules}
        bridge = ExplainBridge(lookup, enable=True)

        runtime = ShadowRuntime(
            engine=engine,
            adapter=adapter,
            explain_bridge=bridge,
        )

        # 使用 fixture 输入
        fixtures_dir = Path(__file__).parent.parent / "fixtures"
        import yaml
        with open(fixtures_dir / "block_input.yaml") as f:
            fixture = yaml.safe_load(f)

        result = runtime.process_and_write(fixture)

        # 验证三组件契约均未漂移
        assert result.gate_result is not None  # engine 契约
        assert result.enhanced_output is not None  # bridge 契约
        assert result.enhanced_output.explanation_bundle is not None  # bridge shadow mode
        assert len(adapter.write_back_log) == 1  # adapter 契约

    def test_adapter_write_back_accepts_gate_result(self, tmp_path):
        """验证 adapter.write_back 仍接受 GateResult（零契约漂移）。"""
        from adapters.openclaw.adapter import OpenClawHostAdapter
        from adapters.openclaw.shadow_runtime import ShadowRuntime
        from stores.protocols import GateResult

        engine = self._make_engine(tmp_path)
        adapter = OpenClawHostAdapter()

        runtime = ShadowRuntime(
            engine=engine,
            adapter=adapter,
            explain_bridge=None,
        )

        fixtures_dir = Path(__file__).parent.parent / "fixtures"
        import yaml
        with open(fixtures_dir / "block_input.yaml") as f:
            fixture = yaml.safe_load(f)

        result = runtime.process_and_write(fixture)

        # 验证 write_back 接受的仍是 GateResult
        assert isinstance(adapter.write_back_log[0], GateResult)
        assert adapter.write_back_log[0].decision == result.gate_result.decision

    def test_bridge_enhance_output_returns_adapter_explain_output(self, tmp_path):
        """验证 bridge.enhance_output 返回 AdapterExplainOutput。"""
        from adapters.openclaw.explain_bridge import AdapterExplainOutput, ExplainBridge
        from core.governance.loader import load_governance

        schemas_dir = Path(__file__).parent.parent.parent / "schemas" / "governance"
        schema = load_governance(schemas_dir)
        lookup = {r.id: r for r in schema.rules}
        bridge = ExplainBridge(lookup, enable=True)

        # 用 engine 生成一个真实的 GateResult
        engine = self._make_engine(tmp_path)
        fixtures_dir = Path(__file__).parent.parent / "fixtures"
        import yaml
        with open(fixtures_dir / "block_input.yaml") as f:
            fixture = yaml.safe_load(f)

        gate_result = engine.process_event(fixture)

        # 验证 enhance_output 返回 AdapterExplainOutput
        output = bridge.enhance_output(gate_result)
        assert isinstance(output, AdapterExplainOutput)
        assert output.decision == gate_result.decision
        assert output.raw_result == gate_result
