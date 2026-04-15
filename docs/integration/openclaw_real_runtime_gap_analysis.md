# 真实宿主差距分析

> M3 — 真实宿主集成 PoC 包
> 来源：基于 oh-my-opencode v3.13.1 真实源码（`src/openclaw/` + `src/config/schema/openclaw.ts`）

---

## 1. 分析范围

本文档基于实际 TypeScript 源码分析，非基于 mock 推断。

**源码位置：** `github.com/code-yeongyu/oh-my-openagent` v3.13.1
**关键文件：**
- `src/openclaw/index.ts` — 入口：`wakeOpenClaw()`, `initializeOpenClaw()`
- `src/openclaw/dispatcher.ts` — 分发器：`wakeGateway()`, `wakeCommandGateway()`
- `src/openclaw/config.ts` — 网关解析：`resolveGateway()`
- `src/openclaw/runtime-dispatch.ts` — 运行时桥接：`dispatchOpenClawEvent()`
- `src/config/schema/openclaw.ts` — 配置 schema
- `src/create-managers.ts` — 管理器初始化（OpenClaw 在此处被调用）

---

## 2. 核心结论

### 2.1 OpenClaw 不是"输出拦截器"，而是"事件通知调度器"

OpenClaw 的真实架构与我们 mock adapter 的假设存在**根本性结构差异**：

| 维度 | SaucyClaw mock adapter | 真实 OpenClaw |
|------|----------------------|--------------|
| 触发时机 | 每次 `process_event()` 后 | 特定 runtime event（session.created / session.idle / session.deleted 等） |
| 数据流 | collect_event → process → write_back | dispatchOpenClawEvent → wakeOpenClaw → wakeGateway (HTTP/Command) |
| 方向 | 双向（可拦截、可回写） | **单向**（只发送通知，不接收回写） |
| 粒度 | 每次治理决策 | 会话级事件（生命周期级别） |
| 输出面 | GateResult 结构 | `OpenClawPayload`（event + instruction + text + context） |

### 2.2 不存在等价于 write_back / output_transformer 的接点

OpenClaw **没有任何**以下概念：
- `write_back()` — 向宿主回写治理决策
- `output_intercept()` — 拦截 agent 输出并修改
- `response_transformer` — 转换 agent 响应内容
- `middleware` — 在 agent 输出链路中插入中间件

OpenClaw 有的只是：
- **Gateway**（HTTP POST 或 shell command）— 把 `OpenClawPayload` 发送到外部
- **Hook**（event 名 → gateway 名 + instruction 模板）— 决定哪个事件走哪个 gateway
- **Reply Listener**（daemon 进程）— 从 Discord/Telegram 轮询回复，注入到 session

### 2.3 OpenClaw 的真实事件流

```
runtime event (session.created / session.deleted / session.idle / etc.)
    ↓
dispatchOpenClawEvent()
    ├── mapRawEventToOpenClawEvents() — 事件名映射
    │     session.created → session-start
    │     session.deleted → session-end
    │     session.idle → stop
    ↓
resolveGateway(config, event)
    ├── 查找 config.hooks[event]
    ├── 提取 gateway 名和 instruction 模板
    ↓
wakeOpenClaw()
    ├── 构建 variables（sessionId, projectPath, tmuxSession, question, etc.）
    ├── interpolateInstruction(instruction, variables)
    ├── 如果 gateway.type == "command" → wakeCommandGateway()
    └── 如果 gateway.type == "http" → wakeGateway() → HTTP POST OpenClawPayload
    ↓
WakeResult { gateway, success, error?, statusCode?, messageId?, platform?, channelId?, threadId? }
```

### 2.4 OpenClaw 的真实 hook 接口

```typescript
// src/hooks/openclaw.d.ts
function createOpenClawHook(ctx: PluginContext, pluginConfig: OhMyOpenCodeConfig): {
    event: (input: any) => Promise<void>;
    "tool.execute.before": (input: { tool: string; sessionID: string }, output: { args: Record<string, unknown> }) => Promise<void>;
} | null;
```

这个 hook 返回的是 oh-my-opencode 插件标准 hook 接口（`event` + `tool.execute.before`），
**不是** OpenClaw 自身的治理拦截点。
它主要用于跟踪工具执行状态和 session 生命周期，**不具备**治理决策能力。

---

## 3. 与 SaucyClaw mock adapter 的差距

### 3.1 `collect_event()` — 差距：大

| mock 行为 | 真实 OpenClaw |
|-----------|--------------|
| 从 raw_event dict 提取 assignee/reviewer/task_type 等字段 | OpenClaw 的 `OpenClawPayload` 不包含这些治理字段 |
| 用于 `engine.process_event()` | OpenClaw 不处理治理事件，只分发运行时事件 |

**结论：** `collect_event()` 的字段映射概念与 OpenClaw 不兼容。
治理事件（task_assign 等）需要 SaucyClaw 自己维护，OpenClaw 只是通知通道。

### 3.2 `write_back()` — 差距：大

| mock 行为 | 真实 OpenClaw |
|-----------|--------------|
| 向宿主回写 GateResult 决策 | OpenClaw 没有"回写"概念 |
| 可以 Block/Allow 输出 | OpenClaw 的 gateway 是单向发送，不接收响应 |

**结论：** `write_back()` 在 OpenClaw 中无对应物。
如果要在 OpenClaw 场景下实现"阻断"，需要通过其他方式（如 TMUX 控制、agent 指令注入等）。

### 3.3 `intercept_output()` — 差距：根本性

| mock 行为 | 真实 OpenClaw |
|-----------|--------------|
| 占位实现，返回 Allow | OpenClaw 没有"拦截输出"的概念 |

**结论：** OpenClaw 是一个 notification dispatcher，不是 response interceptor。
治理决策无法通过 OpenClaw 直接作用于 agent 输出。

### 3.4 `connect()` — 差距：小

| mock 行为 | 真实 OpenClaw |
|-----------|--------------|
| 从 dict 提取字段 | OpenClaw 通过 `initializeOpenClaw()` 启动，主要工作是 start/stop reply listener |

**结论：** `connect()` 概念可以映射，但实质不同：OpenClaw 不需要"连接"到某个 session，
它是配置驱动的被动调度。

---

## 4. OpenClaw 可以作为 SaucyClaw 的什么

### 4.1 可用：通知通道（Notification Channel）

OpenClaw 最适合的角色是**治理决策的通知通道**：

```
SaucyClaw governance decision (Block/Allow/Escalate)
    ↓
OpenClaw gateway (HTTP POST to webhook, or command execution)
    ↓
External system receives notification
    - Discord message
    - Telegram message
    - Custom webhook handler
```

这对应 SaucyClaw 已有的 `EvidenceStore` + `explanation_bundle` 消费场景。

### 4.2 部分可用：会话标识传递

OpenClaw 的 `OpenClawContext` 包含：
- `sessionId` — 可用于关联 SaucyClaw 的 `session_id`
- `projectPath` — 可用于定位治理规则目录
- `tmuxSession` — 可用于 TMUX 控制（间接实现 Block）

### 4.3 不可用：治理决策执行面

OpenClaw 不能：
- 拦截 agent 输出
- 修改 agent 响应
- 在 tool 执行前做治理检查
- 回写治理决策到 agent

这些能力需要 SaucyClaw 自己实现（或通过其他 hook 系统如 Claude Code 的 PreToolUse）。

---

## 5. 集成路径评估

### 5.1 最小可行路径（推荐）

将 SaucyClaw 的治理决策通过 OpenClaw gateway 发送为通知：

```python
# SaucyClaw 决策后
result = engine.process_event(raw_event)
# 通过 OpenClaw gateway 发送通知
payload = {
    "event": "governance-decision",
    "instruction": f"Decision: {result.decision} for session {session_id}",
    "text": f"Decision: {result.decision}",
    "context": {"sessionId": session_id, "projectPath": project_path},
}
# HTTP POST 到 OpenClaw 配置的 gateway URL
```

**优点：**
- 与 OpenClaw 现有架构完全兼容
- 不需要修改 OpenClaw 代码
- 可以复用 OpenClaw 的 gateway 配置和 reply listener

**缺点：**
- 通知是单向的，无法直接实现 Block
- 需要外部系统消费通知并采取行动

### 5.2 中期路径：TMUX 级阻断

结合 OpenClaw 的 `tmuxSession` 字段，通过 TMUX 控制实现间接 Block：

```
SaucyClaw 决策 Block
    → 通过 OpenClaw command gateway 执行 TMUX 命令
    → 暂停或终止 agent session
    → 发送通知给审查者
```

**优点：**
- 可以实现实际的"阻断"效果
- 利用 OpenClaw 已有的 TMUX 集成

**缺点：**
- 粗糙（kill session 而非优雅拦截）
- 需要 TMUX 权限和环境

### 5.3 远期路径：独立 hook 系统

在 oh-my-opencode 或 Claude Code 的 hook 系统中注入 SaucyClaw 治理逻辑：

```
tool.execute.before hook
    → 调用 SaucyClaw governance engine
    → 如果 Block，阻止 tool 执行
    → 通过 OpenClaw gateway 发送通知
```

**优点：**
- 真正的治理拦截
- 细粒度控制

**缺点：**
- 需要 oh-my-opencode 插件开发
- 需要深入 oh-my-opencode 的 hook 系统

---

## 6. 差距汇总表

| mock adapter 方法 | 真实对应 | 差距等级 | 说明 |
|------------------|---------|---------|------|
| `connect()` | `initializeOpenClaw()` | 小 | 概念类似，实质不同 |
| `collect_event()` | 无直接对应 | **大** | OpenClaw 不处理治理事件 |
| `intercept_output()` | 无对应 | **根本性** | OpenClaw 不是拦截器 |
| `write_back()` | `wakeGateway()` (单向) | **大** | 方向不同（双向 vs 单向） |
| `GateResult` 回写 | OpenClawPayload 发送 | **大** | 数据结构不同，方向不同 |

---

## 7. 对 SaucyClaw 架构的启示

### 7.1 当前 mock adapter 的价值

Mock adapter 的**内部流程**是正确的：
- `GovernanceEngine.process_event()` → `GateResult` ✓
- `ExplainBridge.enhance_output()` → `AdapterExplainOutput` ✓
- `ShadowRuntime.process_and_write()` ✓

但**外部接口契约**需要重新定义：
- 不再是 `write_back(GateResult)`（因为 OpenClaw 没有 write_back）
- 而是 `send_notification(DecisionBundle)`（通过 OpenClaw gateway）

### 7.2 推荐的适配器重构方向

```python
class OpenClawNotificationAdapter:
    """将 SaucyClaw 治理决策通过 OpenClaw gateway 发送为通知"""

    def __init__(self, gateway_url: str, gateway_type: str = "http"):
        self.gateway_url = gateway_url
        self.gateway_type = gateway_type

    def send_decision(self, result: GateResult, session_context: dict) -> WakeResult:
        """通过 OpenClaw gateway 发送治理决策通知"""
        payload = self._build_payload(result, session_context)
        return self._wake_gateway(payload)

    def _build_payload(self, result: GateResult, ctx: dict) -> dict:
        """构建 OpenClawPayload"""
        ...
```

### 7.3 保持兼容

- `ShadowRuntime` 的 `engine.process_event()` 部分完全可复用
- `ExplainBridge` 的解释输出可注入到 notification payload
- 只有 `adapter` 层需要从 mock 改为真实通知适配器
