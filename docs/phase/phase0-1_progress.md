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
