# SaucyClaw 进化 To-Do 与 Task Stubs（迭代版，2026-03-31）

> 执行原则：先主干后枝叶；先治理后扩展；先可验证再可叙述。  
> 本版新增：分阶段需求分析、落地开发批次、验收门禁与状态跟踪。

---

## 0. 阶段化执行模型（从分析到开发）

### Phase A：需求分解（Analysis）
- 输出：问题定义、影响范围、依赖关系、验收标准。
- 通过门槛：每项工作都有“证据文件 + 验收条件”。

### Phase B：方案细化（Design）
- 输出：文件级改动清单、模板草案、回归点。
- 通过门槛：每项改动可最小独立提交。

### Phase C：落地开发（Implementation）
- 输出：主文件改动、模板补齐、示例回放链路。
- 通过门槛：关键路径可演示（判断→执行→review/eval→收口）。

### Phase D：回归验收（Validation）
- 输出：评测报告、回归结论、剩余风险。
- 通过门槛：达到门禁分数或明确修订动作。

---

## 1. 批次化开发计划（建议按 PR 分批）

- **Batch-1（P0 主叙事与版本治理）**：P0-01, P0-02
- **Batch-2（P0 编排模板化）**：P0-03
- **Batch-3（P0 评测门禁）**：P0-04
- **Batch-4（P1 风险与迁移硬化）**：P1-01, P1-02, P1-03
- **Batch-5（P2 运营化）**：P2-01, P2-02

---

## 2. 状态看板（可持续更新）

| ID | 任务 | 优先级 | 状态 | 依赖 | 产出物 |
|---|---|---|---|---|---|
| P0-01 | 统一主叙事口径 | P0 | DOING | 无 | README/CLAUDE/SYSTEM_SPEC 对齐 |
| P0-02 | V1/V2 生效机制 | P0 | DOING | P0-01 | system 版本治理段落 |
| P0-03 | A-E 模板化与字段门禁 | P0 | DOING | P0-02 | templates + orchestration 更新 |
| P0-04 | 主干回归门禁 | P0 | TODO | P0-03 | eval gate + report 模板 |
| P1-01 | FAILURE_MODES 矩阵化 | P1 | TODO | P0-04 | 风险控制矩阵 |
| P1-02 | core/adapter 文件归属矩阵 | P1 | TODO | P0-02 | portability 边界契约 |
| P1-03 | OpenClaw 兼容安全基线 | P1 | TODO | P1-02 | 兼容实施指南 |
| P2-01 | onboarding 回放路径标准化 | P2 | TODO | P0-04 | 30 分钟验证路径 |
| P2-02 | 季度趋势报告机制 | P2 | TODO | P2-01 | 趋势报告模板 |

---

## 3. P0 任务（主干优先）

问题：入口文档对项目定位口径不完全一致，影响后续执行一致性。  
task-stub{title="P0-01 统一主叙事口径（README/CLAUDE/SYSTEM_SPEC）"}
1. 在 `README.md`、`CLAUDE.md`、`system/SYSTEM_SPEC.md` 对齐项目定位描述。
2. 统一表达为：通用 hardness baseline + OpenClaw-compatible（非绑定）。
3. 在 `CLAUDE.md` 增加“语义裁决来源”为 `system/SYSTEM_SPEC.md` 的声明。
4. 增加文档一致性检查清单并放入 `docs/`。
5. 验收：三处文件定位无冲突，术语一致。

问题：V1/V2 并存但缺少明确生效机制，容易引发执行分叉。  
task-stub{title="P0-02 建立系统主规 V1/V2 生效与迁移机制"}
1. 在 `system/SYSTEM_SPEC.md` 增加“当前生效版本”和“切换触发条件”。
2. 在 `system/SYSTEM_SPEC_V2.md` 增加“退出草案条件”。
3. 给 `ORCHESTRATION` 与 `STANDARDS` 的 V1/V2 加差异对照节。
4. 给出单一引用入口，避免执行时同时引用两套规范。
5. 验收：执行者可在 1 分钟内判断当前应遵循版本。

问题：A-E 编排规则尚未完全字段化，难以程序化检查。  
task-stub{title="P0-03 A-E 编排模板化与字段门禁"}
1. 在 `templates/` 增加 `task-judgement`、`stage-contract`、`handoff`、`closure-check` 模板。
2. 在 `system/ORCHESTRATION.md` 声明最小必填字段。
3. 将“缺关键字段”定义为不可进入下一阶段。
4. 更新 `examples/first-run-task.md` 提供完整示例。
5. 验收：D 类任务可按模板完整回放。

问题：评测有 rubric 但缺少“主干变更必回归”的制度化门禁。  
task-stub{title="P0-04 主干改动回归门禁（Eval Gate）"}
1. 在 `evals/README.md` 增加主干改动触发回归规则。
2. 在 `evals/reports/` 增加标准报告模板。
3. 将 `team-hardness-rubric` 的分值映射到动作（通过/修订/阻断）。
4. 将回归报告纳入每次主干修改的交付物。
5. 验收：每次主干改动均有报告留痕。

---

## 4. P1 任务（机制硬化）

问题：失效模式是描述清单，缺少机制化的责任链与处置策略。  
task-stub{title="P1-01 FAILURE_MODES 矩阵化"}
1. 为每个 failure mode 增加触发信号、检测时点、责任角色、处置动作。
2. 与 reviewer / evaluator / policy guardian 输出模板做映射。
3. 在 `evals/scenarios/` 增加失效复发回放样例。
4. 验收：每个失效模式可被检测并可被处置。

问题：可迁移性原则存在，但缺少文件级 core/adapter 边界契约。  
task-stub{title="P1-02 定义 Core 与 OpenClaw Adapter 的文件归属矩阵"}
1. 在 `docs/13-portability-and-mapping.md` 增加文件级归属矩阵。
2. 标注哪些文件允许出现 OpenClaw 专有语义。
3. 标注哪些文件必须保持工具无关。
4. 新增“新工具接入流程”节（限定改动范围在 adapter 层）。
5. 验收：新增工具接入时核心治理文件无需改语义。

问题：OpenClaw 兼容实现缺少安全基线说明。  
task-stub{title="P1-03 OpenClaw 兼容实施安全基线"}
1. 文档化 workspace 与 sandbox 的关系（避免误把 workspace 当硬隔离）。
2. 给出 trusted / untrusted agent 的最小权限策略模板。
3. 给出 tools deny 与审批策略示例。
4. 验收：兼容层具备可复用的最低安全配置指引。

---

## 5. P2 任务（运营与持续演进）

问题：新成员进入后的首轮验证路径尚不够标准化。  
task-stub{title="P2-01 Onboarding 回放路径标准化"}
1. 扩展 `examples/first-run-task.md` 增加失败样例与期望输出骨架。
2. 在 `docs/` 增加 30 分钟 onboarding 验证步骤。
3. 将输出映射到 rubric 各评分项。
4. 验收：新代理 30 分钟内可完成一次标准回放与评分。

问题：缺少长期趋势视角，难判断系统硬度是否持续提升。  
task-stub{title="P2-02 季度 Hardness 趋势报告机制"}
1. 每季度汇总 rubric 分数、失效复发率、回归通过率。
2. 输出趋势图与主要根因。
3. 对下季度主干治理目标给出可验证指标。
4. 验收：连续两季度可对比趋势。

---

## 6. 开发验收清单（每个 Batch 都要过）

1. 改动是否触及主干文件（`system/`, `README.md`, `CLAUDE.md`）？
2. 是否补充了对应模板/示例/验证路径？
3. 是否记录了回归报告位置？
4. 是否更新状态看板（TODO -> DOING -> DONE）？

---

## 7. 执行日志（Iteration Log）

- 2026-03-31（第 1 次落地）：
  - 已开始执行 Batch-1；
  - 已更新 README / CLAUDE 的语义收敛说明；
  - 已在 SYSTEM_SPEC 增加 V1/V2 生效机制；
  - 已在 SYSTEM_SPEC_V2 增加退出草案条件；
  - 已在 ORCHESTRATION / STANDARDS 增加 V1 生效与 V2 参考标记。

- 2026-03-31（第 2 次落地）：
  - 已开始执行 Batch-2；
  - 已将 ORCHESTRATION 的阶段契约升级为“最小必填 + 缺失阻断”；
  - 已补充 task judgement / stage contract / handoff / closure check 模板；
  - 已扩展 first-run 示例，加入任务判断骨架、阶段验收与模板回放指引。
