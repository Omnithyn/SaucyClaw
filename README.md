<h1 align="center">🦞 SaucyClaw </h1>

> A governance-first OpenClaw multi-agent starter kit.  
> 一个围绕 **OpenClaw 多智能体组织化配置、治理方法、模板复用、快速铺设与体验** 构建的样例工程。

<p align="left">
  <img alt="OpenClaw Friendly" src="https://img.shields.io/badge/OpenClaw-friendly-blue">
  <img alt="Governance First" src="https://img.shields.io/badge/governance-first-orange">
  <img alt="AGENTS.md Centered" src="https://img.shields.io/badge/AGENTS.md-centered-green">
  <img alt="Demo Ready" src="https://img.shields.io/badge/demo-ready-purple">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue" alt="MIT License"></a>
</p>


---

## Why SaucyClaw

在很多 OpenClaw 使用场景里，单个 agent 很容易演变成“多个 agent 同时启动、各自抢答”的混乱状态：

- 收到任务后多个 agent 同时启动
- 没有唯一流程负责人
- specialist 直接面向用户输出最终结果
- 没有 handoff、review、状态板与统一收口
- 角色行为只存在于上下文里，没有沉淀为长期设定
- 想快速复制一套多智能体配置时，缺少统一模板、脚本和 demo

**SaucyClaw** 的目标，就是把这件事做成一套：

- **可复制**
- **可管理**
- **可解释**
- **可演进**
- **更贴近 OpenClaw 实际结构**

它不是一个新的 agent 运行时，也不是要替代 OpenClaw 本体。  
它更像一个 **OpenClaw 多智能体治理样例工程 + 配置化工具箱 + 快速体验基线**。

---

## What It Is

SaucyClaw 是一个围绕 OpenClaw 的样例工程，核心内容包括：

- 以 `AGENTS.md` 为中心的角色设定
- 系统级治理规则
- 多智能体协作方法样例
- handoff / review / artifact 模板
- 可复制的目录结构
- Shell / Python 工具骨架
- 快速体验 demo 结构
- 面向分享和交流的文档体系

---

## What It Is Not

SaucyClaw **不是**：

- 一个新的 AI agent 运行时框架
- 一个优先开发 Python orchestrator 的项目
- 一个企业级多租户 / RBAC 平台
- 一个要替代 OpenClaw 本体的产品
- 一个只强调人格娱乐化表达的项目

---

## Core Model

SaucyClaw 采用如下组织模型：

```text
姚总（CEO，人类 / 外部角色）
    ↓
虾酱（General Manager，主智能体）
    ↓
specialist agents
    ↓
reviewer
````

* **CEO 是外部人类角色**，不是 agent
* **虾酱** 是系统中最高的实际 agent 节点
* specialist 负责阶段性专业交付
* reviewer 负责守门，不代写
* 多智能体不是默认动作，而是由虾酱判断后启用的升级动作

---

## Key Ideas

### 1. 先判断，再决定是否调度

虾酱收到任务后的默认第一动作不是派单，而是先做 **任务处理判断**。

任务处理模式固定为五类：

* **A**：虾酱自己直接完成
* **B**：只调用一个 specialist
* **C**：一个 specialist + review
* **D**：多角色串行协作
* **E**：暂不启动执行

### 2. 多智能体不是默认动作

只有在单人或单 specialist 无法稳定闭环时，才升级为多角色协作。

### 3. specialist 默认待命

所有 specialist 的默认行为应为：

* 未被点名不得启动
* 不根据用户原始需求自行开工
* 默认输出中间产物，而不是直接对外最终答案

### 4. review 是正式关卡

复杂任务或正式交付必须经过 reviewer 审查。

reviewer 只负责：

* `pass`
* `revise`
* `reject`

不负责代写主体成果。

### 5. 长期行为必须写入文件设定

角色行为不能只存在于上下文里，应该优先落到：

* `AGENTS.md`
* `soul.md`
* `memory.md`

---

## OpenClaw Compatibility

SaucyClaw 明确用更贴近 OpenClaw 的结构设计：

### 角色文件优先级

1. `AGENTS.md`：角色主设定
2. `soul.md`：长期身份与边界
3. `memory.md`：长期经验
4. `PROMPT.md`：辅助说明，可选

### 设计原则

* `AGENTS.md` 是主入口
* `PROMPT.md` 不是必须文件
* 角色默认行为、启动条件、边界、禁止事项优先写入 `AGENTS.md`
* 保留 `soul / memory` 用于增强长期稳定性

---

## Project Structure

```text
SaucyClaw/
├── README.md
├── LICENSE
├── CHANGELOG.md
│
├── docs/                       # 项目说明、架构、方法、升级记录
├── system/                     # 系统治理规则
├── agents/                     # 内部智能体角色
├── focus/                      # 当前关注面
├── plaza/                      # 公共信息流
├── templates/                  # 模板层
├── examples/                   # 示例层
├── scripts/                    # shell 脚本入口
├── tools/                      # Python 工具层
├── demo/                       # 快速体验环境
└── assets/                     # 图片、图示、截图等资源
```

---

## Repository Layout

### `system/`

系统治理核心，定义多智能体组织如何运行，包括：

* `SYSTEM_SPEC.md`
* `AGENTS.md`
* `HUMAN_ROLES.md`
* `ORCHESTRATION.md`
* `MESSAGE_ROUTING.md`
* `TRIGGERS.md`
* `STANDARDS.md`
* `PROJECT_CONTEXT.md`
* `TASK_BOARD.yaml`
* `agenda.yaml`
* `DECISIONS.md`

### `agents/`

内部智能体角色定义。

重点角色包括：

* `general-manager/`
* `reviewer/`
* `specialists/researcher/`
* `specialists/architect/`
* `specialists/developer/`
* `specialists/writer/`
* `specialists/designer/`

### `focus/`

用于定义各角色当前阶段：

* 最该关注什么
* 最容易犯什么错

### `plaza/`

用于组织级公共信息流沉淀，例如：

* 公告
* 发现
* 更新

### `templates/`

用于存放：

* 任务处理判断模板
* 任务契约模板
* handoff 模板
* review 模板
* artifact 模板
* OpenClaw 模板
* Docker 模板

### `examples/`

用于存放：

* 示例任务
* 示例配置
* 示例工作区
* 示例项目

### `scripts/`

Shell 优先，用于：

* 初始化目录
* 注入 SaucyClaw 配置
* 校验结构
* 启停 demo
* 备份与导出

### `tools/`

Python 工具层，用于：

* 目录生成
* 模板渲染
* 配置解析
* 合规校验
* bundle 打包
* demo 辅助

### `demo/`

用于快速体验项目结构与样例配置。

---

## Quick Start

### Option 1 — Read as a governance starter kit

推荐阅读顺序：

1. `README.md`
2. `CLAUDE.md`
3. `docs/01-project-overview.md`
4. `system/SYSTEM_SPEC.md`
5. `system/AGENTS.md`
6. `system/HUMAN_ROLES.md`
7. `agents/general-manager/AGENTS.md`
8. `examples/first-run-task.md`

适合快速理解项目思路。

---

### Option 2 — Copy into your OpenClaw workspace

建议最小复制集合：

* `system/`
* `agents/`
* `focus/`
* `templates/`
* `examples/`
* `CLAUDE.md`

然后根据你的组织模型调整：

* 角色命名
* specialist 数量
* 输出风格
* review 严格程度
* 模板字段

---

### Option 3 — Use as a tooling baseline

如果你想继续把 SaucyClaw 做成可铺设项目，建议优先做：

#### Shell 脚本

* `scripts/bootstrap/init_saucyclaw.sh`
* `scripts/bootstrap/inject_into_openclaw.sh`
* `scripts/validate/check_structure.sh`

#### Python 工具

* scaffold 生成器
* AGENTS.md 校验器
* bundle 打包器
* demo 配置生成器

#### Docker demo

* `demo/docker/`
* `templates/docker/`

---

## Recommended Reading Order

如果你第一次接触 SaucyClaw，建议顺序如下：

### 第一步：理解整体思路

看这些文件：

* `README.md`
* `CLAUDE.md`
* `docs/`
* `system/`

### 第二步：理解角色模型

重点看：

* `system/HUMAN_ROLES.md`
* `agents/general-manager/AGENTS.md`
* `agents/reviewer/AGENTS.md`
* specialist 目录中的 `AGENTS.md`

### 第三步：理解模板与流转

重点看：

* `templates/`
* `examples/first-run-task.md`

### 第四步：复制到自己的项目

先最小复制，再本地化定制。

### 第五步：增加工具与 demo

完善：

* `scripts/`
* `tools/`
* `demo/`

---

## Use Cases

SaucyClaw 适合：

* OpenClaw 多智能体组织化配置样例
* 一人公司 / 小团队 agent 治理
* 对外分享与交流的样板工程
* 内部规范与模板基线
* 快速铺设 OpenClaw 多智能体工作区
* 作为工具化与 demo 化演进的基础项目

---

## Non-goals

SaucyClaw 当前不适合：

* 直接替代 OpenClaw 运行时
* 直接作为企业级权限与多租户平台
* 一开始就重投入做复杂 swarm engine
* 把它误解为“纯 Python 编排器项目”
* 把它误解为“人格娱乐化项目”

---

## Contributing

欢迎围绕以下方向进行贡献：

* OpenClaw 兼容结构优化
* `AGENTS.md` 角色设定增强
* 新的 specialist 样例
* 模板补强
* Shell / Python 工具补齐
* Demo 与示例工作区完善
* 文档与图示优化

### 建议的贡献原则

1. 不轻易推翻已验证有效的治理机制
2. 新增内容优先补强已有结构，而不是平行再造体系
3. 涉及角色默认行为的改动，优先落到 `AGENTS.md`
4. 涉及组织方法论的改动，同步更新 `docs/` 与 `system/`
