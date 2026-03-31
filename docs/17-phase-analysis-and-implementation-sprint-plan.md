# SaucyClaw 分阶段需求分析与落地开发计划（Sprint Plan）

- 日期：2026-03-31
- 目标：把 `docs/16-evolution-todo-and-task-stubs-2026-03-31.md` 从任务清单推进为可执行开发迭代。

---

## Sprint 0（准备与基线）

### 需求分析
- 明确 P0 四项的输入/输出与依赖。
- 定义统一完成标准（DoD）：文档对齐、模板可复用、回归可追踪。

### 开发动作
1. 建立状态看板（TODO/DOING/DONE）。
2. 定义每个任务的最小 PR 范围。
3. 设定每次提交必须附带的验证项。

### 产出物
- 更新后的 `docs/16`（状态化、批次化）。
- 本文件（Sprint 执行图）。

---

## Sprint 1（P0-01 + P0-02）

### 目标
完成主叙事统一 + 版本生效机制，确保“先有一致裁决源，再继续扩展”。

### 涉及文件
- `README.md`
- `CLAUDE.md`
- `system/SYSTEM_SPEC.md`
- `system/SYSTEM_SPEC_V2.md`
- `system/ORCHESTRATION.md`
- `system/ORCHESTRATION_V2.md`
- `system/STANDARDS.md`
- `system/STANDARDS_V2.md`

### 验收标准
1. 各入口对项目定位一致。
2. V1/V2 生效规则可一眼识别。
3. V1/V2 差异有对照入口。

---

## Sprint 2（P0-03）

### 目标
完成 A-E 编排模板化与门禁化，打通“规范 -> 可执行”。

### 涉及文件
- `templates/`
- `system/ORCHESTRATION.md`
- `examples/first-run-task.md`

### 验收标准
1. 提供 task judgement / stage contract / handoff / closure check 模板。
2. 缺字段不可推进成为明确规则。
3. 示例可回放。

---

## Sprint 3（P0-04）

### 目标
建立主干变更的回归门禁机制。

### 涉及文件
- `evals/README.md`
- `evals/rubrics/team-hardness-rubric.md`
- `evals/reports/`

### 验收标准
1. 触发条件清楚。
2. 报告模板可用。
3. rubric 分值映射到行动决策。

---

## Sprint 4（P1）

### 目标
风险治理与迁移治理硬化。

### 涉及文件
- `system/FAILURE_MODES.md`
- `docs/13-portability-and-mapping.md`
- `agents/policy-guardian/AGENTS.md`

### 验收标准
1. 失效模式矩阵化并可复盘。
2. core/adapter 文件边界清晰。
3. OpenClaw 兼容安全基线明确。

---

## Sprint 5（P2）

### 目标
持续运营化：onboarding 回放 + 趋势分析。

### 涉及文件
- `examples/first-run-task.md`
- `docs/`
- `evals/reports/`

### 验收标准
1. 新代理 30 分钟完成一次回放。
2. 季度趋势报告机制可执行。

---

## 风险与控制

1. 风险：只补外围文档，主干不改。
   - 控制：每 Sprint 至少包含一个主干文件改动任务。
2. 风险：任务过大导致长期不落地。
   - 控制：每个任务保证可最小独立 PR。
3. 风险：评测流程写了但没人跑。
   - 控制：把回归报告作为主干改动的交付物。

