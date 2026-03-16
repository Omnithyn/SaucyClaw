# HUMAN_ROLES.md - 外部人类角色说明

## 说明

SaucyClaw v1.2.1 明确区分：

- **外部人类角色**
- **内部智能体角色**

其中，CEO 在本项目中不是一个智能体，而是**外部人类角色**。

---

## CEO（姚总）

### 角色性质
- 外部人类角色
- 不属于 `agents/` 目录
- 不作为 OpenClaw 中的一个 agent 运行

### 核心职责
1. 提出目标
2. 设定优先级
3. 决定最终期望
4. 对重大方向与边界变化进行拍板
5. 对最终结果做验收

### 不承担的工作
1. 不直接拆底层任务
2. 不直接进入 specialist 执行链路
3. 不直接维护任务状态板
4. 不直接替代 General Manager 进行流程调度

### 与系统的关系
CEO 是 SaucyClaw 组织模型中的上游人类角色，其输入进入 General Manager，由 General Manager 判断任务处理模式并决定后续是否需要调用其他智能体。

---

## 为什么 CEO 不建成 agent

因为在当前组织模型中：

- CEO 就是用户本人
- 虾酱才是用户实际面对的主智能体
- 若再建立一个 ceo agent，会造成角色重复、决策权混乱和链路不自然

因此，SaucyClaw v1.2.1 采用以下模型：

姚总（CEO，人类/外部角色）
-> 虾酱（General Manager，主智能体）
-> specialist agents
-> reviewer
