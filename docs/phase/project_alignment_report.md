# SaucyClaw 项目对齐审计报告

> 日期：2026-04-14
> 审计范围：基于当前分支 `feat/phase0-1-commit1` 真实代码
> 审计目标：统一项目目标、最终形态、阶段定位、文档表述

---

## 一、项目统一目标

### 核心定位

**SaucyClaw = 以本体、证据、治理规则为核心的多智能体治理 Harness**

一个能够插入多种智能体运行时中的治理系统，逐步演进为可实施、可配置、可解释、可验证、可平台化的治理能力面。

### 核心价值

> "你的智能体引擎再好，也需要交通规则。"

SaucyClaw 不替代智能体运行时，也不做终端应用，而是为它们提供：
- **治理规则** — 角色、分类、审查、权限边界
- **本体建模** — 定义事物、行为、约束、场景
- **证据与记忆** — 执行记录、教训沉淀、经验复用
- **评估反馈** — 量化治理效果，追踪规则效能
- **解释能力** — 运行时可解释、可追溯、可验证

### 与相邻项目的定位差异

| 维度 | Hermes Agent | OpenHarness | SaucyClaw |
|------|-------------|-------------|-----------|
| **本质** | 终端应用（TUI + 多平台） | 智能体运行时框架 | 多智能体治理 Harness |
| **解决什么** | 让 LLM 成为日常生产力工具 | 提供可运行的 AI 智能体基础设施 | 让多智能体协作有序且持续进化 |
| **关键词** | 自改进、多平台、记忆 | 引擎、工具、技能、权限 | 角色边界、本体模型、证据沉淀、解释验证 |
| **类比** | 智能助手汽车 | 智能体发动机工厂 | 交通规则 + 驾照考试 + 经验积累 |

---

## 二、最终形态定义

### 四层一体的体系

#### A. 治理内核层（已基本完成）

当前仓库已完成的核心能力：

**治理域数据模型**
- `GovernanceRule`：规则定义（conditions, applies_when, metadata）
- `RoleDefinition`：角色定义（5 种角色：developer, specialist, reviewer, manager, orchestrator）
- `TaskType`：任务类型（A-E 五类）
- 规则元数据：category, source, rationale, risk_level

**规则加载与匹配**
- `load_governance()`：批量加载 YAML 规则/角色/任务类型
- `match_rules()`：规则匹配器（支持 applies_when 适用性判断）
- `evaluate_rule()`：规则评估（两段式：先判适用，再判合规）

**证据与记忆主流程**
- `EvidenceGenerator`：证据生成（违规时生成记录）
- `MemoryBuilder`：记忆构建（Block/Allow/Escalate 三类记录）
- `FileEvidenceStore`：证据存储（JSONL，按 session_id）
- `FileMemoryStore`：记忆存储（JSON，单记录单文件）
- `GovernanceEngine`：引擎编排（normalizer → matcher → evidence → memory）

**回归验证体系**
- 136+ 单元测试 + 集成测试
- 6 个 governance_cases fixture（Block/Escalate/Allow 场景）
- 批量回归测试框架

#### B. 解释与证据层（已基本完成）

当前仓库已完成的核心能力：

**运行时解释能力**
- `explain_matched_rules()`：将匹配规则转换为结构化解释（category, risk_level, source, rationale）
- `bundle_explanations()`：解释打包器（生成 ExplanationBundle，包含 readable_summary, risk_summary, suggestions）

**解释输出**
- `ExplanationBundle`：完整的解释输出包
- `AdapterExplainOutput`：Adapter 边界的带解释输出包（包含 explanation_bundle + raw_result）

**Shadow Mode**
- `ExplainBridge`：解释桥接器（独立于 adapter，不改变核心契约）
- `enable_shadow_mode()` / `disable_shadow_mode()`：运行时开关
- 可选生成解释信息，不影响现有流程

#### C. 宿主桥接层（已具备基础）

当前仓库已完成的核心能力：

**Mock Adapter**
- `OpenClawHostAdapter`：OpenClaw 宿主适配器（mock 实现）
- `intercept_output()`：输出拦截占位
- `write_back()`：结果写回（当前仅记录到内部日志）

**Bridge Pattern**
- `ExplainBridge`：解释能力接入 adapter 边界
- 形成清晰的接入层抽象

**待完成**
- 真实 OpenClaw 运行时的 hook 接入
- 其他 runtime 的 adapter（OpenHarness, Hermes, Claude Code）

#### D. 平台化演进方向（未来规划）

**可配置规则/本体**
- 治理规则的动态加载与热更新
- 本体模型的可视化编辑与版本管理

**可视化与审查**
- 规则执行的可视化展示
- 记忆与证据的查询界面
- 治理效果的仪表盘

**实施适配**
- 多 runtime 适配器体系
- 跨框架的治理能力迁移

**规则解释查询**
- 基于本体的规则检索
- 语义化的规则查询

**运营与治理资产化**
- 治理规则库
- 场景库
- 最佳实践库

---

## 三、当前阶段能力盘点

### 已完成的阶段

| 阶段 | 核心能力 | 完成度 | 验证方式 |
|------|---------|--------|---------|
| Phase 1.5 | schema ↔ runtime 对齐 | ✅ 100% | `test_governance_alignment.py` 14 tests |
| Phase 1.6 | 批量 YAML 回归验证 | ✅ 100% | `test_governance_fixtures.py` 6 fixtures |
| Phase 1.7 | 规则元数据（category/source/rationale/risk_level） | ✅ 100% | `test_governance_alignment.py` metadata tests |
| Phase 1.8 | 运行时解释能力（explain_matched_rules） | ✅ 100% | `test_governance_explainer.py` 5 tests |
| Phase 1.9 | 解释输出包（ExplanationBundle） | ✅ 100% | `test_governance_explainer_bundle.py` 8 tests |
| Phase 2.0 | adapter 边界 Shadow Mode explain bridge | ✅ 100% | `test_explain_bridge.py` 7 tests |
| Phase 2.1 | 真实 OpenClaw hook 勘测（文档） | ✅ 100% | `phase2-1_hook_survey.md` |

### 当前代码事实

**核心文件统计**：
- `core/`：12 个 Python 模块（governance/events/evidence/engine/meta_model）
- `stores/`：4 个存储实现（evidence/memory/file/memory）
- `adapters/`：2 个适配器模块（openclaw/adapter + explain_bridge）
- `schemas/governance/`：3 个 YAML 定义（rules/roles/task_types）
- `tests/`：159+ 测试（unit + integration）

**关键数据流**：
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

**当前治理闭环**：
```
规则定义 → 引擎处理 → 证据生成 → 记忆沉淀 → 解释输出
```

---

## 四、发现的主要偏差

### 1. 文档表述过窄的问题

#### 问题 1：README 过度强调 "hardness engineering"

**现状**：README 标题为 "agent hardness engineering project baseline"，强调"强团队、强约束、强评测、强迁移"。

**偏差**：过度聚焦于"工程硬度"，弱化了"治理核心"（本体、证据、规则、解释）。

**修正建议**：
- 标题改为："多智能体治理 Harness + 治理规则引擎"
- 副标题补充："基于本体模型、证据沉淀、可解释规则的多智能体治理系统"
- 强调治理闭环（规则定义 → 执行 → 证据 → 解释 → 进化）

#### 问题 2：SYSTEM_SPEC 过度强调"角色边界"

**现状**：SYSTEM_SPEC.md 重点描述 General Manager / Specialist / Reviewer 的职责边界。

**偏差**：弱化了治理规则引擎、证据记忆、解释能力等技术核心。

**修正建议**：
- 补充"技术架构"章节，描述四层体系（治理内核/解释证据/宿主桥接/平台演进）
- 将"角色边界"作为治理内核的一部分，而非唯一重点
- 补充当前已完成的技术能力（matcher/loader/explainer/explain_bridge）

#### 问题 3：Phase 进度文档未体现治理能力

**现状**：`phase0-1_progress.md` 重点描述"Memory 接入"、"规则扩展"等任务。

**偏差**：未明确表述已完成的"治理闭环"（规则加载 → 匹配 → 证据 → 记忆 → 解释）。

**修正建议**：
- 补充"治理能力盘点"章节，明确已完成的闭环
- 区分"数据层"（schema/models）和"运行层"（matcher/engine/explainer）
- 补充"解释能力"作为独立章节（Phase 1.8-1.9-2.0）

### 2. 项目定位表述不足的问题

#### 问题 4：缺乏"治理 Harness"的明确表述

**现状**：文档中多次使用"基线工程"、"骨架"、"模板"等词汇。

**偏差**：未明确表述"治理 Harness"的概念（可插拔、可配置、可迁移的治理能力）。

**修正建议**：
- 在 README 和 SYSTEM_SPEC 中明确"治理 Harness"定位
- 补充"宿主桥接层"的概念（adapter/bridge/hook）
- 强调"可插拔"特性（不绑定特定 runtime）

#### 问题 5：最终形态描述缺失

**现状**：文档重点描述当前已完成的能力。

**偏差**：缺乏对"平台化演进"的清晰表述（可视化、配置化、跨 runtime 适配）。

**修正建议**：
- 补充"演进路线图"章节
- 明确四层体系的未来规划（治理内核已基本完成，解释证据层已基本完成，宿主桥接层待完善，平台化层待启动）
- 补充"治理资产化"概念（规则库、场景库、最佳实践库）

### 3. 技术术语不统一的问题

#### 问题 6：术语混用

**现状**：
- "治理规则" vs "规则定义" vs "schema"
- "解释能力" vs "可解释性" vs "explain"
- "宿主" vs "运行时" vs "runtime" vs "adapter"

**偏差**：术语不统一导致理解混乱。

**修正建议**：
- 统一术语：
  - **治理规则**：GovernanceRule（YAML 定义 + dataclass）
  - **解释能力**：解释输出包（ExplanationBundle + ExplainBridge）
  - **宿主桥接**：Host Adapter（OpenClawHostAdapter + 其他 runtime adapter）
- 在 README 中增加"术语表"章节

---

## 五、后续阶段建议分层

### 近期（Phase 2.2-2.5）

| 阶段 | 目标 | 层级 |
|------|------|------|
| Phase 2.2 | 真实 OpenClaw hook 接入（外围包装） | 宿主桥接层 |
| Phase 2.3 | 其他 runtime adapter（OpenHarness/Hermes） | 宿主桥接层 |
| Phase 2.4 | 治理规则动态加载与热更新 | 治理内核层 |
| Phase 2.5 | 规则效能指标采集与报告 | 评估反馈层 |

### 中期（Phase 3.0-3.5）

| 阶段 | 目标 | 层级 |
|------|------|------|
| Phase 3.0 | 治理规则可视化编辑器（CLI/简单 UI） | 平台化演进层 |
| Phase 3.1 | 记忆与证据查询接口 | 平台化演进层 |
| Phase 3.2 | 本体模型定义与加载（智能体本体） | 治理内核层 |
| Phase 3.3 | 场景库与回归测试自动化 | 评估反馈层 |
| Phase 3.4 | 治理规则版本管理与回滚 | 平台化演进层 |

### 远期（Phase 4.0+）

| 阶段 | 目标 | 层级 |
|------|------|------|
| Phase 4.0 | 治理规则自适应优化（基于效能指标） | 平台化演进层 |
| Phase 4.1 | 跨 runtime 治理能力迁移工具 | 宿主桥接层 |
| Phase 4.2 | 业务本体 + 领域本体框架 | 治理内核层 |
| Phase 4.3 | 治理资产市场（规则库/场景库/最佳实践） | 平台化演进层 |

---

## 六、SaucyClaw 的更新后一句话定义

**SaucyClaw = 一个以本体、证据、治理规则为核心的多智能体治理 Harness，能够插入多种智能体运行时，提供可配置、可解释、可验证、可进化的治理能力。**

---

## 七、文档修正计划

### 高优先级（必须修正）

1. **README.md**
   - 修正标题和副标题
   - 补充"治理闭环"描述
   - 补充"四层体系"架构图
   - 增加"术语表"章节

2. **SYSTEM_SPEC.md**
   - 补充"技术架构"章节
   - 补充"治理能力盘点"
   - 修正项目定位表述

3. **phase0-1_progress.md**
   - 补充"治理能力盘点"章节
   - 明确已完成的治理闭环
   - 区分数据层和运行层

### 中优先级（建议修正）

4. **CLAUDE.md**
   - 修正项目定位表述
   - 补充"治理 Harness"概念
   - 明确四层体系

5. **AGENTS.md**
   - 统一术语
   - 补充技术能力描述

### 低优先级（可选修正）

6. **repositioning-design.md**
   - 更新为"架构设计说明书"
   - 补充当前已完成的能力
   - 明确阶段边界

---

## 八、总结

### 当前已完成的核心能力

1. **治理内核**：规则加载、匹配、证据生成、记忆沉淀的完整闭环
2. **解释与证据层**：运行时解释、解释输出包、Shadow Mode bridge
3. **宿主桥接层**：Mock adapter + ExplainBridge 基础架构
4. **回归验证**：136+ 测试 + 6 个场景 fixture

### 当前文档的主要偏差

1. **表述过窄**：过度强调"hardness engineering"，弱化"治理核心"
2. **定位不足**：未明确"治理 Harness"概念，缺乏平台化演进描述
3. **术语不统一**："治理规则"、"解释能力"、"宿主桥接"等术语混用

### 后续修正方向

1. **统一目标**：明确"治理 Harness"定位
2. **统一术语**：建立术语表，统一表述
3. **统一体系**：明确四层体系（治理内核/解释证据/宿主桥接/平台演进）
4. **统一阶段**：明确当前已完成的能力和未来规划

---

**审计人**：core-engineer
**审计日期**：2026-04-14
**审计分支**：feat/phase0-1-commit1
