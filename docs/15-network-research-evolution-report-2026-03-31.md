# SaucyClaw 研究再评估与进化方案报告（联网复核版）

- 日期：2026-03-31
- 目标：在“兼容 OpenClaw”的同时，推进 SaucyClaw 成为工具无关的 agent hardness engineering 基线工程。
- 方法：外部实践复核（OpenAI/Anthropic/NIST/MCP/OpenClaw）+ 仓库主干文件对照分析。

---

## 1. 结论摘要

### 1.1 当前方向判断

SaucyClaw 当前方向总体正确：

1. 已明确“不是 runtime，而是治理与工程基线”；
2. 已具备 Team/Constraint/Evaluation/Portability 的四层模型；
3. 已建立 A-E 编排分类与边界红线。

但当前仍处于“概念结构较完整、工程闭环未完全硬化”的阶段。

### 1.2 联网复核后的关键增量发现

1. 业界成熟实践普遍强调：先 workflow，再逐步上 agent autonomy；
2. 评测必须进入迭代闭环（不是一次性打分）；
3. OpenClaw 的 workspace 不是安全沙箱替代，权限与隔离必须显式治理；
4. 协议（如 MCP）通常不替代执行侧安全，治理需要落实为本地检查与门禁。

---

## 2. 外部研究结论（面向工程可落地）

### 2.1 成熟 agent hardness engineering 的共同能力

1. **统一主叙事**：系统定位、角色边界、执行纪律有唯一裁决源。
2. **编排可执行**：任务判断/阶段契约/handoff/review 可以模板化与检查化。
3. **风险前置**：高风险节点前置 policy check 或 human approval。
4. **评测闭环**：smoke/replay/rubric/report 与改动触发机制绑定。
5. **可迁移架构**：核心治理与工具适配分层，避免被单平台绑定。

### 2.2 OpenClaw 兼容的现实要求

1. 明确多 agent 的 workspace 与工具权限边界；
2. 把 AGENTS/SOUL/MEMORY/PROMPT 放在“角色行为配置层”，而非系统主规层；
3. 兼容层应承接 OpenClaw 的工作区习惯与工具调用习惯，不反向污染核心治理语义。

### 2.3 “兼容 OpenClaw”与“仅服务 OpenClaw”的分界

- 兼容 OpenClaw：
  - 保持可映射；
  - 提供 adapter；
  - 不破坏 core。
- 仅服务 OpenClaw：
  - 核心概念直接依赖 OpenClaw 实现细节；
  - 迁移到其他环境时主规失效。

---

## 3. 与仓库现状的主干一致性

### 3.1 已与目标一致的部分

1. README 明确通用 baseline 与 OpenClaw-compatible 定位；
2. SYSTEM_SPEC 明确系统主规地位与质量红线；
3. ORCHESTRATION 明确“先判断后调度”与 A-E 模式；
4. evals 与 rubric 已形成评测入口。

### 3.2 尚未完全到位的主干差距

1. 入口口径未完全收敛（README 与 CLAUDE 对外叙事仍有偏差）；
2. V1/V2 并存但缺少生效切换机制；
3. A-E 规则偏“文本规范”，尚未全面“模板化+门禁化”；
4. 评测层有 rubric，但“主干变更必回归”机制不够硬；
5. portability 已有原则，但缺文件级 core/adapter 边界契约。

---

## 4. 目标进化模型（能力域）

1. **Narrative Governance**：主叙事一致、版本生效清晰。
2. **Execution Discipline**：判断-调度-流转可验证。
3. **Boundary Hardness**：越界可检测且可阻断。
4. **Evaluation Hardness**：评测与回归成为变更门禁。
5. **Portability Hardness**：核心与适配层清晰分离。
6. **OpenClaw Adapter Safety**：兼容实现具备最低安全基线。

---

## 5. 建议改造顺序（先主干后枝叶）

### Phase P0：主干收敛

1. 统一 README/CLAUDE/SYSTEM_SPEC 主叙事；
2. 建立 V1/V2 生效开关与迁移条件；
3. 将 A-E 最小字段模板化；
4. 建立主干改动触发回归门禁。

### Phase P1：机制硬化

1. FAILURE_MODES 矩阵化（触发信号/检测点/责任人/处置动作）；
2. portability 文档加入 core/adapter 文件归属矩阵；
3. OpenClaw 兼容指南补充 workspace/权限/隔离安全基线。

### Phase P2：运营化

1. onboard 回放路径（first-run -> eval report）标准化；
2. 形成季度回归与评分趋势报告。

---

## 6. 外部参考（联网复核）

- OpenAI：A practical guide to building AI agents  
  https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/
- OpenAI：Agent builder safety（官方文档）  
  https://platform.openai.com/docs/guides/agents?api-mode=responses#safety-checks
- OpenAI：Evals design guide（官方文档）  
  https://platform.openai.com/docs/guides/evals
- Anthropic：Building effective agents  
  https://www.anthropic.com/engineering/building-effective-agents
- NIST：AI RMF Generative AI Profile  
  https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence
- MCP Specification  
  https://modelcontextprotocol.io/specification/2025-06-18
- OpenClaw：Multi-agent concepts  
  https://docs.openclaw.ai/concepts/multi-agent
- OpenClaw：Agent workspace  
  https://openclawlab.com/en/docs/concepts/agent-workspace/
- OpenClaw：AGENTS template reference  
  https://docs.openclaw.ai/reference/templates/AGENTS
