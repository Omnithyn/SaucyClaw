# Phase 0-1 仓库基线报告

> 生成时间：2026-04-12
> 目的：记录实施前的仓库现状，识别冲突、风险、迁移路径

---

## 1. 当前目录结构

```
SaucyClaw/
├── .claude/              # Claude Code 配置（agents、hooks、skills、settings）
├── .codex/               # Codex 入口配置
├── .github/              # GitHub workflow（CI/PR 模板、CODEOWNERS）
├── agents/               # 智能体角色定义（governance 当前形态）
│   ├── general-manager/  #   AGENTS.md, PROMPT.md, memory.md, soul.md
│   ├── reviewer/         #   同上
│   └── specialists/      #   architect, designer, developer, researcher, writer
├── assets/               # 占位（diagrams, logos, screenshots）
├── demo/                 # Docker demo 环境
│   ├── docker/           #   Dockerfile, docker-compose.yml
│   └── openclaw-demo/    #   OpenClaw 演示 workspace 占位
├── docs/                 # 文档体系
│   ├── 01-project-overview.md
│   ├── 02-architecture.md
│   ├── 03-operating-model.md
│   ├── 04-agent-design.md
│   ├── 05-copy-and-customize.md
│   ├── 06-tooling-and-bootstrap.md
│   ├── 07-docker-demo.md
│   ├── 08-github-workflow.md
│   ├── 10-codex-debugging.md
│   └── superpowers/specs/
│       ├── 2026-04-12-saucyclaw-repositioning-design.md  ← 本次头脑风暴产出
│       └── SaucyClaw_详细设计说明书_vNext.md             ← GPT 深度分析产出
├── examples/             # 使用示例
│   ├── codex/            # Codex smoke task
│   ├── first-run-task.md
│   ├── openclaw-agent-structure-note.md
│   ├── openclaw-sample-config.json
│   ├── sample-configs/   # basic.yaml, demo.yaml, team-lite.yaml（均为占位）
│   ├── sample-openclaw-workspace/
│   ├── sample-project/
│   └── setting-update-instruction.md
├── focus/                # 各角色关注点文件（CEO, DEVELOPER, REVIEWER 等）
├── openspec/             # OpenSpec 配置
├── plaza/                # 公告与发现（治理协作占位）
├── scripts/              # Shell 脚本集合
│   ├── bootstrap/        #   项目初始化、角色创建、注入 OpenClaw
│   ├── codex/            #   Codex 调试
│   ├── demo/             #   Docker demo 管理
│   ├── openclaw-bootstrap/ # OpenClaw 安装脚本（PowerShell + Bash）
│   ├── setup/            #   Git hooks 安装
│   ├── utils/            #   分支管理、PR 创建、备份等
│   └── validate/         #   结构验证、模板验证
├── system/               # 系统级治理文件
│   ├── AGENTS.md
│   ├── DECISIONS.md
│   ├── HUMAN_ROLES.md
│   ├── MESSAGE_ROUTING.md
│   ├── ORCHESTRATION.md  #   ← 当前任务分类 A-E 的核心定义
│   ├── PROJECT_CONTEXT.md
│   ├── STANDARDS.md
│   ├── SYSTEM_SPEC.md
│   ├── TASK_BOARD.yaml   #   ← 占位任务列表，非治理规则
│   ├── TRIGGERS.md
│   └── agenda.yaml
├── templates/            # 模板文件
│   ├── AGENT_PROMPT_TEMPLATE.md
│   ├── ARTIFACT_TEMPLATE.md
│   ├── HANDOFF_TEMPLATE.md
│   ├── REVIEW_TEMPLATE.md
│   ├── TASK_CONTRACT.md
│   ├── TASK_PROCESS_DECISION.md
│   └── docker/, openclaw/
├── tools/                # Python 工具包
│   ├── pyproject.toml
│   ├── requirements.txt
│   ├── saucyclaw/
│   │   ├── __init__.py   #   只导出 cli
│   │   ├── cli.py        #   CLI 入口（init/validate/create-agent/demo/bundle）
│   │   ├── packagers/    #   bundle.py, demo_env.py（有实现）
│   │   ├── scaffold/     #   generator.py, merger.py, renderer.py（有实现）
│   │   ├── utils/        #   file_ops.py, yaml_ops.py（yaml_ops 占位）
│   │   └── validators/   #   agents_md.py, configs.py, structure.py（有实现）
│   └── tests/            #   test_bundle.py, test_scaffold.py, test_validators.py
├── AGENTS.md
├── CLAUDE.md
├── CONTRIBUTING.md
├── IMPLEMENTATION_SUMMARY.md   ← 未提交
├── QUICKSTART.md
├── README.md
└── scripts/openclaw-bootstrap/ ← 未提交目录
```

---

## 2. 与 Phase 0-1 目标相近的模块

| 现有模块 | 与 Phase 0-1 的关系 | 处理方式 |
|---------|-------------------|---------|
| `system/ORCHESTRATION.md` | 当前 A-E 任务分类定义，**即治理规则的当前形态** | 保留，后续结构化到 `schemas/governance/` |
| `system/MESSAGE_ROUTING.md` | 消息流向，**即治理规则的路由部分** | 保留，后续结构化 |
| `agents/` | 角色定义以 Markdown prompt 形式存在 | 保留，后续部分内容提取到 `schemas/governance/roles.yaml` |
| `tools/saucyclaw/cli.py` | CLI 入口，使用 `os.system()` 调 shell 脚本 | **重写入口**，Phase 0-1 的新 core 模块不依赖旧 CLI |
| `tools/saucyclaw/validators/` | 结构验证、配置验证已有部分实现 | **可复用**，但需适配新架构 |
| `tools/saucyclaw/scaffold/` | 脚手架生成器 | **可复用**，但需适配新架构 |
| `tools/saucyclaw/utils/yaml_ops.py` | YAML 工具，占位 | **需实现**，Phase 0-1 需要 |
| `examples/sample-configs/*.yaml` | 配置样例，均为占位 | 替换为 Phase 0-1 的真实 schema |
| `docs/superpowers/specs/` | 两份设计文档 | 保留作为参考，不作为实现依据 |

---

## 3. 风险项

### 3.1 命名冲突

| 冲突点 | 说明 | 解决 |
|-------|------|------|
| `tools/saucyclaw/` vs `core/` | 现有 Python 包在 `tools/` 下，Phase 0-1 建议 `core/` 在项目根目录 | `core/` 是新增目录，不与 `tools/` 冲突。旧 `tools/` 暂保留，后续迁移或废弃 |
| `stores/` vs `tools/saucyclaw/utils/` | 新 `stores/` 是独立目录，无冲突 | 无冲突 |
| `adapters/` vs `agents/` | `agents/` 是治理角色定义（Markdown），`adapters/` 是宿主接入（Python），不同层级 | 无冲突，但需在文档中明确区分 |

### 3.2 目录冲突

无直接冲突。Phase 0-1 新增的目录（`core/`, `stores/`, `adapters/`, `schemas/`）均为新目录，不与现有目录重叠。

### 3.3 已有实现重叠风险

- `tools/saucyclaw/validators/structure.py` 已有项目结构验证逻辑，新的 `meta_model` 可能与其功能重叠
  - **处理**：Phase 0-1 不碰旧 validators，新 `meta_model` 从零实现。后续考虑迁移或废弃旧 validators
- `tools/saucyclaw/cli.py` 是现有 CLI 入口
  - **处理**：Phase 0-1 的新 engine 不依赖旧 CLI，后续可考虑让旧 CLI 调用新 engine

### 3.4 迁移 vs 重写

| 内容 | 迁移 | 重写 | 延后 |
|------|------|------|------|
| system/ 治理文件（ORCHESTRATION, MESSAGE_ROUTING） | 提取规则到 schemas/ | - | 保留原文档 |
| agents/ 角色定义 | 提取到 schemas/governance/roles.yaml | - | 保留 Markdown prompt |
| tools/saucyclaw/validators/ | - | - | Phase 0-1 不碰 |
| tools/saucyclaw/scaffold/ | - | - | Phase 0-1 不碰 |
| tools/saucyclaw/cli.py | - | - | Phase 0-1 不碰 |
| examples/sample-configs/ | - | 替换为真实 schema | - |
| docs/ 现有文档 | - | - | 保留，不修改 |

---

## 4. 结论

### 保留
- 所有现有文档（docs/, system/, agents/, focus/, templates/）
- 所有现有脚本（scripts/）
- 现有 Python 工具包（tools/）
- .claude/ 配置

### 新增
- `core/` — Phase 0-1 核心模块
- `stores/` — 文件存储实现
- `adapters/` — 宿主适配器
- `schemas/` — YAML schema DSL
- `tests/` — 新架构的测试
- `docs/phase/` — 过程文档
- `docs/adr/` — 架构决策记录

### 延后
- 旧 tools/ 的迁移或废弃（Phase 2+）
- Web 管理台
- Sidecar 模式
- 多宿主适配

### 第一刀从哪里下

**Commit 0（本次）**：建立过程文档和 ADR
**Commit 1**：创建新目录结构 + 首批 YAML schema 样例 + dataclass 骨架
**Commit 2**：`meta_model` + `governance` 最小匹配逻辑
**Commit 3**：`events` + `evidence` 转换与记录
**Commit 4**：`file_store` + `engine` 编排闭环
**Commit 5**：`openclaw_adapter` + 集成测试
