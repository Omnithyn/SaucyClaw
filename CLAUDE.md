# CLAUDE.md

SaucyClaw 是一个**通用 agent hardness engineering 基线工程**，并保持对 OpenClaw 的兼容适配能力（兼容，不绑定）。

本文件用于给 Claude / Codex / 其他进入仓库的 AI 编程工具一个简明入口，避免它们一进来就把项目误判为普通代码仓库。

## 语义裁决来源（必读）

若本文件与其他入口文档存在表达差异，统一以 `system/SYSTEM_SPEC.md` 为准。

## 先看哪里
首次进入仓库时，建议按以下顺序阅读：

1. `README.md`
2. `AGENTS.md`
3. `system/SYSTEM_SPEC.md`
4. `system/AGENTS.md`
5. `agents/general-manager/AGENTS.md`
6. `examples/first-run-task.md`
7. `examples/codex/smoke-task.md`

## 仓库本质
SaucyClaw 当前更像：
- 通用 hardness engineering 治理基线
- 角色组织与边界模板
- OpenClaw 兼容结构样例（非 OpenClaw 专属）
- 便于复制与二次定制的基线工程

而不是：
- 新的 agent runtime
- 优先追求 swarm 的编排引擎
- 先上复杂代码再补治理的项目

## 进入本仓库时的默认行为

### 对开发型 AI 工具
- 先读治理文件，再改代码
- 优先最小增量改动
- 优先补入口、脚本、示例、校验
- 每轮改动都要说明验证方法

### 对研究型 AI 工具
- 优先分析角色边界、调度模型、handoff 与 review 机制
- 不要把 CEO 误当内部 agent
- 不要把 specialist 直接暴露成面向用户的最终交付角色

## 当前建议的 Codex 使用方式
把 SaucyClaw 当作“治理基线仓库”来调试，而不是一开始就要求它在 Codex 中扮演完整运行时。

推荐顺序：
1. 先验证入口是否清晰
2. 再验证 smoke task 是否能稳定执行
3. 再补脚本与校验
4. 最后再接 OpenClaw 真实 workspace 或运行时

## 本仓库的最小验证目标
一名进入仓库的 AI 代理，应能在短时间内正确理解以下事实：

1. 谁是外部人类角色
2. 谁是内部总控角色
3. 是否应该默认启动多智能体
4. review 的职责边界是什么
5. 从哪里开始进行第一次 smoke test
