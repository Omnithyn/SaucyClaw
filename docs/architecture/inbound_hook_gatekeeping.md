# Inbound Hook Gatekeeping

> M15 — Inbound Hook Gatekeeping Base Package
> M16 — OpenHarness Inbound Base Adoption
> 目的：定义 inbound_hook_gatekeeping 的宿主无关公共基座，并实现第一个真实消费者

---

## 一、什么是 Inbound Hook Gatekeeping

Inbound hook gatekeeping 是 `HookInteractionPattern.INBOUND_HOOK_GATEKEEPING` 模式的具体实现：

- **方向**：宿主 → SaucyClaw
- **主动方**：宿主（runtime）
- **响应方**：SaucyClaw（治理端点）
- **用途**：实时治理阻断（阻止危险操作）

**典型流程：**
```
1. Runtime executor 在事件点触发（如 pre_tool_use）
2. POST 到 SaucyClaw 端点（如 /governance）
3. SaucyClaw 执行治理检查 → GateResult
4. SaucyClaw 返回 HTTP 200 (blocked=false) 或 403 (blocked=true)
5. Runtime 根据 blocked 决定是否继续执行
```

---

## 二、与 Outbound Hook Push 的区别

| 维度 | outbound_hook_push | inbound_hook_gatekeeping |
|------|-------------------|-------------------------|
| 方向 | SaucyClaw → 宿主 | 宿主 → SaucyClaw |
| 主动方 | SaucyClaw | 宿主 |
| 响应方 | 宿主 | SaucyClaw |
| API 端点 | 宿主 `/hooks/agent` | SaucyClaw `/governance` |
| 响应结构 | `{runId: ...}` | `{blocked: true/false}` |
| 阻断能力 | 无（仅通知） | 有（block_on_failure=True） |
| 代表 runtime | OpenClaw | OpenHarness |

**抽象边界：**
- `outbound_hook_push` 由 OpenClaw 具体实现，SaucyClaw 不需要公共基座
- `inbound_hook_gatekeeping` 由多个 runtime 共享（OpenHarness、Hermes），需要公共基座

---

## 三、公共基座定义

`adapters/inbound_hook_protocols.py` 定义宿主无关抽象：

### 3.1 核心结构

| 结构 | 用途 |
|------|------|
| `InboundHookEvent` | inbound hook 事件最小结构（event_type + payload） |
| `GatekeepingResponse` | gatekeeping 响应最小结构（blocked + decision + status_code） |
| `InboundHookResult` | probe 发送请求后收到的结果（success + blocked） |
| `InboundHookEvidence` | live validation evidence 最小结构 |

### 3.2 协议

| 协议 | 用途 |
|------|------|
| `InboundHookReceiver` | 接收宿主 hook 请求，执行治理检查，返回响应 |
| `InboundHookProbe` | 模拟宿主发送 hook 请求，用于本地验证 |

### 3.3 Helper Functions

| 函数 | 用途 |
|------|------|
| `build_gatekeeping_response_from_gate_result` | 从 GateResult 构建 GatekeepingResponse |
| `parse_inbound_hook_event_minimal` | 解析 inbound hook 事件的最小公共部分 |

---

## 四、可复用基座 vs 具体实现

### 4.1 可复用公共部分（由基座提供）

| 公共部分 | 说明 |
|---------|------|
| 事件结构 | `InboundHookEvent` — event_type + payload |
| 响应结构 | `GatekeepingResponse` — blocked + decision + status_code |
| Evidence 结构 | `InboundHookEvidence` — live validation 记录 |
| Receiver 协议 | `InboundHookReceiver` — handle_hook_request 签名 |
| Probe 协议 | `InboundHookProbe` — send_hook_event 签名 |
| Helper 函数 | `build_gatekeeping_response_from_gate_result` — 构建响应 |
| Helper 函数 | `parse_inbound_hook_event_minimal` — 解析事件 |

### 4.2 由具体 runtime 实现

| 具体部分 | OpenHarness | Hermes（待实现） |
|---------|-------------|----------------|
| Payload 格式 | `{event, payload}`（executor.py:148） | 预期类似（待验证） |
| Receiver 具体类 | `OpenHarnessHookReceiver` | `HermesHookReceiver` |
| Probe 具体类 | `OpenHarnessHookProbe` | `HermesHookProbe` |
| 成熟度/验证状态 | MVP（已真实验证） | skeleton |

### 4.3 OpenHarness 复用状态（M16 已落地）

| 复用类型 | OpenHarness 实现 | 状态 |
|---------|-----------------|------|
| Result 结构 | `OpenHarnessHookResult = InboundHookResult` | ✅ 直接复用 |
| 响应构建 | `build_openharness_hook_response` 桥接公共 helper | ✅ 桥接复用 |
| 事件解析 | `parse_openharness_hook_payload` 桥接公共 helper | ✅ 桥接复用 |
| Receiver | `OpenHarnessHookReceiver` 通过 duck typing 符合 Protocol | ✅ 自动符合 |
| Probe | `OpenHarnessHookProbe` 通过 duck typing 符合 Protocol | ✅ 自动符合 |
| 测试验证 | 23 adoption 测试 + 5 live validation | ✅ 全部通过 |

**关键代码改动（M16）：**
```python
# adapters/openharness/hooks_adapter.py
from adapters.inbound_hook_protocols import (
    InboundHookResult,
    build_gatekeeping_response_from_gate_result,
    parse_inbound_hook_event_minimal,
)

# 直接复用
OpenHarnessHookResult = InboundHookResult

# 桥接复用
def build_openharness_hook_response(gate_result):
    base_response = build_gatekeeping_response_from_gate_result(gate_result)
    # 转换为 OpenHarness dict 格式
    ...

def parse_openharness_hook_payload(raw):
    event = parse_inbound_hook_event_minimal(raw)
    return event.event_type, event.payload
```

---

## 五、对 Hermes 的意义

Hermes Agent（M11 调研）的 hooks 系统采用"Hook 脚本发现式"：
- 在 `~/.hermes/hooks/` 放置 shell 脚本
- Hermes 在 `agent:step` 时执行脚本，脚本可 POST 到任意端点

**预期接入方式：**
1. Hermes hook 脚本 POST 到 SaucyClaw `/governance`
2. SaucyClaw 使用 `InboundHookReceiver` 接收请求
3. 返回 `{blocked: true/false}` 响应
4. Hermes 根据脚本返回值决定是否阻断

**复用基座的好处：**
- Hermes 只需实现具体 payload 格式解析
- Receiver/Probe/Evidence 结构可直接复用
- 减少重复代码，降低维护成本

---

## 六、参考

- `adapters/inbound_hook_protocols.py` — 公共基座定义
- `adapters/openharness/hooks_adapter.py` — OpenHarness 具体实现（已验证）
- `adapters/hermes/profile.py` — Hermes skeleton profile（预期复用）
- `docs/architecture/hook_integration_patterns.md` — hook 交互形态总览
- `.local-docs/integration/runtime_capability_matrix.md` — runtime inbound base 状态