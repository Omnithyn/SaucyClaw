"""Ontology Edge Semantics — Edge 编译规则定义。

N1.7 — Ontology Studio Semantic Surface Expansion

定义 Edge 在 Studio 设计时到 Runtime 运行时的编译规则：
- relates 边 → RelationType
- triggers 边 → PolicyBinding.trigger
- requires 边 → PolicyBinding.condition
- derives/contains 边 → visual-only（不编译）

Edge 不再只是"画线"，而是有明确的语义和编译目标。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ontology.policy_binding import PolicyBinding
from ontology.semantic_surface import (
    get_edge_compilation_target,
    get_semantic_surface,
    is_preview_edge_type,
    is_visual_only_edge,
    SemanticSurface,
)
from ontology.visual_model import VisualEdge, VisualNode

# N1.7: RelationType 在 core.meta_model 中定义
from core.meta_model.models import RelationType


# ─── Edge Compilation Errors ───


class EdgeCompilationError(Exception):
    """Edge 编译失败。"""

    def __init__(
        self,
        edge_id: str,
        edge_type: str,
        reason: str,
    ) -> None:
        self.edge_id = edge_id
        self.edge_type = edge_type
        self.reason = reason
        super().__init__(
            f"Edge {edge_id!r} (type={edge_type!r}) 编译失败: {reason}"
        )


# ─── Compilation Result ───


@dataclass(frozen=True)
class EdgeCompilationResult:
    """Edge 编译结果。

    Attributes:
        relation_types: 编译生成的 RelationType 列表
        policy_bindings: 编译生成的 PolicyBinding 列表
        visual_only_edges: visual-only 边列表（不编译）
        compilation_errors: 编译失败的边列表
        compilation_warnings: 编译警告（如信息丢失）
        partial_compilation_notes: 部分编译说明
    """

    relation_types: list[RelationType] = field(default_factory=list)
    policy_bindings: list[PolicyBinding] = field(default_factory=list)
    visual_only_edges: list[str] = field(default_factory=list)
    compilation_errors: list[str] = field(default_factory=list)
    compilation_warnings: list[str] = field(default_factory=list)
    partial_compilation_notes: dict[str, str] = field(default_factory=dict)


# ─── Edge Compilation Functions ───


def compile_edge_to_relation_type(
    edge: VisualEdge,
    nodes: dict[str, VisualNode],
    surface: SemanticSurface | None = None,
) -> RelationType | None:
    """将 relates 边编译为 RelationType。

    Args:
        edge: VisualEdge（type_id="relates"）
        nodes: 节点字典 {node_id: VisualNode}
        surface: SemanticSurface

    Returns:
        RelationType 或 None（编译失败）

    Note:
        - 仅处理 type_id="relates" 的边
        - cardinality/constraints 可能丢失（Preview 边）
    """
    s = surface or get_semantic_surface()

    if edge.type_id != "relates":
        return None

    target = get_edge_compilation_target(edge.type_id, s)
    if target is None or target.target_type != "relation_type":
        return None

    source_node = nodes.get(edge.source_id)
    target_node = nodes.get(edge.target_id)

    if source_node is None or target_node is None:
        return None

    # 只有 entity 节点可以建立 RelationType
    if not source_node.type_id.startswith("entity"):
        return None
    if not target_node.type_id.startswith("entity"):
        return None

    # 构建 RelationType
    # 注意：Preview 边的 cardinality/constraints 不保证编译
    return RelationType(
        id=edge.edge_id,
        name=edge.label or f"{source_node.label}-{target_node.label}",
        source=source_node.properties.get("entity_type", source_node.type_id),
        target=target_node.properties.get("entity_type", target_node.type_id),
        cardinality=edge.properties.get("cardinality", "many-to-many"),
    )


def compile_edge_to_policy_binding(
    edge: VisualEdge,
    nodes: dict[str, VisualNode],
    trigger_or_condition: str,
    surface: SemanticSurface | None = None,
) -> PolicyBinding | None:
    """将 triggers/requires 边编译为 PolicyBinding。

    Args:
        edge: VisualEdge（type_id="triggers" 或 "requires"）
        nodes: 节点字典 {node_id: VisualNode}
        trigger_or_condition: "trigger" 或 "condition"
        surface: SemanticSurface

    Returns:
        PolicyBinding 或 None（编译失败）

    Note:
        - triggers 边 → PolicyBinding.trigger
        - requires 边 → PolicyBinding.condition
        - Preview 边的 conditions/judgments/scope 可能丢失
    """
    s = surface or get_semantic_surface()

    if edge.type_id not in ("triggers", "requires"):
        return None

    target = get_edge_compilation_target(edge.type_id, s)
    if target is None or target.target_type != "policy_binding":
        return None

    source_node = nodes.get(edge.source_id)
    target_node = nodes.get(edge.target_id)

    if source_node is None or target_node is None:
        return None

    # triggers: source 应为 event/fact，target 应为 policy
    # requires: source 应为 policy，target 应为 entity/fact
    if trigger_or_condition == "trigger":
        # 触发边：事件/事实 → 策略
        if not (
            source_node.type_id.startswith("event")
            or source_node.type_id.startswith("fact")
        ):
            return None
        if not target_node.type_id.startswith("policy"):
            return None

        trigger_event_type = source_node.node_id

        return PolicyBinding(
            id=f"binding-{edge.edge_id}",
            policy_type=target_node.properties.get("policy_type", target_node.node_id),
            trigger=trigger_event_type,
            condition=None,
            judgment=None,
            scope="global",
        )

    elif trigger_or_condition == "condition":
        # 条件边：策略 → 实体/事实
        if not source_node.type_id.startswith("policy"):
            return None
        if not (
            target_node.type_id.startswith("entity")
            or target_node.type_id.startswith("fact")
        ):
            return None

        condition_type = target_node.node_id

        return PolicyBinding(
            id=f"binding-{edge.edge_id}",
            policy_type=source_node.properties.get(
                "policy_type", source_node.node_id
            ),
            trigger=None,
            condition=condition_type,
            judgment=None,
            scope="global",
        )

    return None


def compile_edges_from_visual_graph(
    edges: list[VisualEdge],
    nodes: dict[str, VisualNode],
    surface: SemanticSurface | None = None,
    strict: bool = False,
) -> EdgeCompilationResult:
    """从 VisualGraph 编译所有边。

    Args:
        edges: 边列表
        nodes: 节点字典 {node_id: VisualNode}
        surface: SemanticSurface
        strict: 严格模式（遇到不支持边抛异常）

    Returns:
        EdgeCompilationResult

    Note:
        - Supported 边：完整编译
        - Preview 边：部分编译，记录信息丢失
        - Visual-only 边：不编译，记录在 visual_only_edges
        - Unknown 边：记录错误（strict=True 则抛异常）
    """
    s = surface or get_semantic_surface()

    relation_types: list[RelationType] = []
    policy_bindings: list[PolicyBinding] = []
    visual_only: list[str] = []
    errors: list[str] = []
    warnings: list[str] = []
    partial_notes: dict[str, str] = {}

    for edge in edges:
        # 检查边类型 Surface 层级
        target = get_edge_compilation_target(edge.type_id, s)

        if is_visual_only_edge(edge.type_id, s):
            # Visual-only 边：不编译
            visual_only.append(edge.edge_id)
            continue

        if target is None:
            # 未知边类型
            msg = f"边 {edge.edge_id!r} 使用未知类型 {edge.type_id!r}"
            if strict:
                raise EdgeCompilationError(
                    edge.edge_id, edge.type_id, "未知边类型"
                )
            errors.append(msg)
            continue

        # Preview 边：记录信息丢失警告
        if is_preview_edge_type(edge.type_id, s):
            warnings.append(
                f"边 {edge.edge_id!r} 是 Preview 类型 {edge.type_id!r}"
                f"，部分信息可能丢失：{target.compilation_notes}"
            )
            partial_notes[edge.edge_id] = target.compilation_notes

        # 根据编译目标类型处理
        if target.target_type == "relation_type":
            rt = compile_edge_to_relation_type(edge, nodes, s)
            if rt is not None:
                relation_types.append(rt)
            else:
                msg = (
                    f"边 {edge.edge_id!r} 编译为 RelationType 失败"
                    f"：节点类型不匹配"
                )
                if strict:
                    raise EdgeCompilationError(
                        edge.edge_id, edge.type_id, "节点类型不匹配"
                    )
                errors.append(msg)

        elif target.target_type == "policy_binding":
            trigger_or_condition = (
                "trigger" if edge.type_id == "triggers"
                else "condition"
            )
            pb = compile_edge_to_policy_binding(
                edge, nodes, trigger_or_condition, s
            )
            if pb is not None:
                policy_bindings.append(pb)
            else:
                msg = (
                    f"边 {edge.edge_id!r} 编译为 PolicyBinding 失败"
                    f"：节点类型不匹配"
                )
                if strict:
                    raise EdgeCompilationError(
                        edge.edge_id, edge.type_id, "节点类型不匹配"
                    )
                errors.append(msg)

    return EdgeCompilationResult(
        relation_types=relation_types,
        policy_bindings=policy_bindings,
        visual_only_edges=visual_only,
        compilation_errors=errors,
        compilation_warnings=warnings,
        partial_compilation_notes=partial_notes,
    )


# ─── Edge Semantics Query ───


def get_edge_semantics_description(
    edge_type: str,
    surface: SemanticSurface | None = None,
) -> str:
    """获取边类型的语义描述。

    Args:
        edge_type: 边类型 ID
        surface: SemanticSurface

    Returns:
        语义描述字符串
    """
    s = surface or get_semantic_surface()
    target = get_edge_compilation_target(edge_type, s)

    if target is None:
        return f"未知边类型 {edge_type!r}"

    if target.is_visual_only:
        return (
            f"边类型 {edge_type!r} 是 Visual-only"
            f"：仅用于设计时可视化，不编译为 Runtime"
        )

    return (
        f"边类型 {edge_type!r} 编译为 {target.target_type}"
        f"（{target.target_field or '未知字段'}）"
        f"：{target.compilation_notes}"
    )


def get_all_edge_semantics(
    surface: SemanticSurface | None = None,
) -> dict[str, str]:
    """获取所有边类型的语义描述。

    Args:
        surface: SemanticSurface

    Returns:
        {edge_type: semantics_description} 字典
    """
    s = surface or get_semantic_surface()
    all_edges = (
        s.supported_edge_types
        + s.preview_edge_types
        + s.reserved_edge_types
    )

    return {
        edge_type: get_edge_semantics_description(edge_type, s)
        for edge_type in all_edges
    }


# ─── Internal Helpers ───


def _extract_string_keys(data: Any) -> list[str]:
    """从数据中提取字符串键列表。

    支持 list[str] 或 dict（取 keys）。
    """
    if isinstance(data, list):
        return [str(x) for x in data if isinstance(x, str)]
    if isinstance(data, dict):
        return list(data.keys())
    return []
