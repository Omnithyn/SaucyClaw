# ADR-0003: 证据模型设计

> 日期：2026-04-12
> 状态：已接受

---

## 背景

目标态设计中的证据模型包含 15+ 字段，
容易让实施者误判首轮成本并引入复杂数据库。

## 决策

Phase 0-1 的证据模型分为两层字段：

### 最小必填（6 字段）

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | str | 证据唯一标识 |
| `type` | str | 证据类型（rule_hit / rule_pass / conflict 等） |
| `assertion` | str | 断言描述 |
| `source_ref` | str | 来源事件 ID |
| `timestamp` | str | 采集时间（ISO 8601） |
| `confidence` | float | 置信度，只允许 1.0 / 0.5 / 0.0 |

### 扩展可选（5 字段）

| 字段 | 类型 | 说明 |
|------|------|------|
| `freshness` | str | 新鲜度（fresh / stale / expired） |
| `verification_status` | str | 校验状态（verified / unverified / rejected） |
| `applicable_scope` | dict | 适用范围 |
| `contradicted_by` | list[str] | 冲突证据 ID 列表 |
| `governance_version` | str | 所属治理版本 |

证据存储使用 JSON 文件（`stores/file/evidence/`），不使用数据库。

## 取舍

### 两层字段的理由

1. 最小必填 6 个字段足以立住"证据是结构化对象"这件事
2. 扩展字段预留位置，后续自然生长
3. 避免首轮就实现复杂的关联查询

### confidence 三档离散值的理由

1. Phase 0-1 不做浮点评分模型
2. 三档足够区分：确定性命中 / 部分匹配 / 冲突
3. 后续可细化，但接口签名不变

### JSON 文件的理由

1. 无外部依赖，开箱即用
2. 证据量在 Phase 0-1 很小，不需要数据库
3. 后续迁移到 EvidenceStoreProvider 时数据结构不变

## 后果

- 证据写入使用 JSON 文件，一个证据一个文件或 JSON Lines
- 证据查询通过内存索引或简单文件扫描实现
- 扩展字段在 Phase 0-1 中可以不填写

## 暂不做

- 证据冲突自动检测（contradicted_by 手动维护）
- 证据新鲜度自动计算
- 证据图或关系查询
