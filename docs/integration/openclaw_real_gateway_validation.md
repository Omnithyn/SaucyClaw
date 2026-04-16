# OpenClaw 真实 Gateway 验证记录单

> M8 / M8-R1 — Hooks Live Validation 文档与测试对齐
> 目的：记录真实 OpenClaw hooks gateway 验证结果
> Payload 类型：HookAgentPayload（使用 `message` 字段）
> 创建时间：2026-04-15
> 最后更新：2026-04-16

---

## 一、验证基本信息

| 字段 | 值 |
|------|-----|
| 验证人 | Claude (via SaucyClaw M8 Live Validation) |
| 验证日期 | 2026-04-16 |
| 验证环境 | `[X] Real`（Hooks API） |
| Gateway Endpoint | `/hooks/agent` |
| Payload 格式 | `HookAgentPayload`（`message`, `name`, `wakeMode`, `channel`） |
| 认证方式 | `Authorization: Bearer <token>` |
| 运行命令 | `python -m experiments.openclaw_poc.live_validation` |
| 证据输出目录 | `real_validation_output/` |

---

## 二、Block 通知验证

### 2.1 场景信息

| 字段 | 值 |
|------|-----|
| Fixture | `block_reviewer_same_as_assignee.yaml` |
| 预期决策 | `Block` |
| 预期触发规则 | `rule-reviewer-must-differ` |

### 2.2 Hooks Payload 检查项

- [ ] `payload.message` 包含 `"[governance|Block]"`
- [ ] `payload.message` 包含 `"决策: Block"`
- [ ] `payload.message` 包含 `"rule-reviewer-must-differ"`
- [ ] `payload.name` = `"SaucyClaw Governance"`
- [ ] `payload.wakeMode` = `"now"`
- [ ] `payload.channel` = `"last"`
- [ ] `payload.deliver` = `true`

### 2.3 Hooks 响应检查项

- [ ] 响应 `ok` = `true`
- [ ] 响应包含 `runId`
- [ ] HTTP 状态码 = `200`

### 2.4 证据检查项

- [ ] Payload 文件存在：`real_validation_output/block_reviewer_same_as_assignee_payload.json`
- [ ] Evidence 文件存在：`real_validation_output/block_reviewer_same_as_assignee_evidence.json`
- [ ] Evidence 中 `mode` = `"live"`
- [ ] Evidence 中 `success` = `true`
- [ ] Evidence 中 `run_id` 非空
- [ ] Evidence 中 `status_code` = `200`

### 2.5 Real 模式结果（已验证）

| 检查项 | 结果 | 说明 |
|--------|------|------|
| 发送成功 | `[X] PASS` | runId: `9841ee87-9588-4200-8bd6-679436761540` |
| Payload 结构 | `[X] PASS` | HookAgentPayload 格式正确 |
| message 内容 | `[X] PASS` | 包含完整治理决策信息 |
| runId 返回 | `[X] PASS` | 响应包含 runId |

### 2.6 服务端响应

```json
{
  "ok": true,
  "runId": "9841ee87-9588-4200-8bd6-679436761540"
}
```

---

## 三、Allow 通知验证

### 3.1 场景信息

| 字段 | 值 |
|------|-----|
| Fixture | `allow_specialist_via_reviewer.yaml` |
| 预期决策 | `Allow` |
| 预期触发规则 | `[]`（无规则触发） |

### 3.2 Hooks Payload 检查项

- [ ] `payload.message` 包含 `"[governance|Allow]"`
- [ ] `payload.message` 包含 `"未触发治理规则"`
- [ ] `payload.message` 包含 `"原因: 无规则触发"`
- [ ] `payload.name` = `"SaucyClaw Governance"`

### 3.3 Real 模式结果（已验证）

| 检查项 | 结果 | 说明 |
|--------|------|------|
| 发送成功 | `[X] PASS` | runId: `d9603b89-f08c-441c-8064-4e0fc40fe699` |
| Payload 结构 | `[X] PASS` | HookAgentPayload 格式正确 |
| message 内容 | `[X] PASS` | 包含"未触发治理规则" |

### 3.4 服务端响应

```json
{
  "ok": true,
  "runId": "d9603b89-f08c-441c-8064-4e0fc40fe699"
}
```

---

## 四、失败路径验证（无效 Token）

### 4.1 场景信息

| 字段 | 值 |
|------|-----|
| 测试目的 | 验证无效 token 正确拒绝 |
| Token | `invalid-token-for-testing` |

### 4.2 检查项

- [ ] HTTP 状态码 = `401`
- [ ] 响应包含错误信息
- [ ] 未静默吞掉错误

### 4.3 Real 模式结果（已验证）

| 检查项 | 结果 | 说明 |
|--------|------|------|
| 正确拒绝 | `[X] PASS` | HTTP 401 Unauthorized |
| 错误信息 | `[X] PASS` | 返回 Unauthorized |

---

## 五、验证证据文件清单

当前 `real_validation_output/` 目录中的文件：

| 文件 | 场景 | 说明 | 状态 |
|------|------|------|------|
| `block_reviewer_same_as_assignee_payload.json` | Block | HookAgentPayload（message 字段） | ✅ 已生成 |
| `block_reviewer_same_as_assignee_evidence.json` | Block | LiveValidationEvidence（mode=live） | ✅ 已生成 |
| `allow_specialist_via_reviewer_payload.json` | Allow | HookAgentPayload | ✅ 已生成 |
| `allow_specialist_via_reviewer_evidence.json` | Allow | LiveValidationEvidence | ✅ 已生成 |
| `invalid_token_test_payload.json` | Failure | 测试 payload | ✅ 已生成 |
| `invalid_token_test_evidence.json` | Failure | 失败证据 | ✅ 已生成 |

### Evidence 文件结构（LiveValidationEvidence）

```json
{
  "scenario": "<场景名>",
  "gateway_url": "<gateway URL>",
  "timestamp": "<ISO 8601>",
  "payload": { "<HookAgentPayload>" },
  "gateway": "<gateway 名称>",
  "success": true | false,
  "run_id": "<runId 或 null>",
  "error": null | "<错误信息>",
  "status_code": 200 | null | <HTTP 状态码>,
  "mode": "live"
}
```

---

## 六、验证结论

### 6.1 验证通过条件

- [x] Block 通知验证通过
- [x] Allow 通知验证通过
- [x] 失败路径正确处理（无效 token 返回 401）
- [x] Payload 结构与 `HookAgentPayload` 契约一致
- [x] Evidence 文件包含 `runId` 和正确字段

### 6.2 当前状态

| 场景 | 结果 | Payload 格式 | Evidence |
|------|------|--------------|----------|
| Block | ✅ PASS | HookAgentPayload | LiveValidationEvidence |
| Allow | ✅ PASS | HookAgentPayload | LiveValidationEvidence |
| Failure | ✅ PASS | - | LiveValidationEvidence |

### 6.3 验证人签字

| 字段 | 值 |
|------|-----|
| 验证人 | Claude (M8 Live Validation) |
| 签字日期 | 2026-04-16 |
| 验证结论 | `[X] 通过` |
| 备注 | Hooks 真实 gateway 已打通，HookAgentPayload 格式正确 |

---

## 七、参考文档

- `docs/integration/openclaw_hooks_contract.md` — Hooks Payload 契约定义
- `docs/integration/openclaw_notification_runner.md` — Notification runner 说明
- `adapters/openclaw/hooks_adapter.py` — Hooks 适配器实现
- `experiments/openclaw_poc/live_validation.py` — Live validation runner