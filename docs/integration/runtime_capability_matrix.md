# Runtime Capability Matrix

> M10 — Runtime-Neutral Host Abstraction
> 目的：按能力维度比较不同 runtime 的治理接入状态
> 成熟度：概念定义

---

## 一、能力矩阵总览

| 能力维度 | OpenClaw | OpenHarness（预留） | Hermes（预留） |
|---------|----------|-------------------|---------------|
| shadow 支持 | ✅ 正式工程面 | ⏳ 未实现 | ⏳ 未实现 |
| notification 支持 | ✅ 正式工程面 | ⏳ 未实现 | ⏳ 未实现 |
| hooks/live 支持 | ⚠️ MVP | ⏳ 未实现 | ⏳ 未实现 |
| 当前成熟度 | 三种模式已定义 | 待调研 | 待调研 |
| 真实验证 | ✅ 已验证 | ❌ 无 | ❌ 无 |

---

## 二、OpenClaw 详细能力

### 2.1 Shadow Mode

| 维度 | 状态 |
|------|------|
| 成熟度 | ✅ 正式工程面 |
| 入口模块 | `adapters/openclaw/shadow_runtime.py` |
| 结果类型 | `ShadowRunResult` |
| 测试覆盖 | ✅ 有单元测试 |
| 真实验证 | ✅ 本地 mock 验证 |

### 2.2 Notification Mode

| 维度 | 状态 |
|------|------|
| 成熟度 | ✅ 正式工程面 |
| 入口模块 | `adapters/openclaw/notification_adapter.py` |
| 结果类型 | `WakeResult` |
| Payload 格式 | `OpenClawPayload` |
| 测试覆盖 | ✅ 有单元测试 |
| 真实验证 | ✅ HTTP gateway 验证 |

### 2.3 Hooks-Live Mode

| 维度 | 状态 |
|------|------|
| 成熟度 | ⚠️ MVP（最小可用） |
| 入口模块 | `adapters/openclaw/hooks_adapter.py` |
| 结果类型 | `HooksWakeResult` |
| Payload 格式 | `HookAgentPayload` |
| 测试覆盖 | ✅ 有单元测试 |
| 真实验证 | ✅ 真实 gateway 已打通 |
| 未完成 | 队列、持久化、高可用 |

---

## 三、OpenHarness（预留）

| 维度 | 状态 |
|------|------|
| 成熟度 | ⏳ 待调研 |
| 调研内容 | OpenHarness 的 hook 机制、notification API、事件输出方式 |
| 预期 | 可能支持 shadow 和 notification 模式 |

---

## 四、Hermes（预留）

| 维度 | 状态 |
|------|------|
| 成熟度 | ⏳ 待调研 |
| 调研内容 | Hermes 的消息发送机制、通知通道 |
| 预期 | 可能支持 notification 模式 |

---

## 五、模式与能力维度说明

### shadow
- 不依赖真实 runtime
- 通过 mock adapter 模拟宿主行为
- 所有 runtime 都应支持（因为不依赖具体 runtime）

### notification
- 需要 runtime 提供 HTTP endpoint 或 command 通道
- 用于发送治理决策通知
- 适用于内部通知场景

### hooks/live
- 需要 runtime 提供专门的 hooks API
- 用于真实的消息发送
- 适用于生产级治理通知

---

## 六、参考

- `.local-docs/architecture/runtime_host_abstraction.md` — 宿主抽象架构说明
- `adapters/host_protocols.py` — 宿主抽象协议
- `adapters/openclaw/profile.py` — OpenClaw 宿主 profile
- `docs/integration/openclaw_integration_modes.md` — OpenClaw 接入模式详情
