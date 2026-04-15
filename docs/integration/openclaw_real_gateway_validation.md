# OpenClaw 真实 Gateway 验证报告

> M5 — 真实 Gateway 验证与 Notification 线路收口包
> 目的：记录真实 OpenClaw gateway 验证结果，明确当前 notification 线路是否可用
> 验证时间：2026-04-15
> 验证人：`<待填写>`
> 环境类型：`<mock / real>`（根据实际选择）

---

## 一、验证环境说明

### 1.1 环境类型

- [ ] **Mock 模式** — 本地 mock_gateway.py 接收端
- [ ] **Real 模式** — 真实 OpenClaw gateway（Discord / Telegram / 本地 oh-my-opencode）

### 1.2 环境配置

#### Mock 模式配置

| 配置项 | 值 |
|--------|-----|
| Gateway Type | `mock` |
| Gateway URL | `http://127.0.0.1:18790` |
| Gateway Name | `mock-gateway` |
| Timeout | 10000 ms |
| Output Dir | `./validation_output` |

#### Real 模式配置（示例）

| 配置项 | 值 |
|--------|-----|
| Gateway Type | `real` |
| Gateway URL | `http://your-openclaw-server:18789/hooks/agent` |
| Gateway Headers | `{"Content-Type": "application/json"}` |
| Timeout | 10000 ms |
| Output Dir | `./validation_output` |
| oh-my-opencode 版本 | `v3.13.1`（或实际版本） |

### 1.3 验证命令

```bash
# Mock 模式（默认）
python -m experiments.openclaw_poc.run_poc

# Real 模式（需配置环境变量）
export OPENCLAW_GATEWAY_TYPE="real"
export OPENCLAW_GATEWAY_URL="http://your-openclaw-server:18789/hooks/agent"
export OPENCLAW_GATEWAY_HEADERS='{"Content-Type": "application/json"}'
python -m experiments.openclaw_poc.run_poc
```

---

## 二、验证结果

### 2.1 Block 通知验证

#### 验证场景

- **Fixture**: `block_reviewer_same_as_assignee.yaml`
- **预期决策**: `Block`
- **触发规则**: `rule-reviewer-must-differ`

#### 验证结果

| 检查项 | 结果 | 说明 |
|--------|------|------|
| `WakeResult.success` | `<True / False>` | 适配器返回成功/失败 |
| `WakeResult.status_code` | `<200-399 / 400+>` | HTTP 状态码 |
| `WakeResult.error` | `<None / 错误信息>` | 错误信息（如失败） |
| 服务端收到 payload | `<是 / 否>` | 需人工检查日志 |
| payload.event | `governance-decision` | 事件类型正确 |
| payload.instruction 包含 Block | `<是 / 否>` | 决策类型正确 |
| payload.instruction 包含规则 | `<是 / 否>` | 规则信息正确 |
| payload.instruction 包含解释 | `<是 / 否>` | 解释信息正确 |

#### 证据文件

- `validation_output/block_reviewer_same_as_assignee_payload.json` — 发送的 payload
- `validation_output/block_reviewer_same_as_assignee_result.json` — WakeResult

#### 服务端日志（Real 模式必需）

```
<粘贴服务端收到的通知日志>
```

### 2.2 Allow 通知验证

#### 验证场景

- **Fixture**: `allow_specialist_via_reviewer.yaml`
- **预期决策**: `Allow`
- **触发规则**: `[]`（无规则触发）

#### 验证结果

| 检查项 | 结果 | 说明 |
|--------|------|------|
| `WakeResult.success` | `<True / False>` | 适配器返回成功/失败 |
| `WakeResult.status_code` | `<200-399 / 400+>` | HTTP 状态码 |
| `WakeResult.error` | `<None / 错误信息>` | 错误信息（如失败） |
| 服务端收到 payload | `<是 / 否>` | 需人工检查日志 |
| payload.event | `governance-decision` | 事件类型正确 |
| payload.instruction 包含 Allow | `<是 / 否>` | 决策类型正确 |
| payload.instruction 包含"未触发治理规则" | `<是 / 否>` | 无规则说明正确 |
| payload.instruction 包含解释 | `<是 / 否>` | 解释信息正确（"未触发治理规则"） |

#### 证据文件

- `validation_output/allow_specialist_via_reviewer_payload.json` — 发送的 payload
- `validation_output/allow_specialist_via_reviewer_result.json` — WakeResult

#### 服务端日志（Real 模式必需）

```
<粘贴服务端收到的通知日志>
```

### 2.3 Timeout / Failure 验证

#### 验证场景

- **Gateway URL**: `http://127.0.0.1:9999/nonexistent`（不可达）
- **Timeout**: 1000 ms

#### 验证结果

| 检查项 | 结果 | 说明 |
|--------|------|------|
| `WakeResult.success` | `<False>` | 必须为 False |
| `WakeResult.error` | `<Connection refused / timeout>` | 明确错误信息 |
| 未静默吞掉 | `<是>` | 有明确失败返回 |

#### 证据文件

- `validation_output/timeout_result.json` — WakeResult

---

## 三、验证总结

### 3.1 成功条件

当前验证视为**成功**，当且仅当：

- [ ] Block 通知发送成功（`WakeResult.success=True`）
- [ ] Allow 通知发送成功（`WakeResult.success=True`）
- [ ] Timeout 处理正确（`WakeResult.success=False` + 明确 error）
- [ ] Mock 模式：mock gateway 收到 payload
- [ ] Real 模式：服务端日志确认收到 payload
- [ ] payload 字段与 `OpenClawPayload` 契约一致（见 `docs/integration/openclaw_notification_contract.md`）

### 3.2 失败条件

当前验证视为**失败**，当：

- [ ] Block 通知发送失败（`WakeResult.success=False`）
- [ ] Allow 通知发送失败（`WakeResult.success=False`）
- [ ] Timeout 未正确处理（静默吞掉或无明确 error）
- [ ] payload 字段与契约不一致
- [ ] 解释信息未携带

### 3.3 当前状态（根据实际验证结果填写）

#### Mock 模式验证状态

- [x] Block 通知：**PASS**
- [x] Allow 通知：**PASS**
- [x] Timeout 处理：**PASS**
- [x] payload 结构对齐：**PASS**（参考 `block_reviewer_same_as_assignee_payload.json`）
- [x] 解释信息携带：**PASS**（payload.instruction 包含"解释: ..."）

#### Real 模式验证状态（如已验证）

- [ ] Block 通知：`<待验证>`
- [ ] Allow 通知：`<待验证>`
- [ ] Timeout 处理：`<待验证>`
- [ ] 服务端日志确认：`<待验证>`
- [ ] payload 结构对齐：`<待验证>`

---

## 四、当前 Notification 线路可用性判断

### 4.1 已验证的能力

| 能力 | 状态 | 说明 |
|------|------|------|
| HTTP POST 通知发送 | ✅ 已验证（Mock 模式） | `OpenClawNotificationAdapter` |
| payload 构建对齐 | ✅ 已验证 | 对齐 oh-my-opencode v3.13.1 `OpenClawPayload` |
| Explanation 携带 | ✅ 已验证 | 通过 `explanation_summary` 参数 |
| Timeout 处理 | ✅ 已验证 | 返回明确 `WakeResult` |
| 证据保存 | ✅ 已验证 | 自动保存到 `validation_output/` |
| Mock / Real 模式切换 | ✅ 已支持 | 通过环境变量 |

### 4.2 待验证的能力（Real 模式）

| 能力 | 状态 | 说明 |
|------|------|------|
| 真实 OpenClaw gateway 接收 | ⏳ 待验证 | 需真实环境 |
| Discord / Telegram 通知 | ⏳ 待验证 | 需配置 webhook |
| oh-my-opencode 集成 | ⏳ 待验证 | 需部署 OpenClaw |
| Reply listener 双向通信 | ⏳ 未来扩展 | 不在本轮范围 |

### 4.3 结论

当前 notification 线路：

- [x] **Mock 模式**：已验证可用，可作为本地测试和开发基础
- [ ] **Real 模式**：`<待填写>`（需补充真实环境验证）

---

## 五、还差什么才算"更正式的真实接入"

### 5.1 必须补充的能力

| 能力 | 优先级 | 说明 |
|------|--------|------|
| 真实环境验证 | 🔴 高 | 在真实 OpenClaw gateway 上完成一次完整验证 |
| 错误重试机制 | 🟡 中 | 超时/失败后自动重试（当前未实现） |
| 持久化未发送通知 | 🟡 中 | 失败通知暂存，后续重发 |
| 日志集成 | 🟢 低 | 与项目日志系统对接 |

### 5.2 可选扩展能力

| 能力 | 优先级 | 说明 |
|------|--------|------|
| Reply listener 双向通信 | 🔵 低 | 接收 OpenClaw 回复 |
| 多平台支持（Discord / Telegram） | 🔵 低 | 当前已支持，需配置 |
| Command gateway 支持 | 🔵 低 | `OpenClawCommandNotificationAdapter` 已实现 |
| 通知模板可配置化 | 🔵 低 | 当前硬编码在 `_build_openclaw_payload()` |

### 5.3 非本轮范围的能力

| 能力 | 说明 |
|------|------|
| 真正的 Block/拦截能力 | 需在 oh-my-opencode 插件层实现 |
| 平台管理面（规则热更新） | 需额外管理台开发 |
| UI/可视化 | 需前端开发 |
| 多租户/并发控制 | 需架构扩展 |

---

## 六、后续演进建议

### 6.1 短期（M6）

- **目标**：完成真实 OpenClaw gateway 验证
- **行动**：
  1. 配置真实环境（本地 oh-my-opencode / Discord / Telegram）
  2. 运行 `python -m experiments.openclaw_poc.run_poc`（Real 模式）
  3. 填写本报告第 2 节和第 3 节
  4. 更新本报告第 4 节结论

### 6.2 中期（M7）

- **目标**：Notification 线路正式化
- **行动**：
  1. 添加错误重试机制
  2. 添加持久化未发送通知
  3. 添加日志集成
  4. 补充单元测试覆盖边界情况

### 6.3 长期（M8+）

- **目标**：oh-my-opencode 插件治理拦截
- **行动**：
  1. 开发 SaucyClaw oh-my-opencode 插件
  2. 在 `tool.execute.before` hook 中注入治理检查
  3. 实现真正的治理拦截能力

---

## 七、附录

### 7.1 验证证据

所有验证证据保存在 `validation_output/` 目录：

- `block_reviewer_same_as_assignee_payload.json` — Block 场景 payload
- `block_reviewer_same_as_assignee_result.json` — Block 场景 WakeResult
- `allow_specialist_via_reviewer_payload.json` — Allow 场景 payload
- `allow_specialist_via_reviewer_result.json` — Allow 场景 WakeResult
- `timeout_result.json` — Timeout 场景 WakeResult

### 7.2 参考文档

- `docs/integration/openclaw_notification_poc.md` — Notification PoC 架构说明
- `docs/integration/openclaw_notification_contract.md` — 通知载荷契约定义
- `docs/integration/openclaw_real_gateway_requirements.md` — 真实环境需求清单
- `adapters/openclaw/notification_adapter.py` — 通知适配器实现
- `experiments/openclaw_poc/run_poc.py` — PoC 入口脚本

---

## 八、签字

验证人：`<待填写>`
验证时间：`<待填写>`
验证结论：`<待填写>`
