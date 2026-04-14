# Phase 0-1 実施進度

> 创建时间：2026-04-12
> 规则：每完成一个提交，更新此文件

---

## Commit 0 — 过程资料与仓库基线

状态：**已完成**

### 完成内容
- [x] `docs/phase/phase0-1_status.md` — 阶段状态基线
- [x] `docs/phase/phase0-1_repo_baseline.md` — 仓库基线报告
- [x] `docs/phase/phase0-1_implementation_plan.md` — 実施蓝图
- [x] `docs/phase/open_questions.md` — 未決问题清单
- [x] `docs/phase/phase0-1_progress.md` — 本文件
- [x] `docs/adr/ADR-0001-phase0-1-scope.md`
- [x] `docs/adr/ADR-0002-minimal-interfaces.md`
- [x] `docs/adr/ADR-0003-evidence-model.md`
- [x] `docs/adr/ADR-0004-store-and-layout-defaults.md`

### 未完成
- 无

### 风险/偏差
- 无

---

## Commit 1 — 项目骨架与 Schema 样例

状态：**已完成**

### 完成内容
- [x] `pyproject.toml` — 根目录开发配置
- [x] `stores/protocols.py` — 三个 Protocol 抽象
- [x] `core/governance/models.py` — 治理域 dataclass
- [x] `schemas/governance/roles.yaml` — 角色定义样例
- [x] `schemas/governance/task_types.yaml` — 任务类型定义样例
- [x] `schemas/governance/rules.yaml` — 治理规则定义样例
- [x] `tests/fixtures/block_input.yaml` — Block 场景 fixture
- [x] `tests/fixtures/allow_input.yaml` — Allow 场景 fixture

### 未完成
- 无

### 风险/偏差
- 无

---

## Commit 2 — meta_model + governance 最小闭环

状态：已完成

### 完成内容
- [x] meta_model dataclass + loader + validator
- [x] governance dataclass + matcher
- [x] 单元测试（27 tests, 98% coverage）

### 未完成
- 无

### 风险/偏差
- 无

---

## Commit 3 — events + evidence

状态：已完成

### 完成内容
- [x] events normalizer
- [x] evidence generator
- [x] 单元测试（19 tests, 新增模块 100% 覆盖）

### 未完成
- 无

### 风险/偏差
- 无

---

## Commit 4 — file stores + engine

状态：已完成

### 完成内容
- [x] Protocol 抽象
- [x] FileEvidenceStore (JSONL, 按 session_id 分文件)
- [x] FileMemoryStore (JSON, 单记录单文件)
- [x] Engine 编排
- [x] 单元测试（22 tests, 新增模块 95%+ 覆盖）

### 未完成
- 无

### 风险/偏差
- 无（OQ-001/002/004 已決，见 ADR-0004）

---

## Commit 5 — openclaw adapter + integration test

状态：已完成

### 完成内容
- [x] OpenClawHostAdapter (mock)
- [x] 集成测试（Block + Allow，使用真实 YAML 规则）

### 未完成
- 无（Phase 1.1 已接入主流程）

### 风险/偏差
- 无（OQ-001/002/004 已決，见 ADR-0004）

---

## Commit 5 — openclaw adapter + integration test

状态：已完成

### 完成内容
- [x] OpenClawHostAdapter (mock)
- [x] 集成测试（Block + Allow，使用真实 YAML 规则）

### 未完成
- OpenClawHostAdapter.intercept_output 仅为占位実现，真实 hook 尚未接入

### 风险/偏差
- 无（OQ-003 已決，见 ADR-0004）

---

## Phase 0-1 実施口径说明（PR 评审后补充）

> 以下条目来自 PR #8 评审，用于锁定"代码真相"与文档的一致点。

### Memory 状態
- **已完成**：MemoryStore 接口 + FileMemoryStore 默認実现
- **已完成**（Phase 1.1）：治理流程中的记忆沉淀接入

### Allow 证据策略
- Allow 场景（无规则触发）**不生成 evidence**
- 只有规则触发（違規）时才生成 Evidence 记录

### 语义修正
- `Evidence.governance_version` 在 Phase 0-1 固定为 `None`，留待上层注入
- `match_rules()` 返回的是**違規触发**的规则列表（条件不满足 = 違規），非"条件匹配"的规则

---

## Phase 1.1 — Memory 接入主流程

状态：已完成

### 完成内容
- [x] `core/engine/memory_builder.py` — MemoryRecord 模板化構造器
- [x] GovernanceEngine 在决策后写入 MemoryRecord（Block 和 Allow 都写）
- [x] 单元测试（10 tests，覆盖 violation/pass/review 类型）
- [x] 集成测试更新（验证 memory 中可査到对应记录）

### 记忆规则
- 有触发规则 → type="violation"
- 无触发规则 → type="pass"
- Tags：task:<type>, decision:<decision>, source:<source>, rule:<id>（仅 violation）

### 风险/偏差
- 无

---

## Phase 1.2 — 规则扩展与治理语义充実

状态：已完成

### 完成内容
- [x] `schemas/governance/roles.yaml` — 从 2 角色扩展到 5 角色（developer, specialist, reviewer, manager, orchestrator）
- [x] `schemas/governance/task_types.yaml` — 从 C 类单类型扩展到 A-E 五类
- [x] `schemas/governance/rules.yaml` — 从 1 条规则扩展到 5 条：
  - `rule-reviewer-must-differ` → Block（审查者 ≠ 执行者）
  - `rule-specialist-not-direct-output` → Block（direct_output 必须为 false）
  - `rule-handoff-required` → Block（handoff 必须为 true）
  - `rule-restricted-routing` → Block（assignee 必须在允许列表中）
  - `rule-escalate-on-conflict` → Escalate（conflict 必须为 false）
- [x] 单元测试新增 10 个 Phase 1.2 场景（Block/Escalate/Allow/正向路由）
- [x] 集成测试 fixtures 更新（allow_input.yaml 和 block_input.yaml 补充 compliance 字段）

### 规则条件设计原则
- 所有规则条件采用**合规检查风格**：条件通过 = 状態合规，条件不通过 = 違規触发
- 这与 `evaluate_rule()` 和 `match_rules()` 的现有语义保持一致：
  - `evaluate_rule()` 返回 True = 条件全部通过 = 合规
  - `match_rules()` 返回 `evaluate_rule()` 为 False 的规则 = 違規
- 固有限制：AND-only 匹配器无法表达 "NOT (A AND B)" 的条件性适用规则，
  因此每条规则只用单个核心合规条件，角色/任务类型限由 routing 层保证

### 风险/偏差
- AND-only 匹配器限了条件性规则的表达能力（如需 "仅当 task_type=D 时検査 handoff"），
  后续如需支持，可引入 OR/NOT 操符或条件嵌套

---

## Phase 1.3 — 规则适用性层（applies_when）

状态：已完成

### 完成内容
- [x] `core/governance/models.py` — `GovernanceRule` 新增 `applies_when: list[Condition]` 字段
- [x] `core/governance/matcher.py` — `evaluate_rule()` 改为两段式：先判适用性，再判合规性
- [x] `schemas/governance/rules.yaml` — 2 条规则迁移到 `applies_when`：
  - `rule-specialist-not-direct-output`: applies_when `assignee in [specialist, developer]`
  - `rule-handoff-required`: applies_when `task_type == "D"`
- [x] `tests/integration/test_openclaw_adapter.py` — YAML 装载器适配 `applies_when` 解析
- [x] `tests/unit/test_governance_matcher.py` — 5 个新场景（适用/不适用/違規/合规）
- [x] 101 tests 全部通过，pyflakes 零报错

### applies_when 语义
- applies_when 不满足 → 规则不适用 → `evaluate_rule()` 返回 True（不違規）
- applies_when 满足 → 再 eval conditions，决定合规/違規
- applies_when 与 conditions 一样，Phase 1.3 保持 AND-only，不支持 OR/NOT/分组

### 风险/偏差
- 无

---

## Phase 1.4 — 治理规则 YAML 装载统一化

状态：已完成

### 完成内容
- [x] `core/governance/loader.py` — 正式治理 schema 装载器，暴露：
  - `load_rules(path)` — 解析 rules.yaml（含 applies_when）
  - `load_roles(path)` — 解析 roles.yaml
  - `load_task_types(path)` — 解析 task_types.yaml
  - `load_governance(dir)` — 批量加载，返回 GovernanceSchema
  - `SchemaError` — 最小校验错误类型
- [x] `tests/integration/test_openclaw_adapter.py` — 移除手工 `_load_rules()`，改用正式 `load_rules()`
- [x] `tests/unit/test_governance_loader.py` — 14 个测试（真实 YAML / 错误处理 / 解析完整性）
- [x] 116 tests 全部通过，pyflakes 零报错

### 设计原则
- 最小校验：仅检查必填字段和基础类型
- 不存在文件不报错，返回空列表
- 不做复杂 schema 验证框架

### 风险/偏差
- 无

---

## Phase 1.5 — 治理 schema 与运行模型对齐

状态：已完成

### 完成内容
- [x] `core/governance/models.py` — `TaskType` 补上 `allowed_roles` 字段；`RoleDefinition` 补上 `description`
- [x] `core/governance/loader.py` — `load_task_types()` 补装 `allowed_roles`；`load_roles()` 补装 `description`
- [x] `tests/unit/test_governance_alignment.py` — 契约一致性测试（14 个）：
  - YAML 字段 → dataclass 字段完整映射检查
  - C 类 allowed_roles 加载確認
  - specialist can_output_to_ceo 权限確認
  - applies_when 有无规则加载確認
  - blocking_rules 引用完整性检查
  - load_governance() 作为系统入口的集成验证
- [x] `tests/integration/test_openclaw_adapter.py` — 新增 `TestFullSchemaIntegration` 使用 `load_governance()` 作为入口
- [x] 129 tests 全部通过，pyflakes 零报错

### 对齐过程中发现的漏斗
- `TaskType` 缺 `allowed_roles` — 已补
- `RoleDefinition` 缺 `description` — 已补

### 风险/偏差
- 无

---

## Phase 1.6 — 治理规则集的批量 YAML 驱动集成验证

状态：已完成

### 完成内容
- [x] `tests/fixtures/governance_cases/` — 6 个场景 fixture：
  - `block_reviewer_same_as_assignee.yaml`
  - `block_specialist_direct_output.yaml`
  - `allow_specialist_via_reviewer.yaml`
  - `block_d_without_handoff.yaml`
  - `block_a_wrong_assignee.yaml`
  - `escalate_on_conflict.yaml`
- [x] `tests/integration/test_governance_fixtures.py` — 场景驱动批量回归测试：
  - 自动发现所有 governance_cases/*.yaml
  - 每个 fixture 验证 `expected.decision` 和 `expected.matched_rules`
  - 所有场景一次性跑通，支持规则集扩展与回归验证
- [x] `rule-restricted-routing` 补上 `applies_when: task_type == "A"`，避免跨 task_type 泄漏
- [x] `allow_specialist_via_reviewer.yaml` 改回 `assignee: specialist`，真正验证 specialist 正向路径
- [x] `block_specialist_direct_output.yaml` 移除误触发的 `rule-restricted-routing`
- [x] 136 tests 全部通过，pyflakes 零报错

### 验证结构
- 每个 fixture 两段：input + expected
- expected 必填：decision, matched_rules（Allow 时显式写 `[]`）
- 不依赖文件遍历顺序，按文件名排序

### 边界控制
- **0 行 core 代码改动**
- 只新增 fixture 和 1 个集成测试文件
- 完全复用现有 `load_governance` + `GovernanceEngine`

### 风险/偏差
- 无

---

## Phase 1.7 — 规则元数据与可解释性增强

状态：已完成

### 完成内容
- [x] `core/governance/models.py` — `GovernanceRule` 补上 4 个元数据字段：
  - `category`: 规则分类（separation_of_duties / routing / handoff / escalation）
  - `source`: 规则来源文档（ORCHESTRATION.md / MESSAGE_ROUTING.md / SYSTEM_SPEC.md）
  - `rationale`: 规则理由（单行字符串）
  - `risk_level`: 风险等级（low / medium / high）
- [x] `core/governance/loader.py` — `load_rules()` 补装 `.get(field, "")`
- [x] `schemas/governance/rules.yaml` — 所有 5 条规则补全元数据：
  - `rule-reviewer-must-differ`: separation_of_duties, ORCHESTRATION.md, high
  - `rule-specialist-not-direct-output`: routing, SYSTEM_SPEC.md, high
  - `rule-handoff-required`: handoff, ORCHESTRATION.md, medium
  - `rule-restricted-routing`: routing, MESSAGE_ROUTING.md, medium
  - `rule-escalate-on-conflict`: escalation, SYSTEM_SPEC.md, high
- [x] `tests/unit/test_governance_alignment.py` — 新增 `TestRuleMetadataRoundtrip`：
  - `test_category_roundtrip`: 验证 category 和 risk_level
  - `test_rationale_roundtrip`: 验证 rationale 非空且包含关键字段
- [x] 138 tests 全部通过，pyflakes 零报错

### 边界控制
- **0 行 `matcher.py` / `engine.py` 改动**
- 元数据不影响执行逻辑，仅增强可解释性
- 所有字段默认空字符串，保持向后兼容

### 价值
- 规则分类可过滤、分组、统计
- 来源文档支持追溯
- 理由字段支持解释"为什么有这条规则"
- 风险等级支持区分规则重要程度
- 为 Memory summary、debug 输出、管理台 / 可视化打基础

### 风险/偏差
- 无

---

## Phase 1.8 — 规则元数据运行时解释能力

状态：已完成

### 完成内容
- [x] `core/governance/explainer.py` — 解释构造器，包含：
  - `RuleExplanation` dataclass（rule_id, category, risk_level, source, rationale）
  - `explain_matched_rules()`：将 `matched_rules` 转换为结构化解释列表
- [x] `tests/unit/test_governance_explainer.py` — 5 个单元测试：
  - `test_explain_single_matched_rule`：单规则解释
  - `test_explain_multiple_matched_rules`：多规则解释
  - `test_explain_no_matched_rules`：无匹配时返回空列表
  - `test_explain_without_lookup`：不传 lookup 表时的降级行为
  - `test_explanation_fields_completeness`：验证所有字段完整非空
- [x] `tests/unit/test_governance_alignment.py` — 补上 `test_source_roundtrip`，闭合 Phase 1.7 的小缺口
- [x] 144 tests 全部通过（+6 新测试），pyflakes 零报错

### 设计原则
- **独立 helper**：explainer 是纯函数，不修改 `matcher.py` / `engine.py`
- **保持克制**：未修改 `GateResult` 结构，避免过度设计
- **向后兼容**：所有解释字段非空（Phase 1.7 已保证元数据完整）
- **按需扩展**：lookup 表可选，支持未来补充额外信息

### 解释能力价值
- **运行时可用**：匹配规则时可即时获取结构化解释，而非仅规则 ID
- **调试友好**：解释包含分类、风险、来源、理由，便于定位问题
- **下游消费基础**：为后续 Memory summary 增强、debug 输出、管理台解释打下基础
- **语义闭环**：Phase 1.7 的元数据真正浮出到运行时，完成"静态→动态"转化

### 风险/偏差
- 无（保持克制，未侵入核心逻辑）

---
## Phase 1.9 — 解释信息接入运行时输出面

状态：已完成

### 完成内容
- [x] `core/governance/explainer_bundle.py` — 解释输出打包器，包含：
  - `ExplanationBundle` dataclass（decision, matched_rule_ids, explanations, readable_summary, suggestions, risk_summary）
  - `bundle_explanations()`：输入 `matched_rule_ids`（来自 GateResult）+ lookup 表，输出完整解释包
- [x] `tests/unit/test_governance_explainer_bundle.py` — 8 个单元测试：
  - `test_bundle_single_rule`：单规则打包（所有字段非空）
  - `test_bundle_multiple_rules`：多规则打包（summaries 合并）
  - `test_bundle_no_matched_rules`：无匹配降级
  - `test_risk_summary_computation`：风险摘要计算（取最高风险）
  - `test_unknown_rule_id_degradation`：未知 rule_id 降级（不崩溃）
  - `test_explanation_bundle_fields_completeness`：字段完整性验证
  - `test_bundle_with_escalate_decision`：Escalate 决策打包
  - `test_decision_text_mapping`：决策类型到可读文本映射
- [x] 152 tests 全部通过（+8 新测试），pyflakes 零报错

### 设计原则
- **外围 helper**：不修改 `GateResult` / `matcher.py` / `engine.py`
- **完整包装**：包含解释结构 + 可读文本 + 建议 + 风险等级摘要
- **独立文件**：`explainer_bundle.py` 与 `explainer.py` 平级
- **可选使用**：不影响现有流程，只在需要时调用
- **直接接入**：`bundle_explanations()` 直接接受 `matched_rule_ids`（来自 GateResult），无需调用方转换
- **降级安全**：未知 rule_id 直接忽略，不崩溃

### 解释输出包字段
| 字段 | 来源 | 说明 |
|------|------|------|
| `decision` | GateResult.decision | 决策结果 |
| `matched_rule_ids` | GateResult.matched_rules | 匹配的规则 ID 列表 |
| `explanations` | explain_matched_rules() | RuleExplanation 列表 |
| `readable_summary` | 自动生成 | 可读摘要（基于 decision + risk_level + category + rationale，不硬编码 task_type） |
| `suggestions` | GateResult.suggestions | 建议列表 |
| `risk_summary` | 自动生成 | 风险等级摘要（取最高风险：high > medium > low） |

### 可读摘要规则
- **无匹配**：`未触发治理规则`
- **单规则**：`触发{decision}（{risk_level}/{category}）：{rationale}`
- **多规则**：`触发{decision}（{最高风险}，{数量}条规则）：{categories}`

### 风险摘要规则
- 有 `high` → `高风险规则触发`
- 否则有 `medium` → `中风险规则触发`
- 否则有 `low` → `低风险规则触发`
- 无匹配 → `未触发风险规则`

### 价值体现
- **解释信息真正出现在运行结果旁边**：不再只是"可调用 helper"，而是完整的输出包
- **调试友好**：可读摘要 + 风险摘要 + 完整解释结构，便于日志记录和调试输出
- **下游消费基础**：为未来接入 Memory/管理台提供标准格式
- **语义闭环**：完成从"可调用 helper"到"真实输出面"的转化

### 使用示例
```python
result = engine.process_event(raw_event)
bundle = bundle_explanations(
    decision=result.decision,
    matched_rule_ids=result.matched_rules,  # 直接从 GateResult 来
    schema_rules_lookup={r.id: r for r in schema.rules},
    suggestions=result.suggestions,
)

print(bundle.readable_summary)
# "触发阻断（high/separation_of_duties）：防止审查者与执行者同一人，确保独立审查"
print(bundle.risk_summary)
# "高风险规则触发"
```

### 风险/偏差
- 无（完全外围 helper，不影响核心决策链）

---

## Phase 2.0 — 解释输出接入 Adapter 边界（Shadow Mode）

状态：已完成

### 完成内容
- [x] `adapters/openclaw/explain_bridge.py` — 解释桥接器，包含：
  - `AdapterExplainOutput` dataclass（decision, matched_rules, explanation_bundle, raw_result）
  - `ExplainBridge` 桥接器：
    - `__init__(schema_rules_lookup, enable=False)`：初始化，支持开关
    - `enable_shadow_mode()` / `disable_shadow_mode()`：运行时切换
    - `enhance_output(result: GateResult)`：生成桥接输出
- [x] `tests/unit/test_explain_bridge.py` — 7 个单元测试

### 关键设计点
- **外围桥接**：不修改 `adapter.write_back()` 契约，仍接受 `GateResult`
- **Shadow Mode**：默认关闭（enable=False），显式开启
- **伴随输出**：`enhance_output()` 生成额外的解释包，原始 `GateResult` 保持完整

### 风险/偏差
- 无（完全外围桥接，不影响 adapter 核心契约）

---

## M1 — 宿主接入可交付包

状态：**已完成**

### 概述

从 Phase 2.0 到 Phase 2.6 的外围接入能力已收口为一个可交付包：
**治理决策、解释输出、运行摘要、调试渲染与接入契约已形成闭环。**

### 完成内容

#### 结构收口（Phase 2.2 / 2.3 / 2.4）
- [x] `adapters/openclaw/shadow_runtime.py` — Shadow Mode 外围接入模板
- [x] `adapters/openclaw/hook_contract.py` — 4 个 Protocol 定义外部接入契约
- [x] `adapters/openclaw/__init__.py` — 完整导出所有公开 API
- [x] `ExplainBridge.enabled` — 补公开只读 property，与 Protocol 对齐

#### 可观测性（Phase 2.5 / 2.6）
- [x] `adapters/openclaw/runtime_trace.py` — frozen dataclass + build_runtime_trace 纯函数
- [x] `adapters/openclaw/debug_render.py` — render_shadow_run 调试输出渲染器

#### 示例与文档
- [x] `examples/openclaw_shadow_runtime_example.py` — 统一为 RuntimeTrace + render_shadow_run
- [x] `docs/integration/openclaw_shadow_runtime.md` — 宿主接入说明文档

#### 测试证明
- [x] `tests/unit/test_shadow_runtime.py` — 5 个测试（无 bridge / bridge 关闭 / bridge 开启 / Allow / write_back_log）
- [x] `tests/unit/test_hook_contract.py` — 8 个测试（Protocol shape / example smoke / 组件兼容性）
- [x] `tests/unit/test_hook_contract_conformance.py` — 20 个测试（4 组件 × 运行时一致性 + 5 个 example 验证）
- [x] `tests/unit/test_runtime_trace.py` — 6 个测试（Block / Allow / 无 bridge / bridge 关闭 / frozen）
- [x] `tests/unit/test_debug_render.py` — 3 个测试（Block / Allow / 无 bridge）

### 保证
- **零 core 改动**：所有模块位于 `adapters/openclaw/`
- **零 adapter 契约改动**：`write_back(GateResult)` 签名不变
- **零真实 hook 接入**：基于 mock adapter 的最小闭环

### 风险/偏差
- 当前仍为 mock adapter，真实 OpenClaw hook 接入需后续完成
