# HARDNESS_ENGINEERING.md - 智能体 Hardness Engineering 核心说明

## 一、定位

SaucyClaw 不应只被理解为 OpenClaw 友好的多智能体骨架。
它更应该被理解为一个 Agent Hardness Engineering 项目基线：

- 用于构建强大但受约束的 agent 团队
- 用于沉淀角色边界、调度纪律、评测方法与失效防控
- 用于在不同 agent runtime 或 orchestrator 上迁移与复用
- 用于让多智能体系统既能协作，又不失控

OpenClaw 是当前兼容的重要目标之一，但不是唯一宿主。

## 二、什么是 Hardness Engineering

这里的 Hardness，不是指更强模型本身，而是指系统层面的：

1. 边界硬度：角色不越权、不串岗、不抢答
2. 流程硬度：不跳过判断、handoff、review、收口
3. 约束硬度：高风险动作必须经过约束检查
4. 证据硬度：关键结论可追踪、可审计、可回放
5. 协作硬度：多角色协作时不失去单 owner 纪律
6. 抗扰硬度：面对模糊需求或冲突指令时不失控
7. 演进硬度：系统可持续迭代，而不会越改越乱

## 三、项目目标

SaucyClaw 的 hardness engineering 目标是：

1. 构建一套可复用的 agent 团队组织方法
2. 让团队在不同运行环境中保持基本一致的行为边界
3. 让强大与受约束同时成立
4. 让多角色协作不以失控为代价
5. 让评测、回放、回归成为正式能力，而不是临时动作

## 四、四层结构

### 1. Team Layer（团队层）
定义：
- General Manager
- Specialists
- Reviewer
- Evaluator
- Policy Guardian

### 2. Constraint Layer（约束层）
定义：
- 角色边界
- 工具调用边界
- 信息可见性边界
- 动作前置条件
- 高风险动作审批点

### 3. Evaluation Layer（评测层）
定义：
- smoke tests
- regression cases
- challenge scenarios
- score rubric
- trace 与结果留痕

### 4. Portability Layer（可迁移层）
定义：
- 与具体 runtime 解耦的治理方法
- OpenClaw 兼容映射
- Codex、Claude 与其他系统中的最小入口

## 五、核心原则

1. 能力增强不能以边界失守为代价
2. 多角色协作不能以 owner 消失为代价
3. 自动化增强不能以证据缺失为代价
4. 结果更快不能以 review 失效为代价
5. 角色更强不能以约束失效为代价
6. 兼容具体框架不能牺牲通用性

## 六、最小闭环

一个合格的 hardness engineering agent 团队，至少要具备：

1. 明确的角色边界
2. 明确的启动条件
3. 明确的 handoff 结构
4. 明确的 review 关卡
5. 明确的高风险动作约束
6. 明确的评测样例与 rubric

## 七、与 OpenClaw 的关系

SaucyClaw 当前对 OpenClaw 友好，但不应被限制为 OpenClaw 专属骨架。

更准确的定位是：

- 方法论上：通用 agent hardness engineering 基线
- 结构上：兼容 OpenClaw 的组织化工作区样例
- 落地上：可映射到不同 agent 工具链与运行时
