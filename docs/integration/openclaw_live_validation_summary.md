# OpenClaw Live Validation 总结

> M8 — 真实 Gateway Live Validation 包
> 目的：记录真实 OpenClaw hooks gateway 的 live validation 结果
> 验证日期：2026-04-16
> 成熟度：Live validation 已完成

---

## 一、验证基本信息

| 字段 | 值 |
|------|-----|
| 验证人 | Claude (via SaucyClaw) |
| 验证日期 | 2026-04-16 |
| 验证环境 | Real (OpenClaw hooks) |
| Gateway URL | `http://127.0.0.1:26277/hooks/agent` |
| Endpoint | `/hooks/agent` |
| 认证方式 | `Authorization: Bearer <token>` |
| 运行命令 | `python -m experiments.openclaw_poc.live_validation` |
| 证据输出目录 | `real_validation_output/` |

---

## 二、验证结果

### 2.1 Block 通知验证

| 检查项 | 结果 | 说明 |
|--------|------|------|
| 发送成功 | ✅ PASS | `{"ok":true,"runId":"..."}` |
| Payload 结构 | ✅ PASS | HookAgentPayload 格式正确 |
| 解释信息 | ✅ PASS | message 包含完整治理决策信息 |
| runId 返回 | ✅ PASS | `9841ee87-9588-4200-8bd6-679436761540` |
| Evidence 保存 | ✅ PASS | `real_validation_output/block_reviewer_same_as_assignee_evidence.json` |

### 2.2 Allow 通知验证

| 检查项 | 结果 | 说明 |
|--------|------|------|
| 发送成功 | ✅ PASS | `{"ok":true,"runId":"..."}` |
| Payload 结构 | ✅ PASS | HookAgentPayload 格式正确 |
| 解释信息 | ✅ PASS | message 包含"未触发治理规则" |
| runId 返回 | ✅ PASS | `d9603b89-f08c-441c-8064-4e0fc40fe699` |
| Evidence 保存 | ✅ PASS | `real_validation_output/allow_specialist_via_reviewer_evidence.json` |

### 2.3 失败路径验证（无效 token）

| 检查项 | 结果 | 说明 |
|--------|------|------|
| 正确拒绝 | ✅ PASS | HTTP 401 Unauthorized |
| 错误信息 | ✅ PASS | 明确返回 Unauthorized |
| 未静默吞掉 | ✅ PASS | 正确返回错误 |

---

## 三、验证证据文件清单

| 文件 | 场景 | 状态 |
|------|------|------|
| `block_reviewer_same_as_assignee_payload.json` | Block | ✅ 已生成 |
| `block_reviewer_same_as_assignee_evidence.json` | Block | ✅ 已生成 |
| `allow_specialist_via_reviewer_payload.json` | Allow | ✅ 已生成 |
| `allow_specialist_via_reviewer_evidence.json` | Allow | ✅ 已生成 |
| `invalid_token_test_payload.json` | Failure | ✅ 已生成 |
| `invalid_token_test_evidence.json` | Failure | ✅ 已生成 |

---

## 四、关键技术发现

### 4.1 OpenClaw Hooks Payload 格式

OpenClaw `/hooks/agent` endpoint 接收 `HookAgentPayload` 格式：

```json
{
  "message": "完整消息内容（支持多行）",
  "name": "Hook 名称",
  "wakeMode": "now",
  "deliver": true,
  "channel": "last"
}
```

**关键区别：**
- `OpenClawPayload`（oh-my-opencode 内部）：使用 `event`, `instruction`, `text`, `timestamp`
- `HookAgentPayload`（hooks API）：使用 `message`, `name`, `wakeMode`, `channel`

### 4.2 认证方式

两种认证方式：
1. `Authorization: Bearer <token>`
2. `X-OpenClaw-Token: <token>`

### 4.3 新增适配器

创建了 `OpenClawHooksAdapter`（`adapters/openclaw/hooks_adapter.py`）专门用于 `/hooks/agent` endpoint。

---

## 五、最终结论

### 5.1 当前状态

| 能力 | 状态 | 说明 |
|------|------|------|
| 真实 Gateway 打通 | ✅ 完成 | Block/Allow 成功发送 |
| Hooks 认证 | ✅ 完成 | Bearer token 认证通过 |
| Payload 格式适配 | ✅ 完成 | HookAgentPayload 格式正确 |
| Evidence 落盘 | ✅ 完成 | 真实验证证据已保存 |

### 5.2 距离正式生产接入还差什么

| 差距 | 说明 |
|------|------|
| **消息队列** | 当前是同步发送，未引入异步队列 |
| **持久化 Outbox** | 失败消息未持久化，无法重试 |
| **Tracing** | 无分布式追踪能力 |
| **幂等性** | 依赖 idempotencyKey，未验证 |
| **多通道支持** | 当前仅 channel="last"，未测试 Discord/Telegram 等 |
| **高可用** | Gateway 单点，无冗余 |

### 5.3 成熟度评估

当前 notification 路处于 **"最小可用（MVP）"** 成熟度：
- ✅ 能发送真实通知到 OpenClaw
- ✅ Block/Allow 场景验证通过
- ✅ 失败路径正确处理
- ❌ 不具备生产级可靠性（队列、持久化、高可用）

---

## 六、后续建议

1. **保持当前 MVP** — 作为 SaucyClaw governance 的最小通知能力
2. **不急于引入队列** — 当前满足治理决策通知的基本需求
3. **渐进增强** — 当有真实生产场景时再补队列/持久化

---

## 七、里程碑链

| 里程碑 | 主要交付 |
|--------|---------|
| M5-M7 | Mock 模式验证、契约定义、工程化收口 |
| M8 | 真实 Gateway Live Validation（本文档） |

---

## 八、参考

- `adapters/openclaw/hooks_adapter.py` — OpenClaw Hooks 适配器
- `experiments/openclaw_poc/live_validation.py` — Live validation runner
- `../clawdbot/src/gateway/hooks.ts` — OpenClaw hooks payload 定义