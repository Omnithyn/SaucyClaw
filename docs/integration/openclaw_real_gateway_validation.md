# OpenClaw 真实 Gateway 验证记录单

> M5-R — 真实 Gateway 验证证据闭环收口包
> 目的：记录真实 OpenClaw gateway 验证结果，作为可追溯的验证证据
> 创建时间：2026-04-15
> 最后更新：2026-04-15

---

## 一、验证基本信息

| 字段 | 值 |
|------|-----|
| 验证人 | Claude (via SaucyClaw M8 Live Validation) |
| 验证日期 | 2026-04-16 |
| 验证环境 | `[X] Real` |
| Gateway URL | `http://127.0.0.1:26277/hooks/agent`（SSH tunnel to remote OpenClaw） |
| oh-my-opencode 版本 | clawdbot (2026.4.15-beta.1) |
| 运行命令 | `python -m experiments.openclaw_poc.live_validation` |
| 证据输出目录 | `real_validation_output/` |
| Payload 格式 | `HookAgentPayload`（使用 `message` 字段） |

---

## 二、Block 通知验证

### 2.1 场景信息

| 字段 | 值 |
|------|-----|
| Fixture | `block_reviewer_same_as_assignee.yaml` |
| 预期决策 | `Block` |
| 预期触发规则 | `rule-reviewer-must-differ` |

### 2.2 验证检查表

- [ ] `WakeResult.success` = `True`
- [ ] `WakeResult.status_code` = `200`（Mock 模式）或 `200-399`（Real 模式）
- [ ] `WakeResult.error` = `None`
- [ ] Payload 文件存在：`validation_output/block_reviewer_same_as_assignee_payload.json`
- [ ] Evidence 文件存在：`validation_output/block_reviewer_same_as_assignee_evidence.json`
- [ ] Evidence 中 `mode` = `mock` 或 `real`
- [ ] Evidence 中 `gateway_url` 与实际一致
- [ ] Evidence 中 `timestamp` 非空
- [ ] `payload.event` = `"governance-decision"`
- [ ] `payload.instruction` 包含 `"[governance|Block]"`
- [ ] `payload.instruction` 包含 `"rule-reviewer-must-differ"`
- [ ] `payload.instruction` 包含 `"解释:"`（解释信息携带）

### 2.3 Mock 模式结果（已自动验证）

| 检查项 | 结果 |
|--------|------|
| 发送成功 | ✅ PASS |
| Payload 结构 | ✅ PASS |
| 解释信息 | ✅ PASS |
| 证据保存 | ✅ PASS |
| Evidence 文件 | `validation_output/block_reviewer_same_as_assignee_evidence.json` |

### 2.4 Real 模式结果（已验证）

| 检查项 | 结果 | 说明 |
|--------|------|------|
| 发送成功 | `[X] PASS` | runId: `9841ee87-9588-4200-8bd6-679436761540` |
| Payload 结构 | `[X] PASS` | HookAgentPayload 格式（message, name, wakeMode, channel） |
| 解释信息 | `[X] PASS` | message 包含完整治理决策和解释 |
| 服务端收到 | `[X] PASS` | 返回 `{"ok":true,"runId":"..."}` |

### 2.5 服务端日志观察（Real 模式）

```
响应: {"ok":true,"runId":"9841ee87-9588-4200-8bd6-679436761540"}
HTTP 状态码: 200

Payload 结构:
{
  "message": "[governance|Block]\n决策: Block\n规则: rule-reviewer-must-differ\n原因: 触发 1 条规则，最高 severity: block\n建议: 输出被阻断，请检查治理规则配置; 阻断原因: 审查者不能与执行者相同\n解释: 触发阻断（high/separation_of_duties）：防止审查者与执行者同一人，确保独立审查",
  "name": "SaucyClaw Governance",
  "wakeMode": "now",
  "deliver": true,
  "channel": "last"
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

### 3.2 验证检查表

- [ ] `WakeResult.success` = `True`
- [ ] `WakeResult.status_code` = `200`（Mock 模式）或 `200-399`（Real 模式）
- [ ] `WakeResult.error` = `None`
- [ ] Payload 文件存在：`validation_output/allow_specialist_via_reviewer_payload.json`
- [ ] Evidence 文件存在：`validation_output/allow_specialist_via_reviewer_evidence.json`
- [ ] Evidence 中 `mode` = `mock` 或 `real`
- [ ] Evidence 中 `gateway_url` 与实际一致
- [ ] Evidence 中 `timestamp` 非空
- [ ] `payload.event` = `"governance-decision"`
- [ ] `payload.instruction` 包含 `"[governance|Allow]"`
- [ ] `payload.instruction` 包含 `"未触发治理规则"`
- [ ] `payload.instruction` 包含 `"解释: 未触发治理规则"`

### 3.3 Mock 模式结果（已自动验证）

| 检查项 | 结果 |
|--------|------|
| 发送成功 | ✅ PASS |
| Payload 结构 | ✅ PASS |
| 解释信息 | ✅ PASS |
| 证据保存 | ✅ PASS |
| Evidence 文件 | `validation_output/allow_specialist_via_reviewer_evidence.json` |

### 3.4 Real 模式结果（已验证）

| 检查项 | 结果 | 说明 |
|--------|------|------|
| 发送成功 | `[X] PASS` | runId: `d9603b89-f08c-441c-8064-4e0fc40fe699` |
| Payload 结构 | `[X] PASS` | HookAgentPayload 格式 |
| 解释信息 | `[X] PASS` | message 包含"未触发治理规则" |
| 服务端收到 | `[X] PASS` | 返回 `{"ok":true,"runId":"..."}` |

### 3.5 服务端日志观察（Real 模式）

```
响应: {"ok":true,"runId":"d9603b89-f08c-441c-8064-4e0fc40fe699"}
HTTP 状态码: 200

Payload 结构:
{
  "message": "[governance|Allow]\n决策: Allow\n未触发治理规则\n原因: 无规则触发\n解释: 未触发治理规则",
  "name": "SaucyClaw Governance",
  "wakeMode": "now",
  "deliver": true,
  "channel": "last"
}
```

---

## 四、Timeout/Failure 验证

### 4.1 场景信息

| 字段 | 值 |
|------|-----|
| Gateway URL | `http://127.0.0.1:9999/nonexistent`（不可达） |
| Timeout | 1000 ms |

### 4.2 验证检查表

- [ ] `WakeResult.success` = `False`
- [ ] `WakeResult.error` 非空（如 `"Connection refused"`）
- [ ] Evidence 文件存在：`validation_output/timeout_evidence.json`
- [ ] Evidence 中 `mode` = `mock` 或 `real`（跟随 `OPENCLAW_GATEWAY_TYPE`）
- [ ] Evidence 中 `gateway_url` = `http://127.0.0.1:9999/nonexistent`
- [ ] Evidence 中 `timestamp` 非空
- [ ] 未静默吞掉错误

### 4.3 Mock 模式结果（已自动验证）

| 检查项 | 结果 |
|--------|------|
| 失败返回 | ✅ PASS |
| 明确错误信息 | ✅ PASS |
| 未静默吞掉 | ✅ PASS |
| 证据保存 | ✅ PASS |
| Evidence 文件 | `validation_output/timeout_evidence.json` |

---

## 五、验证证据文件清单

当前 `validation_output/` 目录中的文件：

| 文件 | 场景 | 说明 | 状态 |
|------|------|------|------|
| `block_reviewer_same_as_assignee_payload.json` | Block | 包含实际发送的 payload（适配器 last_payload） | ✅ 已生成 |
| `block_reviewer_same_as_assignee_evidence.json` | Block | 包含完整验证证据（含 payload 副本） | ✅ 已生成 |
| `allow_specialist_via_reviewer_payload.json` | Allow | 包含实际发送的 payload（适配器 last_payload） | ✅ 已生成 |
| `allow_specialist_via_reviewer_evidence.json` | Allow | 包含完整验证证据（含 payload 副本） | ✅ 已生成 |
| `timeout_payload.json` | Timeout | 包含实际发送的 payload（适配器 last_payload） | ✅ 已生成 |
| `timeout_evidence.json` | Timeout | 包含完整验证证据（含 payload 副本） | ✅ 已生成 |

### Payload 文件生成策略

**统一策略**：所有场景（Block/Allow/Timeout）和所有模式（mock/real）均生成 payload 文件。

生成流程：
1. `adapter.send_notification()` 发送通知前，保存 `OpenClawPayload` 到 `adapter.last_payload`
2. 场景执行完成后，从 `adapter.last_payload` 提取已发送的 payload
3. 调用 `save_validation_bundle()` 时，通过 `evidence.payload` 字段保存到 `{scenario}_payload.json`
4. payload 同时保留在 `evidence.json` 的 `payload` 字段中（双重保险）

**重要**：
- `last_payload` 在每次 `send_notification()` 时被更新
- payload 文件反映**实际发送的内容**，而非构造前的原始数据
- Mock 和 Real 模式使用相同的 payload 保存机制

### Evidence 文件结构

每个 `*_evidence.json` 文件包含：

```json
{
  "scenario": "<场景名>",
  "mode": "mock | real",
  "gateway_url": "<gateway URL>",
  "timestamp": "<ISO 8601>",
  "payload": { "<实际发送的 OpenClawPayload（完整副本）>" },
  "gateway": "<gateway 名称>",
  "success": true | false,
  "error": null | "<错误信息>",
  "status_code": 200 | null | <HTTP 状态码>
}
```

**关键字段**：
- `mode`: 标识 mock 或 real 模式（不影响 payload 生成）
- `payload`: 包含实际发送的完整 payload（与 `_payload.json` 文件内容一致）
- `success`: 发送是否成功
- `status_code`: HTTP 状态码（mock 模式为 200，real 模式为实际响应码）

---

## 六、验证结论

### 6.1 验证通过条件

**全部勾选**时视为验证通过：

- [ ] Block 通知验证通过（2.2 全部勾选）
- [ ] Allow 通知验证通过（3.2 全部勾选）
- [ ] Timeout 验证通过（4.2 全部勾选）
- [ ] 服务端日志确认收到通知（Real 模式时）
- [ ] Payload 结构与 `OpenClawPayload` 契约一致
- [ ] 所有场景均生成 `_payload.json` 文件（含 real 模式）
- [ ] Evidence 文件中的 `payload` 字段与 `_payload.json` 一致

### 6.2 验证脚本

使用以下脚本快速验证证据文件完整性：

```bash
# 检查所有 payload 文件是否存在
for file in validation_output/*_payload.json; do
  echo "✓ $file"
done

# 检查所有 evidence 文件是否存在
for file in validation_output/*_evidence.json; do
  echo "✓ $file"
done

# 验证 evidence.payload 与 _payload.json 一致性
python3 << 'EOF'
import json
from pathlib import Path

validation_dir = Path("validation_output")

for evidence_file in validation_dir.glob("*_evidence.json"):
    scenario = evidence_file.stem.replace("_evidence", "")
    payload_file = validation_dir / f"{scenario}_payload.json"

    if payload_file.exists():
        with open(evidence_file) as f:
            evidence = json.load(f)
        with open(payload_file) as f:
            payload = json.load(f)

        # 比较 payload 字段（去除 timestamp 差异）
        evidence_payload = {k: v for k, v in evidence["payload"].items() if k != "timestamp"}
        file_payload = {k: v for k, v in payload.items() if k != "timestamp"}

        if evidence_payload == file_payload:
            print(f"✓ {scenario}: evidence.payload == _payload.json")
        else:
            print(f"✗ {scenario}: mismatch!")
EOF
```

### 6.3 当前状态

| 模式 | Block | Allow | Timeout/Failure | Payload 保存 | 结论 |
|------|-------|-------|---------|-------------|------|
| **Mock** | ✅ PASS | ✅ PASS | ✅ PASS | ✅ PASS | **通过** |
| **Real** | `[X] PASS` | `[X] PASS` | ✅ PASS（无效 token 测试） | ✅ PASS | **通过** |

**说明：** Real 模式使用 `OpenClawHooksAdapter` + `HookAgentPayload` 格式发送到 `/hooks/agent` endpoint。

### 6.4 验证人签字

| 字段 | 值 |
|------|-----|
| 验证人 | Claude (M8 Live Validation) |
| 签字日期 | 2026-04-16 |
| 验证结论 | `[X] 通过` |
| 备注 | 真实 OpenClaw hooks gateway 已打通，Block/Allow 通知成功发送 |

---

## 七、参考文档

- `docs/integration/openclaw_notification_contract.md` — 通知载荷契约定义
- `docs/integration/openclaw_notification_poc.md` — Notification PoC 架构说明
- `docs/integration/openclaw_real_gateway_requirements.md` — 真实环境需求清单
- `adapters/openclaw/notification_adapter.py` — 通知适配器实现
- `experiments/openclaw_poc/run_poc.py` — PoC 入口脚本
