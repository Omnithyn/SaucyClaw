# OpenClaw 真实 Gateway 环境需求清单

> M5 — 真实 Gateway 验证与 Notification 线路收口包
> 目的：明确运行 M5 所需的最小真实环境条件，区分"必须有"和"可选项"

---

## 一、运行 M5 真实 Gateway 验证的前提条件

### 1.1 必须有（Required）

| 条目 | 说明 | 配置方式 | 默认值 |
|------|------|---------|--------|
| **Gateway URL** | OpenClaw gateway HTTP endpoint | 环境变量 `OPENCLAW_GATEWAY_URL` | 无（必须提供） |
| **Gateway Type** | 区分 mock / real | 环境变量 `OPENCLAW_GATEWAY_TYPE` | `"mock"`（默认） |
| **Gateway Headers** | HTTP headers（如认证） | 环境变量 `OPENCLAW_GATEWAY_HEADERS` | `{"Content-Type": "application/json"}` |

#### Gateway URL 示例

```bash
# OpenClaw oh-my-opencode 默认 webhook
export OPENCLAW_GATEWAY_URL="http://127.0.0.1:18789/hooks/agent"

# OpenClaw Discord gateway
export OPENCLAW_GATEWAY_URL="https://discord.com/api/webhooks/..."

# 自定义 OpenClaw HTTP server
export OPENCLAW_GATEWAY_URL="http://your-openclaw-server:8080/notify"
```

#### Gateway Type 说明

```bash
# Mock 模式：使用本地 mock_gateway.py
export OPENCLAW_GATEWAY_TYPE="mock"

# Real 模式：使用真实 OpenClaw gateway
export OPENCLAW_GATEWAY_TYPE="real"
```

#### Gateway Headers 示例

```bash
# 简单 Token 认证
export OPENCLAW_GATEWAY_HEADERS='{"Content-Type": "application/json", "Authorization": "Bearer YOUR_TOKEN"}'

# Discord webhook 不需要额外 headers（已有 token 在 URL 中）
export OPENCLAW_GATEWAY_HEADERS='{"Content-Type": "application/json"}'
```

### 1.2 可选项（Optional）

| 条目 | 说明 | 配置方式 | 默认值 |
|------|------|---------|--------|
| **Gateway Token** | 认证 token（如果 headers 未包含） | 环境变量 `OPENCLAW_GATEWAY_TOKEN` | 无 |
| **Timeout** | 请求超时（毫秒） | 环境变量 `OPENCLAW_TIMEOUT_MS` | `10000` |
| **验证输出目录** | 保存 payload / response 证据 | 环境变量 `VALIDATION_OUTPUT_DIR` | `./validation_output` |

---

## 二、当前仓库已具备的条件

### 2.1 已实现的代码能力

| 能力 | 文件 | 说明 |
|------|------|------|
| **HTTP POST 通知发送** | `adapters/openclaw/notification_adapter.py` | `OpenClawNotificationAdapter` |
| **Command gateway 支持** | `adapters/openclaw/notification_adapter.py` | `OpenClawCommandNotificationAdapter` |
| **Mock gateway server** | `experiments/openclaw_poc/mock_gateway.py` | 本地 HTTP server 接收端 |
| **统一 PoC 入口** | `experiments/openclaw_poc/run_poc.py` | 验证 Block / Allow / timeout |
| **Payload 构建对齐** | `adapters/openclaw/notification_adapter.py` | 对齐 oh-my-opencode v3.13.1 `OpenClawPayload` |
| **Explanation 携带** | `core/governance/explainer_bundle.py` | `bundle_explanations()` 生成解释摘要 |

### 2.2 已验证的 PoC 能力（Mock 模式）

```bash
# 当前可运行（Mock 模式）
export OPENCLAW_GATEWAY_TYPE="mock"
python -m experiments.openclaw_poc.run_poc

# 预期输出
[mock-gateway] Received event: governance-decision
[mock-gateway] Instruction:
  [governance|Block]
  决策: Block
  规则: rule-reviewer-must-differ
  ...
PoC Results:
  Block notification:  PASS
  Allow notification:  PASS
  Timeout handling:    PASS
```

### 2.3 待验证的真实能力（Real 模式）

```bash
# 配置真实环境后可运行（Real 模式）
export OPENCLAW_GATEWAY_TYPE="real"
export OPENCLAW_GATEWAY_URL="http://your-openclaw-server:18789/hooks/agent"
export OPENCLAW_GATEWAY_HEADERS='{"Content-Type": "application/json"}'
python -m experiments.openclaw_poc.run_poc

# 预期输出（需人工验证服务端日志）
[poc] Decision: Block
[poc] Notification sent to real gateway
[poc] WakeResult: success=True, status_code=200
```

---

## 三、当前仓库缺失的真实环境信息

### 3.1 完全缺失的信息

| 信息 | 说明 | 需要用户提供 |
|------|------|-------------|
| 真实 Gateway URL | OpenClaw webhook endpoint | ✅ 必须 |
| 认证方式 | Token / API Key / OAuth | ✅ 如果需要 |
| Gateway 日志查看方式 | 如何确认通知已接收 | ✅ 必须 |
| oh-my-opencode 部署路径 | 项目根目录位置 | ✅ 如果本地部署 |
| oh-my-opencode 版本 | 确认与 v3.13.1 类型对齐 | ✅ 建议 |

### 3.2 可推断但未验证的信息

| 信息 | 推断来源 | 需要验证 |
|------|---------|---------|
| HTTP POST 方法 | `notification_adapter.py` 实现 | ✅ 建议 |
| Content-Type: application/json | `notification_adapter.py` 默认 headers | ✅ 建议 |
| OpenClawPayload 字段 | oh-my-opencode v3.13.1 TS 类型 | ✅ 建议 |
| 200-399 成功 / 400+ 失败 | `notification_adapter.py` 逻辑 | ✅ 建议 |

---

## 四、如何准备真实环境

### 4.1 方式一：本地 oh-my-opencode 部署

1. 克隆 oh-my-opencode 仓库
   ```bash
   git clone https://github.com/OpenDevin/oh-my-opencode.git
   cd oh-my-opencode
   ```

2. 启动 OpenClaw webhook server
   ```bash
   # 根据 oh-my-opencode 文档启动 webhook server
   # 通常会监听 18789 端口
   npm run start:webhook
   ```

3. 获取 webhook URL
   ```bash
   export OPENCLAW_GATEWAY_URL="http://127.0.0.1:18789/hooks/agent"
   ```

4. 运行验证
   ```bash
   export OPENCLAW_GATEWAY_TYPE="real"
   python -m experiments.openclaw_poc.run_poc
   ```

### 4.2 方式二：Discord / Telegram webhook

1. 在 Discord / Telegram 创建 webhook
   - Discord: Server Settings → Integrations → Webhooks
   - Telegram: BotFather 创建 bot，获取 webhook URL

2. 配置环境变量
   ```bash
   # Discord webhook（token 已在 URL 中）
   export OPENCLAW_GATEWAY_URL="https://discord.com/api/webhooks/ID/TOKEN"

   # Telegram webhook
   export OPENCLAW_GATEWAY_URL="https://api.telegram.org/botTOKEN/sendMessage"
   export OPENCLAW_GATEWAY_HEADERS='{"Content-Type": "application/json"}'
   ```

3. 运行验证
   ```bash
   export OPENCLAW_GATEWAY_TYPE="real"
   python -m experiments.openclaw_poc.run_poc
   ```

### 4.3 方式三：自定义 HTTP server

1. 部署接收 OpenClawPayload 的 HTTP server
   - 可基于 Flask / FastAPI / Node.js
   - 实现 POST `/notify` endpoint
   - 记录收到的 payload

2. 配置环境变量
   ```bash
   export OPENCLAW_GATEWAY_URL="http://your-server:8080/notify"
   ```

3. 运行验证
   ```bash
   export OPENCLAW_GATEWAY_TYPE="real"
   python -m experiments.openclaw_poc.run_poc
   ```

---

## 五、最小验证清单

### 5.1 环境准备检查清单

- [ ] 已设置 `OPENCLAW_GATEWAY_TYPE="real"`
- [ ] 已设置 `OPENCLAW_GATEWAY_URL`
- [ ] 已设置 `OPENCLAW_GATEWAY_HEADERS`（如需要）
- [ ] 已确认 gateway server 正在运行
- [ ] 已确认可查看 gateway server 日志

### 5.2 运行验证检查清单

- [ ] 运行 `python -m experiments.openclaw_poc.run_poc`
- [ ] Block 场景发送成功（`WakeResult.success=True`）
- [ ] Allow 场景发送成功（`WakeResult.success=True`）
- [ ] Timeout 场景处理正确（`WakeResult.success=False` + 明确 error）
- [ ] 服务端日志确认收到 payload
- [ ] payload 字段与 `OpenClawPayload` 契约一致

### 5.3 验证证据保存

- [ ] 保存 payload dump（JSON 格式）
- [ ] 保存 WakeResult（JSON 格式）
- [ ] 保存服务端日志截图或文本
- [ ] 记录验证时间与环境信息

---

## 六、后续步骤

1. **准备真实环境** — 按第 4 节选择一种方式
2. **配置环境变量** — 按第 1 节设置必要变量
3. **运行验证** — 按第 5 节执行验证
4. **保存证据** — 按第 5.3 节保存验证结果
5. **更新验证文档** — 填写 `docs/integration/openclaw_real_gateway_validation.md`

---

## 七、常见问题

### Q1: 没有真实 OpenClaw 环境怎么办？

**A:** 可以先使用 Mock 模式验证代码链路，等待后续有真实环境再补充验证。

### Q2: Gateway URL 应该是什么格式？

**A:** 通常是 HTTP/HTTPS URL，包含完整路径。例如：
- `http://127.0.0.1:18789/hooks/agent`
- `https://discord.com/api/webhooks/ID/TOKEN`

### Q3: 如何确认通知已发送成功？

**A:**
- 代码侧：`WakeResult.success=True` 且 `status_code=200-399`
- 服务端：查看 gateway server 日志，确认收到 payload

### Q4: 超时时间如何调整？

**A:** 设置环境变量 `OPENCLAW_TIMEOUT_MS`，单位毫秒。默认 10000（10 秒）。

---

## 八、参考文档

- `docs/integration/openclaw_notification_poc.md` — Notification PoC 架构说明
- `docs/integration/openclaw_notification_contract.md` — 通知载荷契约定义
- `docs/integration/openclaw_real_runtime_gap_analysis.md` — 真实 OpenClaw 调查报告
- `adapters/openclaw/notification_adapter.py` — 通知适配器实现
