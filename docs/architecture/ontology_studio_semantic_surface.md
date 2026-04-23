# Ontology Studio Semantic Surface Expansion — 架构文档

## N1.7 — Ontology Studio Semantic Surface Expansion

**版本**: 1.0
**日期**: 2026-04-23
**里程碑**: N1.7

---

## 1. 目标与动机

### 1.1 问题背景

N1.6 完成了 Studio Contract Closure，建立了二元结构：
- Supported：event, context, fact
- Reserved：entity, relation, policy

但存在以下问题：

1. **entity 是本体核心，不应作为 reserved**：entity 是所有 ontology 的基础类型，将其标记为 reserved 阻碍了完整本体语义的表达

2. **relation/policy 不应等同于"不支持"**：这两类复杂类型需要更精细的边界定义，而非简单归入 reserved

3. **Edge 只能画线，没有语义**：边在 N1.6 中只有 derives 是 supported，其他边类型都是 reserved，但实际上 relates/triggers/requires 都有明确的编译目标

4. **Source of Truth 模糊**：Studio 设计时和 Runtime 运行时的主从关系不清晰

### 1.2 N1.7 目标

将 Studio 从"可视化骨架"推进到"语义完整的设计平台"：

1. **Surface 三层结构**：Supported / Preview / Reserved
2. **Entity 正式支持**：entity 升级为 Supported
3. **Relation/Policy 预览支持**：介于 supported 和 reserved 之间，明确信息丢失边界
4. **Edge Semantics**：边有明确的编译目标，不再只是画线
5. **Source of Truth 明确化**：AuthoringPackage > RuntimePackage

---

## 2. Semantic Surface 三层结构

### 2.1 三层定义

| 层级 | 定义 | 编译承诺 | 运行时状态 |
|------|------|----------|------------|
| **Supported** | 正式支持，完整语义 | 完整编译，无信息丢失 | 可完整映射到 Schema |
| **Preview** | 预览支持，部分语义 | 部分编译，明确信息丢失 | 可部分映射，记录丢失字段 |
| **Reserved** | 预留不支持 | 不承诺编译 | 仅作设计占位 |

### 2.2 N1.7 Surface 分布

#### Node Types

| 类型前缀 | 层级 | 说明 |
|----------|------|------|
| `event` | Supported | 事件类型，完整支持 |
| `context` | Supported | 上下文类型，完整支持 |
| `fact` | Supported | 事实类型，完整支持 |
| `entity` | Supported（N1.7 新增） | 实体类型，完整支持 |
| `relation` | Preview（N1.7 新增） | 关系类型，部分支持 |
| `policy` | Preview（N1.7 新增） | 策略类型，部分支持 |

#### Edge Types

| Edge ID | 层级 | 编译目标 | 语义说明 |
|---------|------|----------|----------|
| `derives` | Supported | Visual-only | 推导关系，由 GovernanceEngine 处理 |
| `relates` | Preview（N1.7 新增） | RelationType | 实体间关系 |
| `triggers` | Preview（N1.7 新增） | PolicyBinding.trigger | 策略触发条件 |
| `requires` | Preview（N1.7 新增） | PolicyBinding.condition | 策略约束条件 |
| `contains` | Preview（N1.7 新增） | Visual-only | 组合关系，不编译 |

### 2.3 与 N1.6 的对比

| 类型 | N1.6 状态 | N1.7 状态 | 变化 |
|------|-----------|-----------|------|
| entity | Reserved | Supported | 升级 |
| relation | Reserved | Preview | 升级（部分支持） |
| policy | Reserved | Preview | 升级（部分支持） |
| relates | Reserved | Preview | 升级（有编译目标） |
| triggers | Reserved | Preview | 升级（有编译目标） |
| requires | Reserved | Preview | 升级（有编译目标） |

---

## 3. Edge Semantics 编译规则

### 3.1 Edge 编译目标

```
Edge.type_id          → Compilation Target
─────────────────────────────────────────────
derives               → Visual-only（不编译）
relates               → RelationType
triggers              → PolicyBinding.trigger
requires              → PolicyBinding.condition
contains              → Visual-only（不编译）
```

### 3.2 RelationType 编译规则

`relates` 边编译为 `RelationType`：

```python
VisualEdge(
    type_id="relates",
    source_id="entity-agent",
    target_id="entity-role",
    properties={"cardinality": "one-to-many"}
)
                ↓ 编译
RelationType(
    id="relates-1",
    source_type="agent",
    target_type="role",
    cardinality="one-to-many"  # Preview: 可能丢失
)
```

**Preview 信息丢失**：`cardinality`、`constraints` 字段不保证编译。

### 3.3 PolicyBinding 编译规则

`triggers` 边编译为 `PolicyBinding.trigger`：

```python
VisualEdge(
    type_id="triggers",
    source_id="event-tool-invocation",
    target_id="policy-review-rule"
)
                ↓ 编译
PolicyBinding(
    id="binding-triggers-1",
    trigger="tool-invocation",
    policy_type="review-rule",
    condition=None,
    judgment=None
)
```

`requires` 边编译为 `PolicyBinding.condition`：

```python
VisualEdge(
    type_id="requires",
    source_id="policy-review-rule",
    target_id="entity-agent"
)
                ↓ 编译
PolicyBinding(
    id="binding-requires-1",
    trigger=None,
    condition="agent",
    policy_type="review-rule"
)
```

### 3.4 Visual-only Edge

`derives` 和 `contains` 边不编译为 Schema：

- `derives`：推导关系由 GovernanceEngine 在运行时处理，不存储在 Schema 中
- `contains`：组合关系仅用于设计时组织，不进入运行时

---

## 4. Source of Truth 主从关系

### 4.1 架构图

```
┌─────────────────────────────────────────────────────────────┐
│  Design-Time (Studio)                                        │
│                                                              │
│  1. AuthoringPackage (持久化)                                 │
│     ├─ studio_manifest.yaml (Surface 声明)                   │
│     ├─ visual_graph.yaml (用户设计)                          │
│     ├─ form_schemas.yaml (表单定义)                          │
│     └─ catalog_index.yaml (类型索引)                         │
│                                                              │
│  Source of Truth: AuthoringPackage                           │
│  - 所有设计意图在这里定义                                      │
│  - 是 Studio 导出/导入的唯一格式                               │
│  - 不依赖 Runtime                                            │
└─────────────────────────────────────────────────────────────┘
                          ↓ compile_authoring_to_runtime()
┌─────────────────────────────────────────────────────────────┐
│  Run-Time (GovernanceEngine)                                 │
│                                                              │
│  2. RuntimePackage (编译产物)                                 │
│     ├─ OntologySchema (EventType, EntityType, FactType...)   │
│     ├─ RelationTypes (from relates edges)                    │
│     ├─ PolicyBindings (from triggers/requires edges)         │
│     └─ evidence_chain_templates (推导规则)                    │
│                                                              │
│  Source of Truth: RuntimePackage                             │
│  - 运行时唯一权威数据源                                        │
│  - 不保证反向编译回 Authoring（Preview 类型信息有损）           │
│  - GovernanceEngine 直接消费                                  │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 主从关系声明

**AuthoringPackage > RuntimePackage**：

1. AuthoringPackage 是设计意图的 Source of Truth
2. RuntimePackage 是 AuthoringPackage 的编译产物
3. 编译可能存在信息丢失（Preview 类型）
4. 不承诺反向编译（Runtime → Authoring）

### 4.3 Package 边界

#### AuthoringPackage 包含

- Visual design intent（节点、边、位置、颜色）
- Form schemas（用户交互定义）
- Semantic Surface declarations（支持状态声明）
- Catalog index（类型注册）

#### RuntimePackage 包含

- Ontology types（Schema 结构）
- Relation bindings（relates 边编译结果）
- Policy bindings（triggers/requires 边编译结果）
- Evidence chain templates（推导规则）

---

## 5. 编译承诺与信息丢失

### 5.1 Supported 类型编译承诺

| 类型 | 保证编译字段 |
|------|-------------|
| event | node_id, label, subject_type, object_type, properties, timestamp_field |
| context | node_id, label, properties, lifecycle |
| fact | node_id, label, subject_type, object_type, establishment_condition, evidence_binding |
| entity | node_id, label, entity_type, properties, identity_fields |

### 5.2 Preview 类型信息丢失

| 类型 | 保证字段 | 不保证字段 |
|------|----------|-----------|
| relation | node_id, label, source_entity_type, target_entity_type | cardinality, properties, constraints |
| policy | node_id, label, policy_type | conditions, judgments, scope, priority |

### 5.3 Visual-only 字段

以下字段不进入 Runtime：

- `visual_hint`
- `color`
- `position`
- `min_instances`
- `max_instances`
- `metadata`

---

## 6. 为什么 N1.7 后再做 N2/N3 合理

### 6.1 N1.7 解决的核心问题

1. **本体语义完整**：entity 正式支持，Studio 可表达完整本体结构
2. **Edge 有语义**：边不再只是画线，有明确的编译目标
3. **边界清晰**：三层 Surface 让 Preview 类型的信息丢失明确化
4. **Source of Truth 明确**：设计时和运行时的主从关系清晰

### 6.2 为后续里程碑铺路

- **N2 Governance Loop**：需要完整的本体类型（entity 正式支持）
- **N3 Query Language**：需要 RelationType（relates 边编译）
- **N4 GovernanceEngine**：需要 PolicyBinding（triggers/requires 边编译）

### 6.3 升级路径

```
N1.6 (二元结构) → N1.7 (三层结构)
  entity: Reserved → Supported
  relation/policy: Reserved → Preview
  edges: Reserved → Preview (with semantics)
```

---

## 7. 实现文件

### 7.1 新增文件

| 文件 | 说明 |
|------|------|
| `ontology/semantic_surface.py` | SemanticSurface 数据结构，三层检测函数 |
| `ontology/edge_semantics.py` | Edge 编译规则，RelationType/PolicyBinding 编译 |
| `ontology/authoring_package.py` | AuthoringPackage / RuntimePackage 模型 |
| `tests/unit/test_semantic_surface_contract.py` | Contract 级测试 |
| `schemas/ontology/studio_manifest.yaml` | 更新 manifest 以支持三层结构 |

### 7.2 修改文件

| 文件 | 修改内容 |
|------|----------|
| `ontology/studio_loader.py` | 加载 SemanticSurface，支持 preview categories |
| `ontology/validation.py` | Preview 类型发 warning，Reserved 类型发 error |
| `ontology/roundtrip.py` | 支持 Preview 边的部分编译 |
| `ontology/__init__.py` | 导出 N1.7 新类型 |

---

## 8. 测试覆盖

N1.7 新增测试覆盖：

- SemanticSurface 三层结构测试
- Supported / Preview / Reserved 节点类型检测
- Edge semantics 编译规则测试
- AuthoringPackage → RuntimePackage 编译测试
- Preview 类型信息丢失报告测试
- Studio Manifest 加载测试（含 preview categories）

目标：25+ 新测试，确保三层 Surface 和 Edge Semantics 的边界清晰。

---

## 9. 完成标准

完成后，仓库可回答：

1. ✓ Ontology Studio 能设计哪些本体语义（supported + preview）
2. ✓ entity/relation/policy 的平台状态明确
3. ✓ Edge 有正式语义（不再是画线）
4. ✓ Studio 和 Runtime 的 Source of Truth 清晰
5. ✓ 为什么 N1.7 后再做 N2/N3 合理（语义边界清晰，为后续铺路）

---

## 10. 附录：SemanticSurface 数据结构

```python
@dataclass(frozen=True)
class SemanticSurface:
    """三层语义 Surface：supported / preview / reserved"""

    # Node type prefixes
    supported_node_prefixes: list[str]  # event, context, fact, entity
    preview_node_prefixes: list[str]    # relation, policy
    reserved_node_prefixes: list[str]   # 无

    # Edge types
    supported_edge_types: list[str]     # derives
    preview_edge_types: list[str]       # relates, triggers, requires, contains
    reserved_edge_types: list[str]      # 无

    # Compilation promises
    supported_compilation_fields: dict[str, list[str]]
    preview_partial_fields: dict[str, list[str]]

    # Edge semantics
    edge_compilation_targets: dict[str, EdgeCompilationTarget]
    visual_only_edges: list[str]
```

```python
@dataclass(frozen=True)
class EdgeCompilationTarget:
    """Edge 编译目标声明"""

    target_type: Literal["relation_type", "policy_binding", "visual_only"]
    target_field: str | None
    is_visual_only: bool
    compilation_notes: str
```