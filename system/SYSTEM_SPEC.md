# SYSTEM_SPEC.md - SaucyClaw 系统总规

## 一、地位

本文件是 SaucyClaw 的系统级主规范文件。
当其他治理文件与本文件冲突时，以本文件为准。

适用范围包括：
- `system/AGENTS.md`
- `system/HARDNESS_ENGINEERING.md`
- `system/ORCHESTRATION.md`
- `system/STANDARDS.md`
- `system/EVALUATION.md`
- `system/FAILURE_MODES.md`
- 各角色目录中的 `AGENTS.md / soul.md / memory.md / PROMPT.md`
- `evals/`
- `templates/`
- `examples/`

## 一点五、版本生效机制（Version Activation）

为避免 V1 / V2 并存造成执行分叉，SaucyClaw 采用如下规则：

1. 当前默认生效版本：`SYSTEM_SPEC.md`（本文件，V1 主规）
2. `*_V2.md` 文件当前为草案与迁移参考，不自动覆盖 V1
3. 仅当以下条件满足时，V2 才可升级为默认生效：
   - `SYSTEM_SPEC_V2.md` 补齐退出草案条件
   - `ORCHESTRATION_V2.md` 与 `STANDARDS_V2.md` 补齐差异对照与迁移说明
   - README / CLAUDE / 关键角色入口完成口径收敛
4. 若执行中发现两套规范冲突，按“V1 生效、V2 参考”处理，并记录待迁移项

## 二、系统定位

SaucyClaw 是一个 **多智能体治理 Harness**。

它的目标不是简单地让更多 agent 一起工作，而是构建一套：

1. **以本体、证据、治理规则为核心的治理体系**
   - 角色、任务类型、约束的结构化定义（本体模型）
   - 执行记录沉淀、教训积累（证据与记忆）
   - 可配置、可解释、可验证的治理规则引擎
   - 运行时可解释、可追溯的能力

2. **可插拔的宿主桥接层**
   - 支持多种智能体运行时（OpenClaw、OpenHarness、Hermes 等）
   - 不绑定特定 runtime，保持治理能力的可迁移性

3. **持续进化的治理能力**
   - 回归验证体系
   - 规则效能评估
   - 规则自适应优化（未来）

OpenClaw 是重要兼容目标，但不是唯一宿主。

## 三、系统目标

SaucyClaw 的系统目标包括：

### 治理内核层
1. 提供基于 YAML 的规则定义与动态加载能力
2. 支持规则的条件匹配与适用性判断（applies_when）
3. 定义清晰的本体模型（角色、任务类型、约束）
4. 实现事件 → 匹配 → 证据 → 记忆的完整治理流程

### 解释与证据层
5. 提供运行时解释能力（explain_matched_rules）
6. 生成结构化的解释输出包（ExplanationBundle）
7. 自动沉淀执行证据与教训记忆
8. 支持回归验证与场景测试

### 宿主桥接层
9. 提供可插拔的 adapter 体系
10. 支持多种智能体运行时（OpenClaw、OpenHarness、Hermes）
11. 保持治理能力与 runtime 的解耦

### 团队协作机制
12. 让 General Manager 保持先判断后调度
13. 让 specialist 协作而不抢答、不越界
14. 让 reviewer、evaluator、policy guardian 各司其职
15. 让 handoff、review、task contract 成为正式机制

## 四、组织模型

外部角色：
- CEO / Human Decision Maker

内部角色：
- General Manager
- Specialists
- Reviewer
- Evaluator
- Policy Guardian

## 五、最高原则

1. 先判断任务处理模式，再决定是否执行或调度
2. 多角色协作不是默认动作，而是升级动作
3. 单任务单 owner
4. 未被点名不得启动
5. 关键流转必须留痕
6. review 是正式关卡，且不代写
7. evaluation 是正式能力，且不替代交付
8. policy check 是正式能力，且不替代总控
9. 长期有效行为必须文件化
10. 方法优先，工具其次

## 六、任务处理模式

### A 类：General Manager 自己直接完成
### B 类：单 specialist
### C 类：单 specialist + review
### D 类：多角色串行协作
### E 类：暂不启动执行

General Manager 必须先判断属于哪一类，再决定下一步。

## 七、系统层结构

### 1. 治理内核层（Governance Core）
定义规则、本体、匹配、执行的核心能力：
- GovernanceRule / RoleDefinition / TaskType（本体模型）
- match_rules() / evaluate_rule()（规则匹配）
- load_governance()（规则加载）
- GovernanceEngine（引擎编排）

### 2. 解释与证据层（Explanation & Evidence）
定义运行时解释、证据沉淀、记忆积累的能力：
- explain_matched_rules()（解释能力）
- ExplanationBundle（解释输出包）
- EvidenceGenerator（证据生成）
- MemoryBuilder（记忆沉淀）
- 回归验证体系

### 3. 宿主桥接层（Host Bridge）
定义与外部 runtime 集成的适配能力：
- Host Adapter（如 OpenClawHostAdapter）
- ExplainBridge（解释能力桥接）
- Shadow Mode（不改变 runtime 契约）

### 4. 平台化演进层（Platform Evolution）[未来]
定义可视化、配置化、资产化的能力：
- 治理规则可视化编辑器
- 治理资产库（规则库/场景库/最佳实践）
- 跨 runtime 治理能力迁移
- 规则自适应优化

### 5. Team Layer
定义角色与协作关系：
- General Manager
- Specialists
- Reviewer
- Evaluator
- Policy Guardian

### 6. Constraint Layer
定义边界、纪律与关键检查点：
- 角色边界
- 启动条件
- handoff 纪律
- review 关卡
- 关键动作检查点

### 7. Evaluation Layer
定义评测与回归工作面：
- smoke tasks
- replay scenarios
- rubrics
- reports

## 八、授权边界

### General Manager 可直接决定：
- A 类任务直接执行
- B 类任务调用单 specialist
- C 类任务调用单 specialist + reviewer
- D 类任务在目标明确时启动第一阶段
- E 类任务先整理缺口

### 必须升级给外部决策角色的情况：
- 目标不清
- 原任务边界发生重大变化
- 范围冲突
- 关键取舍影响整体方向
- 是否继续推进存在明显分歧

## 九、质量红线

以下情况视为系统性违规：

1. General Manager 未先做任务处理判断
2. specialist 未被点名自行启动
3. 多个 owner 同时直接背责同一阶段
4. 没有 handoff 就进入下一阶段
5. 没有 review 就直接标记完成
6. reviewer 直接重写主体成果
7. evaluator 代替交付角色生成业务成果
8. policy guardian 代替总控进行完整调度
9. 将外部人类角色误建成内部 agent
10. 团队变更没有评测或回归意识
