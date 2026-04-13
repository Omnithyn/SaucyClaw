# Phase 0-1 未决问题清单

> 创建时间：2026-04-12
> 规则：只列真正还没定的事。已决事项进入 phase0-1_status.md

---

## 未决问题

| # | 问题 | 候选方案 | 影响模块 | 决定时限 |
|---|------|---------|---------|---------|
| OQ-001 | `FileMemoryStore` 与 `InMemoryMemoryStore` 首轮选哪个为默认？ | A: 只实现 FileMemoryStore<br>B: 两个都实现，File 为默认 | stores | Commit 4 之前 |
| OQ-002 | `stores/file/` 下 evidence 按什么维度分文件？ | A: 按 session 分目录<br>B: 按日期分目录<br>C: 单文件 JSON Lines | stores/file | Commit 4 之前 |
| OQ-003 | `OpenClawHostAdapter` 首轮挂接点是什么？ | A: 模拟接口（纯测试用 mock）<br>B: 实际 hook OpenClaw 生命周期<br>C: CLI 入口拦截 | adapters/openclaw | Commit 5 之前 |
| OQ-004 | `GateResult.suggestions` 是字符串列表还是结构化对象？ | A: `list[str]`（简单）<br>B: `list[dict]`（结构化） | core/engine | Commit 4 之前 |
| OQ-005 | 旧 `tools/saucyclaw/` 在 Phase 0-1 期间是否标记为 deprecated？ | A: 加 README 说明即将迁移<br>B: 暂不处理 | tools | 非阻塞 |
| OQ-006 | `pyproject.toml` 放在根目录还是 `tools/` 下？新 core 模块的包管理？ | A: 根目录新建 pyproject.toml<br>B: 复用 tools/pyproject.toml | 项目配置 | Commit 1 之前 |

---

## 已决问题（记录在此防止重新讨论）

| # | 问题 | 决定 | 决定时间 |
|---|------|------|---------|
| D-001 | YAML Schema 是否作为 DSL？ | 是，Phase 0-1 YAML + 校验 = DSL | 2026-04-12 |
| D-002 | Evidence confidence 精度？ | 只允许 1.0 / 0.5 / 0.0 | 2026-04-12 |
| D-003 | GovernanceRule conditions 复杂度？ | 单层简单结构，不支持 and/or 嵌套 | 2026-04-12 |
| D-004 | 首轮测试场景？ | Block + Allow 两个场景 | 2026-04-12 |
| D-005 | 是否引入图数据库？ | 否，Phase 0-1 不做 | 2026-04-12 |
| D-006 | 是否引入 Web 管理台？ | 否，Phase 0-1 不做 | 2026-04-12 |
| D-007 | events 模块是否持有状态？ | 否，纯转换层 | 2026-04-12 |
| D-008 | HostAdapter 是否需要 get_capabilities？ | 是，增加此方法 | 2026-04-12 |
| D-009 | MemoryStore.search 是否需要 limit？ | 是，默认 10 | 2026-04-12 |
