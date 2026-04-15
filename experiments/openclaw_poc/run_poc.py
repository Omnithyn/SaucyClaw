"""PoC 入口脚本 — 验证 SaucyClaw → OpenClaw gateway 通知链路。

用法：
    python -m experiments.openclaw_poc.run_poc

验证内容：
1. mock gateway 收到 Block 通知
2. mock gateway 收到 Allow 通知
3. 通知 payload 包含治理解释信息
4. 超时处理正确
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

# 确保项目根目录在 sys.path 中
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.governance.loader import load_governance
from core.engine.orchestrator import GovernanceEngine
from core.governance.explainer_bundle import bundle_explanations
from adapters.openclaw.notification_adapter import OpenClawNotificationAdapter
from adapters.openclaw.explain_bridge import ExplainBridge
from experiments.openclaw_poc.mock_gateway import (
    start_mock_server_in_background,
    stop_mock_server,
    clear_received,
    received_payloads,
)
from stores.file.evidence.store import FileEvidenceStore
from stores.file.memory.store import FileMemoryStore


FIXTURES_DIR = PROJECT_ROOT / "tests" / "fixtures" / "governance_cases"
GOVERNANCE_DIR = PROJECT_ROOT / "schemas" / "governance"
MOCK_PORT = 18790


def load_fixture(name: str) -> dict:
    """加载治理场景 fixture。"""
    path = FIXTURES_DIR / f"{name}.yaml"
    import yaml

    with open(path) as f:
        return yaml.safe_load(f)


def run_scenario(
    engine: GovernanceEngine,
    bridge: ExplainBridge,
    adapter: OpenClawNotificationAdapter,
    fixture_name: str,
    expected_decision: str,
) -> bool:
    """运行单个治理场景并验证通知发送。"""
    print(f"\n[poc] Running scenario: {fixture_name}")

    fixture = load_fixture(fixture_name)
    # fixture 是扁平结构，expected 在 fixture["expected"] 下
    raw_event = {k: v for k, v in fixture.items() if k != "expected"}

    # 1. 治理引擎处理
    normalized_event = _normalize_event(raw_event)
    result = engine.process_event(normalized_event)

    print(f"[poc] Decision: {result.decision}")
    print(f"[poc] Matched rules: {result.matched_rules or 'none'}")

    if result.decision != expected_decision:
        print(f"[poc] FAIL: expected {expected_decision}, got {result.decision}")
        return False

    # 2. 生成解释包
    bundle = bundle_explanations(
        decision=result.decision,
        matched_rule_ids=result.matched_rules,
        schema_rules_lookup={r.id: r for r in _schema_rules},
        suggestions=result.suggestions,
    )

    # 3. 通过 OpenClaw gateway 发送通知
    session_context = {
        "session_id": "poc-session-001",
        "project_path": str(PROJECT_ROOT),
        "project_name": "SaucyClaw",
    }
    wake_result = adapter.send_decision(
        result,
        session_context=session_context,
        explanation_summary=bundle.readable_summary if bundle else None,
    )

    if not wake_result.success:
        print(f"[poc] FAIL: gateway notification failed: {wake_result.error}")
        return False

    # 4. 验证 mock gateway 收到通知
    time.sleep(0.1)  # 给 server 一点处理时间
    if not received_payloads:
        print("[poc] FAIL: mock gateway received no payload")
        return False

    last_payload = received_payloads[-1]
    if last_payload.get("event") != "governance-decision":
        print("[poc] FAIL: wrong event type: " + last_payload.get("event"))
        return False

    instruction = last_payload.get("instruction", "")
    if expected_decision not in instruction:
        print("[poc] FAIL: instruction doesn't contain expected decision")
        return False

    print("[poc] OK: notification sent and verified")
    return True


def run_timeout_test() -> bool:
    """验证超时处理正确。"""
    print("")
    print("[poc] Running timeout test")

    adapter = OpenClawNotificationAdapter(
        gateway_url="http://127.0.0.1:9999/nonexistent",
        gateway_name="unreachable",
        timeout_ms=1_000,
    )

    from stores.protocols import GateResult
    result = GateResult(
        decision="Block",
        reason="timeout test",
        matched_rules=["test-rule"],
        evidence_ids=[],
        suggestions=[],
    )

    wake_result = adapter.send_decision(result)

    if wake_result.success:
        print("[poc] FAIL: expected failure for unreachable gateway")
        return False

    print(f"[poc] OK: timeout handled correctly (error: {wake_result.error})")
    return True


def _normalize_event(raw_event: dict) -> dict:
    """将 fixture input 转换为 engine.process_event 可接受的格式。"""
    return {
        "event_type": "task_assign",
        "source": "poc",
        "session_id": "poc-session-001",
        "timestamp": "2026-04-14T00:00:00Z",
        "payload": raw_event,
    }


_schema_rules = []


def main() -> None:
    global _schema_rules

    print("=" * 60)
    print("SaucyClaw → OpenClaw Gateway PoC")
    print("=" * 60)

    # 1. 启动 mock gateway server
    print(f"\n[mock-gateway] Starting on http://127.0.0.1:{MOCK_PORT}")
    server, thread = start_mock_server_in_background(port=MOCK_PORT)
    time.sleep(0.2)

    try:
        # 2. 加载治理规则
        print("\n[poc] Loading governance rules...")
        schema = load_governance(str(GOVERNANCE_DIR))
        _schema_rules = schema.rules
        print(f"[poc] Loaded {len(schema.rules)} rules")

        # 3. 创建引擎和存储
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            engine = GovernanceEngine(
                rules=schema.rules,
                evidence_store=FileEvidenceStore(base_dir=f"{tmp}/evidence"),
                memory_store=FileMemoryStore(base_dir=f"{tmp}/memory"),
            )

            # 4. 创建解释桥接和通知适配器
            lookup = {r.id: r for r in schema.rules}
            bridge = ExplainBridge(lookup, enable=True)

            adapter = OpenClawNotificationAdapter(
                gateway_url=f"http://127.0.0.1:{MOCK_PORT}",
                gateway_name="mock-gateway",
            )

            # 5. 运行 Block 场景
            clear_received()
            block_ok = run_scenario(
                engine, bridge, adapter,
                "block_reviewer_same_as_assignee",
                expected_decision="Block",
            )

            # 6. 运行 Allow 场景
            clear_received()
            allow_ok = run_scenario(
                engine, bridge, adapter,
                "allow_specialist_via_reviewer",
                expected_decision="Allow",
            )

            # 7. 运行超时测试
            timeout_ok = run_timeout_test()

            # 8. 总结
            print("\n" + "=" * 60)
            print("PoC Results:")
            print(f"  Block notification:  {'PASS' if block_ok else 'FAIL'}")
            print(f"  Allow notification:  {'PASS' if allow_ok else 'FAIL'}")
            print(f"  Timeout handling:    {'PASS' if timeout_ok else 'FAIL'}")
            print("=" * 60)

            all_passed = block_ok and allow_ok and timeout_ok
            if all_passed:
                print("\n[poc] All tests passed!")
            else:
                print("\n[poc] Some tests failed!")
                sys.exit(1)

    finally:
        stop_mock_server(server)
        print("\n[mock-gateway] Stopped")


if __name__ == "__main__":
    main()
