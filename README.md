<h1 align="center">🦞 SaucyClaw </h1>

> A multi-agent governance harness with ontology, evidence, and explainable rules.
> 一个以**本体、证据、治理规则**为核心的多智能体治理 Harness，提供可配置、可解释、可验证、可进化的治理能力。
<p align="left">
  <img alt="Agent Hardness Engineering" src="https://img.shields.io/badge/agent-hardness%20engineering-blue">
  <img alt="Governance First" src="https://img.shields.io/badge/governance-first-orange">
  <img alt="Evaluation Ready" src="https://img.shields.io/badge/evaluation-ready-green">
  <img alt="OpenClaw Compatible" src="https://img.shields.io/badge/OpenClaw-compatible-purple">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue" alt="MIT License"></a>
</p>
---

## 一、项目定位

### 一句话定义

**SaucyClaw = 一个以本体、证据、治理规则为核心的多智能体治理 Harness，能够插入多种智能体运行时，提供可配置、可解释、可验证、可进化的治理能力。**

### 它是什么

SaucyClaw 是一个**多智能体治理系统**，核心包括：

- **治理规则引擎**：基于 YAML 的规则定义、动态加载、条件匹配
- **本体建模**：角色、任务类型、约束的结构化定义
- **证据与记忆**：执行记录沉淀、教训积累、经验复用
- **解释能力**：运行时可解释、可追溯、可验证
- **宿主桥接层**：可插拔的 adapter 体系，支持多种 runtime

SaucyClaw **不替代**智能体运行时（如 OpenHarness），也不做终端应用（如 Hermes），而是为它们提供**治理能力**。

### 它不是什么

SaucyClaw **不是**：

- 一个新的 AI agent 运行时框架
- 一个把所有问题都推给 swarm 的项目
- 一个只强调人格或角色扮演的项目
- 一个只绑定 OpenClaw 的专属仓库
- 一个只讲 prompt 技巧、不讲团队工程的样板

### 与相邻项目的定位差异

| 维度 | Hermes Agent | OpenHarness | SaucyClaw |
|------|-------------|-------------|-----------|
| **本质** | 终端应用（TUI + 多平台） | 智能体运行时框架 | 多智能体治理 Harness |
| **解决什么** | 让 LLM 成为日常生产力工具 | 提供可运行的 AI 智能体基础设施 | 让多智能体协作有序且持续进化 |
| **关键词** | 自改进、多平台、记忆 | 引擎、工具、技能、权限 | 角色边界、本体模型、证据沉淀、解释验证 |
| **类比** | 智能助手汽车 | 智能体发动机工厂 | 交通规则 + 驾照考试 + 经验积累 |

---

## 二、核心架构

### 四层一体的体系

```
┌─────────────────────────────────────────────────────────────┐
│                    平台化演进层（未来）                        │
│  - 可视化编辑器                                              │
│  - 治理资产库                                                │
│  - 跨 runtime 迁移                                           │
├─────────────────────────────────────────────────────────────┤
│                    宿主桥接层（基础架构已形成）              │
│  - OpenClaw adapter（三种接入模式）                         │
│    - Shadow Mode（正式工程面）                              │
│    - Notification Mode（正式工程面）                        │
│    - Hooks-Live Mode（MVP）                                │
│  - OpenHarness adapter (TODO)                              │
│  - Hermes adapter (TODO)                                   │
├─────────────────────────────────────────────────────────────┤
│                    解释与证据层（已完成）                      │
│  - 解释能力（explain_matched_rules）                        │
│  - 解释输出包（ExplanationBundle）                          │
│  - 证据生成（EvidenceGenerator）                            │
│  - 记忆沉淀（MemoryBuilder）                                │
├─────────────────────────────────────────────────────────────┤
│                    治理内核层（已完成）                        │
│  - 规则加载（load_governance）                              │
│  - 规则匹配（match_rules + applies_when）                   │
│  - 本体模型（Role/TaskType/GovernanceRule）                │
│  - 引擎编排（GovernanceEngine）                             │
└─────────────────────────────────────────────────────────────┘
```

### 治理闭环

```
规则定义 → 引擎处理 → 证据生成 → 记忆沉淀 → 解释输出 → 回归验证 → 规则演进
```

### 核心数据流

```
raw_event
  → NormalizedEvent (events/normalizer.py)
  → match_rules() (governance/matcher.py)
  → GateResult (decision + matched_rules)
  → EvidenceGenerator (evidence/generator.py)
  → MemoryBuilder (engine/memory_builder.py)
  → FileEvidenceStore / FileMemoryStore (stores/file/*)
  → OpenClawHostAdapter.write_back() (adapters/openclaw/adapter.py)
  → ExplainBridge.enhance_output() (adapters/openclaw/explain_bridge.py)
  → ExplanationBundle (governance/explainer_bundle.py)
```

---

## 三、当前能力

### 治理内核（已完成）

- ✅ **规则定义**：YAML 驱动的治理规则（conditions + applies_when + metadata）
- ✅ **规则匹配**：两段式评估（先判适用，再判合规）
- ✅ **本体模型**：5 种角色（developer/specialist/reviewer/manager/orchestrator）+ 5 类任务（A-E）
- ✅ **规则元数据**：category / source / rationale / risk_level
- ✅ **引擎编排**：事件 → 匹配 → 证据 → 记忆的完整流程
- ✅ **回归验证**：136+ 单元测试 + 6 个场景 fixture

### 解释与证据层（已完成）

- ✅ **运行时解释**：`explain_matched_rules()` 生成结构化解释
- ✅ **解释输出包**：`ExplanationBundle` 包含 readable_summary / risk_summary / suggestions
- ✅ **Shadow Mode**：`ExplainBridge` 独立桥接，不改变 adapter 契约
- ✅ **证据生成**：违规时自动生成 Evidence 记录
- ✅ **记忆沉淀**：Block / Allow / Escalate 三类 MemoryRecord

### 宿主桥接层（基础架构）

- ✅ **Mock Adapter**：`OpenClawHostAdapter`（intercept_output + write_back）
- ✅ **ExplainBridge**：解释能力接入 adapter 边界
- ✅ **Shadow Mode**：`ShadowRuntime` 外围接入模板（正式工程面）
- ✅ **Notification Mode**：`OpenClawNotificationAdapter` 旧通知线兼容（正式工程面）
- ✅ **Hooks-Live Mode**：`OpenClawHooksAdapter` 真实 hooks 对接（MVP）
- ⏳ **多 runtime 支持**：待实现 OpenHarness / Hermes adapter

#### OpenClaw 三种接入模式

| 模式 | 目的 | 入口模块 | 成熟度 |
|------|------|---------|--------|
| **shadow** | 本地 mock 测试、治理引擎外围接入 | `ShadowRuntime` | 正式工程面 |
| **notification** | 旧通知线兼容、内部通知 | `OpenClawNotificationAdapter` | 正式工程面 |
| **hooks-live** | 真实 OpenClaw gateway 对接 | `OpenClawHooksAdapter` | MVP |

详细说明：`docs/integration/openclaw_integration_modes.md`

---

## 四、术语表

| 术语 | 定义 |
|------|------|
| **治理规则**（GovernanceRule） | YAML 定义的规则，包含 conditions / applies_when / metadata |
| **本体模型** | 角色、任务类型、约束的结构化定义（RoleDefinition / TaskType） |
| **证据**（Evidence） | 违规执行的记录，包含事件、规则、时间戳 |
| **记忆**（Memory） | 任务执行的教训沉淀，包含 success/failure/lesson |
| **解释能力** | 运行时生成结构化解释（category/risk/source/rationale） |
| **解释输出包**（ExplanationBundle） | 完整的解释输出，包含 readable_summary / risk_summary |
| **宿主桥接**（Host Adapter） | 连接 SaucyClaw 与外部 runtime 的适配器（如 OpenClawHostAdapter） |
| **治理 Harness** | 可插拔、可配置、可迁移的治理能力体系 |

---

## 五、项目结构

```text
SaucyClaw/
├── core/                          # 治理内核
│   ├── governance/                # 规则引擎（models/matcher/loader/explainer）
│   ├── events/                    # 事件标准化
│   ├── evidence/                  # 证据生成
│   ├── engine/                    # 引擎编排
│   └── meta_model/                # 元模型
├── stores/                        # 存储层
│   ├── file/                      # 文件存储（evidence/memory）
│   └── protocols.py               # 存储协议
├── adapters/                      # 宿主桥接层
│   └── openclaw/                  # OpenClaw 适配器 + ExplainBridge
├── schemas/                       # 本体定义
│   └── governance/                # rules.yaml / roles.yaml / task_types.yaml
├── tests/                         # 测试
│   ├── unit/                      # 单元测试
│   └── integration/               # 集成测试
├── docs/                          # 文档
│   └── phase/                     # 阶段文档
└── README.md                      # 本文件
```

---

## 六、推荐阅读顺序

第一次进入仓库，建议按以下顺序阅读：

1. `README.md`（本文件）
2. `docs/integration/openclaw_integration_modes.md`（OpenClaw 三种接入模式）
3. `docs/phase/project_alignment_report.md`（项目对齐报告）
4. `system/SYSTEM_SPEC.md`（系统规范）
5. `core/governance/models.py`（治理模型）
6. `core/governance/matcher.py`（规则匹配器）
7. `adapters/openclaw/__init__.py`（OpenClaw 接入面总入口）
8. `tests/integration/test_governance_fixtures.py`（回归测试）

> 语义裁决说明：若入口文件表达存在差异，以 `system/SYSTEM_SPEC.md` 为准。

---

## 七、使用场景

SaucyClaw 适合：

- 构建强大且受约束的 agent 团队
- 设计可回放、可比较、可回归的团队评测体系
- 作为 OpenClaw、OpenHarness、Hermes 等场景下的治理基线
- 作为角色模板、流程模板、评测模板的统一底座
- 治理规则的可配置化、可视化、资产化

---

## 八、当前方向

当前阶段，SaucyClaw 已完成：
- **治理内核**（规则引擎、本体模型、引擎编排）
- **解释与证据层**（解释能力、证据生成、记忆沉淀）
- **宿主桥接层基础架构**（三种 OpenClaw 接入模式）

**OpenClaw 接入面当前状态：**

| 接入线 | 成熟度 | 说明 |
|-------|--------|------|
| Shadow Mode | ✅ 正式工程面 | 本地 mock 测试、治理引擎外围接入 |
| Notification Mode | ✅ 正式工程面 | 旧通知线兼容、内部通知 |
| Hooks-Live Mode | ⚠️ MVP | 真实 gateway 已打通，无队列/持久化 |

下一步规划：
- 多 runtime adapter 体系（OpenHarness / Hermes）
- 治理规则的动态加载与热更新
- 可视化编辑器与治理资产库
- 跨 runtime 的治理能力迁移

---

## 九、许可

MIT License
