# 真实宿主 PoC 计划

> M3 — 真实宿主集成 PoC 包
> 前提：已基于真实 OpenClaw 源码完成差距分析（见 `openclaw_real_runtime_gap_analysis.md`）

---

## 1. PoC 目标

**核心目标：** 验证 SaucyClaw 治理决策可以通过 OpenClaw gateway 真实发送通知。

**不做的事：**
- 不重写 core 治理引擎
- 不修改 adapter 契约（`write_back()` 签名不变）
- 不实现真正的 Block/拦截能力
- 不接入真实 Discord/Telegram reply listener

---

## 2. PoC 架构

```
governance_cases/*.yaml
    ↓ (load)
GovernanceSchema
    ↓
GovernanceEngine.process_event(raw_event)
    ↓
GateResult { decision, matched_rules, reason, suggestions }
    ↓
ExplainBridge.enhance_output(result)  [optional]
    ↓
OpenClawNotificationAdapter.send_decision(result, context)
    ↓
HTTP POST → OpenClaw gateway URL (e.g., http://127.0.0.1:18789/hooks/agent)
    ↓
OpenClawPayload {
    event: "governance-decision",
    instruction: "Block: rule-reviewer-must-differ triggered",
    text: "...",
    context: { sessionId, projectPath, ... }
}
```

---

## 3. PoC 文件清单

### 3.1 新增文件

| 文件 | 职责 |
|------|------|
| `adapters/openclaw/notification_adapter.py` | 真实通知适配器，通过 HTTP POST 发送治理决策 |
| `experiments/openclaw_poc/__init__.py` | PoC 包标记 |
| `experiments/openclaw_poc/run_poc.py` | PoC 入口脚本 |
| `experiments/openclaw_poc/mock_gateway.py` | 本地 mock gateway server（接收并打印 OpenClawPayload） |

### 3.2 复用文件（零修改）

- `core/governance/loader.py` — YAML 装载
- `core/governance/matcher.py` — 规则匹配
- `core/governance/models.py` — 数据模型
- `core/governance/explainer_bundle.py` — 解释打包
- `core/engine/orchestrator.py` — 治理引擎
- `core/evidence/generator.py` — 证据生成
- `core/engine/memory_builder.py` — 记忆构建
- `adapters/openclaw/explain_bridge.py` — 解释桥接
- `stores/file/evidence/store.py` — 证据存储
- `stores/file/memory/store.py` — 记忆存储
- `tests/fixtures/governance_cases/*.yaml` — 治理场景

### 3.3 参考文件（不复用，但作为设计参考）

- `docs/integration/openclaw_real_runtime_gap_analysis.md` — 差距分析结论
- `docs/integration/openclaw_shadow_runtime.md` — 现有 Shadow Mode 流程

---

## 4. PoC 步骤

### Step 1: 创建 OpenClawNotificationAdapter

```python
# adapters/openclaw/notification_adapter.py

@dataclass(frozen=True)
class WakeResult:
    gateway: str
    success: bool
    error: str | None = None
    status_code: int | None = None


class OpenClawNotificationAdapter:
    """通过 HTTP POST 将 SaucyClaw 治理决策发送到 OpenClaw gateway"""

    def __init__(self, gateway_url: str, gateway_name: str = "saucyclaw") -> None:
        self.gateway_url = gateway_url
        self.gateway_name = gateway_name

    def send_decision(
        self,
        result: GateResult,
        session_context: dict[str, str] | None = None,
    ) -> WakeResult:
        """构建 OpenClawPayload 并 POST 到 gateway"""
        ...
```

**关键设计点：**
- 使用 `httpx` 或 `urllib` 做 HTTP POST（不引入新依赖优先用 urllib）
- Payload 结构对齐 OpenClaw 的 `OpenClawPayload` interface
- 超时默认 10s（对齐 OpenClaw 的 `DEFAULT_HTTP_TIMEOUT_MS = 10_000`）

### Step 2: 创建 mock gateway server

```python
# experiments/openclaw_poc/mock_gateway.py

"""本地 HTTP server，模拟 OpenClaw gateway 接收端"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class MockGatewayHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        body = self.rfile.read(content_length)
        payload = json.loads(body)
        # 打印接收到的 payload
        print(f"[gateway] Received: {payload['event']}")
        print(f"[gateway] Decision: {payload.get('instruction', 'N/A')}")
        self.send_response(200)
        self.end_headers()
        self.write(b'{"success": true}')
```

**用途：** 无需真实 OpenClaw 运行即可验证 PoC

### Step 3: 创建 PoC 入口脚本

```python
# experiments/openclaw_poc/run_poc.py

"""
PoC 入口：
1. 启动 mock gateway server（后台线程）
2. 加载治理规则
3. 运行 Block/Allow 场景
4. 通过 OpenClawNotificationAdapter 发送决策
5. 验证 mock gateway 收到通知
"""
```

**验证内容：**
- Block 场景：gateway 收到 `event: "governance-decision"`, `instruction` 包含 "Block"
- Allow 场景：gateway 收到 `event: "governance-decision"`, `instruction` 包含 "Allow"
- 解释信息：gateway 收到的 payload 包含 explanation_bundle 的 readable_summary

### Step 4: 运行验证

```bash
# 启动 PoC
python -m experiments.openclaw_poc.run_poc

# 预期输出
[mock-gateway] Listening on http://127.0.0.1:18790
[poc] Running Block scenario: block_reviewer_same_as_assignee
[poc] Decision: Block
[gateway] Received: governance-decision
[gateway] Instruction: Block (high/separation_of_duties): 防止审查者与执行者同一人...
[poc] Block scenario: OK
[poc] Running Allow scenario: allow_specialist_via_reviewer
[poc] Decision: Allow
[gateway] Received: governance-decision
[gateway] Instruction: 未触发治理规则
[poc] Allow scenario: OK
[poc] All scenarios passed
```

---

## 5. 保证

- **零 core 改动**：不修改 `core/` 下任何文件
- **零 adapter 契约改动**：不修改 `OpenClawHostAdapter` 接口
- **零 mock 改动**：不修改 `adapters/openclaw/adapter.py`（mock adapter 保持原样）
- **新文件隔离**：所有 PoC 代码在 `experiments/openclaw_poc/` 下

---

## 6. 验收标准

| 标准 | 验证方式 |
|------|---------|
| mock gateway 收到 Block 通知 | 输出包含 "Block" |
| mock gateway 收到 Allow 通知 | 输出包含 "Allow" |
| 通知 payload 包含解释信息 | `instruction` 字段包含 rationale |
| 超时处理正确 | gateway 不可用时返回 `success=False` |
| 零 core 改动 | `git diff core/` 为空 |
| 零现有测试破坏 | `pytest tests/ -v` 全部通过 |

---

## 7. 后续演进路径

### PoC 之后

1. **真实 OpenClaw gateway 验证**：用真实 OpenClaw 实例替换 mock gateway
2. **TMUX 级 Block**：通过 OpenClaw command gateway 执行 TMUX 命令实现间接阻断
3. **oh-my-opencode 插件**：开发 SaucyClaw 插件，在 `tool.execute.before` hook 中注入治理检查

### 不在此 PoC 范围

- 真实 Discord/Telegram 通知
- Reply Listener 双向通信
- 规则热更新
- 平台管理面
- UI/管理台
