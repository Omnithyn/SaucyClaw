# OpenClaw Notification Integration PoC

> M4 — Notification 集成 PoC 包
> 现状：已完成 M3 基础验证（notification_adapter / mock_gateway / PoC 入口）
> 本轮：收口 notification 路径结构、文档、契约、对照说明

---

## 1. 为什么真实 OpenClaw 不能按 write_back 模型接入

### 1.1 核心结论（来自 M3 差距分析）

基于 oh-my-opencode v3.13.1 真实源码分析，**OpenClaw 不是"输出拦截器"，而是"事件通知调度器"**。

| 维度 | Mock Adapter 假设 | 真实 OpenClaw |
|------|-------------------|--------------|
| 触发时机 | 每次治理决策（process_event 后） | 特定 runtime event（session.created / session.deleted / session.idle） |
| 方向 | 双向（可拦截 + 可回写） | **单向**（只发送通知，不接收回写） |
| 输出面 | `GateResult` 结构 | `OpenClawPayload`（event + instruction + text + context） |
| 接点 | `write_back()`, `intercept_output()` | `wakeOpenClaw()` → HTTP POST / shell command |

### 1.2 不存在 write_back 等价物

OpenClaw 没有以下概念：
- `write_back()` — 向宿主回写治理决策
- `output_intercept()` — 拦截 agent 输出并修改
- `response_transformer` — 转换 agent 响应内容
- `middleware` — 在 agent 输出链路中插入中间件

### 1.3 OpenClaw 真实接口契约

```typescript
// oh-my-opencode v3.13.1 → src/openclaw/index.ts

interface OpenClawPayload {
    event: string;
    instruction: string;
    text: string;
    timestamp: string;
    sessionId?: string;
    projectPath?: string;
    projectName?: string;
    tmuxSession?: string;
    context: OpenClawContext;
}

interface WakeResult {
    gateway: string;
    success: boolean;
    error?: string;
    statusCode?: number;
    messageId?: string;
    platform?: string;
}

function wakeOpenClaw(config: OpenClawConfig, event: string, context: OpenClawContext): Promise<WakeResult | null>;
```

---

## 2. Notification 线路设计目标

### 2.1 本轮核心目标

验证 **SaucyClaw 治理决策可通过 OpenClaw gateway 真实发送为通知**。

三条路径：
1. **Block 路径** — 治理决策 Block → 发送通知 → 验证 payload 包含 decision + explanation
2. **Allow 路径** — 治理决策 Allow → 发送通知 → 验证 payload 正确
3. **Timeout 路径** — gateway 不可达 → 验证超时处理正确

### 2.2 不做的目标

- 不实现真正的 Block/拦截能力
- 不接入真实 Discord/Telegram reply listener
- 不重写 core 治理引擎
- 不修改 adapter 契约

### 2.3 预期边界

当前 PoC 只验证：
- Notification 发送链路畅通
- Payload 结构对齐 OpenClaw
- Basic timeout handling
- PoC 验证可重复、可解释

---

## 3. Notification PoC 架构与职责

### 3.1 文件职责与边界

| 文件 | 职责 | 通用/专属 | 是否生产级 |
|------|------|-----------|-----------|
| `core/governance/matcher.py` | 规则匹配器 | 通用治理能力 | ✓ |
| `core/engine/orchestrator.py` | 治理引擎 | 通用治理能力 | ✓ |
| `core/governance/explainer_bundle.py` | ExplanationBundle 构造 | 通用治理能力 | ✓ |
| `adapters/openclaw/explain_bridge.py` | 解释桥接器 | 通用治理能力 | ✓ |
| `adapters/openclaw/runtime_trace.py` | 运行摘要 | 通用治理能力 | ✓ |
| `adapters/openclaw/debug_render.py` | 调试渲染 | 通用治理能力 | ✓ |
| **`adapters/openclaw/notification_adapter.py`** | **HTTP/Command gateway 通知适配器** | **Notification 线专属** | **实验性** |
| **`experiments/openclaw_poc/mock_gateway.py`** | **本地 mock gateway server** | **Notification 线专属** | **PoC 专用** |
| **`experiments/openclaw_poc/run_poc.py`** | **PoC 入口脚本** | **Notification 线专属** | **PoC 专用** |

### 3.2 数据流

```
governance_cases/*.yaml
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
    ↓
WakeResult { gateway, success, error? }
```

### 3.3 notification_adapter.py 核心接口

```python
class OpenClawNotificationAdapter:
    def __init__(
        self,
        gateway_url: str,           # OpenClaw gateway URL
        gateway_name: str = "saucyclaw",
        headers: dict | None = None,
        timeout_ms: int = 10_000,
    ) -> None: ...

    def send_decision(
        self,
        result: GateResult,         # 治理决策结果
        session_context: dict | None = None,  # session 上下文
        explanation_summary: str | None = None,  # 解释摘要（来自 ExplanationBundle）
    ) -> WakeResult:
        """构建 OpenClawPayload 并 POST 到 gateway"""
        ...

    @property
    def log(self) -> list[tuple[GateResult, WakeResult]]:
        """发送日志（只读）"""
        ...
```

### 3.4 mock_gateway.py 核心接口

```python
def start_mock_server_in_background(
    host: str = "127.0.0.1",
    port: int = 18790,
) -> tuple[HTTPServer, threading.Thread]:
    """在后台启动 mock gateway server"""
    ...

def stop_mock_server(server: HTTPServer) -> None:
    """停止 mock server"""
    ...

# 全局列表：存储接收到的 payload（供 PoC 验证）
received_payloads: list[dict] = []
```

### 3.5 run_poc.py 执行逻辑

```python
def run_scenario(
    engine: GovernanceEngine,
    bridge: ExplainBridge,
    adapter: OpenClawNotificationAdapter,
    fixture_name: str,          # 如 "block_reviewer_same_as_assignee"
    expected_decision: str,     # 如 "Block"
) -> bool:
    """运行单个治理场景并验证通知发送"""
    ...
```

---

## 4. Block / Allow / Timeout 三条路径说明

### 4.1 Block 路径

```bash
# 1. 加载 Block fixture（reviewer 与 assignee 相同）
fixture: tests/fixtures/governance_cases/block_reviewer_same_as_assignee.yaml
expected.decision: "Block"
expected.matched_rules: ["rule-reviewer-must-differ"]

# 2. 治理引擎处理
result = engine.process_event(raw_event)
# result.decision == "Block"
# result.matched_rules == ["rule-reviewer-must-differ"]

# 3. 生成解释包
bundle = bundle_explanations(...)
# bundle.readable_summary == "触发阻断（high/separation_of_duties）：防止审查者与执行者同一人..."

# 4. 发送通知
adapter.send_decision(result, explanation_summary=bundle.readable_summary)

# 5. mock gateway 接收到的 payload
{
    "event": "governance-decision",
    "instruction": "[governance|Block]\n决策: Block\n规则: rule-reviewer-must-differ\n...",
    "context": { "sessionId": "poc-session-001", ... }
}
```

### 4.2 Allow 路径

```bash
# 1. 加载 Allow fixture（无规则触发）
fixture: tests/fixtures/governance_cases/allow_specialist_via_reviewer.yaml
expected.decision: "Allow"
expected.matched_rules: []

# 2. 治理引擎处理
result = engine.process_event(raw_event)
# result.decision == "Allow"
# result.matched_rules == []

# 3. 生成解释包
bundle = bundle_explanations(...)
# bundle.readable_summary == "未触发治理规则"

# 4. 发送通知
adapter.send_decision(result, explanation_summary=bundle.readable_summary)

# 5. mock gateway 接收到的 payload
{
    "event": "governance-decision",
    "instruction": "[governance|Allow]\n决策: Allow\n未触发治理规则...",
    "context": { "sessionId": "poc-session-001", ... }
}
```

### 4.3 Timeout 路径

```bash
# 1. 创建适配器（指向不存在的 gateway）
adapter = OpenClawNotificationAdapter(
    gateway_url="http://127.0.0.1:9999/nonexistent",
    timeout_ms=1_000,
)

# 2. 发送决策
wake_result = adapter.send_decision(result)

# 3. 结果
wake_result.success == False
wake_result.error == "Connection refused" or "timeout"
```

---

## 5. 当前 PoC 边界

### 5.1 已实现

- ✓ `notification_adapter.py` — HTTP POST 通知适配器
- ✓ `mock_gateway.py` — 本地 HTTP server 接收端
- ✓ `run_poc.py` — PoC 入口，验证 Block/Allow/timeout
- ✓ 13 个单元测试（`tests/unit/test_notification_adapter.py`）
- ✓ 与治理引擎/解释链路完整集成
- ✓ Payload 结构对齐 OpenClaw `OpenClawPayload`

### 5.2 未实现（不在本轮范围）

- ✗ 真实 Discord/Telegram 通知
- ✗ Reply Listener 双向通信
- ✗ 真正的 Block/拦截能力
- ✗ 网关 retry / 回退策略
- ✗ 持久化存储未发送通知
- ✗ UI/管理台
- ✗ 平台管理面（规则热更新等）

### 5.3 后续演进方向

#### 短期（真实 gateway 验证）
1. 替换 mock gateway → 真实 OpenClaw gateway
2. 验证通知真实发送到 OpenClaw webhook
3. 验证 OpenClaw reply listener 能接收回复

#### 中期（TMUX 级 Block）
1. 通过 OpenClaw command gateway 执行 TMUX 命令
2. 实现间接阻断（暂停/终止 agent session）
3. 结合 notification 发送审查请求

#### 长期（oh-my-opencode 插件）
1. 开发 SaucyClaw oh-my-opencode 插件
2. 在 `tool.execute.before` hook 中注入治理检查
3. 实现真正的治理拦截能力

---

## 6. 如何运行当前 PoC

### 6.1 一条命令运行

```bash
python -m experiments.openclaw_poc.run_poc
```

### 6.2 验证输出

预期输出包含：

```
[mock-gateway] Received event: governance-decision
[mock-gateway] Session: poc-session-001
[mock-gateway] Instruction:
  [governance|Block]
  决策: Block
  规则: rule-reviewer-must-differ
  原因: 触发 1 条规则，最高 severity: block
  建议: ...
  解释: 触发阻断（high/separation_of_duties）：防止审查者与执行者同一人...

PoC Results:
  Block notification:  PASS
  Allow notification:  PASS
  Timeout handling:    PASS
```

### 6.3 验证标准

| 标准 | 验证方式 |
|------|---------|
| Block 通知发送成功 | mock gateway 打印 "Block" |
| Allow 通知发送成功 | mock gateway 打印 "Allow" |
| 通知包含解释信息 | instruction 字段包含 explanation_summary |
| 超时处理正确 | unreachable gateway 返回 success=False |
| 零 core 改动 | `git diff core/` 为空 |
| 零现有测试破坏 | `pytest tests/ -v` 全部通过 |

---

## 7. Shadow Runtime 线 vs Notification 线对照

### 7.1 两条线的本质区别

| 维度 | Shadow Runtime 线（M1/M2） | Notification 线（M3/M4） |
|------|---------------------------|------------------------|
| **目标** | 外围包装模板，模拟宿主接入流程 | 真实通知路径，验证 OpenClaw gateway 接入 |
| **输出方向** | 内部调试/日志（`debug_render`） | 外部 gateway（HTTP POST / command） |
| **核心组件** | `ShadowRuntime` + `ExplainBridge` + `RuntimeTrace` | `OpenClawNotificationAdapter` + `mock_gateway` |
| **验证方式** | 单元测试 + 集成测试（201 tests） | PoC 脚本 + 单元测试（13 tests） |
| **成熟度** | 已稳定，可作为接入模板 | 实验性，待真实 gateway 验证 |
| **后续演进** | 保持作为接入参考模板 | 真实 OpenClaw gateway → TMUX 阻断 → oh-my-opencode 插件 |

### 7.2 当前推荐使用场景

#### 使用 Shadow Runtime 线

- 调试治理引擎和规则集
- 验证规则语义和治理逻辑
- 演示治理能力（内部演示）
- 作为未来其他 runtime 接入的模板参考

#### 使用 Notification 线

- 验证 OpenClaw gateway 接入可行性
- 测试真实通知发送路径
- 为后续真实宿主接入做准备
- 研究 notification-based governance 模式

### 7.3 后续演进路径

#### Shadow Runtime 线
- 保持稳定，不主动扩展
- 作为接入模板参考
- 可能后续用于其他 runtime（非 OpenClaw）接入

#### Notification 线
1. **短期** — 真实 OpenClaw gateway 验证
2. **中期** — TMUX 级间接阻断
3. **长期** — oh-my-opencode 插件治理拦截

---

## 8. 本轮交付清单

### 8.1 新增文档

| 文件 | 职责 |
|------|------|
| `docs/integration/openclaw_notification_poc.md` | 本文档 — PoC 架构、路径、边界、运行说明 |
| `docs/integration/openclaw_notification_contract.md` | 通知载荷契约定义（见下文） |

### 8.2 新增代码

| 文件 | 职责 |
|------|------|
| `adapters/openclaw/notification_adapter.py` | HTTP/Command gateway 通知适配器 |
| `experiments/openclaw_poc/mock_gateway.py` | 本地 mock gateway server |
| `experiments/openclaw_poc/run_poc.py` | PoC 入口脚本 |

### 8.3 新增测试

| 文件 | 职责 |
|------|------|
| `tests/unit/test_notification_adapter.py` | 13 个单元测试（payload 构建 / HTTP 发送 / log 记录 / WakeResult） |

### 8.4 已验证

- ✓ PoC 全路径通过（Block / Allow / timeout）
- ✓ 214 tests 全部通过（201 原有 + 13 新增）
- ✓ pyflakes 零报错
- ✓ 零 core 改动

---

## 9. 后续真实接入建议

### 9.1 下一轮（M5）建议目标

**目标：真实 OpenClaw gateway 验证**

- 替换 mock gateway → 真实 OpenClaw HTTP gateway
- 配置 OpenClaw gateway URL 和 headers
- 验证通知真实发送到 OpenClaw webhook
- 验证 OpenClaw reply listener 能接收回复

### 9.2 再下一轮（M6）建议目标

**目标：TMUX 级间接阻断**

- 通过 OpenClaw command gateway 执行 TMUX 命令
- 实现暂停/终止 agent session
- 结合 notification 发送审查请求

### 9.3 长期（M7+）建议目标

**目标：oh-my-opencode 插件治理拦截**

- 开发 SaucyClaw oh-my-opencode 插件
- 在 `tool.execute.before` hook 中注入治理检查
- 实现真正的治理拦截能力
