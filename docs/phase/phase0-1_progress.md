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

状态：未开始

### 完成内容
- [ ] events normalizer
- [ ] evidence generator
- [ ] 单元测试

### 未完成
- 无

### 风险/偏差
- 无

---

## Commit 4 — file stores + engine

状态：未开始

### 完成内容
- [ ] Protocol 抽象
- [ ] FileEvidenceStore
- [ ] FileMemoryStore
- [ ] Engine 编排
- [ ] 单元测试

### 未完成
- 无

### 风险/偏差
- 无（OQ-001/002/004 已决，见 ADR-0004）

---

## Commit 5 — openclaw adapter + integration test

状态：未开始

### 完成内容
- [ ] OpenClawHostAdapter
- [ ] 集成测试（Block + Allow）

### 未完成
- 无

### 风险/偏差
- 无（OQ-003 已决，见 ADR-0004）
