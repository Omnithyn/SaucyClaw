# OpenClaw Integration Modes

> M9 — OpenClaw 接入面统一收口包
> 目的：定义 OpenClaw 的三种接入模式，明确适用场景、入口模块、成熟度
> 成熟度：正式工程面（shadow/notification） + MVP（hooks-live）

---

## 一、三种接入模式

| 模式 | 目的 | 适用场景 | 入口模块 | 成熟度 | 正式工程面 |
|------|------|---------|---------|--------|-----------|
| **shadow** | 治理决策外围包装 | 本地 mock 测试、治理引擎外围接入 | `ShadowRuntime` | 正式工程面 | ✅ 是 |
| **notification** | 通知发送（OpenClawPayload） | 旧通知线兼容、内部通知 | `OpenClawNotificationAdapter` | 正式工程面 | ✅ 是 |
| **hooks-live** | 真实 hooks 对接 | 真实 OpenClaw gateway、治理决策通知 | `OpenClawHooksAdapter` | MVP | ⚠️ 最小可用 |

---

## 二、Shadow Mode

### 2.1 目的

提供一个治理引擎的外围包装模板，让 Shadow Mode 从"手工调用示例"变成"可复用运行时入口"。

### 2.2 适用场景

- 本地 mock 测试
- 治理引擎外围接入
- 不需要真实 OpenClaw gateway 的场景

### 2.3 入口模块

```python
from adapters.openclaw import ShadowRuntime, ShadowRunResult

# 使用方式
runtime = ShadowRuntime(engine, adapter, explain_bridge)
result = runtime.process_and_write(raw_event)
```

### 2.4 输出结构

- `ShadowRunResult.gate_result` — 治理引擎决策结果
- `ShadowRunResult.enhanced_output` — 增强的解释输出

### 2.5 当前成熟度

**正式工程面**：
- 核心逻辑稳定
- 有单元测试覆盖
- 不依赖真实 gateway

---

## 三、Notification Mode

### 3.1 目的

提供通知发送能力，使用 `OpenClawPayload` 格式。

### 3.2 适用场景

- 旧通知线兼容
- oh-my-opencode 内部通知
- 不需要 `/hooks/agent` endpoint

### 3.3 入口模块

```python
from adapters.openclaw import OpenClawNotificationAdapter, WakeResult

# 使用方式
adapter = OpenClawNotificationAdapter(
    gateway_url="http://your-gateway",
    gateway_name="notification",
)
result = adapter.send_decision(gate_result, session_context)
```

### 3.4 输出结构

- `WakeResult.gateway` — gateway 名称
- `WakeResult.success` — 是否成功
- `WakeResult.error` — 错误信息
- `WakeResult.status_code` — HTTP 状态码

### 3.5 Payload 格式

`OpenClawPayload`：
- `event` — 事件类型
- `instruction` — 指令文本
- `text` — 可读摘要
- `timestamp` — 时间戳

### 3.6 当前成熟度

**正式工程面**：
- 核心逻辑稳定
- 有单元测试覆盖
- payload 结构对齐 OpenClaw

---

## 四、Hooks-Live Mode

### 4.1 目的

提供真实 OpenClaw hooks 对接能力，使用 `HookAgentPayload` 格式。

### 4.2 适用场景

- 真实 OpenClaw gateway 对接
- 治理决策通知（Block/Allow）
- 需要 `/hooks/agent` endpoint

### 4.3 入口模块

```python
from adapters.openclaw import OpenClawHooksAdapter, HooksWakeResult

# 使用方式（从配置加载）
from core.config import load_notification_config

config = load_notification_config()
adapter = OpenClawHooksAdapter(
    gateway_url=config.gateway_url,
    token=config.hooks_token,
)
result = adapter.send_decision(gate_result, explanation_summary)
```

### 4.4 输出结构

- `HooksWakeResult.gateway` — gateway 名称
- `HooksWakeResult.success` — 是否成功
- `HooksWakeResult.run_id` — OpenClaw 返回的 runId
- `HooksWakeResult.error` — 错误信息
- `HooksWakeResult.status_code` — HTTP 状态码

### 4.5 Payload 格式

`HookAgentPayload`：
- `message` — 消息内容（支持多行）
- `name` — Hook 名称
- `wakeMode` — "now" 或 "next-heartbeat"
- `channel` — 发送通道（默认 "last"）

### 4.6 当前成熟度

**MVP（最小可用）**：
- Block/Allow 真实发送已验证
- 有单元测试覆盖
- 不具备生产级可靠性（队列、持久化、高可用）

---

## 五、模式选择指南

### 5.1 如何选择

| 需求 | 推荐模式 |
|------|---------|
| 本地 mock 测试 | **shadow** |
| 内部通知（不需要 hooks） | **notification** |
| 真实 OpenClaw gateway 对接 | **hooks-live** |

### 5.2 配置方式

**hooks-live 模式需要配置：**

配置文件 `~/.saucyclaw/saucyclaw.json`：
```json
{
  "notification": {
    "gateway_url": "http://your-gateway/hooks/agent",
    "hooks_token": "your-token",
    "timeout_ms": 10000
  }
}
```

---

## 六、PoC/Experiment 模块

以下模块属于 PoC/experiment，不是正式工程面：

| 文件 | 用途 | 说明 |
|------|------|------|
| `experiments/openclaw_poc/notification_contract.py` | PoC 验证契约 | 用于 validation runner |
| `experiments/openclaw_poc/notification_retry.py` | PoC retry 机制 | 最小 retry 实现 |
| `experiments/openclaw_poc/run_poc.py` | PoC runner | mock/real 验证脚本 |
| `experiments/openclaw_poc/live_validation.py` | Live validation | hooks 真实验证脚本 |

**说明**：这些模块服务于验证和实验，当正式化时可平滑迁移。

---

## 七、参考

- `docs/integration/openclaw_hooks_contract.md` — Hooks Payload 契约
- `.local-docs/integration/openclaw_notification_contract.md` — Notification Payload 契约
- `docs/integration/openclaw_results_evidence.md` — 结果与证据关系
- `docs/configuration.md` — 配置说明