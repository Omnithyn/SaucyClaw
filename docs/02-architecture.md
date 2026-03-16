# 02 架构设计

## 2.1 总体层次

SaucyClaw 的逻辑层次分为五层：

### 第一层：治理层
存放系统级约束与组织规则，例如：
- `system/SYSTEM_SPEC.md`
- `system/AGENTS.md`
- `system/HUMAN_ROLES.md`
- `system/ORCHESTRATION.md`
- `system/MESSAGE_ROUTING.md`
- `system/TRIGGERS.md`
- `system/STANDARDS.md`

### 第二层：角色层（OpenClaw 友好）
存放各内部智能体目录，其中 **`AGENTS.md` 是角色主设定文件**。  
为兼容展示与阅读，仍可保留 `PROMPT.md / soul.md / memory.md`，但在 OpenClaw 语境下，`AGENTS.md` 必须是主入口。

### 第三层：任务运行层
- `system/TASK_BOARD.yaml`
- `system/agenda.yaml`
- `tasks/`
- `handoff/`
- `reviews/`
- `artifacts/`

### 第四层：运行增强层（Clawith-lite）
- `focus/`
- `plaza/`
- `system/TRIGGERS.md`

### 第五层：模板与示例层
- `templates/`
- `examples/`
- `docs/`

## 2.2 组织模型

SaucyClaw v1.2.1 明确采用以下模型：

姚总（CEO，人类/外部角色）
-> 虾酱（General Manager，主智能体）
-> Specialist Agents
-> Reviewer

说明：

1. CEO 是外部人类角色，不在 `agents/` 目录中存在
2. 虾酱是系统中最高的实际 agent 节点
3. 所有 specialist 与 reviewer 都由虾酱判断后决定是否启动

## 2.3 为什么取消 ceo agent

因为在你的真实使用模型中：

- CEO 就是你本人
- 虾酱才是你面对的主智能体
- 若再建立一个 ceo agent，会造成角色重复、决策权混乱和链路失真

因此 v1.2.1 采用“保留 CEO 角色，但不把它建成 agent”的方式。

## 2.4 任务处理模式

### A. 由 General Manager 自己直接完成
### B. 单 specialist
### C. 单 specialist + review
### D. 多角色串行协作
### E. 暂不启动执行

## 2.5 Clawith-lite 元素的保留原则

SaucyClaw 并不照搬 Clawith，而是保留轻量但高价值的机制：

- `TRIGGERS`：事件驱动意识
- `focus/`：当前关注面
- `plaza/`：公共知识流
- `agenda`：当前周期节奏
- `soul / memory`：长期角色稳定性
