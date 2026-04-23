# Ontology Package Compilation Pipeline

N1.8 — Ontology Package Compilation & Projection Pipeline

## 概述

本文档描述 Ontology Package 的编译和投影流程：

- **编译**：AuthoringPackage → RuntimePackage
- **投影**：RuntimePackage → VisualGraph
- **Round-trip 保证**：Supported 元素完整往返，Preview 元素有损

## Source of Truth

编译流程遵循以下 Source of Truth 优先级：

```
AuthoringPackage > RuntimePackage > VisualGraph（投影）
```

- **AuthoringPackage**：设计时的唯一真实来源
- **RuntimePackage**：运行时的真实来源（从 Authoring 编译）
- **VisualGraph（投影）**：可视化预览（从 Runtime 投影）

## Package 结构

### AuthoringPackage（设计时）

```python
@dataclass(frozen=True)
class AuthoringPackage:
    package_id: str
    version: str
    name: str
    description: str
    visual_graph: VisualGraph | None  # 可视化图（节点、边、布局）
    form_schemas: list[Any]           # 表单定义
    catalog_index: dict[str, str]     # 类型注册索引
    surface: SemanticSurface | None   # 语义 Surface
    metadata: dict[str, Any]          # 元数据
```

**用途**：
- Studio 导出/导入的唯一格式
- 设计意图的完整表达
- 支持 YAML 序列化/反序列化

### RuntimePackage（运行时）

```python
@dataclass(frozen=True)
class RuntimePackage:
    package_id: str
    version: str
    ontology_schema: OntologySchema  # Event/Context/Fact 类型
    relation_types: list[RelationType]  # 关系类型（从 relates 边编译）
    policy_bindings: list[Any]       # 策略绑定（从 triggers/requires 边编译）
    compilation_report: CompilationReport | None  # 编译报告
    metadata: dict[str, Any]
```

**用途**：
- GovernanceEngine 直接消费的格式
- 运行时决策的真实来源
- 信息丢失被记录但不可逆

### CompilationReport（编译报告）

```python
@dataclass(frozen=True)
class CompilationReport:
    is_complete: bool            # 是否完整编译（无信息丢失）
    supported_types: int         # Supported 类型数量
    preview_types: int           # Preview 类型数量
    visual_only_elements: int    # Visual-only 元素数量
    information_loss_notes: dict[str, str]  # 信息丢失说明
    warnings: list[str]          # 编译警告
```

## 编译流程

### PackageCompiler

```python
compiler = PackageCompiler(surface=SemanticSurface, strict=True)

# 1. 编译前校验
validation = compiler.validate_before_compile(authoring)
# ValidationResult: reserved_elements, unknown_elements, preview_elements

# 2. 编译
runtime = compiler.compile(authoring)
```

### 编译规则

| 元素类型 | Surface 层级 | 编译行为 |
|---------|-------------|---------|
| event-* 节点 | Supported | 完整编译 → EventType |
| context-* 节点 | Supported | 完整编译 → ContextType |
| fact-* 节点 | Supported | 完整编译 → FactType |
| entity-* 节点 | Supported | 跳过（OntologySchema 不包含 EntityType） |
| relation-* 节点 | Preview | 跳过（不编译到 Schema） |
| policy-* 节点 | Preview | 跳过（不编译到 Schema） |
| derives 边 | Visual-only | 跳过（不编译） |
| contains 边 | Visual-only | 跳过（不编译） |
| relates 边 | Preview | 部分编译 → RelationType |
| triggers 边 | Preview | 部分编译 → PolicyBinding.trigger |
| requires 边 | Preview | 部分编译 → PolicyBinding.condition |

### 编译流程图

```
AuthoringPackage
    │
    ├─ validate_before_compile()
    │   ├─ Reserved 元素 → 阻止编译（strict=True）
    │   ├─ Unknown 元素 → 阻止编译
    │   ├─ Preview 元素 → 警告信息丢失
    │   └─ Visual-only 边 → 警告跳过
    │
    ├─ compile_nodes() (visual_graph_to_schema)
    │   ├─ Supported 节点 → OntologySchema
    │   └─ Preview/Reserved 节点 → 跳过
    │
    ├─ compile_edges() (compile_edges_from_visual_graph)
    │   ├─ relates 边 → RelationType
    │   ├─ triggers 边 → PolicyBinding.trigger
    │   ├─ requires 边 → PolicyBinding.condition
    │   └─ Visual-only 边 → 跳过
    │
    ├─ build CompilationReport
    │   ├─ supported_types 计数
    │   ├─ preview_types 计数
    │   ├─ information_loss_notes 收集
    │   └─ warnings 收集
    │
    └─ RuntimePackage
```

## 投影流程

### Projector

```python
projector = Projector(surface=SemanticSurface)

# 投影 Runtime → Visual
graph, report = projector.project(runtime)
```

### 投影规则

| Runtime 元素 | 投影目标 | 信息丢失 |
|-------------|---------|---------|
| EventType | VisualNode (event-*) | 无（完整回流） |
| ContextType | VisualNode (context-*) | 无（完整回流） |
| FactType | VisualNode (fact-*) | 无（完整回流） |
| RelationType | VisualEdge (relates) | Preview 边部分字段丢失 |
| PolicyBinding | VisualEdge (triggers/requires) | Preview 边部分字段丢失 |

### 投影流程图

```
RuntimePackage
    │
    ├─ project OntologySchema
    │   ├─ EventType → VisualNode (event-*)
    │   ├─ ContextType → VisualNode (context-*)
    │   └─ FactType → VisualNode (fact-*)
    │
    ├─ project RelationTypes
    │   └─ RelationType → VisualEdge (relates)
    │       └─ 丢失：constraints 等额外字段
    │
    ├─ project PolicyBindings
    │   ├─ binds_to_event_type → VisualEdge (triggers)
    │   └─ binds_to_fact_type → VisualEdge (requires)
    │       └─ 丢失：conditions, judgments, scope 等字段
    │
    ├─ build ProjectionReport
    │   ├─ projected_nodes/edges 计数
    │   ├─ lost_fields 收集
    │   └─ warnings 收集（Preview 元素不可逆）
    │
    └─ VisualGraph + ProjectionReport
```

## Round-trip 保证

### Supported 元素

**完整往返保证**：

```
AuthoringPackage (Supported)
    → 编译 → RuntimePackage
    → 投影 → VisualGraph
    → 重新加载 → AuthoringPackage (无损)
```

保证字段：
- Event: node_id, label, subject_type, object_type, properties, timestamp_field
- Context: node_id, label, properties, lifecycle
- Fact: node_id, label, subject_type, object_type, establishment_condition

### Preview 元素

**单向编译，回流有损**：

```
AuthoringPackage (Preview)
    → 编译 → RuntimePackage (部分信息丢失)
    → 投影 → VisualGraph (部分信息丢失)
    → 重新加载 → AuthoringPackage (信息丢失不可逆)
```

丢失字段：
- Relation: cardinality, properties, constraints
- Policy: conditions, judgments, scope, priority

### Visual-only 元素

**不编译，仅可视化**：

```
AuthoringPackage (Visual-only 边)
    → 编译 → RuntimePackage (跳过)
    → 投影 → VisualGraph (无法恢复)
```

Visual-only 边：
- derives：推导关系（由 GovernanceEngine 处理）
- contains：组合关系（不编译）

## SemanticSurface 三层结构

编译和投影基于 SemanticSurface 三层结构：

```
Supported → 正式支持 → 完整编译/投影
Preview   → 预览支持 → 部分编译/有损投影
Reserved  → 预留不支持 → 阻止编译
```

当前配置（N1.7）：

| 类型 | Supported | Preview | Reserved |
|-----|-----------|---------|----------|
| 节点前缀 | event, context, fact, entity | relation, policy | （空） |
| 边类型 | derives | relates, triggers, requires, contains | （空） |

## 使用示例

### 编译 AuthoringPackage

```python
from ontology.authoring_package import AuthoringPackage
from ontology.compiler import compile_package

# 加载 AuthoringPackage
authoring = load_authoring_package("my_package.yaml")

# 编译为 RuntimePackage
runtime = compile_package(authoring, strict=True)

# 检查编译报告
if runtime.compilation_report.is_complete:
    print("完整编译，无信息丢失")
else:
    print(f"部分编译，{runtime.compilation_report.preview_types} 个 Preview 类型")
    for element_id, note in runtime.compilation_report.information_loss_notes.items():
        print(f"  {element_id}: {note}")
```

### 投影 RuntimePackage

```python
from ontology.projection import project_runtime_to_visual

# 投影为 VisualGraph
graph, report = project_runtime_to_visual(runtime)

# 检查投影报告
if report.is_complete:
    print("完整投影")
else:
    print(f"部分投影，丢失字段: {report.lost_fields}")
```

### Round-trip 验证

```python
from ontology.compiler import PackageCompiler
from ontology.projection import Projector

# 编译
compiler = PackageCompiler()
runtime = compiler.compile(authoring)

# 投影
projector = Projector()
projected_graph, projection_report = projector.project(runtime)

# 验证
assert runtime.compilation_report.is_complete
assert projection_report.is_complete
```

## 模块结构

```
ontology/
├── authoring_package.py  # AuthoringPackage, RuntimePackage, CompilationReport
├── compiler.py           # PackageCompiler, ValidationResult
├── projection.py         # Projector, ProjectionReport
├── semantic_surface.py   # SemanticSurface 三层结构
├── edge_semantics.py     # Edge 编译规则
├── roundtrip.py          # 节点编译/投影逻辑
├── validation.py         # VisualGraph 校验
└── studio_loader.py      # Studio Manifest 加载
```

## 测试验证

编译和投影流程的测试覆盖：

- `tests/unit/test_compilation.py`：PackageCompiler 和 Projector 测试
- `tests/unit/test_semantic_surface_contract.py`：SemanticSurface 三层测试
- `tests/unit/test_ontology_studio_contract.py`：Studio Contract 测试

测试命令：

```bash
pytest tests/unit/test_compilation.py -v
pytest tests/unit/test_semantic_surface_contract.py -v
pytest tests/unit/test_ontology_studio_contract.py -v
```

## 未来扩展

### N1.8 后续工作

1. **Entity 节点编译**：当前 Entity 节点跳过编译，未来可扩展
2. **Policy 节点编译**：当前 Policy 节点跳过，未来可扩展为 PolicyDefinition
3. **FormSchema 编译**：当前 FormSchema 不编译，未来可扩展为交互逻辑
4. **增量编译**：支持部分重新编译（仅修改元素）

### Semantic Surface 升级路径

```
Reserved → Preview → Supported
```

示例：
- N1.6：relation/policy 为 Reserved
- N1.7：relation/policy 升级为 Preview
- 未来：relation/policy 可能升级为 Supported（完整编译保证）