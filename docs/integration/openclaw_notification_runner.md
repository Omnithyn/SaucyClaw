# OpenClaw Notification Runner

> M7 — Notification 线路工程化收口
> 目的：说明 notification 线路的组成、模块关系、使用方式、成熟度边界
> 成熟度：最小可靠投递版（M6）→ 工程化收口（M7）

---

## 1. Notification 线路当前组成

### 1.1 正式工程面（`adapters/openclaw/`）

| 文件 | 职责 | 成熟度 |
|------|------|--------|
| `notification_adapter.py` | HTTP/Command gateway 发送适配器 | **正式工程面** |
| `notification_adapter.py:WakeResult` | 发送结果结构（adapter 核心返回值） | **正式工程面** |

**说明：**
- `OpenClawNotificationAdapter` 是正式 notification 线的核心适配器
- `WakeResult` 是 adapter 层的核心返回值结构
- 这两个是外部调用方接入 notification 线的主要入口

### 1.2 PoC/experiment（`experiments/openclaw_poc/`）

| 文件 | 职责 | 成熟度 |
|------|------|--------|
| `run_poc.py` | PoC runner — 验证 notification 线路的实验脚本 | **PoC/experiment** |
| `mock_gateway.py` | Mock server — 本地 mock gateway 服务器 | **PoC/experiment** |
| `notification_contract.py` | 验证契约 — SendResult/NotificationEvidence | **PoC/experiment** |
| `notification_retry.py` | Retry 机制 — 最小 retry 实现 | **PoC/experiment** |

**说明：**
- 本目录下的模块是 PoC 验证实验包，不是正式 notification 线的核心能力
- `NotificationEvidence` 用于 PoC evidence 保存，不用于正式 notification 线
- `SendResult` 是验证用的包装结构，包含 retry 信息
- `RetryConfig`/`with_retry` 是最小 retry 实现，当 notification 线正式化时可平滑迁移

---

## 2. 契约、Adapter、Retry、Runner 的关系

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Notification 线路架构                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 正式工程面 (adapters/openclaw/)                              │   │
│  │                                                             │   │
│  │  OpenClawNotificationAdapter                                │   │
│  │    └── send_decision() → WakeResult                        │   │
│  │        ├── HTTP gateway 发送                                │   │
│  │        ├── payload 构建                                     │   │
│  │        └── 错误处理                                          │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ PoC/experiment (experiments/openclaw_poc/)                  │   │
│  │                                                             │   │
│  │  run_poc.py                                                 │   │
│  │    └── main() → 运行验证场景                                │   │
│  │        ├── 调用 OpenClawNotificationAdapter                 │   │
│  │        ├── 用 with_retry 包装发送                           │   │
│  │        ├── 保存 NotificationEvidence                        │   │
│  │        └── 输出验证结果                                      │   │
│  │                                                             │   │
│  │  notification_retry.py                                      │   │
│  │    └── with_retry(send_func) → (result, attempts, retried) │   │
│  │                                                             │   │
│  │  notification_contract.py                                   │   │
│  │    ├── SendResult — 验证用的包装结构                        │   │
│  │    └── NotificationEvidence — 验证记录结构                 │   │
│  │                                                             │   │
│  │  mock_gateway.py                                            │   │
│  │    └── 本地 mock HTTP server（仅 mock 模式）                │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Mock / Real 两种模式怎么跑

### 3.1 Mock 模式（默认）

**用法：**
```bash
python -m experiments.openclaw_poc.run_poc
```

**特点：**
- 自动启动本地 mock gateway server（端口 18790）
- 不需要配置环境变量
- 输出验证证据到 `validation_output/`

**验证内容：**
1. Block 场景：触发治理规则，发送 Block 通知
2. Allow 场景：不触发规则，发送 Allow 通知
3. Timeout 场景：不可达 gateway，测试超时处理

### 3.2 Real 模式

**用法：**
```bash
export OPENCLAW_GATEWAY_TYPE="real"
export OPENCLAW_GATEWAY_URL="http://your-openclaw-server:18789/hooks/agent"
python -m experiments.openclaw_poc.run_poc
```

**必需环境变量：**
- `OPENCLAW_GATEWAY_TYPE="real"`
- `OPENCLAW_GATEWAY_URL` — OpenClaw webhook URL

**可选环境变量：**
- `OPENCLAW_GATEWAY_HEADERS` — JSON headers（默认 `{"Content-Type": "application/json"}`）
- `OPENCLAW_TIMEOUT_MS` — 超时毫秒（默认 10000）
- `VALIDATION_OUTPUT_DIR` — 验证证据目录（默认 `./validation_output`）
- `OPENCLAW_RETRY_ENABLED` — 启用/禁用 retry（默认 `true`）

---

## 4. 当前成熟度与边界

### 4.1 已完成

- ✅ mock/real 模式支持
- ✅ evidence 保存（含 pre-send failure 区分）
- ✅ 最小 retry 机制（2 次重试）
- ✅ 契约定义清晰（WakeResult、SendInput、NotificationEvidence）
- ✅ runner 输入/输出/成功/失败路径清晰

### 4.2 未完成（不属于当前范围）

- ❌ 消息队列
- ❌ 持久化 outbox
- ❌ tracing 平台
- ❌ UI 管理面
- ❌ 正式 OpenClaw 插件开发

### 4.3 成熟度说明

**为什么叫"最小可靠投递版"：**
- notification 线路满足基本可靠投递需求
- 不夸大为"正式生产接入完成"
- Retry、Evidence、Contract 仍属于 PoC/experiment
- 当正式化时，可平滑迁移或替换

---

## 5. 哪些东西仍然是实验性质

| 模块 | 实验性质说明 |
|------|-------------|
| `notification_contract.py` | 验证用的契约结构，不是正式 notification 线核心 |
| `notification_retry.py` | 最小 retry 实现，未持久化，无幂等保证 |
| `run_poc.py` | PoC 验证脚本，不是正式运行时入口 |
| `mock_gateway.py` | 仅用于 mock 模式测试，不是生产组件 |
| `NotificationEvidence` | 验证记录结构，用于 PoC evidence 保存 |

---

## 6. 外部调用方应该从哪里接 notification 线

### 6.1 正式接入方式

```python
from adapters.openclaw.notification_adapter import OpenClawNotificationAdapter

adapter = OpenClawNotificationAdapter(
    gateway_url="http://your-openclaw-server:18789/hooks/agent",
    gateway_name="production",
)

result = adapter.send_decision(
    gate_result,
    session_context={"session_id": "..."},
)
```

### 6.2 PoC 验证方式

```bash
# Mock 模式
python -m experiments.openclaw_poc.run_poc

# Real 模式
export OPENCLAW_GATEWAY_TYPE="real"
export OPENCLAW_GATEWAY_URL="..."
python -m experiments.openclaw_poc.run_poc
```

---

## 7. 输出结构

### 7.1 Runner 输出

```
validation_output/
├── block_reviewer_same_as_assignee_evidence.json
├── block_reviewer_same_as_assignee_payload.json
├── allow_specialist_via_reviewer_evidence.json
├── allow_specialist_via_reviewer_payload.json
├── timeout_evidence.json
├── timeout_payload.json
```

### 7.2 Evidence 结构

```json
{
  "scenario": "block_reviewer_same_as_assignee",
  "mode": "mock",
  "timestamp": "2026-04-15T...",
  "success": true,
  "payload": { ... },
  "gateway_url": "http://127.0.0.1:18790",
  "gateway": "mock-gateway",
  "status_code": 200,
  "attempts": 1,
  "retried": false
}
```

---

## 8. 里程碑链

| 里程碑 | 主要交付 |
|--------|---------|
| M5 | 真实 gateway 验证证据闭环 |
| M5-R3 | Evidence 闭环最终修正 |
| M5-R4 | Decision mismatch 失败分支证据落盘 |
| M6 | Notification 线路最小可靠投递版 |
| M6-R1 | 契约与 retry 验证收口 |
| M7 | Notification 线路工程化收口（本文档） |

---

## 9. 参考

- `docs/integration/openclaw_notification_contract.md` — Notification 契约详细说明
- `scripts/validate_evidence.py` — 证据验证脚本
- `tests/unit/test_notification_retry.py` — Retry 机制测试