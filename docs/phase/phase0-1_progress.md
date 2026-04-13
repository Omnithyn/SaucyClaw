# Phase 0-1 实施进度

> 创建时间：2026-04-12
> 规则：每完成一个提交，更新此文件

---

## Commit 0 — 过程资料与仓库基线

状态：**已完成**

### 完成内容
- [x] `docs/phase/phase0-1_status.md` — 阶段状态基线
- [x] `docs/phase/phase0-1_repo_baseline.md` — 仓库基线报告
- [x] `docs/phase/phase0-1_implementation_plan.md` — 实施蓝图
- [x] `docs/phase/open_questions.md` — 未决问题清单
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
- 无（OQ-001/002/004 已决，见 ADR-0004）

---

## Commit 5 — openclaw adapter + integration test

状态：已完成

### 完成内容
- [x] OpenClawHostAdapter (mock)
- [x] 集成测试（Block + Allow，使用真实 YAML 规则）

### 未完成
- 无（Phase 1.1 已接入主流程）

### 风险/偏差
- 无（OQ-001/002/004 已决，见 ADR-0004）

---

## Commit 5 — openclaw adapter + integration test

状态：已完成

### 完成内容
- [x] OpenClawHostAdapter (mock)
- [x] 集成测试（Block + Allow，使用真实 YAML 规则）

### 未完成
- OpenClawHostAdapter.intercept_output 仅为占位实现，真实 hook 尚未接入

### 风险/偏差
- 无（OQ-003 已决，见 ADR-0004）

---

## Phase 0-1 实施口径说明（PR 评审后补充）

> 以下条目来自 PR #8 评审，用于锁定"代码真相"与文档的一致点。

### Memory 状态
- **已完成**：MemoryStore 接口 + FileMemoryStore 默认实现
- **已完成**（Phase 1.1）：治理流程中的记忆沉淀接入

### Allow 证据策略
- Allow 场景（无规则触发）**不生成 evidence**
- 只有规则触发（违规）时才生成 Evidence 记录

### 语义修正
- `Evidence.governance_version` 在 Phase 0-1 固定为 `None`，留待上层注入
- `match_rules()` 返回的是**违规触发**的规则列表（条件不满足 = 违规），非"条件匹配"的规则

---

## Phase 1.1 — Memory 接入主流程

状态：已完成

### 完成内容
- [x] `core/engine/memory_builder.py` — MemoryRecord 模板化构造器
- [x] GovernanceEngine 在决策后写入 MemoryRecord（Block 和 Allow 都写）
- [x] 单元测试（10 tests，覆盖 violation/pass/review 类型）
- [x] 集成测试更新（验证 memory 中可查到对应记录）

### 记忆规则
- 有触发规则 → type="violation"
- 无触发规则 → type="pass"
- Tags：task:<type>, decision:<decision>, source:<source>, rule:<id>（仅 violation）

### 风险/偏差
- 无

---

## Phase 1.2 — 规则扩展与治理语义充实

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
- 所有规则条件采用**合规检查风格**：条件通过 = 状态合规，条件不通过 = 违规触发
- 这与 `evaluate_rule()` 和 `match_rules()` 的现有语义保持一致：
  - `evaluate_rule()` 返回 True = 条件全部通过 = 合规
  - `match_rules()` 返回 `evaluate_rule()` 为 False 的规则 = 违规
- 固有限制：AND-only 匹配器无法表达 "NOT (A AND B)" 的条件性适用规则，
  因此每条规则只用单个核心合规条件，角色/任务类型限定由 routing 层保证

### 风险/偏差
- AND-only 匹配器限制了条件性规则的表达能力（如需 "仅当 task_type=D 时检查 handoff"），
  后续如需支持，可引入 OR/NOT 操作符或条件嵌套

---

## Phase 1.3 — 规则适用性层（applies_when）

状态：已完成

### 完成内容
- [x] `core/governance/models.py` — `GovernanceRule` 新增 `applies_when: list[Condition]` 字段
- [x] `core/governance/matcher.py` — `evaluate_rule()` 改为两段式：先判适用性，再判合规性
- [x] `schemas/governance/rules.yaml` — 2 条规则迁移到 `applies_when`：
  - `rule-specialist-not-direct-output`: applies_when `assignee in [specialist, developer]`
  - `rule-handoff-required`: applies_when `task_type == "D"`
- [x] `tests/integration/test_openclaw_adapter.py` — YAML 加载器适配 `applies_when` 解析
- [x] `tests/unit/test_governance_matcher.py` — 5 个新场景（适用/不适用/违规/合规）
- [x] 101 tests 全部通过，pyflakes 零报错

### applies_when 语义
- applies_when 不满足 → 规则不适用 → `evaluate_rule()` 返回 True（不违规）
- applies_when 满足 → 再 eval conditions，决定合规/违规
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