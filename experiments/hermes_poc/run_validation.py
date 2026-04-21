"""Hermes hooks 最小验证 runner。

M17 — Hermes First Executable Path on Inbound Base

基于 Hermes hooks_adapter，跑通 Block / Allow / failure 三类路径，
落盘 evidence，形成最小验证闭环。

与 OpenHarness live_validation.py 的区别：
- Hermes 事件类型是 agent:step（而非 pre_tool_use）
- payload 格式相同（{event, payload}）
- 响应结构相同（{blocked, reason}）

用法：
    python experiments/hermes_poc/run_validation.py
"""

from __future__ import annotations

import json
import sys
import threading
from dataclasses import asdict
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from adapters.hermes.hooks_adapter import (  # noqa: E402
    HermesHookReceiver,
    HermesHookProbe,
    build_hermes_hook_response,
    parse_hermes_hook_payload,
)
from stores.protocols import GateResult  # noqa: E402


# ─── 模拟治理策略 ───

# 危险工具列表（触发 Block）
_DANGEROUS_TOOLS = {"Write", "Bash", "Edit"}
# 安全工具列表（触发 Allow）
_SAFE_TOOLS = {"Read", "Glob", "Grep"}


def _governance_check(event_type: str, payload: dict[str, Any]) -> GateResult:
    """模拟治理策略：根据工具名判断 Block / Allow。"""
    tool_name = payload.get("tool_name", "Unknown")

    if tool_name in _DANGEROUS_TOOLS:
        return GateResult(
            decision="Block",
            reason=f"危险工具 '{tool_name}' 被治理策略阻断",
            matched_rules=["rule-dangerous-tool-block"],
            evidence_ids=[],
            suggestions=[f"请使用安全替代方案，或申请 '{tool_name}' 的使用权限"],
        )

    if tool_name in _SAFE_TOOLS:
        return GateResult(
            decision="Allow",
            reason=f"工具 '{tool_name}' 通过治理检查",
            matched_rules=[],
            evidence_ids=[],
            suggestions=[],
        )

    # 未知工具 → Allow（默认放行）
    return GateResult(
        decision="Allow",
        reason=f"未知工具 '{tool_name}'，默认放行",
        matched_rules=["rule-unknown-tool-default-allow"],
        evidence_ids=[],
        suggestions=[f"建议为 '{tool_name}' 添加治理规则"],
    )


# ─── HTTP 治理服务器 ───


class _GovernanceHandler(BaseHTTPRequestHandler):
    """治理端点：接收 Hermes hook 请求，执行治理检查，返回响应。"""

    receiver: HermesHookReceiver | None = None

    def do_POST(self) -> None:  # noqa: N802
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        raw_payload = json.loads(body.decode("utf-8"))

        assert self.receiver is not None
        response_body, result = self.receiver.handle_hook_request(raw_payload)

        self.send_response(result.status_code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response_body).encode("utf-8"))

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        pass  # 静默


def _start_server(port: int, receiver: HermesHookReceiver) -> HTTPServer:
    _GovernanceHandler.receiver = receiver
    server = HTTPServer(("127.0.0.1", port), _GovernanceHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


# ─── Evidence 落盘 ───


def _save_evidence(scenario: str, evidence: dict[str, Any], output_dir: Path) -> None:
    evidence_file = output_dir / f"{scenario}_evidence.json"
    with open(evidence_file, "w") as f:
        json.dump(evidence, f, indent=2)
    print(f"  [EVIDENCE] {evidence_file.name}")


# ─── 验证场景 ───


def _test_allow_scenario(probe: HermesHookProbe, output_dir: Path) -> None:
    """Allow 场景：安全工具 Read 通过治理检查。"""
    # Hermes 事件类型是 agent:step
    payload = {"tool_name": "Read", "path": "README.md", "session_id": "test-001"}
    result = probe.send_hook_event("agent:step", payload)

    evidence = {
        "scenario": "allow",
        "event_type": "agent:step",
        "hermes_payload": {"event": "agent:step", "payload": payload},
        "tool_name": "Read",
        "result": asdict(result),
        "expected": {"blocked": False, "success": True},
        "pass": result.blocked is False and result.success is True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    assert result.blocked is False, f"Allow 场景不应被阻断: {result}"
    assert result.success is True, f"Allow 场景应成功: {result}"
    assert result.status_code == 200, f"Allow 场景应返回 200: {result}"

    _save_evidence("allow", evidence, output_dir)
    print("  [PASS] Allow: Read 工具通过治理检查 (200, blocked=false)")


def _test_block_scenario(probe: HermesHookProbe, output_dir: Path) -> None:
    """Block 场景：危险工具 Write 被治理策略阻断。"""
    payload = {"tool_name": "Write", "path": "/etc/passwd", "content": "malicious", "session_id": "test-002"}
    result = probe.send_hook_event("agent:step", payload)

    evidence = {
        "scenario": "block",
        "event_type": "agent:step",
        "hermes_payload": {"event": "agent:step", "payload": payload},
        "tool_name": "Write",
        "result": asdict(result),
        "expected": {"blocked": True},
        "pass": result.blocked is True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    assert result.blocked is True, f"Block 场景应被阻断: {result}"
    assert result.status_code == 403, f"Block 场景应返回 403: {result}"

    _save_evidence("block", evidence, output_dir)
    print("  [PASS] Block: Write 工具被治理策略阻断 (403, blocked=true)")


def _test_failure_scenario(probe: HermesHookProbe, output_dir: Path) -> None:
    """Failure 场景：连接不存在的端点。"""
    bad_probe = HermesHookProbe(
        target_url="http://127.0.0.1:19999/governance",
        timeout_ms=1000,
    )
    result = bad_probe.send_hook_event("agent:step", {"tool_name": "Read", "session_id": "test-003"})

    evidence = {
        "scenario": "failure",
        "event_type": "agent:step",
        "result": asdict(result),
        "expected": {"success": False},
        "pass": result.success is False,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    assert result.success is False, f"Failure 场景应失败: {result}"

    _save_evidence("failure", evidence, output_dir)
    print("  [PASS] Failure: 连接失败正确处理 (success=false, error recorded)")


def _test_payload_format_alignment(output_dir: Path) -> None:
    """验证 payload 格式与 Hermes 预期一致。"""
    # Hermes payload 格式
    raw = {
        "event": "agent:step",
        "payload": {"tool_name": "Bash", "tool_input": "rm -rf /", "session_id": "test-004"},
    }

    event_type, payload = parse_hermes_hook_payload(raw)

    evidence = {
        "scenario": "payload_format_alignment",
        "check": "Hermes payload format",
        "expected_format": {"event": "agent:step", "payload": {"tool_name": "Bash"}},
        "actual_event": event_type,
        "actual_payload": payload,
        "pass": event_type == "agent:step" and payload.get("tool_name") == "Bash",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    assert event_type == "agent:step", f"Event type 不匹配: {event_type}"
    assert payload.get("tool_name") == "Bash", f"Payload 不匹配: {payload}"

    _save_evidence("payload_format", evidence, output_dir)
    print("  [PASS] Payload 格式与 Hermes 预期一致 (event=agent:step)")


def _test_response_structure(output_dir: Path) -> None:
    """验证响应结构与 Hermes hook 脚本预期一致。"""
    # Allow 响应
    allow_result = GateResult(
        decision="Allow", reason="ok", matched_rules=[], evidence_ids=[], suggestions=[]
    )
    allow_body, allow_hook_result = build_hermes_hook_response(allow_result)

    # Block 响应
    block_result = GateResult(
        decision="Block", reason="danger", matched_rules=["rule-1"], evidence_ids=[], suggestions=[]
    )
    block_body, block_hook_result = build_hermes_hook_response(block_result)

    # 验证 Allow
    assert allow_hook_result.status_code == 200
    assert allow_body["blocked"] is False
    # 脚本检查 blocked=false → exit 0 → Hermes 继续

    # 验证 Block
    assert block_hook_result.status_code == 403
    assert block_body["blocked"] is True
    # 脚本检查 blocked=true → exit 1 → Hermes 阻断

    evidence = {
        "scenario": "response_structure",
        "check": "Hermes hook script compatibility",
        "allow": {"status_code": 200, "blocked": False, "script_will_block": False},
        "block": {"status_code": 403, "blocked": True, "script_will_block": True},
        "pass": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    _save_evidence("response_structure", evidence, output_dir)
    print("  [PASS] 响应结构与 Hermes hook 脚本预期一致")


# ─── 入口 ───


def main() -> None:
    output_dir = PROJECT_ROOT / "experiments" / "hermes_poc" / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=== Hermes hooks 最小验证 ===")
    print()

    # 启动治理服务器（使用不同端口避免与 OpenHarness 冲突）
    port = 18991
    receiver = HermesHookReceiver(governance_check=_governance_check)
    server = _start_server(port, receiver)

    passed = 0
    failed = 0

    try:
        probe = HermesHookProbe(
            target_url=f"http://127.0.0.1:{port}/governance",
            timeout_ms=5000,
        )

        scenarios = [
            ("1. Allow 场景", lambda: _test_allow_scenario(probe, output_dir)),
            ("2. Block 场景", lambda: _test_block_scenario(probe, output_dir)),
            ("3. Failure 场景", lambda: _test_failure_scenario(probe, output_dir)),
            ("4. Payload 格式对齐", lambda: _test_payload_format_alignment(output_dir)),
            ("5. 响应结构验证", lambda: _test_response_structure(output_dir)),
        ]

        for name, fn in scenarios:
            print(f"{name}...")
            try:
                fn()
                passed += 1
            except AssertionError as exc:
                print(f"  [FAIL] {exc}")
                failed += 1

        print()
        print(f"=== {passed}/{passed + failed} 项验证通过 ===")

        if failed > 0:
            print("⚠️  存在失败的验证项")
            sys.exit(1)

        print(f"证据文件保存至: {output_dir}")

    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
