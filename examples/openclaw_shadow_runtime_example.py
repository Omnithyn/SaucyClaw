"""Shadow Runtime 接入示例。

Phase 2.3: 演示外部调用方如何使用 SaucyClaw 治理链路。

运行方式：
    python -m examples.openclaw_shadow_runtime_example

演示链路：
1. load_governance() → 加载治理规则
2. 创建 GovernanceEngine
3. 创建 OpenClawHostAdapter
4. 创建 ExplainBridge（Shadow Mode）
5. 创建 ShadowRuntime
6. process_and_write(raw_event) → 执行并回写
"""

from __future__ import annotations

import sys
from pathlib import Path

# 确保项目根目录在 Python 路径中
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.governance.loader import load_governance
from core.engine.orchestrator import GovernanceEngine
from adapters.openclaw.adapter import OpenClawHostAdapter
from adapters.openclaw.explain_bridge import ExplainBridge
from adapters.openclaw.shadow_runtime import ShadowRuntime
from stores.file.evidence.store import FileEvidenceStore
from stores.file.memory.store import FileMemoryStore
import tempfile


def main() -> None:
    """演示最小治理链路。"""
    schemas_dir = PROJECT_ROOT / "schemas" / "governance"
    fixtures_dir = PROJECT_ROOT / "tests" / "fixtures"

    # 1. 加载治理规则
    print("=" * 60)
    print("1. 加载治理规则")
    print("=" * 60)
    schema = load_governance(schemas_dir)
    print(f"   规则数量: {len(schema.rules)}")
    print(f"   角色数量: {len(schema.roles)}")
    print(f"   任务类型: {len(schema.task_types)}")

    # 2. 创建存储
    with tempfile.TemporaryDirectory() as tmp_dir:
        evidence_store = FileEvidenceStore(base_dir=f"{tmp_dir}/evidence")
        memory_store = FileMemoryStore(base_dir=f"{tmp_dir}/memory")

        # 3. 创建治理引擎
        print("\n" + "=" * 60)
        print("2. 创建治理引擎")
        print("=" * 60)
        engine = GovernanceEngine(
            rules=schema.rules,
            evidence_store=evidence_store,
            memory_store=memory_store,
        )
        print("   引擎创建完成")

        # 4. 创建 Mock Adapter
        print("\n" + "=" * 60)
        print("3. 创建 Mock Adapter")
        print("=" * 60)
        adapter = OpenClawHostAdapter()
        print("   Adapter 创建完成")

        # 5. 创建 ExplainBridge（开启 Shadow Mode）
        print("\n" + "=" * 60)
        print("4. 创建 ExplainBridge（Shadow Mode 开启）")
        print("=" * 60)
        lookup = {r.id: r for r in schema.rules}
        bridge = ExplainBridge(lookup, enable=True)
        print("   Bridge 创建完成，Shadow Mode 已开启")

        # 6. 创建 ShadowRuntime
        print("\n" + "=" * 60)
        print("5. 创建 ShadowRuntime")
        print("=" * 60)
        runtime = ShadowRuntime(
            engine=engine,
            adapter=adapter,
            explain_bridge=bridge,
        )
        print("   ShadowRuntime 创建完成")

        # 7. 执行 Block 场景
        import yaml

        print("\n" + "=" * 60)
        print("6. 执行 Block 场景")
        print("=" * 60)
        block_fixture = fixtures_dir / "block_input.yaml"
        with open(block_fixture) as f:
            block_event = yaml.safe_load(f)

        block_result = runtime.process_and_write(block_event)
        print(f"   决策: {block_result.gate_result.decision}")
        print(f"   匹配规则: {block_result.gate_result.matched_rules}")
        print(f"   增强输出: {block_result.enhanced_output is not None}")
        if block_result.enhanced_output:
            bundle = block_result.enhanced_output.explanation_bundle
            if bundle:
                print(f"   可读摘要: {bundle.readable_summary}")
                print(f"   风险摘要: {bundle.risk_summary}")

        # 8. 执行 Allow 场景
        print("\n" + "=" * 60)
        print("7. 执行 Allow 场景")
        print("=" * 60)
        allow_fixture = fixtures_dir / "allow_input.yaml"
        with open(allow_fixture) as f:
            allow_event = yaml.safe_load(f)

        allow_result = runtime.process_and_write(allow_event)
        print(f"   决策: {allow_result.gate_result.decision}")
        print(f"   匹配规则: {allow_result.gate_result.matched_rules}")
        print(f"   增强输出: {allow_result.enhanced_output is not None}")
        if allow_result.enhanced_output:
            bundle = allow_result.enhanced_output.explanation_bundle
            if bundle:
                print(f"   可读摘要: {bundle.readable_summary}")
                print(f"   风险摘要: {bundle.risk_summary}")

        # 9. 验证 Adapter 日志
        print("\n" + "=" * 60)
        print("8. 验证 Adapter 回写日志")
        print("=" * 60)
        print(f"   write_back_log 数量: {len(adapter.write_back_log)}")
        for i, log in enumerate(adapter.write_back_log):
            print(f"   [{i}] {log.decision} - {log.reason}")

        print("\n" + "=" * 60)
        print("演示完成")
        print("=" * 60)


if __name__ == "__main__":
    main()
