# DECISIONS.md

## [2026-03-16] SaucyClaw v1.1 模板层增强
- 决策人：General Manager
- 背景：
  SaucyClaw 当前治理层与角色设定层已较成熟，但模板层偏轻，不足以支撑高质量复制与运行。
- 决策：
  保留当前治理层与角色设定层，增强 templates 目录中的 TASK_CONTRACT、HANDOFF、REVIEW、ARTIFACT、AGENT_PROMPT 模板。
- 原因：
  使 SaucyClaw 从“可展示样例”升级为“可复制基线”。

## [2026-03-16] SaucyClaw v1.2 OpenClaw 兼容化
- 决策人：General Manager
- 决策：
  将角色主设定重心正式迁移到 `AGENTS.md`，并补回 `focus / triggers / plaza / agenda` 等 Clawith-lite 轻量增强元素。

## [2026-03-16] SaucyClaw v1.2.1 组织模型修正
- 决策人：General Manager
- 决策：
  明确 CEO 为外部人类角色，不作为 agent 存在；删除 `agents/ceo/`，新增 `system/HUMAN_ROLES.md`。

## [2026-03-16] SaucyClaw v1.3 工具与 demo 骨架补齐
- 决策人：General Manager
- 决策：
  在不改变治理主线的前提下，补齐 `scripts / tools / demo / templates/docker / examples/sample-* / assets / .github` 目录骨架，并新增完整 `CLAUDE.md`。
- 原因：
  使项目从“治理样例仓库”进化为“治理样例工程 + 配置化工具箱 + 快速体验 demo”基线。
