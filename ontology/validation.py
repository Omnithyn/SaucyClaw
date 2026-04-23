"""Ontology Validation — 一致性校验。

N1.5 — Ontology Platform Architecture & Visual Authoring Foundation

提供比 loader 中 validate_ontology_schema 更深层的一致性校验：
- 跨类型引用检查（subject_type / object_type 是否存在）
- 可视化图校验（悬空边、重复节点、类型匹配）
- 属性完整性校验
- 必填字段检查

与 loader 的区别：
- loader.validate_ontology_schema：基础校验（ID 重复）
- 本模块：深度校验（引用、图结构、属性）
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ontology.catalog import OntologyCatalog
from ontology.schema import OntologySchema
from ontology.visual_model import VisualGraph


@dataclass(frozen=True)
class ValidationResult:
    """校验结果。

    Attributes:
        is_valid: 是否通过
        errors: 错误列表
        warnings: 警告列表
    """

    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def validate_schema_references(schema: OntologySchema) -> ValidationResult:
    """校验 Schema 跨类型引用。

    检查项：
    1. EventType.subject_type / object_type 是否有对应 EntityType
    2. FactType.subject_type / object_type 是否有对应 EntityType
    3. PolicyBinding 绑定的类型是否存在

    注意：此函数目前只做最小检查，
    完整 EntityType 引用校验需要 core/meta_model 的参与。
    """
    errors: list[str] = []
    warnings: list[str] = []

    # 收集所有已知类型 ID（用于交叉引用）
    known_types: set[str] = set()
    for et in schema.event_types:
        known_types.add(et.id)
    for ct in schema.context_types:
        known_types.add(ct.id)
    for ft in schema.fact_types:
        known_types.add(ft.id)

    # 检查 FactType 的 establishment_condition 是否引用了已知类型
    for ft in schema.fact_types:
        if ft.establishment_condition:
            cond = ft.establishment_condition
            # 最小检查：条件不应为空
            if not cond.strip():
                errors.append(
                    f"FactType {ft.id!r} 的 establishment_condition 为空"
                )

    # 检查 EventType 的属性不应为空
    for et in schema.event_types:
        if not et.subject_type:
            errors.append(f"EventType {et.id!r} 缺少 subject_type")

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )


def validate_visual_graph(graph: VisualGraph) -> ValidationResult:
    """校验可视化图结构。

    检查项：
    1. 节点 ID 唯一性
    2. 边引用的源/目标节点是否存在（悬空边检查）
    3. 边的源 != 目标（自环检查，仅 warn）
    """
    errors: list[str] = []
    warnings: list[str] = []

    node_ids: set[str] = set()

    # 检查节点 ID 唯一性
    for node in graph.nodes:
        if node.node_id in node_ids:
            errors.append(f"节点 ID {node.node_id!r} 重复")
        node_ids.add(node.node_id)

    # 检查边引用
    for edge in graph.edges:
        if edge.source_id not in node_ids:
            errors.append(
                f"边 {edge.edge_id!r} 的源节点 {edge.source_id!r} "
                f"不存在（悬空边）"
            )
        if edge.target_id not in node_ids:
            errors.append(
                f"边 {edge.edge_id!r} 的目标节点 {edge.target_id!r} "
                f"不存在（悬空边）"
            )
        if edge.source_id == edge.target_id:
            warnings.append(
                f"边 {edge.edge_id!r} 是自环（{edge.source_id!r}）"
            )

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )


def validate_catalog_completeness(
    catalog: OntologyCatalog,
) -> ValidationResult:
    """校验 Catalog 完整性。

    检查项：
    1. Catalog 不应为空（至少有一种类型）
    2. 如果存在 FactType，应有对应的 EventType（事实通常由事件推导）
    """
    errors: list[str] = []
    warnings: list[str] = []

    type_counts = catalog.type_count()
    total = sum(type_counts.values())

    if total == 0:
        errors.append("Catalog 为空：没有任何已注册的类型")

    # 如果有 FactType 但没有 EventType，发出警告
    if type_counts["fact"] > 0 and type_counts["event"] == 0:
        warnings.append(
            "Catalog 有 FactType 但没有 EventType："
            "事实通常由事件推导，建议同时定义 EventType"
        )

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )


def validate_full_ontology(
    schema: OntologySchema,
    catalog: OntologyCatalog | None = None,
) -> ValidationResult:
    """完整本体校验：合并所有检查项。

    Args:
        schema: 本体 Schema
        catalog: 可选 Catalog（如果为 None，从 schema 构建）

    Returns:
        合并后的 ValidationResult
    """
    all_errors: list[str] = []
    all_warnings: list[str] = []

    # 基础 ID 唯一性检查（loader 层已有，这里也做）
    for category, items in [
        ("EventType", schema.event_types),
        ("ContextType", schema.context_types),
        ("FactType", schema.fact_types),
    ]:
        seen: set[str] = set()
        for item in items:
            if item.id in seen:
                all_errors.append(f"{category} ID {item.id!r} 重复")
            seen.add(item.id)

    # 引用检查
    ref_result = validate_schema_references(schema)
    all_errors.extend(ref_result.errors)
    all_warnings.extend(ref_result.warnings)

    # Catalog 完整性检查
    cat = catalog or OntologyCatalog.from_schema(schema)
    cat_result = validate_catalog_completeness(cat)
    all_errors.extend(cat_result.errors)
    all_warnings.extend(cat_result.warnings)

    return ValidationResult(
        is_valid=len(all_errors) == 0,
        errors=all_errors,
        warnings=all_warnings,
    )
