# Hook Integration Patterns

> M14 — Hook Integration Pattern Refinement
> 目的：区分 hooks_live 模式下 SaucyClaw 与宿主的两种不同交互形态

---

## 一、为什么 hooks_live 不再够用

`HostMode.HOOKS_LIVE` 最初设计时假设所有 runtime 的 hooks 接入形态相同：
SaucyClaw 通过宿主提供的 hooks API 发送治理决策通知。

但随着 OpenHarness 接入（M12/M13），我们发现两种完全不同的交互形态：

| 交互形态 | 方向 | 主动方 | 响应方 | 用途 |
|---------|------|-------|-------|-----|
| outbound_hook_push | SaucyClaw → 宿主 | SaucyClaw | 宿主 | 发送治理决策通知 |
| inbound_hook_gatekeeping | 宿主 → SaucyClaw | 宿主 | SaucyClaw | 实时阻断/放行 |

单一的 `hooks_live` 无法准确表达这种差异。

---

## 二、两种 Hook 交互形态详解

### 2.1 outbound_hook_push

**特征：**
- SaucyClaw 主动调用宿主 hooks API
- SaucyClaw 作为 client，宿主作为 server
- 治理决策由 SaucyClaw 发送，宿主接收并记录

**典型流程：**
```
1. GovernanceEngine.process_event() → GateResult
2. OpenClawHooksAdapter.send_decision(result)
3. POST /hooks/agent (宿主端点)
4. 宿主返回 run_id（确认收到）
```

**适用场景：**
- 治理决策通知（审计日志、事后追溯）
- 不阻断宿主执行，仅记录治理决策

**代表 runtime：** OpenClaw

---

### 2.2 inbound_hook_gatekeeping

**特征：**
- 宿主在事件点 POST 到 SaucyClaw 端点
- SaucyClaw 作为 server，宿主作为 client
- SaucyClaw 返回阻断/放行响应，宿主根据响应决定是否继续执行

**典型流程：**
```
1. OpenHarness executor 在 pre_tool_use 触发
2. POST http://saucyclaw-host/governance
3. SaucyClaw 执行治理检查 → GateResult
4. SaucyClaw 返回 HTTP 200 (blocked=false) 或 403 (blocked=true)
5. OpenHarness 根据 blocked 决定是否继续执行
```

**适用场景：**
- 实时治理阻断（阻止危险操作）
- 宿主执行前检查

**代表 runtime：** OpenHarness

---

## 三、OpenClaw vs OpenHarness 对比

| 维度 | OpenClaw | OpenHarness |
|------|----------|-------------|
| hooks_live 交互形态 | outbound_hook_push | inbound_hook_gatekeeping |
| SaucyClaw 角色 | Client（调用方） | Server（接收方） |
| 宿主角色 | Server（接收方） | Client（调用方） |
| API 端点 | 宿主 `/hooks/agent` | SaucyClaw `/governance` |
| 响应结构 | `{runId: ...}` | `{blocked: true/false}` |
| 阻断能力 | 无（仅通知） | 有（block_on_failure=True） |
| Payload 格式 | HookAgentPayload | `{event, payload}` |

---

## 四、抽象层设计

### 4.1 HookInteractionPattern 枚举

```python
class HookInteractionPattern(Enum):
    OUTBOUND_HOOK_PUSH = "outbound_hook_push"
    INBOUND_HOOK_GATEKEEPING = "inbound_hook_gatekeeping"
```

### 4.2 HostCapabilities 扩展

```python
@dataclass(frozen=True)
class HostCapabilities:
    modes: list[HostMode]
    supports_shadow: bool = True
    supports_notification: bool = False
    supports_hooks_live: bool = False
    hook_pattern: HookInteractionPattern | None = None  # M14 新增
```

**约束：**
- `hook_pattern` 仅当 `supports_hooks_live=True` 时有意义
- 其他模式（shadow / notification）时 `hook_pattern=None`

---

## 五、对 Hermes 的意义

Hermes Agent（M11 调研）的 hooks 系统采用"Hook 脚本发现式"：
- 在 `~/.hermes/hooks/` 放置 shell 脚本
- Hermes 在 `agent:step` 时执行脚本，脚本可 POST 到任意端点

这意味着 Hermes 的 hooks 形态可配置：
- 若脚本 POST 到 SaucyClaw 端点 → inbound_hook_gatekeeping（与 OpenHarness 类似）
- 若脚本作为 SaucyClaw 调用入口 → outbound_hook_push（与 OpenClaw 类似）

M14 的抽象层为 Hermes 预留了灵活性：
- Hermes profile 可根据实际配置标明 hook_pattern
- 同一 runtime 可能同时支持两种 pattern（取决于配置）

---

## 六、参考

- `adapters/host_protocols.py` — HookInteractionPattern 定义
- `adapters/openclaw/profile.py` — OUTBOUND_HOOK_PUSH 示例
- `adapters/openharness/profile.py` — INBOUND_HOOK_GATEKEEPING 示例
- `.local-docs/integration/runtime_capability_matrix.md` — runtime hooks 交互模式对比
- `docs/integration/openclaw_integration_modes.md` — OpenClaw hooks_live 详情
- `.local-docs/integration/openharness_live_validation_record.md` — OpenHarness inbound 验证证据