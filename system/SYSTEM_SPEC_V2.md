# SYSTEM_SPEC_V2.md - SaucyClaw 系统总规（V2 草案）

## 一、定位

SaucyClaw 的 V2 目标，不再只是围绕某个特定 agent 工具的工作区骨架。

它更应被定义为：

- 一个通用的 agent hardness engineering 基线
- 一个用于构建强大且受约束的 agent 团队的工程仓库
- 一个可映射到 OpenClaw、Codex、Claude 等不同工作方式的治理与评测底座

## 二、系统目标

SaucyClaw 的目标不只是让多个 agent 一起工作，而是：

1. 让角色边界清晰且长期稳定
2. 让 General Manager 保持先判断后调度
3. 让 specialist 协作而不失控
4. 让 reviewer、evaluator、policy guardian 各司其职
5. 让团队具备评测、回放、回归能力
6. 让方法不绑定单一工具而可迁移

## 三、系统层结构

### 1. Team Layer
- General Manager
- Specialists
- Reviewer
- Evaluator
- Policy Guardian

### 2. Constraint Layer
- 角色边界
- 启动条件
- handoff 纪律
- review 关卡
- 关键动作检查点

### 3. Evaluation Layer
- smoke tasks
- replay scenarios
- rubrics
- reports

### 4. Portability Layer
- 工具映射
- 入口适配
- 工作区适配

## 四、最高原则

1. 先判断任务处理模式，再决定是否执行或调度
2. 多角色协作不是默认动作，而是升级动作
3. 单任务单 owner
4. 关键流转必须留痕
5. review 不代写
6. evaluator 负责评测，不替代交付
7. policy guardian 负责边界提醒，不替代总控
8. 长期行为必须文件化
9. 方法优先，工具其次

## 五、V2 对旧版的升级点

相较于早期版本，V2 重点增加：

- 对 hardness engineering 的明确定位
- evaluator 与 policy guardian 角色
- 评测与回归工作面
- 跨工具的可迁移性说明

## 六、建议落地顺序

1. 先补系统级 hardness 资产
2. 再补角色与评测资产
3. 再逐步替换旧版主文件
4. 最后统一 README 与项目总览
