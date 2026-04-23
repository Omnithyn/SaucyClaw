# Ontology Studio Contract

> N1.6 — Ontology Studio Contract Closure
>
> 本文档定义 Ontology Studio 当前正式支持的能力边界，明确承诺 vs 预留。

## 一、合同声明

Ontology Studio 当前处于 **"最小可构建平台"（N1.5-N1.6）阶段**，不承诺完整可视化编辑能力，只承诺以下核心能力：

1. **Visual Model 规范定义**：VisualNode / VisualEdge / VisualGraph / Palette 等类型已定义
2. **Catalog 索引构建**：可从 OntologySchema 或 Studio Manifest 构建 OntologyCatalog
3. **Validation 一致性校验**：可校验 VisualGraph 结构完整性
4. **Round-Trip 三向转换**：对**正式支持的元素**保证 YAML ↔ Visual ↔ Schema 等价

**未承诺的能力**（预留）：
- 完整可视化编辑器 UI
- 图数据库存储
- Relation / Policy / Entity 的完整 round-trip
- 复杂 edge types 的运行时投影

## 二、正式支持的 Node Types

### 当前承诺

| 类别 | Node Type 前缀 | Round-Trip 支持 | 映射目标 |
|------|---------------|-----------------|----------|
| Event | `event-*` | **完整** | EventType |
| Context | `context-*` | **完整** | ContextType |
| Fact | `fact-*` | **完整** | FactType |

### Round-Trip 保证覆盖的字段

| Visual Node 属性 | Runtime Schema 字段 | 保证级别 |
|------------------|---------------------|----------|
| `node_id` | `id` | **完整映射** |
| `label` | `name` | **完整映射** |
| `properties.subject_type` | `subject_type` | **完整映射** |
| `properties.object_type` | `object_type` | **完整映射** |
| `properties.properties` | `properties` | **完整映射** |
| `properties.establishment_condition` | `establishment_condition` | **完整映射** |
| `properties.lifecycle` | `lifecycle` | **完整映射** |

### Visual-only 元数据（不进入 Runtime）

| Visual Node 属性 | 用途 | 运行时处理 |
|------------------|------|-----------|
| `visual_hint` | 图标/形状提示 | **忽略** |
| `color` | 节点颜色 | **忽略** |
| `position` | 画布位置 | **忽略** |
| `min_instances` / `max_instances` | 实例数约束 | **忽略** |
| `metadata` | 设计时附加信息 | **忽略** |

### Runtime-only 元数据（不来自 Visual）

| Runtime Schema 字段 | 来源 | 设计时处理 |
|---------------------|------|-----------|
| `timestamp_field` | YAML 默认值 | **设为默认** |
| `evidence_binding` | FactType 默认值 | **设为默认** |
| `description` | YAML 或 Manifest | **部分映射** |

## 三、正式支持的 Edge Types

### 当前承诺

| Edge Type ID | 语义 | Visual 支持 | Runtime 支持 |
|--------------|------|-------------|--------------|
| `derives` | 事件推导事实 | **支持** | **忽略（不进入 Schema）** |

### 边的运行时处理

边在 VisualGraph → OntologySchema 转换中**被忽略**，因为 OntologySchema 不存储图结构。边的作用是：
- 设计时可视化关系表达
- 为未来 N3（查询语言）预留语义基础

## 四、预留能力（未正式支持）

### 预留的 Node Types

| 类别 | Node Type 前缀 | 状态 | 依赖 |
|------|---------------|------|------|
| Entity | `entity-*` | 预留 | 需要 meta_model EntityType 对齐 |
| Relation | `relation-*` | 预留 | 需要 RelationType 边类型完善 |
| Policy | `policy-*` | 预留 | 需要 PolicyBinding 与 GovernanceRule 对齐 |

### 预留的 Edge Types

| Edge Type ID | 语义 | 状态 |
|--------------|------|------|
| `relates` | 实体关系 | 预留 |
| `triggers` | 事件触发事件 | 预留 |
| `requires` | 事实依赖事实 | 预留 |
| `binds` | 策略绑定事实 | 预留 |

### 对未支持元素的处理

当 VisualGraph 包含未正式支持的 node/edge 类型时：
- **Validation**：发出 `error`（而非 `warning`）
- **Round-Trip**：抛出 `RoundTripUnsupportedError`
- **不会悄悄忽略**

## 五、Source of Truth 层级

```
┌─────────────────────────────────────────────────┐
│          schemas/ontology/*.yaml                │
│          （Runtime Schema - 最终 truth）         │
└─────────────────────┬───────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│     schemas/ontology/studio_manifest.yaml       │
│     （Studio Manifest - 设计时 truth）          │
└─────────────────────┬───────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│              OntologyCatalog                     │
│              （内存注册表 - 运行时索引）          │
└─────────────────────────────────────────────────┘
```

**优先级**：
- Runtime Schema > Studio Manifest（冲突时以 Runtime Schema 为准）
- Catalog 是索引层，不产生新类型

## 六、Studio Manifest 结构

`schemas/ontology/studio_manifest.yaml` 组织以下内容：

```yaml
# Studio 设计时入口
studio:
  version: "1.0"

  # 正式支持的 node categories
  supported_categories:
    - id: "event"
      name: "事件类型"
      color: "#4A90D9"
      node_types: ["event-tool-invocation", "event-task-assignment", "event-review-request"]
    - id: "context"
      name: "上下文类型"
      color: "#5DA5DA"
      node_types: ["context-session", "context-workspace", "context-execution"]
    - id: "fact"
      name: "事实类型"
      color: "#FAA43A"
      node_types: ["fact-review-requirement", "fact-permission-grant"]

  # 正式支持的 edge types
  supported_edge_types:
    - id: "derives"
      name: "推导出"
      source_category: "event"
      target_category: "fact"

  # Form schemas（可选）
  form_schemas: []
```

## 七、为什么先收紧 Studio Contract

| 先收紧 Contract | 先做 N2/N3 |
|-----------------|-----------|
| 明确边界，避免过度承诺 | 可能在预留能力上浪费工作 |
| 为 N3 查询语言提供清晰的 supported surface | 查询语言可能建立在未稳定基础上 |
| 让 Studio 用户知道当前能做什么 | 用户可能误以为 Studio 已完整 |
| 为未来 UI 编辑器建立合同级约束 | UI 可能承诺未实现能力 |

**结论**：N1.6 收紧合同后，N3 查询语言和 N2 治理闭环才能建立在稳定承诺之上。

## 八、版本与变更控制

本合同属于 **架构级文档**，变更需：
- 更新 `docs/architecture/ontology_studio_contract.md`
- 同步更新 `schemas/ontology/studio_manifest.yaml`
- 同步更新 `ontology/studio_loader.py` 和 `ontology/roundtrip.py`
- 通过 contract 级测试验证