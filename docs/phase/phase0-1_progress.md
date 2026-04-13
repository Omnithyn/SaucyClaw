# Phase 0-1 实施进度

> 创建时间：2026-04-12
> 规则：每完成一个提交，更新此文件

---

## Commit 0 — 过程资料与仓库基线

状态：**进行中**

### 完成内容
- [x] `docs/phase/phase0-1_status.md` — 阶段状态基线
- [x] `docs/phase/phase0-1_repo_baseline.md` — 仓库基线报告
- [x] `docs/phase/phase0-1_implementation_plan.md` — 实施蓝图
- [x] `docs/phase/open_questions.md` — 未决问题清单
- [x] `docs/phase/phase0-1_progress.md` — 本文件
- [x] `docs/adr/ADR-0001-phase0-1-scope.md`
- [x] `docs/adr/ADR-0002-minimal-interfaces.md`
- [x] `docs/adr/ADR-0003-evidence-model.md`

### 未完成
- 无

### 风险/偏差
- 无

---

## Commit 1 — 项目骨架与 Schema 样例

状态：未开始

### 完成内容
- [ ] 创建目录结构
- [ ] 增加基础 YAML schema 样例
- [ ] 新增 dataclass 骨架
- [ ] 新增测试 fixture

### 未完成
- 无

### 风险/偏差
- 待确认 pyproject.toml 位置（见 OQ-006）

---

## Commit 2 — meta_model + governance 最小闭环

状态：未开始

### 完成内容
- [ ] meta_model dataclass + loader + validator
- [ ] governance dataclass + matcher
- [ ] 单元测试

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
- 待确认 evidence 文件分维度方式（见 OQ-002）
- 待确认 MemoryStore 默认实现（见 OQ-001）
- 待确认 GateResult.suggestions 类型（见 OQ-004）

---

## Commit 5 — openclaw adapter + integration test

状态：未开始

### 完成内容
- [ ] OpenClawHostAdapter
- [ ] 集成测试（Block + Allow）

### 未完成
- 无

### 风险/偏差
- 待确认挂接点方式（见 OQ-003）
