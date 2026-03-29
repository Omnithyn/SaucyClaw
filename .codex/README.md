# .codex/

该目录用于存放 SaucyClaw 在 Codex 中使用时的辅助说明。

当前采取的策略是：

- **先不强绑定特定 Codex 配置语法**
- 优先通过仓库根目录 `AGENTS.md` 与 `CLAUDE.md` 提供稳定入口
- 通过 `examples/codex/smoke-task.md` 提供最小回放任务
- 通过 `scripts/codex/run_smoke.sh` 提供最小检查脚本

这样做的原因是：

1. SaucyClaw 当前重点是治理与组织结构
2. 不同 Codex 运行形态的配置字段可能不一致
3. 与其过早绑定配置，不如先把仓库入口和调试方法做稳

后续若需要，可在此目录继续增加：

- 项目级任务模板
- 回放样例
- 评分 rubric
- 与 OpenClaw workspace 的桥接说明
