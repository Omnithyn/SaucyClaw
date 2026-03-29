# Codex Smoke Task

## 目的
用于验证进入 SaucyClaw 的 Codex 是否能够：

1. 找到正确入口文件
2. 正确理解治理结构
3. 不把多智能体当默认动作
4. 给出最小但可执行的迭代方案

## 任务输入
请基于当前仓库完成一次最小迭代，使 SaucyClaw 更适合在 Codex 中进行调试。

要求：
- 不破坏既有治理结构
- 不重写 system/ 下的核心规范
- 优先补入口与调试工装
- 说明验证方法

## 预期行为
进入仓库后，应优先读取：
- `README.md`
- `AGENTS.md`
- `system/SYSTEM_SPEC.md`
- `system/AGENTS.md`
- `agents/general-manager/AGENTS.md`

## 预期输出骨架

```text
# 任务理解
- SaucyClaw 是治理型 starter kit，而不是新的 agent runtime
- 本轮目标是补 Codex 可直接接手的入口与调试层

# 受影响文件
- AGENTS.md
- CLAUDE.md
- examples/codex/smoke-task.md
- scripts/codex/run_smoke.sh
- docs/10-codex-debugging.md

# 改动内容
- 补根目录入口
- 补 smoke task
- 补调试脚本
- 补 Codex 使用说明

# 验证方式
- 说明首次阅读顺序
- 运行校验脚本
- 让 Codex 根据 smoke task 给出一次最小改动方案

# 后续方向
- 补更多回放样例
- 补评分 rubric
- 视需要接 OpenClaw workspace
```

## 判定失败的信号
若 Codex 出现以下行为，说明入口仍不够清晰：

1. 一进来就大规模重构目录
2. 把 CEO 当内部 agent
3. 直接拉起多个 specialist
4. 忽略 General Manager 的任务判断机制
5. 没有给出验证方法
