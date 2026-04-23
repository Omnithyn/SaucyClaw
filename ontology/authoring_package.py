"""Ontology Authoring Package — 设计时持久化与运行时编译包。

N1.7 — Ontology Studio Semantic Surface Expansion

定义 Studio 设计时的持久化格式和运行时编译产物：
- AuthoringPackage：设计意图持久化（Source of Truth for Design）
- RuntimePackage：运行时编译产物（Source of Truth for Execution）
- 编译函数与信息丢失报告

Source of Truth 主从关系：
- AuthoringPackage > RuntimePackage（设计时是主，运行时是从）
- AuthoringPackage 不依赖 Runtime
- RuntimePackage 不保证反向编译回 Authoring（Preview 类型信息有损）
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from ontology.edge_semantics import (
    EdgeCompilationResult,
    compile_edges_from_visual_graph,
)
from ontology.roundtrip import visual_graph_to_schema
from ontology.schema import OntologySchema
from ontology.semantic_surface import (
    SemanticSurface,
    get_semantic_surface,
    get_unsupported_fields_for_node_type,
    is_preview_node_type,
)
from ontology.visual_model import VisualGraph

# N1.7: RelationType 在 core.meta_model 中定义
from core.meta_model.models import RelationType


# ─── Compilation Report ───


@dataclass(frozen=True)
class CompilationReport:
    """编译报告：记录信息丢失和转换状态。

    Attributes:
        is_complete: 是否完整编译（无信息丢失）
        supported_types: 正式支持的类型数量
        preview_types: 预览支持的类型数量（部分编译）
        visual_only_elements: 仅用于可视化的元素数量
        information_loss_notes: 信息丢失说明（Preview 类型）
        edge_compilation_result: 边编译结果
        warnings: 编译警告列表
    """

    is_complete: bool
    supported_types: int
    preview_types: int
    visual_only_elements: int
    information_loss_notes: dict[str, str] = field(default_factory=dict)
    edge_compilation_result: EdgeCompilationResult | None = None
    warnings: list[str] = field(default_factory=list)


# ─── Authoring Package ───


@dataclass(frozen=True)
class AuthoringPackage:
    """设计时持久化包。

    Studio 导出/导入的唯一格式，是设计意图的 Source of Truth。

    Attributes:
        package_id: 包唯一标识
        version: 包版本
        name: 包名称
        description: 包描述
        visual_graph: 可视化图（节点、边、布局）
        form_schemas: 表单定义列表（用户交互）
        catalog_index: 类型注册索引
        surface: 语义 Surface（支持状态声明）
        metadata: 元数据
    """

    package_id: str
    version: str = "1.0"
    name: str = ""
    description: str = ""
    visual_graph: VisualGraph | None = None
    form_schemas: list[Any] = field(default_factory=list)
    catalog_index: dict[str, str] = field(default_factory=dict)
    surface: SemanticSurface | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


# ─── Runtime Package ───


@dataclass(frozen=True)
class RuntimePackage:
    """运行时编译包。

    GovernanceEngine 直接消费的格式，是运行时的 Source of Truth。

    Attributes:
        package_id: 包唯一标识（与 AuthoringPackage 对应）
        version: 编译版本
        ontology_schema: 本体 Schema（Event/Context/Fact/Entity 类型）
        relation_types: 关系类型（从 relates 边编译）
        policy_bindings: 策略绑定（从 triggers/requires 边编译）
        compilation_report: 编译报告（记录信息丢失）
        metadata: 元数据
    """

    package_id: str
    version: str = "1.0"
    ontology_schema: OntologySchema = field(default_factory=OntologySchema)
    relation_types: list[RelationType] = field(default_factory=list)
    policy_bindings: list[Any] = field(default_factory=list)
    compilation_report: CompilationReport | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


# ─── Compilation Function ───


def compile_authoring_to_runtime(
    authoring: AuthoringPackage,
    strict: bool = False,
) -> RuntimePackage:
    """将 AuthoringPackage 编译为 RuntimePackage。

    Args:
        authoring: 设计时包
        strict: 严格模式（遇到不支持元素抛异常）

    Returns:
        RuntimePackage: 运行时编译包

    Note:
        - Supported 类型：完整编译，无信息丢失
        - Preview 类型：部分编译，记录信息丢失
        - Visual-only 边：不编译，记录在 compilation_report
        - Strict=True：遇到 Preview 类型信息丢失抛异常
    """
    surface = authoring.surface or get_semantic_surface()

    if authoring.visual_graph is None:
        return RuntimePackage(
            package_id=authoring.package_id,
            version=authoring.version,
            ontology_schema=OntologySchema(),
            relation_types=[],
            policy_bindings=[],
            compilation_report=CompilationReport(
                is_complete=True,
                supported_types=0,
                preview_types=0,
                visual_only_elements=0,
                warnings=["AuthoringPackage 不包含 VisualGraph"],
            ),
            metadata=authoring.metadata,
        )

    graph = authoring.visual_graph
    nodes_dict = {n.node_id: n for n in graph.nodes}

    # 1. 编译节点为 OntologySchema
    # 使用 SemanticSurface（N1.7）而非 SupportedSurface
    schema = visual_graph_to_schema(
        graph,
        strict=strict,
        surface=surface,  # 直接传递 SemanticSurface
    )

    # 2. 编译边为 RelationType / PolicyBinding
    edge_result = compile_edges_from_visual_graph(
        graph.edges,
        nodes_dict,
        surface,
        strict=strict,
    )

    # 3. 计算编译报告
    supported_count = 0
    preview_count = 0
    visual_only_count = len(edge_result.visual_only_edges)
    info_loss: dict[str, str] = {}
    warnings: list[str] = []

    for node in graph.nodes:
        if is_preview_node_type(node.type_id, surface):
            preview_count += 1
            unsupported_fields = get_unsupported_fields_for_node_type(
                node.type_id, surface
            )
            if unsupported_fields:
                info_loss[node.node_id] = (
                    f"节点 {node.node_id!r} 是 Preview 类型"
                    f"，以下字段不保证编译: {unsupported_fields}"
                )
        else:
            supported_count += 1

    # Preview 边的信息丢失
    for edge_id, note in edge_result.partial_compilation_notes.items():
        info_loss[edge_id] = note

    # 合并警告
    warnings.extend(edge_result.compilation_warnings)

    report = CompilationReport(
        is_complete=len(info_loss) == 0 and len(warnings) == 0,
        supported_types=supported_count,
        preview_types=preview_count,
        visual_only_elements=visual_only_count,
        information_loss_notes=info_loss,
        edge_compilation_result=edge_result,
        warnings=warnings,
    )

    return RuntimePackage(
        package_id=authoring.package_id,
        version=authoring.version,
        ontology_schema=schema,
        relation_types=edge_result.relation_types,
        policy_bindings=edge_result.policy_bindings,
        compilation_report=report,
        metadata=authoring.metadata,
    )


# ─── Package IO ───


def save_authoring_package(
    authoring: AuthoringPackage,
    path: Path | str,
) -> None:
    """保存 AuthoringPackage 到文件。

    Args:
        authoring: 设计时包
        path: 文件路径（YAML 格式）
    """
    p = Path(path)

    data = {
        "package_id": authoring.package_id,
        "version": authoring.version,
        "name": authoring.name,
        "description": authoring.description,
        "visual_graph": (
            _visual_graph_to_dict(authoring.visual_graph)
            if authoring.visual_graph
            else None
        ),
        "form_schemas": authoring.form_schemas,
        "catalog_index": authoring.catalog_index,
        "metadata": authoring.metadata,
    }

    with open(p, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)


def load_authoring_package(
    path: Path | str,
) -> AuthoringPackage:
    """从文件加载 AuthoringPackage。

    Args:
        path: 文件路径（YAML 格式）

    Returns:
        AuthoringPackage
    """
    from ontology.visual_model import VisualGraph, VisualNode, VisualEdge

    p = Path(path)

    if not p.exists():
        raise FileNotFoundError(f"AuthoringPackage 文件不存在: {p}")

    with open(p) as f:
        data = yaml.safe_load(f) or {}

    # 解析 VisualGraph
    graph_data = data.get("visual_graph")
    graph = None
    if graph_data:
        nodes = [
            VisualNode(
                node_id=n["node_id"],
                type_id=n["type_id"],
                label=n.get("label", n["node_id"]),
                properties=n.get("properties"),
                visual_hint=n.get("visual_hint"),
                color=n.get("color"),
                position=n.get("position"),
                min_instances=n.get("min_instances"),
                max_instances=n.get("max_instances"),
                metadata=n.get("metadata"),
            )
            for n in graph_data.get("nodes", [])
        ]

        edges = [
            VisualEdge(
                edge_id=e["edge_id"],
                type_id=e["type_id"],
                source_id=e["source_id"],
                target_id=e["target_id"],
                label=e.get("label"),
                properties=e.get("properties"),
                directed=e.get("directed", True),
                metadata=e.get("metadata"),
            )
            for e in graph_data.get("edges", [])
        ]

        graph = VisualGraph(
            graph_id=graph_data.get("graph_id", data.get("package_id")),
            name=graph_data.get("name", ""),
            nodes=nodes,
            edges=edges,
            metadata=graph_data.get("metadata"),
        )

    return AuthoringPackage(
        package_id=data.get("package_id", "unknown"),
        version=data.get("version", "1.0"),
        name=data.get("name", ""),
        description=data.get("description", ""),
        visual_graph=graph,
        form_schemas=data.get("form_schemas", []),
        catalog_index=data.get("catalog_index", {}),
        surface=get_semantic_surface(),
        metadata=data.get("metadata", {}),
    )


# ─── Internal Helpers ───


def _convert_semantic_surface_to_supported_surface(
    semantic: SemanticSurface,
) -> Any:
    """将 SemanticSurface 转换为 studio_loader.SupportedSurface 格式。

    用于兼容 N1.6 的 visual_graph_to_schema 函数。
    """
    from ontology.studio_loader import SupportedSurface

    # 合并 supported + preview 作为"支持"的类型
    # 这样 visual_graph_to_schema 可以处理 preview 类型
    all_supported = (
        semantic.supported_node_prefixes
        + semantic.preview_node_prefixes
    )

    return SupportedSurface(
        supported_node_prefixes=all_supported,
        reserved_node_prefixes=semantic.reserved_node_prefixes,
        supported_edge_types=(
            semantic.supported_edge_types + semantic.preview_edge_types
        ),
        reserved_edge_types=semantic.reserved_edge_types,
        supported_node_fields=[],  # 由 semantic surface 管理
        ignored_visual_fields=["visual_hint", "color", "position", "metadata"],
    )


def _visual_graph_to_dict(graph: VisualGraph) -> dict[str, Any]:
    """将 VisualGraph 转换为字典格式（用于 YAML 导出）。"""
    if graph is None:
        return None

    return {
        "graph_id": graph.graph_id,
        "name": graph.name,
        "nodes": [
            {
                "node_id": n.node_id,
                "type_id": n.type_id,
                "label": n.label,
                "properties": n.properties,
                "visual_hint": n.visual_hint,
                "color": n.color,
                "position": n.position,
                "min_instances": n.min_instances,
                "max_instances": n.max_instances,
                "metadata": n.metadata,
            }
            for n in graph.nodes
        ],
        "edges": [
            {
                "edge_id": e.edge_id,
                "type_id": e.type_id,
                "source_id": e.source_id,
                "target_id": e.target_id,
                "label": e.label,
                "properties": e.properties,
                "directed": e.directed,
                "metadata": e.metadata,
            }
            for e in graph.edges
        ],
        "metadata": graph.metadata,
    }
