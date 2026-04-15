"""本地 mock gateway server — 模拟 OpenClaw gateway 接收端。

用于 PoC 验证，无需真实 OpenClaw 运行。
启动后监听 HTTP POST 请求，打印接收到的 OpenClawPayload。
"""

from __future__ import annotations

import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Callable

# 存储接收到的请求，供测试验证
received_payloads: list[dict] = []
server_ready = threading.Event()


class MockGatewayHandler(BaseHTTPRequestHandler):
    """处理 OpenClaw gateway POST 请求的 HTTP handler。"""

    # 可选的回调函数，用于接收通知
    on_receive: Callable[[dict], None] | None = None

    def log_message(self, format: str, *args) -> None:  # noqa: A002
        """抑制默认日志输出。"""
        pass

    def do_POST(self) -> None:  # noqa: N802
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            payload = {"raw": body.decode("utf-8", errors="replace")}

        received_payloads.append(payload)

        # 打印接收到的 payload（PoC 演示用）
        event = payload.get("event", "unknown")
        instruction = payload.get("instruction", "N/A")
        session_id = payload.get("sessionId", "")

        print("[mock-gateway] Received event: " + event)
        if session_id:
            print("[mock-gateway] Session: " + session_id)
        print("[mock-gateway] Instruction:")
        for line in instruction.split("\n"):
            print(f"  {line}")
        print("[mock-gateway] ---")

        # 调用回调（如果有）
        if self.on_receive:
            self.on_receive(payload)

        # 返回 200 OK
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        response = json.dumps({"success": True, "gateway": "mock"})
        self.wfile.write(response.encode("utf-8"))


def create_mock_server(
    host: str = "127.0.0.1",
    port: int = 18790,
) -> HTTPServer:
    """创建并返回 mock gateway server。"""
    server = HTTPServer((host, port), MockGatewayHandler)
    return server


def start_mock_server_in_background(
    host: str = "127.0.0.1",
    port: int = 18790,
) -> tuple[HTTPServer, threading.Thread]:
    """在后台线程启动 mock server。"""
    server = create_mock_server(host, port)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    server_ready.set()
    return server, thread


def stop_mock_server(server: HTTPServer) -> None:
    """停止 mock server。"""
    server.shutdown()
    server.server_close()
    server_ready.clear()


def clear_received() -> None:
    """清空接收记录。"""
    received_payloads.clear()
