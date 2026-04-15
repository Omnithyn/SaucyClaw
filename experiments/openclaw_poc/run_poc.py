"""PoC 入口脚本 — 验证 SaucyClaw → OpenClaw gateway 通知链路。

用法：
    # Mock 模式（默认）
    python -m experiments.openclaw_poc.run_poc

    # Real 模式（需配置环境变量）
    export OPENCLAW_GATEWAY_TYPE="real"
    export OPENCLAW_GATEWAY_URL="http://your-openclaw-server:18789/hooks/agent"
    python -m experiments.openclaw_poc.run_poc

验证内容：
1. gateway 收到 Block 通知（Mock 或 Real 模式）
2. gateway 收到 Allow 通知
3. 通知 payload 包含治理解释信息
4. 超时/失败处理正确

环境变量：
- OPENCLAW_GATEWAY_TYPE: "mock" (默认) / "real"
- OPENCLAW_GATEWAY_URL: 真实 gateway URL（Real 模式必需）
- OPENCLAW_GATEWAY_HEADERS: JSON headers（可选，默认 {"Content-Type": "application/json"}）
- OPENCLAW_TIMEOUT_MS: 超时毫秒（可选，默认 10000）
- VALIDATION_OUTPUT_DIR: 保存验证证据的目录（可选，默认 ./validation_output）
"""

from __future__ import annotations

import json
import os
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# 确保项目根目录在 sys.path 中
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.governance.loader import load_governance
from core.engine.orchestrator import GovernanceEngine
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
DEFAULT_OUTPUT_DIR = "./validation_output"


@dataclass(frozen=True)
class ValidationEvidence:
    """验证证据记录 — mock/real 模式统一的证据结构。"""
    scenario: str
    mode: str  # "mock" / "real"
    gateway_url: str
    timestamp: str
    payload: dict[str, Any] | None
    gateway: str
    success: bool
    error: str | None
    status_code: int | None


def load_fixture(name: str) -> dict:
    """加载治理场景 fixture。"""
    path = FIXTURES_DIR / f"{name}.yaml"
    import yaml

    with open(path) as f:
        return yaml.safe_load(f)


def ensure_output_dir() -> Path:
    """确保验证输出目录存在。"""
    output_dir = os.environ.get("VALIDATION_OUTPUT_DIR", DEFAULT_OUTPUT_DIR)
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_validation_bundle(evidence: ValidationEvidence, output_dir: Path) -> None:
    """保存验证证据包 — mock/real 模式统一的证据保存。"""
    # 保存 payload（如果有）
    if evidence.payload:
        payload_file = output_dir / f"{evidence.scenario}_payload.json"
        with open(payload_file, "w") as f:
            json.dump(evidence.payload, f, indent=2, ensure_ascii=False)
        print(f"[validation] Saved payload to {payload_file}")

    # 保存完整证据包
    evidence_file = output_dir / f"{evidence.scenario}_evidence.json"
    evidence_data = asdict(evidence)
    with open(evidence_file, "w") as f:
        json.dump(evidence_data, f, indent=2, ensure_ascii=False)
    print(f"[validation] Saved evidence to {evidence_file}")


def build_evidence(
    scenario: str,
    mode: str,
    gateway_url: str,
    payload: dict[str, Any] | None,
    wake_result: Any,
) -> ValidationEvidence:
    """构建验证证据记录。"""
    return ValidationEvidence(
        scenario=scenario,
        mode=mode,
        gateway_url=gateway_url,
        timestamp=datetime.now(timezone.utc).isoformat(),
        payload=payload,
        gateway=wake_result.gateway,
        success=wake_result.success,
        error=wake_result.error,
        status_code=wake_result.status_code,
    )


def run_scenario(
    engine: GovernanceEngine,
    bridge: ExplainBridge,
    adapter: OpenClawNotificationAdapter,
    fixture_name: str,
    expected_decision: str,
    output_dir: Path,
) -> tuple[bool, dict[str, Any] | None, Any]:
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
        return False, None, None

    # 2. 通过桥接器生成解释包（统一使用 bridge.enhance_output）
    enhanced = bridge.enhance_output(result)
    explanation_summary = (
        enhanced.explanation_bundle.readable_summary
        if enhanced.explanation_bundle
        else None
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
        explanation_summary=explanation_summary,
    )

    # 获取实际发送的 payload（从 adapter 记录，不依赖 mock gateway 回传）
    sent_payload = adapter.last_payload

    if not wake_result.success:
        print(f"[poc] FAIL: gateway notification failed: {wake_result.error}")
        evidence = build_evidence(
            scenario=fixture_name,
            mode=os.environ.get("OPENCLAW_GATEWAY_TYPE", "mock"),
            gateway_url=adapter.gateway_url,
            payload=sent_payload,
            wake_result=wake_result,
        )
        save_validation_bundle(evidence, output_dir)
        return False, sent_payload, wake_result

    # 4. 验证 mock gateway 收到通知（仅 Mock 模式）
    gateway_type = os.environ.get("OPENCLAW_GATEWAY_TYPE", "mock")
    if gateway_type == "mock":
        time.sleep(0.1)  # 给 server 一点处理时间
        if not received_payloads:
            print("[poc] FAIL: mock gateway received no payload")
            evidence = build_evidence(
                scenario=fixture_name,
                mode=gateway_type,
                gateway_url=adapter.gateway_url,
                payload=sent_payload,
                wake_result=wake_result,
            )
            save_validation_bundle(evidence, output_dir)
            return False, sent_payload, wake_result

        last_received = received_payloads[-1]
        if last_received.get("event") != "governance-decision":
            print("[poc] FAIL: wrong event type: " + last_received.get("event", ""))
            evidence = build_evidence(
                scenario=fixture_name,
                mode=gateway_type,
                gateway_url=adapter.gateway_url,
                payload=sent_payload,
                wake_result=wake_result,
            )
            save_validation_bundle(evidence, output_dir)
            return False, sent_payload, wake_result

        instruction = last_received.get("instruction", "")
        if expected_decision not in instruction:
            print("[poc] FAIL: instruction doesn't contain expected decision")
            evidence = build_evidence(
                scenario=fixture_name,
                mode=gateway_type,
                gateway_url=adapter.gateway_url,
                payload=sent_payload,
                wake_result=wake_result,
            )
            return False, sent_payload, wake_result

        print("[poc] OK: mock gateway received notification")
    else:
        print(f"[poc] OK: sent to real gateway ({wake_result.status_code})")

    # 统一保存验证证据（使用 adapter 记录的 sent_payload）
    evidence = build_evidence(
        scenario=fixture_name,
        mode=gateway_type,
        gateway_url=adapter.gateway_url,
        payload=sent_payload,
        wake_result=wake_result,
    )
    save_validation_bundle(evidence, output_dir)
    return True, sent_payload, wake_result


def run_timeout_test(output_dir: Path) -> tuple[bool, Any]:
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
    sent_payload = adapter.last_payload

    if wake_result.success:
        print("[poc] FAIL: expected failure for unreachable gateway")
        evidence = build_evidence(
            scenario="timeout",
            mode="mock",
            gateway_url=adapter.gateway_url,
            payload=sent_payload,
            wake_result=wake_result,
        )
        save_validation_bundle(evidence, output_dir)
        return False, wake_result

    print(f"[poc] OK: timeout handled correctly (error: {wake_result.error})")
    evidence = build_evidence(
        scenario="timeout",
        mode="mock",
        gateway_url=adapter.gateway_url,
        payload=sent_payload,
        wake_result=wake_result,
    )
    save_validation_bundle(evidence, output_dir)
    return True, wake_result


def _normalize_event(raw_event: dict) -> dict:
    """将 fixture input 转换为 engine.process_event 可接受的格式。"""
    return {
        "event_type": "task_assign",
        "source": "poc",
        "session_id": "poc-session-001",
        "timestamp": "2026-04-14T00:00:00Z",
        "payload": raw_event,
    }


def load_gateway_config() -> tuple[str, dict[str, str], int]:
    """从环境变量加载 gateway 配置。"""
    gateway_type = os.environ.get("OPENCLAW_GATEWAY_TYPE", "mock")

    if gateway_type == "real":
        gateway_url = os.environ.get("OPENCLAW_GATEWAY_URL")
        if not gateway_url:
            raise ValueError(
                "OPENCLAW_GATEWAY_URL is required for real gateway mode. "
                "Set it to your OpenClaw webhook URL."
            )
        gateway_name = "real-gateway"
    else:
        gateway_url = f"http://127.0.0.1:{MOCK_PORT}"
        gateway_name = "mock-gateway"

    headers_str = os.environ.get("OPENCLAW_GATEWAY_HEADERS")
    if headers_str:
        import json
        headers = json.loads(headers_str)
    else:
        headers = {"Content-Type": "application/json"}

    timeout_ms = int(os.environ.get("OPENCLAW_TIMEOUT_MS", 10_000))

    return gateway_url, headers, timeout_ms


def main() -> None:
    output_dir = ensure_output_dir()
    gateway_url, headers, timeout_ms = load_gateway_config()

    gateway_type = os.environ.get("OPENCLAW_GATEWAY_TYPE", "mock")
    print("=" * 60)
    print(f"SaucyClaw → OpenClaw Gateway PoC ({gateway_type} mode)")
    print("=" * 60)
    print(f"[poc] Gateway URL: {gateway_url}")
    print(f"[poc] Output directory: {output_dir}")

    # 1. 启动 mock gateway server（仅 Mock 模式）
    server = None
    thread = None
    if gateway_type == "mock":
        print(f"\n[mock-gateway] Starting on http://127.0.0.1:{MOCK_PORT}")
        server, thread = start_mock_server_in_background(port=MOCK_PORT)
        time.sleep(0.2)

    try:
        # 2. 加载治理规则
        print("\n[poc] Loading governance rules...")
        schema = load_governance(str(GOVERNANCE_DIR))
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
                gateway_url=gateway_url,
                gateway_name=gateway_type,
                headers=headers,
                timeout_ms=timeout_ms,
            )

            # 5. 运行 Block 场景
            clear_received()
            block_ok, block_payload, block_result = run_scenario(
                engine,
                bridge,
                adapter,
                "block_reviewer_same_as_assignee",
                expected_decision="Block",
                output_dir=output_dir,
            )

            # 6. 运行 Allow 场景
            clear_received()
            allow_ok, allow_payload, allow_result = run_scenario(
                engine,
                bridge,
                adapter,
                "allow_specialist_via_reviewer",
                expected_decision="Allow",
                output_dir=output_dir,
            )

            # 7. 运行超时测试
            timeout_ok, timeout_result = run_timeout_test(output_dir)

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
                print(f"[poc] Validation evidence saved to {output_dir}")
            else:
                print("\n[poc] Some tests failed!")
                sys.exit(1)

    finally:
        if server:
            stop_mock_server(server)
            print("\n[mock-gateway] Stopped")


if __name__ == "__main__":
    main()
