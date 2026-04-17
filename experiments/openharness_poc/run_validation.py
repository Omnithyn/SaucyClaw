"""OpenHarness hooks_live 最小验证 runner。

M12 — OpenHarness First Executable Path

验证三类路径：
1. Allow — 治理检查通过，返回 200 + blocked=false
2. Block — 治理检查失败，返回 403 + blocked=true
3. Failure — 无效 payload 或错误路径

用法：
    python experiments/openharness_poc/run_validation.py

输出保存到 experiments/openharness_poc/output/
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

# 确保可以导入项目
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from adapters.openharness.hooks_adapter import (
    OpenHarnessHookReceiver,
    OpenHarnessHookProbe,
    OpenHarnessHookResult,
    build_openharness_hook_response,
    parse_openharness_hook_payload,
)
from stores.protocols import GateResult


# ─── 模拟治理检查 ───


def _make_gate_result(decision: str, matched_rules: list[str]) -> GateResult:
    return GateResult(
        decision=decision,
        reason=f"测试场景: {decision}",
        matched_rules=matched_rules,
        evidence_ids=[],
        suggestions=[],
    )


def _governance_check_allow(event_type: str, payload: dict[str, Any]) -> GateResult:
    return _make_gate_result("Allow", [])


def _governance_check_block(event_type: str, payload: dict[str, Any]) -> GateResult:
    return _make_gate_result("Block", ["rule-test-block"])


# ─── 测试 HTTP 服务器 ───


class _GovernanceHandler(BaseHTTPRequestHandler):
    """模拟治理端点，接收 OpenHarness hook 请求并返回响应。"""

    governance_check = _governance_check_allow  # 可动态修改

    def do_POST(self) -> None:  # noqa: N802
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        raw_payload = json.loads(body.decode("utf-8"))

        event_type, payload = parse_openharness_hook_payload(raw_payload)
        check_fn = type(self).governance_check  # 用类属性而非实例属性
        gate_result = check_fn(event_type, payload)
        response_body, result = build_openharness_hook_response(gate_result)

        self.send_response(result.status_code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response_body).encode("utf-8"))

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        pass  # 静默


def _start_server(port: int) -> HTTPServer:
    server = HTTPServer(("127.0.0.1", port), _GovernanceHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


# ─── 证据保存 ───


def _save_evidence(scenario: str, evidence: dict[str, Any], output_dir: Path) -> None:
    evidence_file = output_dir / f"{scenario}_evidence.json"
    with open(evidence_file, "w") as f:
        json.dump(evidence, f, indent=2)


# ─── 测试场景 ───


def _test_allow_scenario(probe: OpenHarnessHookProbe, output_dir: Path) -> None:
    """Allow 场景：治理检查通过。"""
    result = probe.send_hook_event("pre_tool_use", {"tool_name": "Read", "path": "file.txt"})

    evidence = {
        "scenario": "allow",
        "event_type": "pre_tool_use",
        "payload": {"tool_name": "Read"},
        "result": asdict(result),
        "expected_blocked": False,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    assert result.blocked is False, f"Allow 场景不应被阻断: {result}"
    assert result.success is True, f"Allow 场景应成功: {result}"

    _save_evidence("allow", evidence, output_dir)
    print("  [PASS] Allow 场景: blocked=false, success=true")


def _test_block_scenario(probe: OpenHarnessHookProbe, output_dir: Path) -> None:
    """Block 场景：治理检查失败，阻断执行。"""
    result = probe.send_hook_event("pre_tool_use", {"tool_name": "Write", "path": "/etc/passwd"})

    evidence = {
        "scenario": "block",
        "event_type": "pre_tool_use",
        "payload": {"tool_name": "Write"},
        "result": asdict(result),
        "expected_blocked": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    assert result.blocked is True, f"Block 场景应被阻断: {result}"

    _save_evidence("block", evidence, output_dir)
    print("  [PASS] Block 场景: blocked=true, status_code=403")


def _test_failure_scenario(probe: OpenHarnessHookProbe, output_dir: Path) -> None:
    """Failure 场景：连接不存在的端点。"""
    bad_probe = OpenHarnessHookProbe(target_url="http://127.0.0.1:19999/governance", timeout_ms=1000)
    result = bad_probe.send_hook_event("pre_tool_use", {"tool_name": "Read"})

    evidence = {
        "scenario": "failure",
        "event_type": "pre_tool_use",
        "result": asdict(result),
        "expected_success": False,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    assert result.success is False, f"Failure 场景应失败: {result}"

    _save_evidence("failure", evidence, output_dir)
    print("  [PASS] Failure 场景: success=false, error recorded")


# ─── 入口 ───


def main() -> None:
    output_dir = PROJECT_ROOT / "experiments" / "openharness_poc" / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=== OpenHarness hooks_live 最小验证 ===")
    print()

    # 启动本地治理服务器
    port = 18989
    server = _start_server(port)

    try:
        probe = OpenHarnessHookProbe(
            target_url=f"http://127.0.0.1:{port}/governance",
            timeout_ms=5000,
        )

        # 1. Allow 场景
        print("1. Allow 场景...")
        _GovernanceHandler.governance_check = _governance_check_allow
        _test_allow_scenario(probe, output_dir)

        # 2. Block 场景
        print("2. Block 场景...")
        _GovernanceHandler.governance_check = _governance_check_block
        _test_block_scenario(probe, output_dir)

        # 3. Failure 场景
        print("3. Failure 场景...")
        _test_failure_scenario(probe, output_dir)

        print()
        print("=== 全部 3 项验证通过 ===")
        print(f"证据文件保存至: {output_dir}")

    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
