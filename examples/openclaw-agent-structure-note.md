# OpenClaw 角色文件结构说明

在 SaucyClaw 中，角色目录采用更贴近 OpenClaw 的结构设计：

- `AGENTS.md`：主设定文件，OpenClaw 兼容优先
- `PROMPT.md`：辅助说明，可选
- `soul.md`：长期身份与边界
- `memory.md`：长期经验
- `focus/*.md`：当前关注面（按角色放在全局 focus 目录中）

同时需要注意：

- CEO 是外部人类角色，不在 `agents/` 目录中存在
- 系统中的最高实际 agent 节点是 `agents/general-manager/`

建议在实际复制到 OpenClaw 项目时，至少保证：
1. 内部角色目录中存在 `AGENTS.md`
2. 系统根目录中存在系统级治理文件
3. 若只能保留最少文件，优先保留 `AGENTS.md + soul.md + memory.md`
