# OpenClaw Notification Contract

> M4 — Notification 集成 PoC 包
> 目的：定义 notification 线路的输入载荷、输出结构、字段契约、容错语义

---

## 1. 通知输入载荷（OpenClawPayload）

### 1.1 完整结构

```python
OpenClawPayload = {
    "event": str,                    # 必需：事件类型
    "instruction": str,              # 必需：指令文本
    "text": str,                     # 必需：简短描述
    "timestamp": str,                # 必需：ISO 8601 格式
    "sessionId": str | None,         # 可选：会话 ID
    "projectPath": str | None,       # 可选：项目路径
    "projectName": str | None,       # 可选：项目名
    "tmuxSession": str | None,       # 可选：TMUX session
    "context": {                     # 必需：上下文
        "sessionId": str | None,
        "projectPath": str | None,
        "projectName": str | None,
        "tmuxSession": str | None,
    },
}
```

### 1.2 字段语义

| 字段 | 必需 | 来源 | 说明 |
|------|------|------|------|
| `event` | ✓ | 固定值 `"governance-decision"` | 区分治理决策通知与其他事件 |
| `instruction` | ✓ | 构建（见 2.1） | 完整指令文本，多行格式 |
| `text` | ✓ | 构建（见 2.2） | 简短描述，单行 |
| `timestamp` | ✓ | `datetime.now(timezone.utc).isoformat()` | 决策生成时间 |
| `sessionId` | ✗ | session_context | SaucyClaw session ID |
| `projectPath` | ✗ | session_context | 项目绝对路径 |
| `projectName` | ✗ | session_context | 项目名（可从 projectPath 推导） |
| `tmuxSession` | ✗ | session_context | TMUX session name |
| `context` | ✓ | session_context 或空字典 | 与顶层字段重复，保留对齐 OpenClaw |

### 1.3 instruction 字段构建规则

多行文本，格式：

```
[governance|{decision}]
决策: {decision}
{规则: {规则列表} | 未触发治理规则}
原因: {reason}
{建议: {建议列表} | (无建议时省略)}
{解释: {explanation_summary} | (无解释时省略)}
```

#### 示例：Block

```
[governance|Block]
决策: Block
规则: rule-reviewer-must-differ
原因: 触发 1 条规则，最高 severity: block
建议: 输出被阻断，请检查治理规则配置; 阻断原因: 审查者不能与执行者相同
解释: 触发阻断（high/separation_of_duties）：防止审查者与执行者同一人，确保独立审查
```

#### 示例：Allow

```
[governance|Allow]
决策: Allow
未触发治理规则
原因: 无规则触发
解释: 未触发治理规则
```

### 1.4 text 字段构建规则

单行文本，格式：

```
治理决策: {decision} — {reason}
```

#### 示例

```
治理决策: Block — 触发 1 条规则，最高 severity: block
```

---

## 2. 决策输出载荷（WakeResult）

### 2.1 完整结构

```python
@dataclass(frozen=True)
class WakeResult:
    gateway: str              # 网关名（如 "mock-gateway"）
    success: bool             # 是否成功
    error: str | None = None  # 错误信息（仅 failure 时有值）
    status_code: int | None = None  # HTTP 状态码（仅 HTTP gateway）
```

### 2.2 success 字段语义

| 值 | 含义 | 条件 |
|-----|------|------|
| `True` | 通知发送成功 | HTTP 200-399 / command 退出码 0 |
| `False` | 通知发送失败 | HTTP 400+ / connection refused / timeout / command 非 0 退出 |

### 2.3 error 字段内容

可能的错误信息：

| 错误类型 | 示例 |
|---------|------|
| 连接失败 | `"Connection refused"` |
| 超时 | `"Request timed out"` |
| HTTP 错误 | `"HTTP 404"` / `"HTTP 500"` |
| 命令失败 | `"Exit code 1: command not found"` |

### 2.4 status_code 字段

- **HTTP gateway** — 填充 HTTP 状态码（200 / 404 / 500 等）
- **Command gateway** — 始终为 `None`

---

## 3. 如何携带 explanation / summary / severity

### 3.1 Explanation 携带方式

通过 `explanation_summary` 参数传入 `send_decision()`：

```python
from core.governance.explainer_bundle import bundle_explanations

bundle = bundle_explanations(
    decision=result.decision,
    matched_rule_ids=result.matched_rules,
    schema_rules_lookup={r.id: r for r in schema.rules},
    suggestions=result.suggestions,
)

adapter.send_decision(
    result,
    session_context=session_context,
    explanation_summary=bundle.readable_summary,  # ← 传入解释摘要
)
```

`bundle.readable_summary` 格式：

```
触发阻断（high/separation_of_duties）：防止审查者与执行者同一人，确保独立审查
```

或

```
未触发治理规则
```

### 3.2 Summary 携带方式

`instruction` 字段本身就是摘要，包含：

- 决策类型（Block / Allow）
- 触发规则列表（或"未触发"）
- 原因
- 建议（如果有）
- 解释摘要（如果有）

### 3.3 Severity 携带方式

Severity 不单独携带，而是通过 `explanation_summary` 体现：

```
触发阻断（high/separation_of_duties）：...
               ^^^^
              severity
```

或通过 `instruction` 体现：

```
规则: rule-reviewer-must-differ
```

---

## 4. Timeout / Failure / Retry 最小语义

### 4.1 Timeout 语义

- **HTTP gateway** — 默认 10 秒（`timeout_ms=10_000`）
- **Command gateway** — 默认 5 秒（`timeout_ms=5_000`）
- 超时后返回 `WakeResult(success=False, error="Request timed out")`
- 不自动 retry（PoC 阶段简化）

### 4.2 Failure 语义

| 场景 | `WakeResult` | 说明 |
|------|--------------|------|
| HTTP 200-399 | `success=True` | 成功 |
| HTTP 400+ | `success=False, error="HTTP {code}"` | 客户端/服务端错误 |
| Connection refused | `success=False, error="Connection refused"` | 网关不可达 |
| DNS 解析失败 | `success=False, error="{reason}"` | 主机不存在 |
| Timeout | `success=False, error="Request timed out"` | 超时 |

### 4.3 Retry 语义（当前 PoC 未实现）

当前 **不实现 retry**，理由：

- PoC 阶段验证链路畅通即可
- Retry 需要持久化未发送通知
- Retry 需要幂等性保证
- 这些是生产级需求，待后续演进

---

## 5. 必需字段 vs 未来扩展字段

### 5.1 当前 PoC 必需字段

| 字段 | 说明 |
|------|------|
| `event` | 固定 "governance-decision" |
| `instruction` | 完整指令文本 |
| `text` | 简短描述 |
| `timestamp` | ISO 8601 |
| `context` | 至少空字典 |

### 5.2 未来扩展字段（预留）

| 字段 | 说明 | 何时引入 |
|------|------|---------|
| `messageId` | OpenClaw reply listener 需要 | 接入 reply listener 时 |
| `platform` | Discord / Telegram / etc. | 接入多平台时 |
| `channelId` | channel ID | 接入 reply listener 时 |
| `threadId` | thread ID | 接入 reply listener 时 |
| `replyTo` | 回复目标 | 双向通信时 |
| `attachments` | 附件 | 需要发送文件时 |
| `priority` | 优先级 | 需要分级通知时 |

---

## 6. 与 OpenClaw 官方定义的对齐

### 6.1 TypeScript 定义（oh-my-opencode v3.13.1）

```typescript
// src/openclaw/types.ts

export interface OpenClawPayload {
    event: string;
    instruction: string;
    text: string;
    timestamp: string;
    sessionId?: string;
    projectPath?: string;
    projectName?: string;
    tmuxSession?: string;
    tmuxTail?: string;
    channel?: string;
    to?: string;
    threadId?: string;
    context: OpenClawContext;
}

export interface OpenClawContext {
    sessionId?: string;
    projectPath?: string;
    projectName?: string;
    tmuxSession?: string;
    prompt?: string;
    contextSummary?: string;
    reasoning?: string;
    question?: string;
    tmuxTail?: string;
    replyChannel?: string;
    replyTarget?: string;
    replyThread?: string;
    [key: string]: string | undefined;
}
```

### 6.2 对齐情况

| 字段 | PoC 实现 | OpenClaw 官方 | 对齐 |
|------|---------|--------------|------|
| `event` | ✓ | ✓ | ✓ |
| `instruction` | ✓ | ✓ | ✓ |
| `text` | ✓ | ✓ | ✓ |
| `timestamp` | ✓ | ✓ | ✓ |
| `sessionId` | ✓ | ✓ | ✓ |
| `projectPath` | ✓ | ✓ | ✓ |
| `projectName` | ✓ | ✓ | ✓ |
| `tmuxSession` | ✓ | ✓ | ✓ |
| `context` | ✓ | ✓ | ✓ |
| `channel` | ✗ | ✓ | ✗ (未来扩展) |
| `to` | ✗ | ✓ | ✗ (未来扩展) |
| `threadId` | ✗ | ✓ | ✗ (未来扩展) |
| `tmuxTail` | ✗ | ✓ | ✗ (未来扩展) |

当前实现覆盖了 **核心必需字段**，未来扩展字段待需要时引入。

---

## 7. 契约验证方式

### 7.1 单元测试验证

```python
# tests/unit/test_notification_adapter.py

def test_block_payload_structure() -> None:
    payload = _build_openclaw_payload(...)
    assert payload["event"] == "governance-decision"
    assert payload["timestamp"] is not None
    assert "context" in payload
```

### 7.2 PoC 验证

```bash
python -m experiments.openclaw_poc.run_poc
```

验证输出包含：

```
[mock-gateway] Received event: governance-decision
[mock-gateway] Instruction:
  [governance|Block]
  决策: Block
  规则: rule-reviewer-must-differ
  ...
```

### 7.3 人工验证（未来真实 gateway）

1. 配置真实 OpenClaw gateway URL
2. 运行 PoC
3. 检查 OpenClaw 日志收到 payload
4. 检查 payload 字段完整
