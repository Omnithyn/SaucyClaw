# Phase 0-1 未决问题清单

> 创建时间：2026-04-12
> 规则：只列真正还没定的事。已决事项进入 phase0-1_status.md

---

## 未决问题

无未决问题。

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
| D-010 | MemoryStore 默认实现？ | FileMemoryStore 为默认实现 | 2026-04-13 |
| D-011 | Evidence 文件组织方式？ | 按 session_id 分 JSONL 文件 | 2026-04-13 |
| D-012 | OpenClawHostAdapter 首轮挂接点？ | 模拟接口（纯测试用） | 2026-04-13 |
| D-013 | GateResult.suggestions 类型？ | `list[str]` | 2026-04-13 |
| D-014 | 旧 tools/ 是否标记 deprecated？ | 暂不处理 | 2026-04-13 |
| D-015 | pyproject.toml 放哪里？ | 仓库根目录，不碰旧 tools/ | 2026-04-13 |
