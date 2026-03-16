# 03 运行模型

## 3.1 起点：General Manager 的任务处理判断

SaucyClaw 仍然坚持一个核心原则：

收到任务后，General Manager 的默认第一动作不是派单，而是做 **任务处理判断**。

## 3.2 五类处理模式

- A：General Manager 自己直接完成
- B：只调用一个 specialist
- C：一个 specialist + review
- D：多角色串行协作
- E：暂不启动执行

## 3.3 OpenClaw 兼容约束

为了符合 OpenClaw 的实际文件关注习惯：

1. 每个角色目录必须提供 `AGENTS.md`
2. 角色的默认行为、启动条件、禁止事项、协作边界，应写入 `AGENTS.md`
3. `PROMPT.md` 可以保留，但不应作为唯一关键设定文件

## 3.4 focus / agenda / triggers / plaza 的分工

### focus
回答：当前阶段这个角色最该盯什么、最容易错什么。

### agenda
回答：当前周期的行动节奏与排期是什么。

### triggers
回答：哪些事件发生后，流程应当如何推进。

### plaza
回答：哪些内容应该共享给整个组织，而不是只保留在点对点交互中。

## 3.5 为什么这些不是多余层

- `AGENTS.md` / `prompt` 管的是“怎么干”
- `soul` 管的是“这个角色是谁”
- `memory` 管的是“长期记住什么”
- `focus` 管的是“当前优先盯什么”
- `agenda` 管的是“这个周期先做什么”
- `triggers` 管的是“什么时候动”
- `plaza` 管的是“哪些信息应该公开共享”

这几层并不重复，而是在复杂度可控的前提下，让多智能体系统更稳。
