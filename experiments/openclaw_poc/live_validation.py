"""Live Validation Runner — 真实 OpenClaw gateway 验证。

使用 OpenClawHooksAdapter 通过 /hooks/agent endpoint 发送治理决策通知。

用法：
    # 方式 1：使用配置文件 ~/.saucyclaw/saucyclaw.json
    python -m experiments.openclaw_poc.live_validation

    # 方式 2：使用环境变量
    export SAUCYCLAW_GATEWAY_URL="http://your-gateway/hooks/agent"
    export SAUCYCLAW_HOOKS_TOKEN="your-token"
    python -m experiments.openclaw_poc.live_validation

配置文件结构 (~/.saucyclaw/saucyclaw.json)：
{
  "notification": {
    "gateway_url": "http://your-gateway/hooks/agent",
    "hooks_token": "your-token",
    "timeout_ms": 10000
  }
}

环境变量（优先级高于配置文件）：
- SAUCYCLAW_GATEWAY_URL: hooks endpoint URL
- SAUCYCLAW_HOOKS_TOKEN: hooks 认证 token
- SAUCYCLAW_TIMEOUT_MS: 超时毫秒（默认 10000）
- LIVE_VALIDATION_OUTPUT_DIR: 验证证据输出目录（默认 ./real_validation_output）
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.governance.loader import load_governance
from core.engine.orchestrator import GovernanceEngine
from adapters.openclaw.hooks_adapter import OpenClawHooksAdapter, HooksWakeResult
from adapters.openclaw.explain_bridge import ExplainBridge
from core.config import load_notification_config, ensure_config_exists
from stores.file.evidence.store import FileEvidenceStore
from stores.file.memory.store import FileMemoryStore


FIXTURES_DIR = PROJECT_ROOT / "tests" / "fixtures" / "governance_cases"
GOVERNANCE_DIR = PROJECT_ROOT / "schemas" / "governance"
DEFAULT_OUTPUT_DIR = "./real_validation_output"


@dataclass(frozen=True)
class LiveValidationEvidence:
    """真实 Gateway 验证证据。"""
    scenario: str
    gateway_url: str
    timestamp: str
    payload: dict[str, Any] | None
    gateway: str
    success: bool
    run_id: str | None = None
    error: str | None = None
    status_code: int | None = None
    mode: str = "live"


def load_fixture(name: str) -> dict:
    """加载治理场景 fixture。"""
    import yaml
    path = FIXTURES_DIR / f"{name}.yaml"
    with open(path) as f:
        return yaml.safe_load(f)


def ensure_output_dir() -> Path:
    """确保验证输出目录存在。"""
    output_dir = os.environ.get("LIVE_VALIDATION_OUTPUT_DIR", DEFAULT_OUTPUT_DIR)
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_evidence(evidence: LiveValidationEvidence, output_dir: Path) -> None:
    """保存验证证据。"""
    if evidence.payload:
        payload_file = output_dir / f"{evidence.scenario}_payload.json"
        with open(payload_file, "w") as f:
            json.dump(evidence.payload, f, indent=2, ensure_ascii=False)
        print(f"[live] Saved payload to {payload_file}")

    evidence_file = output_dir / f"{evidence.scenario}_evidence.json"
    evidence_data = asdict(evidence)
    with open(evidence_file, "w") as f:
        json.dump(evidence_data, f, indent=2, ensure_ascii=False)
    print(f"[live] Saved evidence to {evidence_file}")


def build_evidence(
    scenario: str,
    gateway_url: str,
    payload: dict[str, Any] | None,
    wake_result: HooksWakeResult,
) -> LiveValidationEvidence:
    """构建验证证据。"""
    return LiveValidationEvidence(
        scenario=scenario,
        gateway_url=gateway_url,
        timestamp=datetime.now(timezone.utc).isoformat(),
        payload=payload,
        gateway=wake_result.gateway,
        success=wake_result.success,
        run_id=wake_result.run_id,
        error=wake_result.error,
        status_code=wake_result.status_code,
    )


def run_scenario(
    engine: GovernanceEngine,
    bridge: ExplainBridge,
    adapter: OpenClawHooksAdapter,
    fixture_name: str,
    expected_decision: str,
    output_dir: Path,
) -> tuple[bool, dict[str, Any] | None, HooksWakeResult]:
    """运行单个治理场景并验证 hooks 发送。"""
    print(f"\n[live] Running scenario: {fixture_name}")

    fixture = load_fixture(fixture_name)
    raw_event = {k: v for k, v in fixture.items() if k != "expected"}

    # 1. 治理引擎处理
    normalized_event = {
        "event_type": "task_assign",
        "source": "live_validation",
        "session_id": "live-session-001",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": raw_event,
    }
    result = engine.process_event(normalized_event)

    print(f"[live] Decision: {result.decision}")
    print(f"[live] Matched rules: {result.matched_rules or 'none'}")

    if result.decision != expected_decision:
        print(f"[live] FAIL: expected {expected_decision}, got {result.decision}")
        evidence = LiveValidationEvidence(
            scenario=fixture_name,
            gateway_url=adapter.gateway_url,
            timestamp=datetime.now(timezone.utc).isoformat(),
            payload=None,
            gateway="",
            success=False,
            error=f"Decision mismatch: expected {expected_decision}, got {result.decision}",
        )
        save_evidence(evidence, output_dir)
        return False, None, None

    # 2. 生成解释
    enhanced = bridge.enhance_output(result)
    explanation_summary = (
        enhanced.explanation_bundle.readable_summary
        if enhanced.explanation_bundle
        else None
    )

    # 3. 发送通知
    wake_result = adapter.send_decision(result, explanation_summary=explanation_summary)
    sent_payload = adapter.last_payload

    if not wake_result.success:
        print(f"[live] FAIL: hooks notification failed: {wake_result.error}")
        evidence = build_evidence(fixture_name, adapter.gateway_url, sent_payload, wake_result)
        save_evidence(evidence, output_dir)
        return False, sent_payload, wake_result

    print(f"[live] OK: hooks sent successfully (runId: {wake_result.run_id})")
    evidence = build_evidence(fixture_name, adapter.gateway_url, sent_payload, wake_result)
    save_evidence(evidence, output_dir)
    return True, sent_payload, wake_result


def run_failure_test(adapter: OpenClawHooksAdapter, output_dir: Path) -> tuple[bool, HooksWakeResult]:
    """运行失败路径测试（无效 token）。"""
    print("\n[live] Running failure test (invalid token)")

    # 创建一个使用无效 token 的 adapter
    bad_adapter = OpenClawHooksAdapter(
        gateway_url=adapter.gateway_url,
        token="invalid-token-for-testing",
        gateway_name="test-invalid",
    )

    from stores.protocols import GateResult
    result = GateResult(
        decision="Block",
        reason="failure test",
        matched_rules=["test-rule"],
        evidence_ids=[],
        suggestions=[],
    )

    wake_result = bad_adapter.send_decision(result)
    sent_payload = bad_adapter.last_payload

    if wake_result.success:
        print("[live] FAIL: expected failure with invalid token")
        evidence = build_evidence("invalid_token_test", bad_adapter.gateway_url, sent_payload, wake_result)
        save_evidence(evidence, output_dir)
        return False, wake_result

    print(f"[live] OK: correctly rejected (error: {wake_result.error}, status: {wake_result.status_code})")
    evidence = build_evidence("invalid_token_test", bad_adapter.gateway_url, sent_payload, wake_result)
    save_evidence(evidence, output_dir)
    return True, wake_result


def main() -> None:
    """主函数。"""
    # 从配置文件或环境变量加载配置
    config = load_notification_config()

    gateway_url = config.gateway_url
    token = config.hooks_token

    if not gateway_url or not token:
        print("ERROR: Missing gateway configuration")
        print("")
        print("Please configure either:")
        print("  1. Config file: ~/.saucyclaw/saucyclaw.json")
        print("  2. Environment variables:")
        print("     SAUCYCLAW_GATEWAY_URL")
        print("     SAUCYCLAW_HOOKS_TOKEN")
        print("")
        # 创建配置模板
        config_path = ensure_config_exists()
        print(f"Config template created at: {config_path}")
        print("Please fill in gateway_url and hooks_token")
        sys.exit(1)

    timeout_ms = config.timeout_ms
    output_dir = ensure_output_dir()

    print("=" * 60)
    print("OpenClaw Live Validation (hooks/agent)")
    print("=" * 60)
    print(f"[live] Gateway: configured")
    print(f"[live] Output directory: {output_dir}")

    # 加载治理规则
    print("\n[live] Loading governance rules...")
    schema = load_governance(str(GOVERNANCE_DIR))
    print(f"[live] Loaded {len(schema.rules)} rules")

    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        engine = GovernanceEngine(
            rules=schema.rules,
            evidence_store=FileEvidenceStore(base_dir=f"{tmp}/evidence"),
            memory_store=FileMemoryStore(base_dir=f"{tmp}/memory"),
        )

        lookup = {r.id: r for r in schema.rules}
        bridge = ExplainBridge(lookup, enable=True)

        adapter = OpenClawHooksAdapter(
            gateway_url=gateway_url,
            token=token,
            gateway_name="openclaw-live",
            timeout_ms=timeout_ms,
        )

        # 运行 Block 场景
        block_ok, block_payload, block_result = run_scenario(
            engine, bridge, adapter,
            "block_reviewer_same_as_assignee",
            expected_decision="Block",
            output_dir=output_dir,
        )

        # 运行 Allow 场景
        allow_ok, allow_payload, allow_result = run_scenario(
            engine, bridge, adapter,
            "allow_specialist_via_reviewer",
            expected_decision="Allow",
            output_dir=output_dir,
        )

        # 运行失败测试
        failure_ok, failure_result = run_failure_test(adapter, output_dir)

        # 总结
        print("\n" + "=" * 60)
        print("Live Validation Results:")
        print(f"  Block notification:  {'PASS' if block_ok else 'FAIL'}")
        print(f"  Allow notification:  {'PASS' if allow_ok else 'FAIL'}")
        print(f"  Failure handling:    {'PASS' if failure_ok else 'FAIL'}")
        print("=" * 60)

        all_passed = block_ok and allow_ok and failure_ok
        if all_passed:
            print("\n[live] All tests passed!")
            print(f"[live] Validation evidence saved to {output_dir}")
        else:
            print("\n[live] Some tests failed!")
            sys.exit(1)


if __name__ == "__main__":
    main()