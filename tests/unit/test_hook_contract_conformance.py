"""Hook Contract 运行时一致性验证。

Phase 2.4: 验证已实现类与 hook_contract.py 中定义的 Protocol 在运行时一致。

测试方法：运行时结构断言 + 最小行为断言，不追求类型体操。
"""

from __future__ import annotations

from pathlib import Path


# ---------------------------------------------------------------------------
# 层 1：方法/属性存在 + 层 2：最小行为成立
# ---------------------------------------------------------------------------


class TestOpenClawAdapterConformsToHostOutputSink:
    """验证 OpenClawHostAdapter 满足 HostOutputSink 协议。"""

    def test_write_back_method_exists(self):
        """层 1：write_back 方法存在。"""
        from adapters.openclaw.adapter import OpenClawHostAdapter

        adapter = OpenClawHostAdapter()
        assert hasattr(adapter, "write_back")
        assert callable(getattr(adapter, "write_back"))

    def test_write_back_log_property_exists(self):
        """层 1：write_back_log 只读属性存在。"""
        from adapters.openclaw.adapter import OpenClawHostAdapter

        adapter = OpenClawHostAdapter()
        assert hasattr(adapter, "write_back_log")

    def test_write_back_accepts_gate_result(self):
        """层 2：write_back 可接收 GateResult。"""
        from adapters.openclaw.adapter import OpenClawHostAdapter
        from stores.protocols import GateResult

        adapter = OpenClawHostAdapter()
        result = GateResult(
            decision="Allow",
            reason="test",
            matched_rules=[],
            evidence_ids=[],
            suggestions=[],
        )
        # 不抛异常 = 契约成立
        adapter.write_back(result)
        assert len(adapter.write_back_log) == 1
        assert adapter.write_back_log[0] is result

    def test_write_back_log_is_list_of_gate_result(self):
        """层 2：write_back_log 返回 GateResult 列表。"""
        from adapters.openclaw.adapter import OpenClawHostAdapter
        from stores.protocols import GateResult

        adapter = OpenClawHostAdapter()
        result = GateResult(
            decision="Block",
            reason="test",
            matched_rules=["rule-1"],
            evidence_ids=[],
            suggestions=[],
        )
        adapter.write_back(result)
        log = adapter.write_back_log
        assert isinstance(log, list)
        assert all(isinstance(item, GateResult) for item in log)


class TestExplainBridgeConformsToExplainPayload:
    """验证 ExplainBridge 满足 ExplainPayload 协议。"""

    def test_enhance_output_method_exists(self):
        """层 1：enhance_output 方法存在。"""
        from adapters.openclaw.explain_bridge import ExplainBridge

        bridge = ExplainBridge(schema_rules_lookup={}, enable=False)
        assert hasattr(bridge, "enhance_output")
        assert callable(getattr(bridge, "enhance_output"))

    def test_enabled_property_exists(self):
        """层 1：enabled 只读属性存在（Phase 2.4 新增）。"""
        from adapters.openclaw.explain_bridge import ExplainBridge

        bridge = ExplainBridge(schema_rules_lookup={}, enable=True)
        assert hasattr(bridge, "enabled")

    def test_enabled_returns_true_when_shadow_mode_on(self):
        """层 2：enable=True 时 enabled 返回 True。"""
        from adapters.openclaw.explain_bridge import ExplainBridge

        bridge = ExplainBridge(schema_rules_lookup={}, enable=True)
        assert bridge.enabled is True

    def test_enabled_returns_false_when_shadow_mode_off(self):
        """层 2：enable=False 时 enabled 返回 False。"""
        from adapters.openclaw.explain_bridge import ExplainBridge

        bridge = ExplainBridge(schema_rules_lookup={}, enable=False)
        assert bridge.enabled is False

    def test_enabled_reflects_shadow_mode_toggle(self):
        """层 2：enabled 随开关切换同步。"""
        from adapters.openclaw.explain_bridge import ExplainBridge

        bridge = ExplainBridge(schema_rules_lookup={}, enable=False)
        assert bridge.enabled is False
        bridge.enable_shadow_mode()
        assert bridge.enabled is True
        bridge.disable_shadow_mode()
        assert bridge.enabled is False

    def test_enhance_output_returns_adapter_explain_output(self, tmp_path):
        """层 2：enhance_output 返回 AdapterExplainOutput。"""
        from adapters.openclaw.explain_bridge import AdapterExplainOutput, ExplainBridge
        from core.governance.loader import load_governance
        from core.engine.orchestrator import GovernanceEngine
        from stores.file.evidence.store import FileEvidenceStore
        from stores.file.memory.store import FileMemoryStore

        schemas_dir = Path(__file__).parent.parent.parent / "schemas" / "governance"
        schema = load_governance(schemas_dir)
        lookup = {r.id: r for r in schema.rules}
        bridge = ExplainBridge(lookup, enable=True)

        evidence_store = FileEvidenceStore(base_dir=str(tmp_path / "evidence"))
        memory_store = FileMemoryStore(base_dir=str(tmp_path / "memory"))
        engine = GovernanceEngine(
            rules=schema.rules,
            evidence_store=evidence_store,
            memory_store=memory_store,
        )

        fixtures_dir = Path(__file__).parent.parent / "fixtures"
        import yaml
        with open(fixtures_dir / "block_input.yaml") as f:
            fixture = yaml.safe_load(f)

        gate_result = engine.process_event(fixture)
        output = bridge.enhance_output(gate_result)

        assert isinstance(output, AdapterExplainOutput)


class TestGovernanceEngineConformsToGovernanceProcessor:
    """验证 GovernanceEngine 满足 GovernanceProcessor 协议。"""

    def test_process_event_method_exists(self):
        """层 1：process_event 方法存在。"""
        from core.engine.orchestrator import GovernanceEngine

        assert hasattr(GovernanceEngine, "process_event")
        assert callable(getattr(GovernanceEngine, "process_event"))

    def test_process_event_accepts_dict_and_returns_gate_result(self, tmp_path):
        """层 2：process_event 接收 dict 返回 GateResult。"""
        from core.engine.orchestrator import GovernanceEngine
        from core.governance.loader import load_governance
        from stores.file.evidence.store import FileEvidenceStore
        from stores.file.memory.store import FileMemoryStore
        from stores.protocols import GateResult

        schemas_dir = Path(__file__).parent.parent.parent / "schemas" / "governance"
        schema = load_governance(schemas_dir)
        evidence_store = FileEvidenceStore(base_dir=str(tmp_path / "evidence"))
        memory_store = FileMemoryStore(base_dir=str(tmp_path / "memory"))
        engine = GovernanceEngine(
            rules=schema.rules,
            evidence_store=evidence_store,
            memory_store=memory_store,
        )

        fixtures_dir = Path(__file__).parent.parent / "fixtures"
        import yaml
        with open(fixtures_dir / "block_input.yaml") as f:
            fixture = yaml.safe_load(f)

        result = engine.process_event(fixture)

        assert isinstance(result, GateResult)


class TestShadowRuntimeConformsToShadowOutput:
    """验证 ShadowRuntime 满足 ShadowOutput 协议。"""

    def test_process_and_write_method_exists(self):
        """层 1：process_and_write 方法存在。"""
        from adapters.openclaw.shadow_runtime import ShadowRuntime

        assert hasattr(ShadowRuntime, "process_and_write")
        assert callable(getattr(ShadowRuntime, "process_and_write"))

    def _make_runtime(self, tmp_path, enable_bridge=True):
        """辅助：创建 ShadowRuntime。"""
        from adapters.openclaw.adapter import OpenClawHostAdapter
        from adapters.openclaw.explain_bridge import ExplainBridge
        from adapters.openclaw.shadow_runtime import ShadowRuntime
        from core.engine.orchestrator import GovernanceEngine
        from core.governance.loader import load_governance
        from stores.file.evidence.store import FileEvidenceStore
        from stores.file.memory.store import FileMemoryStore

        schemas_dir = Path(__file__).parent.parent.parent / "schemas" / "governance"
        schema = load_governance(schemas_dir)
        lookup = {r.id: r for r in schema.rules}
        bridge = ExplainBridge(lookup, enable=enable_bridge)

        evidence_store = FileEvidenceStore(base_dir=str(tmp_path / "evidence"))
        memory_store = FileMemoryStore(base_dir=str(tmp_path / "memory"))
        engine = GovernanceEngine(
            rules=schema.rules,
            evidence_store=evidence_store,
            memory_store=memory_store,
        )
        adapter = OpenClawHostAdapter()

        return ShadowRuntime(
            engine=engine,
            adapter=adapter,
            explain_bridge=bridge,
        ), adapter

    def test_process_and_write_accepts_dict_returns_shadow_run_result(self, tmp_path):
        """层 2：process_and_write 接收 dict 返回 ShadowRunResult。"""
        from adapters.openclaw.shadow_runtime import ShadowRunResult

        runtime, _ = self._make_runtime(tmp_path)

        fixtures_dir = Path(__file__).parent.parent / "fixtures"
        import yaml
        with open(fixtures_dir / "block_input.yaml") as f:
            fixture = yaml.safe_load(f)

        result = runtime.process_and_write(fixture)

        assert isinstance(result, ShadowRunResult)

    def test_process_and_write_records_to_adapter_write_back(self, tmp_path):
        """层 2：process_and_write 内部调用 adapter.write_back。"""
        runtime, adapter = self._make_runtime(tmp_path)

        fixtures_dir = Path(__file__).parent.parent / "fixtures"
        import yaml
        with open(fixtures_dir / "allow_input.yaml") as f:
            fixture = yaml.safe_load(f)

        runtime.process_and_write(fixture)

        assert len(adapter.write_back_log) == 1


class TestExampleSatisfiesAllProtocols:
    """验证 example 中构建的对象组合符合协议视角。

    不复用 example 文件本身，而是复现其最小对象创建链路。
    """

    def _build_example_objects(self, tmp_path):
        """复现 example 的最小对象创建链路。"""
        from adapters.openclaw.adapter import OpenClawHostAdapter
        from adapters.openclaw.explain_bridge import ExplainBridge
        from adapters.openclaw.shadow_runtime import ShadowRuntime
        from core.engine.orchestrator import GovernanceEngine
        from core.governance.loader import load_governance
        from stores.file.evidence.store import FileEvidenceStore
        from stores.file.memory.store import FileMemoryStore

        schemas_dir = Path(__file__).parent.parent.parent / "schemas" / "governance"
        schema = load_governance(schemas_dir)
        lookup = {r.id: r for r in schema.rules}

        evidence_store = FileEvidenceStore(base_dir=str(tmp_path / "evidence"))
        memory_store = FileMemoryStore(base_dir=str(tmp_path / "memory"))
        engine = GovernanceEngine(
            rules=schema.rules,
            evidence_store=evidence_store,
            memory_store=memory_store,
        )
        adapter = OpenClawHostAdapter()
        bridge = ExplainBridge(lookup, enable=True)
        runtime = ShadowRuntime(
            engine=engine,
            adapter=adapter,
            explain_bridge=bridge,
        )

        return engine, adapter, bridge, runtime

    def test_example_engine_satisfies_governance_processor(self, tmp_path):
        """example 中的 engine 满足 GovernanceProcessor。"""
        from adapters.openclaw.hook_contract import GovernanceProcessor

        engine, _, _, _ = self._build_example_objects(tmp_path)
        assert hasattr(engine, "process_event")
        assert hasattr(GovernanceProcessor, "process_event")

    def test_example_adapter_satisfies_host_output_sink(self, tmp_path):
        """example 中的 adapter 满足 HostOutputSink。"""
        from adapters.openclaw.hook_contract import HostOutputSink

        _, adapter, _, _ = self._build_example_objects(tmp_path)
        assert hasattr(adapter, "write_back")
        assert hasattr(adapter, "write_back_log")
        assert hasattr(HostOutputSink, "write_back")
        assert hasattr(HostOutputSink, "write_back_log")

    def test_example_bridge_satisfies_explain_payload(self, tmp_path):
        """example 中的 bridge 满足 ExplainPayload。"""
        from adapters.openclaw.hook_contract import ExplainPayload

        _, _, bridge, _ = self._build_example_objects(tmp_path)
        assert hasattr(bridge, "enhance_output")
        assert hasattr(bridge, "enabled")
        assert hasattr(ExplainPayload, "enhance_output")
        assert hasattr(ExplainPayload, "enabled")

    def test_example_runtime_satisfies_shadow_output(self, tmp_path):
        """example 中的 runtime 满足 ShadowOutput。"""
        from adapters.openclaw.hook_contract import ShadowOutput

        _, _, _, runtime = self._build_example_objects(tmp_path)
        assert hasattr(runtime, "process_and_write")
        assert hasattr(ShadowOutput, "process_and_write")

    def test_example_objects_can_process_block_scenario(self, tmp_path):
        """层 2：example 构建的对象组合可处理 Block 场景。"""
        from adapters.openclaw.shadow_runtime import ShadowRunResult
        from stores.protocols import GateResult

        _, adapter, _, runtime = self._build_example_objects(tmp_path)

        fixtures_dir = Path(__file__).parent.parent / "fixtures"
        import yaml
        with open(fixtures_dir / "block_input.yaml") as f:
            fixture = yaml.safe_load(f)

        result = runtime.process_and_write(fixture)

        # 验证四组件闭合
        assert isinstance(result, ShadowRunResult)
        assert isinstance(result.gate_result, GateResult)
        assert result.enhanced_output is not None
        assert result.enhanced_output.explanation_bundle is not None
        assert len(adapter.write_back_log) == 1
