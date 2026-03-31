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

SaucyClaw 是一个 **agent hardness engineering 基线工程**。

它的目标不是简单地让更多 agent 一起工作，而是构建一套：

1. 强大且受约束的 agent 团队
2. 角色边界清晰的协作机制
3. 可评测、可回放、可回归的团队工程能力
4. 可映射到不同 agent 工具链的治理与方法底座

OpenClaw 是重要兼容目标，但不是唯一宿主。

## 三、系统目标

SaucyClaw 的系统目标包括：

1. 让 General Manager 保持先判断后调度
2. 让 specialist 协作而不抢答、不越界
3. 让 reviewer、evaluator、policy guardian 各司其职
4. 让 handoff、review、task contract 成为正式机制
5. 让评测与回归成为团队工程的一部分
6. 让方法优先于工具而沉淀下来

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

### 1. Team Layer
定义角色与协作关系：
- General Manager
- Specialists
- Reviewer
- Evaluator
- Policy Guardian

### 2. Constraint Layer
定义边界、纪律与关键检查点：
- 角色边界
- 启动条件
- handoff 纪律
- review 关卡
- 关键动作检查点

### 3. Evaluation Layer
定义评测与回归工作面：
- smoke tasks
- replay scenarios
- rubrics
- reports

### 4. Portability Layer
定义跨工具映射与入口适配：
- OpenClaw
- Codex
- Claude
- 其他 agent 工作方式

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
