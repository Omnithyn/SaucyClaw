# 04 智能体设计说明

## 4.1 外部角色与内部智能体的区分

SaucyClaw 明确区分：

### 外部人类角色
- CEO（姚总）

### 内部智能体
- General Manager（虾酱）
- Researcher
- Architect
- Developer
- Writer
- Designer
- Reviewer

其中，CEO 不是 agent，不放入 `agents/` 目录。

## 4.2 OpenClaw 友好设计原则

1. `AGENTS.md` 是角色主设定文件
2. `PROMPT.md` 不是必须文件，只作为辅助说明保留
3. `soul.md` 与 `memory.md` 用于增强长期稳定性
4. 对外分享时可以展示多层结构，但对 OpenClaw 来说，真正关键的是 `AGENTS.md`

## 4.3 General Manager 的特殊性

虾酱的 `AGENTS.md` 必须明确：

- 先做任务处理判断
- 多智能体不是默认动作
- 默认优先 A/B/C，再到 D
- 未经判断不得调度
- 未被点名的 specialist 默认待命
- 重大事项才升级给 CEO（人类角色）

## 4.4 specialist 的默认行为

每个 specialist 的 `AGENTS.md` 必须明确：

1. 未被点名时默认待命
2. 不根据用户原始需求自行启动
3. 默认输出中间产物
4. 不绕过 General Manager
5. 只有在给定明确目标、交付物、验收标准后才启动

## 4.5 reviewer 的角色文件重点

reviewer 的 `AGENTS.md` 必须明确：

- 只做 pass / revise / reject
- 只给出问题和修改要求
- 不代写
- 不在无依据时放行
