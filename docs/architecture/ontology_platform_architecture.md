# Ontology Platform 架构设计

> N1.5 — Ontology Platform Architecture & Visual Authoring Foundation
>
> 本文档定义 SaucyClaw 本体平台的设计时（Studio）与运行时（Runtime）架构，
> 以及它们与治理层（Governance）和宿主层（Host）的边界与数据流。

## 一、总览

SaucyClaw 的本体平台分为四个核心区域：

```
┌─────────────────────────────────────────────────────────┐
│                    Ontology Studio（设计时）                │
│                                                         │
│  ┌──────────┐   ┌──────────┐   ┌────────────────────┐   │
│  │ Visual   │──▶│ Schema   │──▶│ Catalog / Registry │   │
│  │ Authoring│   │ Builder  │   │                    │   │
│  └──────────┘   └──────────┘   └────────┬───────────┘   │
│                                         │               │
│  ┌──────────┐   ┌──────────┐           │               │
│  │ Round-   │◀──│ Validation│           │               │
│  │ Trip     │   │ (校验)    │◀──────────┘               │
│  └──────────┘   └──────────┘                            │
└─────────────────────────────────────────────────────────┘
         │                                    │
         ▼                                    ▼
┌──────────────────────┐    ┌────────────────────────────────┐
│  Ontology Runtime    │    │  Governance Projection         │
│  （运行时）           │    │  （治理投影）                   │
│                      │    │                                │
│  ┌──────────────┐    │    │  ┌──────────────────────────┐  │
│  │ Schema Layer │    │    │  │ PolicyBinding → Rule     │  │
│  │ (静态类型)    │    │    │  │ OntologyCondition → Check│  │
│  └──────────────┘    │    │  └──────────────────────────┘  │
│  ┌──────────────┐    │    │                                │
│  │ Instance     │    │    │  运行时判断：                    │
│  │ Layer (动态)  │    │    │  raw_event → GateResult        │
│  └──────────────┘    │    │                                │
│  ┌──────────────┐    │    └────────────────────────────────┘
│  │ Binding Layer│    │
│  │ (证据链)      │    │    ┌────────────────────────────────┐
│  └──────────────┘    │    │  Host Projection               │
│  ┌──────────────┐    │    │  （宿主投影）                   │
│  │ Loop Layer   │    │    │                                │
│  │ (治理循环)    │    │    │  ┌──────────────────────────┐  │
│  └──────────────┘    │    │  │ EventMapping → Host Event│  │
└──────────────────────┘    │  │ EntityResolution → User  │  │
                            │  │ FactDerivation → Audit   │  │
                            │  └──────────────────────────┘  │
                            └────────────────────────────────┘
```

## 二、四层架构

### 2.1 Ontology Studio（设计时）

**职责**：本体的创建、编辑、校验、导出。

**不做的事**：
- 不做 UI 渲染
- 不做运行时判断
- 不做治理决策

**做的事**：
- **Visual Authoring**：定义 VisualNode、VisualEdge、PropertySchema、FormSchema，为后续可视化编辑器提供规范模型
- **Schema Builder**：将设计时模型编译为运行时可用的 Schema（OntologySchema）
- **Catalog / Registry**：集中管理所有已注册的本体类型，提供查询和索引
- **Validation**：校验本体一致性（类型引用、循环依赖、必填属性）
- **Round-Trip**：保证 YAML ↔ Visual Model ↔ Runtime Schema 三向等价

**文件映射**：
| 组件 | 文件 |
|------|------|
| Visual Model | `ontology/visual_model.py` |
| Catalog | `ontology/catalog.py` |
| Validation | `ontology/validation.py` |
| Loader | `ontology/loader.py` |
| Round-Trip | `ontology/roundtrip.py` |

### 2.2 Ontology Runtime（运行时）

**职责**：在运行时使用本体进行治理判断。

**层次**：
| 层次 | 职责 | 文件 |
|------|------|------|
| Schema Layer | 类型定义（静态） | `ontology/schema.py` |
| Instance Layer | 实例模型（动态） | `ontology/instances.py` |
| Binding Layer | 证据链绑定 | `ontology/facts.py` |
| Loop Layer | 治理循环 | `ontology/governance_loop.py` |

**不做的事**：
- 不做可视化
- 不做设计时校验
- 不处理 YAML 加载

**做的事**：
- 接收运行时事件
- 映射为 EventInstance + EntityInstance + ContextSnapshot
- 推导 FactRecord
- 通过 PolicyBinding 进行治理判断

### 2.3 Governance Projection（治理投影）

**职责**：将本体类型和实例投影为具体的治理决策。

**核心映射**：
| 本体概念 | 治理投影 |
|---------|---------|
| PolicyBinding → GovernanceRule | 规则绑定 |
| OntologyCondition → Check | 条件检查 |
| EvidenceRef → ValidationBundle | 证据绑定 |

**运行时流**：
```
raw_event
  → EventMappingResult
    → FactEstablishmentResult
      → PolicyJudgment
        → OntologyGovernanceResult
          → GateResult（Allow / Block / Review）
```

### 2.4 Host Projection（宿主投影）

**职责**：将本体事件映射为具体宿主的语义格式。

**核心映射**：
| 本体概念 | 宿主投影 |
|---------|---------|
| EventMapping → Host Event | 宿主事件格式 |
| EntityResolution → User/Role | 用户/角色解析 |
| FactDerivation → Audit Log | 审计日志 |

## 三、边界与约束

### 3.1 设计时 vs 运行时

| 维度 | 设计时（Studio） | 运行时（Runtime） |
|------|-----------------|-------------------|
| 输入 | YAML / JSON 配置 | 运行时事件（dict） |
| 输出 | OntologySchema | GateResult |
| 校验 | 结构一致性 | 语义一致性 |
| 可变性 | 可编辑、可导出 | 不可变、只读 |
| 频率 | 低频（配置变更） | 高频（每事件触发） |

### 3.2 Studio 不进入 Runtime

- Studio 的 VisualNode、VisualEdge、FormSchema 等类型**不进入**运行时判断链路
- Studio 产出的 OntologySchema 是运行时的**唯一输入**
- 这保证了运行时性能和设计时灵活性的完全解耦

### 3.3 Runtime 不依赖 Studio

- 运行时可以完全独立部署，不依赖 Studio 组件
- 运行时只依赖 OntologySchema（已编译、已校验）
- 这意味着 Studio 可以是外部工具，Runtime 是轻量运行时库

## 四、为什么 N1.5 优先于 N2/N3

1. **N2（治理闭环）已经有了 N1 基础代码**，但缺少平台化能力。没有 Studio，本体只能通过手工编写 YAML 构造，无法扩展。
2. **N3（查询语言）需要 Catalog**。没有统一的类型注册和索引，查询无法建立语义基础。
3. **可视化友好是平台化的前提**。一个不可视化构建的本体系统，最终只能是代码工程，不是产品。
4. **Round-Trip 保证可维护性**。YAML ↔ Visual Model ↔ Runtime Schema 的三向等价，确保设计变更不会导致运行时断裂。

## 五、文件索引

### 设计时（Studio）
- `ontology/visual_model.py` — 可视化规范模型
- `ontology/catalog.py` — 类型注册与索引
- `ontology/validation.py` — 一致性校验
- `ontology/loader.py` — YAML 加载（已有，N2 创建）
- `ontology/roundtrip.py` — 三向转换

### 运行时（Runtime）
- `ontology/schema.py` — 本体类型定义（N1）
- `ontology/instances.py` — 实例模型（N1）
- `ontology/facts.py` — 事实与证据绑定（N1）
- `ontology/policy_binding.py` — 策略绑定（N1）
- `ontology/mapping.py` — 事件映射（N2）
- `ontology/establishment.py` — 事实建立（N2）
- `ontology/governance_loop.py` — 治理循环（N2）

### Schema 配置
- `schemas/ontology/event_types.yaml` — 事件类型
- `schemas/ontology/context_types.yaml` — 上下文类型
- `schemas/ontology/fact_types.yaml` — 事实类型

### 元模型（Meta Model）
- `core/meta_model/models.py` — EntityType、RelationType、ActionType
- `core/meta_model/loader.py` — 元模型加载

### 治理核心
- `core/governance/models.py` — GovernanceRule、GovernanceSchema
- `core/governance/loader.py` — 治理规则加载
- `core/engine/orchestrator.py` — GovernanceEngine 编排
