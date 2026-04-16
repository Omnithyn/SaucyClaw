# OpenClaw Hooks Payload 契约

> M8-R1 — Hooks Live Validation 文档与测试对齐
> 目的：说明 hooks 线路的 payload 结构、与旧 notification payload 的区别、响应结构
> 成熟度：最小可用（MVP）

---

## 一、HookAgentPayload 结构

### 1.1 完整定义

根据 OpenClaw 源代码（`src/gateway/hooks.ts`）：

```typescript
type HookAgentPayload = {
  message: string;             // 必需 - 消息内容
  name: string;                // 可选 - Hook 名称（默认 "Hook"）
  agentId?: string;            // 可选 - 目标 agent ID
  idempotencyKey?: string;     // 可选 - 幂等键
  wakeMode: "now" | "next-heartbeat";  // 默认 "now"
  sessionKey?: string;         // 可选 - 会话键（需配置允许）
  deliver: boolean;            // 默认 true
  channel: HookMessageChannel; // 默认 "last"
  to?: string;                 // 可选 - 目标地址
  model?: string;              // 可选 - 模型覆盖
  thinking?: string;           // 可选 - thinking 级别
  timeoutSeconds?: number;     // 可选 - 超时秒数
}

type HookMessageChannel = "last" | "whatsapp" | "telegram" | "discord" | "irc" | "googlechat" | "slack" | "signal" | "imessage" | "msteams";
```

### 1.2 SaucyClaw 使用的最小结构

```json
{
  "message": "[governance|Block]\n决策: Block\n规则: ...\n原因: ...",
  "name": "SaucyClaw Governance",
  "wakeMode": "now",
  "deliver": true,
  "channel": "last"
}
```

### 1.3 字段说明

| 字段 | 必需 | 说明 |
|------|------|------|
| `message` | ✓ | 完整消息内容（支持多行） |
| `name` | ✗ | Hook 名称，默认 "Hook" |
| `wakeMode` | ✗ | "now" 立即执行，"next-heartbeat" 下次心跳 |
| `deliver` | ✗ | 是否发送通知，默认 true |
| `channel` | ✗ | 发送通道，默认 "last"（最近使用的通道） |

---

## 二、与旧 Notification Payload 的区别

### 2.1 结构对比

| 特性 | OpenClawPayload（旧） | HookAgentPayload（hooks） |
|------|----------------------|--------------------------|
| 核心字段 | `event`, `instruction`, `text`, `timestamp` | `message`, `name` |
| 用途 | oh-my-opencode 内部通知 | hooks API `/hooks/agent` |
| endpoint | 无直接 endpoint | `POST /hooks/agent` |
| 认证 | 无 | Bearer token 必需 |

### 2.2 为什么需要两套适配器

- `OpenClawNotificationAdapter` — 用于旧通知线（保留兼容）
- `OpenClawHooksAdapter` — 用于 hooks 真实对接（M8 新增）

### 2.3 message 字段内容格式

hooks 的 `message` 字段承载完整治理决策信息：

```
[governance|Block]
决策: Block
规则: rule-reviewer-must-differ
原因: 触发 1 条规则，最高 severity: block
建议: 输出被阻断，请检查治理规则配置
解释: 触发阻断（high/separation_of_duties）：防止审查者与执行者同一人
```

---

## 三、/hooks/agent 响应结构

### 3.1 成功响应

```json
{
  "ok": true,
  "runId": "9841ee87-9588-4200-8bd6-679436761540"
}
```

### 3.2 失败响应

```json
{
  "ok": false,
  "error": "message required"
}
```

或 HTTP 状态码：
- 401 Unauthorized — token 无效
- 400 Bad Request — payload 格式错误
- 429 Too Many Requests — 认证失败次数过多被限流

---

## 四、当前 hooks 线的边界

### 4.1 已完成

- ✅ HookAgentPayload 格式正确发送
- ✅ Block/Allow 场景验证通过
- ✅ runId 返回并记录
- ✅ 失败路径正确处理（401 错误）

### 4.2 未完成（不属于当前范围）

- ❌ 多通道测试（Discord/Telegram 等）
- ❌ idempotencyKey 幂等性验证
- ❌ sessionKey 会话键测试
- ❌ agentId 路由测试

---

## 五、参考

- `adapters/openclaw/hooks_adapter.py` — Hooks 适配器实现
- `../clawdbot/src/gateway/hooks.ts` — OpenClaw hooks payload 定义
- `experiments/openclaw_poc/live_validation.py` — Live validation runner