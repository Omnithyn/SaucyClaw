"""Ontology Semantic Surface — 三层语义 Surface 定义。

N1.7 — Ontology Studio Semantic Surface Expansion

定义 Studio 设计时平台的三层语义 Surface：
- Supported：正式支持，完整 round-trip 保证
- Preview：预览支持，部分语义可用
- Reserved：预留不支持

同时定义 Edge Semantics 编译规则和 Visual-only 边。

Source of Truth：
- AuthoringPackage > RuntimePackage（设计时是主，运行时是从）
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


# ─── Edge Compilation Target ───


@dataclass(frozen=True)
class EdgeCompilationTarget:
    """Edge 编译目标声明。

    Attributes:
        target_type: 编译目标类型（relation_type / policy_binding / visual_only）
        target_field: 编译到目标类型的哪个字段
        is_visual_only: 是否仅用于设计时可视化
        compilation_notes: 编译说明（哪些信息可能丢失）
    """

    target_type: Literal["relation_type", "policy_binding", "visual_only"]
    target_field: str | None = None
    is_visual_only: bool = False
    compilation_notes: str = ""


# ─── Semantic Surface ───


@dataclass(frozen=True)
class SemanticSurface:
    """三层语义 Surface：supported / preview / reserved。

    N1.7 新增的三层结构，取代 N1.6 的二元 SupportedSurface。

    Attributes:
        supported_node_prefixes: 正式支持的节点类型前缀
        preview_node_prefixes: 预览支持的节点类型前缀
        reserved_node_prefixes: 预留不支持的节点类型前缀
        supported_edge_types: 正式支持的边类型
        preview_edge_types: 预览支持的边类型
        reserved_edge_types: 预留不支持的边类型
        supported_compilation_fields: supported 类型保证编译的字段
        preview_partial_fields: preview 类型部分编译的字段
        edge_compilation_targets: Edge 编译目标映射
        visual_only_edges: 仅用于可视化的边（不编译）
    """

    # Node type prefixes
    supported_node_prefixes: list[str] = field(default_factory=list)
    preview_node_prefixes: list[str] = field(default_factory=list)
    reserved_node_prefixes: list[str] = field(default_factory=list)

    # Edge types
    supported_edge_types: list[str] = field(default_factory=list)
    preview_edge_types: list[str] = field(default_factory=list)
    reserved_edge_types: list[str] = field(default_factory=list)

    # Compilation promises
    supported_compilation_fields: dict[str, list[str]] = field(
        default_factory=dict
    )
    preview_partial_fields: dict[str, list[str]] = field(default_factory=dict)

    # Edge semantics
    edge_compilation_targets: dict[str, EdgeCompilationTarget] = field(
        default_factory=dict
    )
    visual_only_edges: list[str] = field(default_factory=list)


# ─── Default Semantic Surface (N1.7) ───

DEFAULT_SEMANTIC_SURFACE = SemanticSurface(
    # Node type prefixes
    supported_node_prefixes=["event", "context", "fact", "entity"],
    preview_node_prefixes=["relation", "policy"],
    reserved_node_prefixes=[],  # N1.7: 所有原有 reserved 进入 preview

    # Edge types
    supported_edge_types=["derives"],
    preview_edge_types=["relates", "triggers", "requires", "contains"],
    reserved_edge_types=[],  # N1.7: 所有边都有语义定义

    # Supported compilation fields (完整保证)
    supported_compilation_fields={
        "event": [
            "node_id",
            "label",
            "subject_type",
            "object_type",
            "properties",
            "timestamp_field",
        ],
        "context": [
            "node_id",
            "label",
            "properties",
            "lifecycle",
        ],
        "fact": [
            "node_id",
            "label",
            "subject_type",
            "object_type",
            "establishment_condition",
            "evidence_binding",
        ],
        "entity": [
            "node_id",
            "label",
            "entity_type",
            "properties",
            "identity_fields",
        ],
    },

    # Preview partial fields (部分保证)
    preview_partial_fields={
        "relation": [
            "node_id",
            "label",
            "source_entity_type",
            "target_entity_type",
            # 不保证: cardinality, properties, constraints
        ],
        "policy": [
            "node_id",
            "label",
            "policy_type",
            # 不保证: conditions, judgments, scope
        ],
    },

    # Edge compilation targets
    edge_compilation_targets={
        "derives": EdgeCompilationTarget(
            target_type="visual_only",
            is_visual_only=True,
            compilation_notes="推导关系由 GovernanceEngine 处理，不编译为 Schema",
        ),
        "relates": EdgeCompilationTarget(
            target_type="relation_type",
            target_field="source_type/target_type",
            compilation_notes="编译为 RelationType，cardinality/constraints 可能丢失",
        ),
        "triggers": EdgeCompilationTarget(
            target_type="policy_binding",
            target_field="trigger",
            compilation_notes="编译为 PolicyBinding.trigger",
        ),
        "requires": EdgeCompilationTarget(
            target_type="policy_binding",
            target_field="condition",
            compilation_notes="编译为 PolicyBinding.condition",
        ),
        "contains": EdgeCompilationTarget(
            target_type="visual_only",
            is_visual_only=True,
            compilation_notes="组合关系，不编译为 Schema",
        ),
    },

    # Visual-only edges
    visual_only_edges=["derives", "contains"],
)


def get_semantic_surface() -> SemanticSurface:
    """获取当前语义 Surface。

    Returns:
        SemanticSurface: 包含 supported/preview/reserved 三层结构
    """
    return DEFAULT_SEMANTIC_SURFACE


# ─── Surface Detection Functions ───


def is_supported_node_type(
    type_id: str,
    surface: SemanticSurface | None = None,
) -> bool:
    """判断节点类型是否正式支持。

    Args:
        type_id: VisualNodeType.id
        surface: SemanticSurface（默认 get_semantic_surface()）

    Returns:
        True 如果是正式支持的类型前缀
    """
    s = surface or get_semantic_surface()
    for prefix in s.supported_node_prefixes:
        if type_id.startswith(prefix):
            return True
    return False


def is_preview_node_type(
    type_id: str,
    surface: SemanticSurface | None = None,
) -> bool:
    """判断节点类型是否预览支持。

    Args:
        type_id: VisualNodeType.id
        surface: SemanticSurface（默认 get_semantic_surface()）

    Returns:
        True 如果是预览支持的类型前缀
    """
    s = surface or get_semantic_surface()
    for prefix in s.preview_node_prefixes:
        if type_id.startswith(prefix):
            return True
    return False


def is_reserved_node_type(
    type_id: str,
    surface: SemanticSurface | None = None,
) -> bool:
    """判断节点类型是否预留（不支持）。

    Args:
        type_id: VisualNodeType.id
        surface: SemanticSurface（默认 get_semantic_surface()）

    Returns:
        True 如果是预留的类型前缀
    """
    s = surface or get_semantic_surface()
    for prefix in s.reserved_node_prefixes:
        if type_id.startswith(prefix):
            return True
    return False


def get_node_surface_level(
    type_id: str,
    surface: SemanticSurface | None = None,
) -> Literal["supported", "preview", "reserved", "unknown"]:
    """获取节点类型的 Surface 层级。

    Args:
        type_id: VisualNodeType.id
        surface: SemanticSurface（默认 get_semantic_surface()）

    Returns:
        "supported" / "preview" / "reserved" / "unknown"
    """
    if is_supported_node_type(type_id, surface):
        return "supported"
    if is_preview_node_type(type_id, surface):
        return "preview"
    if is_reserved_node_type(type_id, surface):
        return "reserved"
    return "unknown"


def is_supported_edge_type(
    type_id: str,
    surface: SemanticSurface | None = None,
) -> bool:
    """判断边类型是否正式支持。

    Args:
        type_id: VisualEdgeType.id
        surface: SemanticSurface（默认 get_semantic_surface()）

    Returns:
        True 如果是正式支持的边类型
    """
    s = surface or get_semantic_surface()
    return type_id in s.supported_edge_types


def is_preview_edge_type(
    type_id: str,
    surface: SemanticSurface | None = None,
) -> bool:
    """判断边类型是否预览支持。

    Args:
        type_id: VisualEdgeType.id
        surface: SemanticSurface（默认 get_semantic_surface()）

    Returns:
        True 如果是预览支持的边类型
    """
    s = surface or get_semantic_surface()
    return type_id in s.preview_edge_types


def is_reserved_edge_type(
    type_id: str,
    surface: SemanticSurface | None = None,
) -> bool:
    """判断边类型是否预留（不支持）。

    Args:
        type_id: VisualEdgeType.id
        surface: SemanticSurface（默认 get_semantic_surface()）

    Returns:
        True 如果是预留的边类型
    """
    s = surface or get_semantic_surface()
    return type_id in s.reserved_edge_types


def get_edge_surface_level(
    type_id: str,
    surface: SemanticSurface | None = None,
) -> Literal["supported", "preview", "reserved", "unknown"]:
    """获取边类型的 Surface 层级。

    Args:
        type_id: VisualEdgeType.id
        surface: SemanticSurface（默认 get_semantic_surface()）

    Returns:
        "supported" / "preview" / "reserved" / "unknown"
    """
    if is_supported_edge_type(type_id, surface):
        return "supported"
    if is_preview_edge_type(type_id, surface):
        return "preview"
    if is_reserved_edge_type(type_id, surface):
        return "reserved"
    return "unknown"


def is_visual_only_edge(
    type_id: str,
    surface: SemanticSurface | None = None,
) -> bool:
    """判断边是否仅用于可视化（不编译）。

    Args:
        type_id: VisualEdgeType.id
        surface: SemanticSurface（默认 get_semantic_surface()）

    Returns:
        True 如果是 visual-only 边
    """
    s = surface or get_semantic_surface()
    return type_id in s.visual_only_edges


def get_edge_compilation_target(
    type_id: str,
    surface: SemanticSurface | None = None,
) -> EdgeCompilationTarget | None:
    """获取边的编译目标。

    Args:
        type_id: VisualEdgeType.id
        surface: SemanticSurface（默认 get_semantic_surface()）

    Returns:
        EdgeCompilationTarget 或 None（未知边类型）
    """
    s = surface or get_semantic_surface()
    return s.edge_compilation_targets.get(type_id)


# ─── Compilation Promise Query ───


def get_guaranteed_fields_for_node_type(
    type_id: str,
    surface: SemanticSurface | None = None,
) -> list[str]:
    """获取节点类型的保证编译字段。

    Supported 类型返回完整保证字段。
    Preview 类型返回部分保证字段。
    Reserved/Unknown 类型返回空列表。

    Args:
        type_id: VisualNodeType.id
        surface: SemanticSurface（默认 get_semantic_surface()）

    Returns:
        保证编译的字段列表
    """
    s = surface or get_semantic_surface()

    # 提取类型前缀
    prefix = ""
    for p in (
        s.supported_node_prefixes + s.preview_node_prefixes
    ):
        if type_id.startswith(p):
            prefix = p
            break

    if prefix in s.supported_node_prefixes:
        return s.supported_compilation_fields.get(prefix, [])
    if prefix in s.preview_node_prefixes:
        return s.preview_partial_fields.get(prefix, [])

    return []


def get_unsupported_fields_for_node_type(
    type_id: str,
    surface: SemanticSurface | None = None,
) -> list[str]:
    """获取节点类型的不保证编译字段（信息可能丢失）。

    仅对 Preview 类型有意义。
    Supported 类型返回空列表（全部保证）。

    Args:
        type_id: VisualNodeType.id
        surface: SemanticSurface（默认 get_semantic_surface()）

    Returns:
        不保证编译的字段列表
    """
    s = surface or get_semantic_surface()

    if is_preview_node_type(type_id, s):
        # 提取类型前缀
        prefix = ""
        for p in s.preview_node_prefixes:
            if type_id.startswith(p):
                prefix = p
                break

        # Preview 类型常见不保证字段
        # 这些字段在当前实现中不编译
        # 未来版本可能逐步加入
        preview_unsupported_common = {
            "relation": ["cardinality", "properties", "constraints"],
            "policy": ["conditions", "judgments", "scope", "priority"],
        }

        return preview_unsupported_common.get(prefix, [])

    return []
