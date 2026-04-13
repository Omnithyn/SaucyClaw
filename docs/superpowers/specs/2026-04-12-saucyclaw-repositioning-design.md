# SaucyClaw 项目重新定位与架构设计

**日期**: 2026-04-12
**状态**: 待审核
**作者**: 头脑风暴会话

---

## 1. 项目定位

### 一句话定位

**SaucyClaw = 可进化的多智能体治理 Harness**

一个基于本体模型的、能自我学习优化的多智能体治理平台。为 OpenHarness、Hermes、Claude Code 等智能体运行时提供治理规则、评估反馈和持续进化能力。

### 核心价值

> **"你的智能体引擎再好，也需要交通规则。"**

SaucyClaw 不替代智能体运行时（OpenHarness），也不做终端应用（Hermes），而是为它们提供：
- **治理规则** — 角色、分类、审查、权限边界
- **本体建模** — 定义事物、行为、约束、场景
- **评估反馈** — 量化治理效果，追踪规则效能
- **记忆进化** — 从执行中学习，规则自我优化

### 与相邻项目的定位差异

| 维度 | Hermes Agent | OpenHarness | SaucyClaw |
|------|-------------|-------------|-----------|
| **本质** | 生产级终端应用（TUI + 多平台） | 智能体运行时框架（引擎 + 工具） | 多智能体治理 Harness |
| **解决什么** | 让 LLM 成为日常生产力工具 | 提供可运行的 AI 智能体基础设施 | 让多智能体协作有序且持续进化 |
| **关键词** | 自改进、多平台、记忆 | 引擎、工具、技能、权限 | 角色边界、本体模型、评估进化 |
| **类比** | 配好一切的智能助手汽车 | 智能体发动机工厂 | 交通规则 + 驾照考试 + 经验积累 |

### 设计哲学

**目标不变**：输出自我进化的智能体，构建出想要的智能体。

一切子系统（本体、记忆、评估、场景、治理）都是为这个目标服务的信息供给者，不是前置条件。智能体实时决策时，可以从任意信息源获取证据，快速刷新判断。

---

## 2. 架构总览

```
┌──────────────────────────────────────────────────────────────────┐
│                        SaucyClaw                                 │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              进化引擎 (Evolution Engine)                  │    │
│  │   多智能体决策优化 · 规则自适应 · 质量约束 · 置信度控制    │    │
│  └─────────────────────────┬───────────────────────────────┘    │
│                            │ 消费信息                            │
│     ┌──────────┬───────────┼───────────┬──────────────┐        │
│     ▼          ▼           ▼           ▼              ▼        │
│  ┌──────┐  ┌──────┐  ┌────────┐  ┌────────┐  ┌──────────┐   │
│  │本体   │  │记忆  │  │评估    │  │场景    │  │治理规则   │   │
│  │建模   │  │系统  │  │框架    │  │论证    │  │引擎      │   │
│  │平台   │  │      │  │        │  │        │  │          │   │
│  └──────┘  └──────┘  └────────┘  └────────┘  └──────────┘   │
│     │          │           │           │             │         │
│     └──────────┴───────────┴───────────┴─────────────┘         │
│                            │ 实时证据供给                        │
│                            ▼                                   │
│              ┌──────────────────────────┐                      │
│              │    智能体实时决策           │                      │
│              │    (Runtime Agent)        │                      │
│              │                           │                      │
│              │  ← 本体: 事物定义          │                      │
│              │  ← 记忆: 历史经验          │                      │
│              │  ← 评估: 置信度指标        │                      │
│              │  ← 场景: 运行验证结果      │                      │
│              │  ← 治理: 适用规则          │                      │
│              │                           │                      │
│              │  → 决策结果输出             │                      │
│              │  → 反哺新的经验记录         │                      │
│              └──────────────────────────┘                      │
└──────────────────────────────────────────────────────────────────┘
```

### 关键原则

1. **松耦合**：五个子系统并列，不互相强依赖。智能体可以从任意组合获取信息。
2. **实时供给**：证据信息快速刷新，不是静态加载后不变。
3. **异常补偿**：某个信息源不可用时，其他源顶上，保证决策不阻塞。
4. **质量约束**：整套系统只在置信度最高时输出。

---

## 3. 子系统详细设计

### 3.1 本体建模平台（Ontology Modeling Platform）

#### 3.1.1 方法论参考

- **Palantir 操作型本体论**：对象 + 属性 + 关系 + 动作，不仅描述世界，还能改变世界
- **OntoFlow**：本体构建平台（待补充详细信息）
- **传统语义网**：OWL/RDF 作为知识表示的补充

#### 3.1.2 三类本体

**智能体本体（Agent Ontology）**
- 主体类型：角色定义（General Manager、Developer、Reviewer、Researcher...）
- 属性：能力集、权限边界、协作关系、置信度
- 行为模型：能做什么、不能做什么、什么时候交接、异常时怎么补偿

**业务本体（Business Ontology）**
- 业务对象：支付、订单、用户、产品、合同...
- 属性：状态、约束、业务规则、验证条件
- 行为模型：CRUD 操作、状态转换、副作用、审计日志

**专业领域本体（Domain Ontology）**
- 领域专家知识：金融合规、医疗诊断、电商风控、物流调度...
- 结构化定义：流程、规则、判断标准、最佳实践
- 置信度：每条知识的来源可靠度、时效性、适用范围

#### 3.1.3 三层架构（借鉴 Palantir）

```
┌─────────────────────────────────────────┐
│  动态层（Dynamic）                       │
│  实时交互、历史追踪、人机协作              │
│  - 本体数据实时更新                      │
│  - 变更记录和回滚                        │
│  - 人机协作审核点                        │
├─────────────────────────────────────────┤
│  动力层（Kinetic）                       │
│  动作类型、前置条件、副作用、权限          │
│  - 定义可对本体执行的操作                 │
│  - 每个动作有验证规则和权限控制            │
│  - 动作执行触发下游效应                   │
├─────────────────────────────────────────┤
│  语义层（Semantic）                      │
│  对象、属性、链接、业务术语映射            │
│  - 定义事物是什么                        │
│  - 定义事物之间的关系                     │
│  - 统一业务词汇                           │
└─────────────────────────────────────────┘
```

#### 3.1.4 本体数据模型

```yaml
# 对象类型定义
ObjectType:
  id: "agent-role"
  name: "智能体角色"
  description: "定义多智能体系统中的角色类型"
  properties:
    - name: "capabilities"
      type: "array[string]"
      description: "该角色具备的能力集"
    - name: "permissions"
      type: "object"
      description: "权限边界定义"
    - name: "confidence_threshold"
      type: "float"
      description: "该角色输出结果的最低置信度要求"
  relationships:
    - name: "collaborates_with"
      target: "agent-role"
      type: "many-to-many"
    - name: "reviews"
      target: "agent-role"
      type: "one-to-many"

# 动作类型定义
ActionType:
  id: "assign-task"
  name: "分配任务"
  target_object: "task"
  editable_properties: ["assignee", "priority", "deadline"]
  preconditions:
    - "assignee has capability required by task"
    - "assignee permission covers task scope"
    - "assignee current workload < max_capacity"
  postconditions:
    - "task status = assigned"
    - "assignee workload += task.estimated_effort"
  side_effects:
    - "notify assignee"
    - "log to execution record"
  permissions:
    - "role: general-manager"
    - "role: orchestrator"
```

#### 3.1.5 本体演化机制

- **分支**：在本体分支上测试更改，不影响生产
- **提案**：变更通过提案流程审核
- **审核**：reviewer 审核本体变更
- **合并**：审核通过后合并到生产本体
- **回滚**：支持历史版本恢复

### 3.2 记忆系统（Memory System）

#### 3.2.1 记忆分层

```
┌─────────────────────────────────────┐
│  瞬时记忆（会话级）                   │
│  当前对话上下文，会话结束即释放        │
├─────────────────────────────────────┤
│  短期记忆（任务级）                   │
│  单次任务的执行记录和中间状态          │
│  保留周期：任务完成后 7 天            │
├─────────────────────────────────────┤
│  中期记忆（项目级）                   │
│  跨任务的经验教训、规则演化历史        │
│  保留周期：30 天，按权重衰减          │
├─────────────────────────────────────┤
│  长期记忆（领域级）                   │
│  跨项目的通用教训、领域专家知识        │
│  保留周期：持久化，按需清理            │
└─────────────────────────────────────┘
```

#### 3.2.2 记忆操作

- **写入**：任务完成后自动归档执行记录
- **检索**：按领域、角色、任务类型、关键词检索
- **衰减**：时间越久远、使用频率越低的记忆权重越低
- **合并**：相似记忆自动合并，避免冗余
- **失效**：被新证据推翻的记忆标记为失效

#### 3.2.3 记忆数据模型

```yaml
MemoryRecord:
  id: "mem-20260412-001"
  type: "lesson"                # lesson | rule_evolution | expertise | pattern
  timestamp: "2026-04-12T10:30:00Z"
  domain: "fintech"
  context:
    task_type: "C"
    roles_involved: ["developer", "reviewer"]
    governance_version: "v0.3.1"
  content:
    what_worked: "角色分工清晰，review 拦截了安全漏洞"
    what_failed: "initial implementation 忽略了边界条件"
    lesson: "C 类任务应强制要求边界测试 checklist"
  metrics:
    confidence: 0.85
    evidence_count: 3
    contradicted_by: []
  decay:
    created_at: "2026-04-12"
    last_accessed: "2026-04-12"
    access_count: 1
    weight: 1.0
```

### 3.3 评估框架（Evaluation Framework）

#### 3.3.1 指标体系

```yaml
# 规则效能指标
RuleEffectiveness:
  rule_id: "c-review-checklist"
  adherence_rate: 0.92            # 遵守率
  false_positive_rate: 0.08       # 误报率
  average_cost_seconds: 120       # 平均执行成本
  trend: "improving"              # improving | stable | degrading
  last_updated: "2026-04-12"

# 任务效能指标
TaskEffectiveness:
  task_type: "C"
  success_rate: 0.87
  avg_review_iterations: 1.8
  avg_time_to_complete_seconds: 1800
  defect_rate: 0.13
  trend: "stable"

# 智能体效能指标
AgentEffectiveness:
  agent_role: "developer"
  tasks_completed: 150
  avg_quality_score: 0.82
  avg_review_iterations: 1.5
  rule_violation_rate: 0.03
  trend: "improving"

# 综合置信度
ConfidenceScore:
  ontology_coverage: 0.75         # 本体对当前任务的覆盖度
  memory_relevance: 0.82          # 记忆与当前任务的相关度
  evaluation_quality: 0.90        # 评估框架的数据质量
  governance_maturity: 0.70       # 治理规则成熟度
  composite_score: 0.79           # 加权综合得分
  threshold_for_output: 0.75      # 低于此值不输出
```

#### 3.3.2 评估流程

```
任务完成 → 采集指标 → 更新效能记录 → 计算趋势
                                      ↓
                              检测规则退化
                                      ↓
                          是 → 生成改进建议 → 人工审核
                          否 → 归档记录
```

### 3.4 场景论证（Scenario Argumentation）

#### 3.4.1 场景定义

场景是本体实例化的运行环境，用于验证治理规则的有效性：

```yaml
Scenario:
  id: "scenario-fintech-payment"
  name: "金融支付系统多智能体协作"
  domain: "fintech"
  ontology_bindings:
    agent_roles: ["developer", "reviewer", "security-auditor"]
    business_objects: ["Payment", "Transaction", "AuditLog"]
    domain_rules: ["pci-dss-compliance", "input-validation-strict"]
  execution:
    task_stream: [task1, task2, task3, ...]
    expected_outcomes: {...}
    acceptance_criteria:
      - "all security reviews pass"
      - "no PII data leakage"
      - "avg response time < 3000s"
```

#### 3.4.2 异常补偿机制

```
检测异常 → 分类异常类型 → 选择补偿策略
                                  ↓
        ┌─────────────────────────┼─────────────────────────┐
        ▼                         ▼                         ▼
   信息源不可用              规则冲突                 置信度过低
        │                         │                         │
        ▼                         ▼                         ▼
   启用备用源                 优先级裁决                  人工介入
   降级到部分证据              记录冲突                   暂停输出
   标记证据不完整              事后review                  等待补充信息
```

### 3.5 治理规则引擎（Governance Rule Engine）

基于现有的五类任务分类体系（A/B/C/D/E），增强为动态匹配：

```yaml
GovernanceRule:
  id: "rule-c-review-required"
  task_types: ["C"]
  description: "C 类任务需要单人执行 + 审查"
  conditions:
    - "exactly one specialist assigned"
    - "reviewer is different from assignee"
    - "review checklist completed"
  derived_from:
    ontology: "agent-role#developer"
    memory: "mem-20260401-003 (历史教训：无人审查导致质量下降)"
    evaluation: "rule-effectiveness#adherence-rate=0.92"
  enforcement:
    blocking: true               # 不满足则阻止输出
    auto_check: true             # 自动验证
    manual_override: false       # 不允许人工覆盖
```

---

## 4. 实时性与证据供给性能

### 4.1 工程化设计原则

本体构建后的证据信息必须**快速、可靠、按需供给**给智能体实时决策：

```
本体数据 → 索引化存储 → 快速查询 → 证据供给 → 智能体决策
            ↑                │
            │           缓存 + 预计算
            │           按需加载
            │           增量更新
            │           降级策略
```

### 4.2 查询性能目标

| 操作类型 | 延迟目标 | 实现方式 |
|---------|---------|---------|
| 本体对象查询（ByID） | < 1ms | 内存索引 / Hash Map |
| 关系遍历（1-hop） | < 5ms | 邻接表 + 预计算 |
| 规则匹配 | < 10ms | Rete 算法或前缀树 |
| 记忆检索（语义） | < 50ms | 向量索引 + 缓存 |
| 置信度计算 | < 5ms | 加权求和（预计算权重） |

### 4.3 证据供给策略

- **高频证据预热**：常用领域本体的关键规则在系统启动时预加载
- **增量更新**：本体变更只刷新受影响的部分，不重建整个索引
- **按需加载**：只在智能体请求相关领域时才加载详细证据
- **降级策略**：高延迟或信息源不可用时，返回部分证据 + 置信度标记，保证决策不阻塞
- **批量预取**：智能体开始任务时，预取可能需要的本体和记忆

### 4.4 数据结构选型

```
本体对象存储:  YAML/JSON 文件 + 内存 Hash Map（轻量级）
              或 SQLite（中量级，支持查询）

关系索引:      邻接表 + 反向索引

记忆存储:      文件系统（短期）+ SQLite（中长期）

向量检索:      内积 / 余弦相似度（轻量级，无需外部依赖）

配置管理:      YAML 文件 + 热加载
```

---

## 5. 进化循环

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  定义/更新本体 ──→ 加载治理规则 ──→ 场景运行 ──→ 收集证据    │
│       ↑                                                  │  │
│       │     提取教训                                      │  │
│       │     更新记忆                                      │  │
│       │     评估效能                                      │  │
│       │     检测规则退化                                   │  │
│       │     生成改进建议                                   │  │
│       │     人工审核确认                                   │  │
│       └──── 本体/规则/记忆更新 ←────────────────────────────┘  │
│                                                             │
│  每次循环后:                                                 │
│  - 规则效能指标更新                                          │
│  - 记忆权重调整                                              │
│  - 本体置信度更新                                            │
│  - 综合置信度重新计算                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. 实现路线图

| 阶段 | 内容 | 优先级 | 预估产出 |
|------|------|--------|---------|
| **Phase 0** | 治理模板完善（当前能力补齐） | P0 | 五类任务模板、角色定义完善 |
| **Phase 1** | 本体建模平台 MVP | P0 | 智能体本体定义、语义层、基本查询 |
| **Phase 2** | 记忆系统 + 评估框架 MVP | P0 | 任务记录、指标采集、效能报告 |
| **Phase 3** | 进化引擎（闭环打通） | P1 | 从执行到规则更新的完整循环 |
| **Phase 4** | 业务本体 + 领域本体框架 | P1 | 可扩展的本体定义体系 |
| **Phase 5** | 场景论证 + 异常补偿 | P2 | 场景定义、运行验证、降级策略 |
| **Phase 6** | 跨框架适配器 | P2 | OpenHarness/Hermes/Claude Code 适配 |

---

## 7. 参考项目

| 项目 | 借鉴方向 |
|------|---------|
| **Palantir Foundry Ontology** | 操作型本体论、对象-动作-关系模型、三层架构、演化机制 |
| **OntoFlow** | 本体构建平台（待补充详细信息） |
| **OpenHarness** | 智能体运行时、工具系统、技能系统、多提供商支持 |
| **Hermes Agent** | 多平台网关、技能系统、插件架构、用户工程化 |
| **Anthropic Harness Engineering** | 长周期智能体可靠性、上下文管理、子代理编排 |

---

## 8. 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| 过度设计 | 实现周期过长，失去敏捷性 | 从 MVP 开始，每阶段有可交付物 |
| 本体复杂度爆炸 | 查询性能下降 | 严格的查询复杂度目标，增量加载 |
| 进化失控 | 规则变更引入退化 | 变更审核流程、指标监控、回滚机制 |
| 语义漂移 | 本体定义偏离实际需求 | 定期 review、场景验证、用户反馈 |
| 性能不达标 | 证据供给延迟影响决策 | 缓存策略、预热机制、降级路径 |
