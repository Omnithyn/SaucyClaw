# SaucyClaw 总体设计

> 以本体、证据、治理规则为核心的多智能体治理 Harness

---

## 一、项目定位

SaucyClaw 是一个**多智能体治理系统**，为 OpenClaw、OpenHarness、Hermes 等 agent runtime 提供可插拔的治理能力。

**它不是什么：**
- 不是 agent runtime（不替代 OpenClaw / OpenHarness）
- 不是把所有问题推给 swarm 的编排引擎
- 不是只绑定某个 runtime 的专属插件

**它的核心能力：**
- 治理规则引擎 — YAML 定义、动态加载、条件匹配
- 本体建模 — 角色、任务类型、约束的结构化定义
- 证据与记忆 — 执行记录沉淀、教训积累、经验复用
- 解释能力 — 运行时可解释、可追溯、可验证
- 宿主桥接 — 可插拔 adapter，支持多种 runtime 接入

---

## 二、架构分层

```
┌─────────────────────────────────────────────────────────────┐
│                    平台化演进层（未来）                        │
│  - 可视化编辑器  - 治理资产库  - 跨 runtime 迁移              │
├─────────────────────────────────────────────────────────────┤
│                    宿主桥接层（基础架构已形成）                │
│  - 宿主抽象协议（HostMode / HostCapabilities）               │
│  - OpenClaw profile（第一个已落地的 host profile）           │
│  - OpenClaw adapter（三种接入模式）                          │
├─────────────────────────────────────────────────────────────┤
│                    解释与证据层（已完成）                      │
│  - 解释能力（explain_matched_rules）                         │
│  - 解释输出包（ExplanationBundle）                           │
│  - 证据生成（EvidenceGenerator）                             │
│  - 记忆沉淀（MemoryBuilder）                                 │
├─────────────────────────────────────────────────────────────┤
│                    治理内核层（已完成）                        │
│  - 规则加载（load_governance）                               │
│  - 规则匹配（match_rules + applies_when）                    │
│  - 本体模型（Role/TaskType/GovernanceRule）                  │
│  - 引擎编排（GovernanceEngine）                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 三、治理内核

### 3.1 数据模型

```
core/governance/models.py
  ├── Condition          — 单层条件表达式（op: ==, !=, in, exists）
  ├── RoleDefinition     — 角色定义（id/name/capabilities/handoff_to）
  ├── TaskType           — 任务类型（id/required_roles/review_required）
  ├── GovernanceRule     — 治理规则（conditions + applies_when + metadata）
  ├── ReviewPolicy       — 审查策略（reviewer_must_differ_from）
  └── EscalationPolicy   — 升级策略（escalate_to / timeout_ms）
```

### 3.2 规则引擎

```
core/governance/
  ├── loader.py          — YAML → GovernanceRule 列表
  ├── matcher.py         — 两段式匹配：先判适用（applies_when），再判合规（conditions）
  ├── explainer.py       — 规则匹配后生成结构化解释
  └── explainer_bundle.py — 打包完整解释输出（readable_summary / risk_summary）
```

### 3.3 本体模型

```
core/meta_model/
  ├── models.py          — 元模型校验（object_types / relation_types）
  └── loader.py          — YAML 本体定义加载
```

本体定义位于 `schemas/meta/`：
- `object_types.yaml` — 对象类型定义
- `relation_types.yaml` — 关系类型定义

### 3.4 引擎编排

```
core/engine/orchestrator.py — GovernanceEngine

处理流程：
raw_event → NormalizedEvent → match_rules() → GateResult
  → EvidenceGenerator → FileEvidenceStore → FileMemoryStore
```

---

## 四、解释与证据层

### 4.1 核心数据流

```
raw_event
  → NormalizedEvent (core/events/normalizer.py)
  → match_rules() (core/governance/matcher.py)
  → GateResult (decision + matched_rules)
  → EvidenceGenerator (core/evidence/generator.py)
  → MemoryBuilder (core/engine/memory_builder.py)
  → FileEvidenceStore / FileMemoryStore (stores/file/*)
  → HostAdapter.write_back() (adapters/*)
  → ExplainBridge.enhance_output() (adapters/openclaw/explain_bridge.py)
  → ExplanationBundle (core/governance/explainer_bundle.py)
```

### 4.2 关键类型

```python
# stores/protocols.py
GateResult(decision, reason, matched_rules, evidence_ids, suggestions)
Evidence(id, type, assertion, source_ref, timestamp, confidence, ...)
MemoryRecord(id, type, summary, tags, source_evidences, created_at, ...)
```

---

## 五、宿主桥接层

### 5.1 宿主抽象协议

```
adapters/host_protocols.py
  ├── HostMode         — 枚举：SHADOW / NOTIFICATION / HOOKS_LIVE
  ├── HostWakeResult   — 统一 wake 结果结构
  ├── HostCapabilities — 能力声明（支持哪些模式）
  └── HostAdapterProfile — 宿主 profile 协议（每个 runtime 实现）
```

### 5.2 OpenClaw 三种接入模式

| 模式 | 目的 | 入口模块 | 成熟度 |
|------|------|---------|--------|
| **shadow** | 本地 mock 测试、治理引擎外围接入 | `ShadowRuntime` | 正式工程面 |
| **notification** | 旧通知线兼容、内部通知 | `OpenClawNotificationAdapter` | 正式工程面 |
| **hooks-live** | 真实 OpenClaw gateway 对接 | `OpenClawHooksAdapter` | MVP |

详细说明：`docs/integration/openclaw_integration_modes.md`

### 5.3 OpenClaw Profile

```
adapters/openclaw/profile.py — OpenClawProfile

声明：
- 支持的模式：shadow + notification + hooks_live
- 各模式入口模块、成熟度、验证状态
```

### 5.4 OpenClaw 适配器文件

```
adapters/openclaw/
  ├── adapter.py              — OpenClawHostAdapter（mock adapter）
  ├── shadow_runtime.py       — ShadowRuntime（外围包装模板）
  ├── notification_adapter.py — OpenClawNotificationAdapter（HTTP/command）
  ├── hooks_adapter.py        — OpenClawHooksAdapter（真实 hooks）
  ├── explain_bridge.py       — ExplainBridge（解释能力接入）
  ├── hook_contract.py        — HookAgentPayload 契约
  ├── profile.py              — OpenClawProfile
  ├── runtime_trace.py        — 运行时追踪
  └── debug_render.py         — 调试渲染
```

### 5.5 配置

私有配置位于 `~/.saucyclaw/saucyclaw.json`，不进入版本控制：

```json
{
  "notification": {
    "gateway_url": "http://your-gateway/hooks/agent",
    "hooks_token": "your-hooks-token",
    "timeout_ms": 10000
  }
}
```

详细说明：`docs/configuration.md`

---

## 六、存储层

```
stores/
  ├── protocols.py            — EvidenceStore / MemoryStore 协议
  └── file/
      ├── evidence/store.py   — 文件证据存储实现
      └── memory/store.py     — 文件记忆存储实现
```

---

## 七、项目结构

```
SaucyClaw/
├── core/                          # 治理内核（runtime 无关）
│   ├── meta_model/                # 元模型定义与校验
│   ├── governance/                # 规则引擎（models/matcher/loader/explainer）
│   ├── engine/                    # 引擎编排（orchestrator/memory_builder）
│   ├── events/                    # 事件标准化
│   ├── evidence/                  # 证据生成
│   └── config/                    # 配置加载
├── stores/                        # 存储层
│   ├── file/                      # 文件存储（evidence/memory）
│   └── protocols.py               # 存储协议
├── adapters/                      # 宿主桥接层
│   ├── host_protocols.py          # 宿主抽象协议（M10）
│   └── openclaw/                  # OpenClaw 适配器
├── schemas/                       # 本体定义
│   ├── governance/                # rules.yaml / roles.yaml / task_types.yaml
│   └── meta/                      # object_types.yaml / relation_types.yaml
├── tests/                         # 测试
│   ├── unit/                      # 单元测试
│   └── integration/               # 集成测试
└── docs/                          # 终稿设计文档
```

---

## 八、测试

当前测试覆盖：283 单元测试，全部通过。

```bash
pytest tests/unit -v          # 单元测试
pytest tests/integration -v   # 集成测试
```

---

## 九、文档索引

`docs/` 中保留的终稿文档：

| 文档 | 内容 |
|------|------|
| `docs/integration/openclaw_integration_modes.md` | 三种接入模式详解 |
| `docs/integration/openclaw_hooks_contract.md` | Hooks Payload 契约 |
| `docs/integration/openclaw_results_evidence.md` | 结果与证据关系 |
| `docs/integration/runtime_capability_matrix.md` | 多 runtime 能力矩阵 |
| `docs/configuration.md` | 配置说明 |

过程文档、阶段规划、ADR 等保存在 `.local-docs/`，不公开。
