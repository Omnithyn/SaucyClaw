# Runtime Host Abstraction

> M10 — Runtime-Neutral Host Abstraction
> 目的：定义宿主无关的接入抽象层，为多 runtime 扩展做准备
> 成熟度：概念定义 + OpenClaw 首个 profile

---

## 一、什么是 Host Runtime

Host Runtime 是指 SaucyClaw 治理内核外部的**执行环境**——即被治理的 agent 系统。

SaucyClaw 不替代 runtime，而是作为**治理基座**挂载到 runtime 上，通过以下方式介入：

1. **接收事件** — 从 runtime 获取原始事件
2. **执行治理** — 通过 GovernanceEngine 处理
3. **回写结果** — 将决策写回 runtime 或发送到通知通道

```
┌──────────────────────┐
│    SaucyClaw Core    │  ← 治理内核（runtime 无关）
│  engine / governance │
│  evidence / memory   │
├──────────────────────┤
│   Host Abstraction   │  ← 宿主抽象层（本层定义）
│  protocols / modes   │
│  profiles / results  │
├──────────────────────┤
│     Host Runtime     │  ← 外部执行环境（OpenClaw/Hermes/...）
│  events / hooks /    │
│  notification / UI   │
└──────────────────────┘
```

---

## 二、SaucyClaw 对宿主的最小要求

接入 SaucyClaw 的宿主必须提供：

| 能力 | 必需 | 说明 |
|------|------|------|
| 事件输出 | ✅ | 能暴露原始输出事件供治理拦截 |
| 结果回写 | ✅ | 能接收治理决策并响应 |
| 通知通道 | ❌ | 用于发送治理通知（可选） |
| Hooks API | ❌ | 用于真实消息发送（可选） |

---

## 三、当前已识别的三种接入模式

| 模式 | 目的 | 必需宿主能力 | 成熟度 |
|------|------|-------------|--------|
| **shadow** | 本地 mock 测试、治理引擎外围接入 | 结果回写 | 正式工程面 |
| **notification** | 旧通知线兼容、内部通知 | 通知通道（HTTP/command） | 正式工程面 |
| **hooks-live** | 真实 runtime hooks 对接 | Hooks API | MVP |

### 3.1 Shadow Mode

- 不依赖真实 runtime
- 使用 mock adapter 模拟宿主行为
- 适用于本地测试和治理引擎验证

### 3.2 Notification Mode

- 通过 HTTP POST 或 shell command 发送通知
- 使用 runtime 特定的 payload 格式
- 适用于内部通知和旧通知线兼容

### 3.3 Hooks-Live Mode

- 通过 runtime 的真实 Hooks API 发送消息
- 使用 runtime 特定的 hooks payload 格式
- 适用于生产级治理通知发送

---

## 四、模式与宿主的关系

```
                    ┌─────────────────┐
                    │   Host Profile  │
                    │   (per runtime) │
                    └────────┬────────┘
                             │
           ┌─────────────────┼─────────────────┐
           │                 │                 │
    ┌──────▼──────┐  ┌──────▼──────┐  ┌───────▼──────┐
    │   shadow    │  │ notification│  │  hooks-live  │
    │   mode      │  │    mode     │  │    mode      │
    └─────────────┘  └─────────────┘  └──────────────┘
           │                 │                 │
           ▼                 ▼                 ▼
    MockAdapter       NotificationAdapter  HooksAdapter
```

- **Host Profile** 定义某个 runtime 支持哪些模式
- **每种模式** 对应一个具体的 adapter 实现
- **同一 runtime** 可以同时支持多种模式

---

## 五、为什么这层抽象对多 runtime 扩展必要

### 5.1 避免重复定义

没有抽象层时，每个 runtime 都需要重新定义：
- 什么是 "wake result"
- 什么是 "send decision"
- 什么是 "mode"

有了抽象层后，这些概念有统一的上位定义。

### 5.2 模式可迁移

Shadow Mode 不依赖任何具体 runtime，因此可以直接用于新 runtime 的治理引擎验证。

### 5.3 能力可比较

通过 capability matrix，可以清晰比较不同 runtime 的治理接入能力。

### 5.4 新 runtime 接入路径清晰

新 runtime 接入时只需：
1. 定义 HostProfile（声明支持哪些模式）
2. 实现对应模式的 Adapter
3. 接入现有治理内核

---

## 六、参考

- `stores/protocols.py` — 基础协议定义（HostAdapter、GateResult）
- `docs/integration/runtime_capability_matrix.md` — 能力矩阵
- `adapters/host_protocols.py` — 宿主抽象协议
- `adapters/openclaw/profile.py` — OpenClaw 宿主 profile
