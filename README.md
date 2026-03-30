<h1 align="center">🦞 SaucyClaw </h1>

> A governance-first agent hardness engineering project baseline.  
> 一个围绕 **强团队、强约束、强评测、强迁移** 构建的智能体 hardness engineering 基线工程。

<p align="left">
  <img alt="Agent Hardness Engineering" src="https://img.shields.io/badge/agent-hardness%20engineering-blue">
  <img alt="Governance First" src="https://img.shields.io/badge/governance-first-orange">
  <img alt="Evaluation Ready" src="https://img.shields.io/badge/evaluation-ready-green">
  <img alt="OpenClaw Compatible" src="https://img.shields.io/badge/OpenClaw-compatible-purple">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue" alt="MIT License"></a>
</p>

---

## Why SaucyClaw

很多多智能体项目的问题，不是“模型不够强”，而是团队工程不够硬：

- 收到任务后多个角色同时开工
- 没有唯一 owner
- specialist 抢答并直接对外交付
- 没有 handoff、review、评测与回归
- 角色规则只存在于上下文里，难以长期复用
- 一旦换到别的工具链，原有方法就散掉

**SaucyClaw** 的目标，就是把这件事做成一套可复制、可约束、可评测、可迁移的工程基线。

它不是新的 agent runtime，也不是只服务某一个工具。  
它更像一个 **agent hardness engineering 项目骨架 + 团队治理方法库 + 评测与回归工作面**。

---

## What It Is

SaucyClaw 是一个通用的 agent hardness engineering 基线工程，核心内容包括：

- 以 `AGENTS.md` 为中心的角色设定
- General Manager 主导的先判断后调度机制
- Reviewer / Evaluator / Policy Guardian 等角色分工
- handoff / review / task contract 模板
- evals / rubrics / scenarios / reports 工作面
- Shell / Python 工具骨架
- 面向 OpenClaw、Codex、Claude 等场景的入口层

---

## What It Is Not

SaucyClaw **不是**：

- 一个新的 AI agent 运行时框架
- 一个把所有问题都推给 swarm 的项目
- 一个只强调人格或角色扮演的项目
- 一个只绑定 OpenClaw 的专属仓库
- 一个只讲 prompt 技巧、不讲团队工程的样板

---

## Core Model

SaucyClaw 采用如下组织模型：

```text
CEO / Human Decision Maker
        ↓
General Manager
        ↓
Specialists ── Reviewer
        ↓          ↓
   Evaluator / Policy Guardian
```

- **CEO / Human Decision Maker** 是外部角色，不是内部 agent
- **General Manager** 是系统中的实际总控
- **Specialists** 负责阶段性交付
- **Reviewer** 负责质量审查，不代写
- **Evaluator** 负责评测、回放、回归判断
- **Policy Guardian** 负责约束提醒与边界检查

---

## Key Ideas

### 1. 先判断，再决定是否调度

General Manager 的默认第一动作不是派单，而是先做 **任务处理判断**。

### 2. 多智能体不是默认动作

多角色协作是升级动作，不是默认动作。能单人闭环，就不多人协作。

### 3. 角色要强，但不能越界

SaucyClaw 强调：

- specialist 默认待命
- reviewer 只审不代写
- evaluator 不替代交付
- policy guardian 不替代总控

### 4. 团队不仅要能做事，还要能被验证

项目不仅关注交付，也关注：

- smoke tasks
- replay scenarios
- rubrics
- reports
- regression checks

### 5. 方法优先，工具其次

SaucyClaw 会兼容 OpenClaw，但不把自身限制为 OpenClaw 专属骨架。

---

## Project Structure

```text
SaucyClaw/
├── README.md
├── AGENTS.md
├── CLAUDE.md
├── docs/
├── system/
├── agents/
├── evals/
├── templates/
├── examples/
├── scripts/
├── tools/
├── focus/
├── plaza/
└── demo/
```

---

## Recommended Reading Order

第一次进入仓库，建议按以下顺序阅读：

1. `README.md`
2. `AGENTS.md`
3. `CLAUDE.md`
4. `system/SYSTEM_SPEC.md`
5. `system/HARDNESS_ENGINEERING.md`
6. `agents/general-manager/AGENTS.md`
7. `evals/README.md`
8. `templates/`

---

## Use Cases

SaucyClaw 适合：

- 构建强大且受约束的 agent 团队
- 设计可回放、可比较、可回归的团队评测体系
- 作为 OpenClaw、Codex、Claude 等场景下的治理基线
- 作为角色模板、流程模板、评测模板的统一底座

---

## Current Direction

当前阶段，SaucyClaw 正在从 “OpenClaw-friendly 多智能体骨架” 继续演进为 “通用 agent hardness engineering 基线”。

这意味着项目会持续补强：

- 系统级 hardness 文档
- 角色约束与职责分层
- 评测与回归资产
- 可迁移性与映射说明
- 主文件的 V2 改写与收敛
