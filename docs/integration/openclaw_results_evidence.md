# OpenClaw 结果与证据关系

> M9 — OpenClaw 接入面统一收口包
> 目的：说明各接入模式的结果类型、证据类型、保存机制之间的关系
> 成熟度：正式工程面

---

## 一、结果类型概览

每种接入模式有对应的结果类型：

| 模式 | 结果类型 | 用途 | 成熟度 |
|------|---------|------|--------|
| **shadow** | `ShadowRunResult` | 包含治理决策和增强输出 | 正式工程面 |
| **notification** | `WakeResult` | HTTP/command 通知发送结果 | 正式工程面 |
| **hooks-live** | `HooksWakeResult` | Hooks API 调用结果（含 runId） | MVP |

---

## 二、Shadow Mode 结果

### 2.1 ShadowRunResult 结构

```python
@dataclass(frozen=True)
class ShadowRunResult:
    gate_result: GateResult        # 治理引擎决策结果
    enhanced_output: AdapterExplainOutput | None  # 增强的解释输出（可选）
```

### 2.2 GateResult 结构

```python
@dataclass(frozen=True)
class GateResult:
    decision: str                  # "Block" | "Allow" | "Timeout"
    reason: str                    # 决策原因
    matched_rules: list[str]       # 触发的规则列表
    evidence_ids: list[str]        # 关联的证据 ID
    suggestions: list[str]         # 建议列表
```

### 2.3 AdapterExplainOutput 结构

```python
@dataclass(frozen=True)
class AdapterExplainOutput:
    explanation_bundle: str | None  # 解释输出文本（可选）
    trace_id: str                   # 追踪 ID
    timestamp: str                  # 时间戳
```

### 2.4 证据保存机制

Shadow Mode 使用 `EvidenceStore` 保存证据：

- **证据类型**：`ValidationEvidence`
- **保存位置**：`stores/file/evidence/`
- **文件命名**：`{scenario}_evidence.json`

---

## 三、Notification Mode 结果

### 3.1 WakeResult 结构

```python
@dataclass(frozen=True)
class WakeResult:
    gateway: str           # gateway 名称
    success: bool          # 是否成功
    error: str | None      # 错误信息
    status_code: int | None  # HTTP 状态码
```

### 3.2 Payload 格式

使用 `OpenClawPayload` 格式：

```json
{
  "event": "governance-decision",
  "instruction": "[governance|Block]\n决策: Block...",
  "text": "治理决策: Block — 原因",
  "timestamp": "2026-04-16T00:00:00Z",
  "context": {
    "sessionId": "...",
    "projectPath": "...",
    "projectName": "...",
    "tmuxSession": "..."
  }
}
```

### 3.3 证据保存机制

Notification Mode 用于内部通知，一般不保存外部证据。

---

## 四、Hooks-Live Mode 结果

### 4.1 HooksWakeResult 结构

```python
@dataclass(frozen=True)
class HooksWakeResult:
    gateway: str           # gateway 名称
    success: bool          # 是否成功
    run_id: str | None     # OpenClaw 返回的 runId（关键）
    error: str | None      # 错误信息
    status_code: int | None  # HTTP 状态码
```

### 4.2 Payload 格式

使用 `HookAgentPayload` 格式：

```json
{
  "message": "[governance|Block]\n决策: Block\n规则: rule-1\n原因: ...",
  "name": "SaucyClaw Governance",
  "wakeMode": "now",
  "deliver": true,
  "channel": "last"
}
```

### 4.3 Evidence 结构

Hooks-Live Mode 使用 `LiveValidationEvidence`：

```python
@dataclass(frozen=True)
class LiveValidationEvidence:
    scenario: str                  # 场景名称
    gateway_url: str               # gateway URL
    timestamp: str                 # 时间戳
    payload: dict | None           # 发送的 payload
    gateway: str                   # gateway 名称
    success: bool                  # 是否成功
    run_id: str | None             # runId（关键）
    error: str | None              # 错误信息
    status_code: int | None        # HTTP 状态码
    mode: str = "live"             # 固定为 "live"
```

### 4.4 证据保存机制

- **证据类型**：`LiveValidationEvidence`
- **保存位置**：`real_validation_output/` 或 `validation_output/`
- **文件命名**：`{scenario}_payload.json` 和 `{scenario}_evidence.json`
- **保存函数**：`save_evidence(evidence, output_dir)`

---

## 五、结果与证据的对应关系

### 5.1 对应表

| 模式 | 结果类型 | Evidence 类型 | Payload 类型 |
|------|---------|--------------|-------------|
| shadow | ShadowRunResult | ValidationEvidence | 无外部 payload |
| notification | WakeResult | 无外部证据 | OpenClawPayload |
| hooks-live | HooksWakeResult | LiveValidationEvidence | HookAgentPayload |

### 5.2 关键差异

| 特性 | ValidationEvidence | LiveValidationEvidence |
|------|--------------------|------------------------|
| mode 字段 | "mock" 或 "validation" | "live" |
| run_id 字段 | 无 | 有（OpenClaw 返回） |
| payload 字段 | 无 | 有（发送的 payload） |
| gateway_url 字段 | 无 | 有（gateway URL） |

---

## 六、证据保存实现

### 6.1 save_evidence 函数

```python
def save_evidence(evidence: LiveValidationEvidence, output_dir: Path) -> None:
    """保存 payload 和 evidence 文件。"""
    # 保存 payload（如果有）
    if evidence.payload:
        payload_file = output_dir / f"{evidence.scenario}_payload.json"
        with open(payload_file, "w") as f:
            json.dump(evidence.payload, f, indent=2)

    # 保存 evidence
    evidence_file = output_dir / f"{evidence.scenario}_evidence.json"
    with open(evidence_file, "w") as f:
        json.dump(asdict(evidence), f, indent=2)
```

### 6.2 build_evidence 函数

```python
def build_evidence(
    scenario: str,
    gateway_url: str,
    payload: dict,
    wake_result: HooksWakeResult,
) -> LiveValidationEvidence:
    """从 wake_result 构建 evidence。"""
    return LiveValidationEvidence(
        scenario=scenario,
        gateway_url=gateway_url,
        timestamp=datetime.now(timezone.utc).isoformat(),
        payload=payload,
        gateway=wake_result.gateway,
        success=wake_result.success,
        run_id=wake_result.run_id,
        error=wake_result.error,
        status_code=wake_result.status_code,
    )
```

---

## 七、参考

- `docs/integration/openclaw_integration_modes.md` — 三种接入模式说明
- `docs/integration/openclaw_hooks_contract.md` — Hooks Payload 契约
- `.local-docs/integration/openclaw_notification_contract.md` — Notification Payload 契约
- `stores/protocols.py` — GateResult 定义
- `experiments/openclaw_poc/live_validation.py` — Live validation 实现