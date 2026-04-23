"""Ontology Projection — Runtime 到 Visual 的投影层。

N1.8 — Ontology Package Compilation & Projection Pipeline

定义 Projector 类：
- 将 RuntimePackage 投影回 VisualGraph
- 记录投影信息丢失（Preview 元素不可逆）
- 提供投影报告

投影规则：
- OntologySchema → VisualNodes（完整回流）
- RelationTypes → VisualEdges（relates 边）
- PolicyBindings → VisualEdges（triggers/requires 边）

注意：
- Preview 元素的额外字段在投影中丢失（不可逆）
- ProjectionReport 记录丢失信息
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ontology.authoring_package import RuntimePackage
from ontology.schema import (
    EventType,
    ContextType,
    FactType,
)
from ontology.semantic_surface import (
    SemanticSurface,
    get_semantic_surface,
)
from ontology.visual_model import (
    VisualEdge,
    VisualGraph,
    VisualNode,
)

# RelationType 在 core.meta_model 中定义
from core.meta_model.models import RelationType


# ─── Projection Report ───


@dataclass(frozen=True)
class ProjectionReport:
    """投影报告：记录投影过程中的信息丢失。

    Attributes:
        is_complete: 是否完整投影（无信息丢失）
        projected_nodes: 投影的节点数量
        projected_edges: 投影的边数量
        lost_fields: 丢失的字段（Preview 元素不可逆）
        warnings: 投影警告
        note: Preview 元素信息丢失说明
    """

    is_complete: bool
    projected_nodes: int
    projected_edges: int
    lost_fields: dict[str, list[str]] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    note: str = ""


# ─── Projector ───


@dataclass(frozen=True)
class Projector:
    """Runtime 到 Visual 的投影器。

    将 RuntimePackage 投影回 VisualGraph。

    投影规则：
    - OntologySchema.event_types → VisualNodes (event-*)
    - OntologySchema.context_types → VisualNodes (context-*)
    - OntologySchema.fact_types → VisualNodes (fact-*)
    - RelationTypes → VisualEdges (relates)
    - PolicyBindings → VisualEdges (triggers/requires)

    信息丢失：
    - Preview 节点的额外字段（cardinality, constraints 等）不可恢复
    - Preview 边的部分属性（conditions, judgments 等）不可恢复
    - Visual-only 边（derives, contains）不可恢复

    Attributes:
        surface: 语义 Surface（用于标记 Preview 元素）
    """

    surface: SemanticSurface = field(default_factory=get_semantic_surface)

    def project(
        self,
        runtime: RuntimePackage,
    ) -> tuple[VisualGraph, ProjectionReport]:
        """将 RuntimePackage 投影为 VisualGraph。

        Args:
            runtime: 运行时包

        Returns:
            (VisualGraph, ProjectionReport)
        """
        nodes: list[VisualNode] = []
        edges: list[VisualEdge] = []
        lost_fields: dict[str, list[str]] = {}
        warnings: list[str] = []

        # 1. 投影 OntologySchema
        schema = runtime.ontology_schema
        for et in schema.event_types:
            nodes.append(self._project_event_type(et))
        for ct in schema.context_types:
            nodes.append(self._project_context_type(ct))
        for ft in schema.fact_types:
            nodes.append(self._project_fact_type(ft))

        # 2. 投影 RelationTypes
        for rt in runtime.relation_types:
            edge, lost = self._project_relation_type(rt)
            edges.append(edge)
            if lost:
                lost_fields[rt.id] = lost
                warnings.append(
                    f"RelationType {rt.id!r} 投影时丢失字段: {lost}"
                )

        # 3. 投影 PolicyBindings
        # 注意：当前 PolicyBinding 结构与 VisualEdge 不完全匹配
        # 这里只做基础投影
        for pb in runtime.policy_bindings:
            edge = self._project_policy_binding(pb)
            if edge:
                edges.append(edge)

        # 4. 检查编译报告
        if runtime.compilation_report:
            if runtime.compilation_report.preview_types > 0:
                warnings.append(
                    f"Runtime 包含 {runtime.compilation_report.preview_types} "
                    f"个 Preview 类型元素，部分信息不可逆"
                )
            if runtime.compilation_report.information_loss_notes:
                for element_id, note in runtime.compilation_report.information_loss_notes.items():
                    warnings.append(f"元素 {element_id!r}: {note}")

        # 5. 构建报告
        report = ProjectionReport(
            is_complete=len(lost_fields) == 0 and len(warnings) == 0,
            projected_nodes=len(nodes),
            projected_edges=len(edges),
            lost_fields=lost_fields,
            warnings=warnings,
            note="Preview 元素的信息丢失不可逆（字段缺失）",
        )

        # 6. 构建 VisualGraph
        graph = VisualGraph(
            graph_id=f"{runtime.package_id}-projection",
            name=f"{runtime.package_id} 投影",
            nodes=nodes,
            edges=edges,
            metadata={
                "source": "projection",
                "runtime_version": runtime.version,
                "projection_report": {
                    "is_complete": report.is_complete,
                    "projected_nodes": report.projected_nodes,
                    "projected_edges": report.projected_edges,
                },
            },
        )

        return graph, report

    def _project_event_type(
        self,
        et: EventType,
    ) -> VisualNode:
        """将 EventType 投影为 VisualNode。"""
        return VisualNode(
            node_id=et.id,
            type_id=f"event-{et.id}",
            label=et.name,
            properties={
                "subject_type": et.subject_type,
                "object_type": et.object_type,
                "properties": et.properties,
                "timestamp_field": et.timestamp_field,
            },
            metadata={
                "source": "projection",
                "category": "event",
                "description": et.description,
            },
        )

    def _project_context_type(
        self,
        ct: ContextType,
    ) -> VisualNode:
        """将 ContextType 投影为 VisualNode。"""
        return VisualNode(
            node_id=ct.id,
            type_id=f"context-{ct.id}",
            label=ct.name,
            properties={
                "properties": ct.properties,
                "lifecycle": ct.lifecycle,
            },
            metadata={
                "source": "projection",
                "category": "context",
                "description": ct.description,
            },
        )

    def _project_fact_type(
        self,
        ft: FactType,
    ) -> VisualNode:
        """将 FactType 投影为 VisualNode。"""
        return VisualNode(
            node_id=ft.id,
            type_id=f"fact-{ft.id}",
            label=ft.name,
            properties={
                "subject_type": ft.subject_type,
                "object_type": ft.object_type,
                "establishment_condition": ft.establishment_condition,
                "evidence_binding": ft.evidence_binding,
            },
            metadata={
                "source": "projection",
                "category": "fact",
                "description": ft.description,
            },
        )

    def _project_relation_type(
        self,
        rt: RelationType,
    ) -> tuple[VisualEdge, list[str]]:
        """将 RelationType 投影为 VisualEdge (relates)。

        Returns:
            (VisualEdge, lost_fields)
        """
        # Preview 类型信息丢失
        # RelationType 只有 source/target/cardinality
        # 但 VisualEdge.properties 可能有更多字段（constraints 等）
        lost = []
        # cardinality 在 RelationType 中，但 VisualEdge.properties 中可能丢失

        edge = VisualEdge(
            edge_id=rt.id,
            type_id="relates",  # Preview 边
            source_id=rt.source,
            target_id=rt.target,
            label=rt.name,
            properties={
                "cardinality": rt.cardinality,
                "source": "projection",
                "edge_category": "preview",
            },
        )

        return edge, lost

    def _project_policy_binding(
        self,
        pb: Any,  # PolicyBinding 的结构需要适配
    ) -> VisualEdge | None:
        """将 PolicyBinding 投影为 VisualEdge。

        注意：PolicyBinding 当前结构与 VisualEdge 不完全匹配。
        这里做基础投影，可能返回 None。
        """
        # PolicyBinding 有 policy_id, policy_name, binds_to_*
        # 这些字段与 VisualEdge 的 source_id/target_id 不直接匹配
        # 需要根据绑定目标类型构建边

        # 简化处理：如果绑定到 event_type，构建 triggers 边
        if hasattr(pb, "binds_to_event_type") and pb.binds_to_event_type:
            return VisualEdge(
                edge_id=f"binding-{pb.policy_id}-trigger",
                type_id="triggers",  # Preview 边
                source_id=pb.binds_to_event_type,
                target_id=pb.policy_id,
                label=f"{pb.policy_name} trigger",
                properties={
                    "source": "projection",
                    "edge_category": "preview",
                    "policy_name": pb.policy_name,
                },
            )

        # 如果绑定到 fact_type，构建 requires 边
        if hasattr(pb, "binds_to_fact_type") and pb.binds_to_fact_type:
            return VisualEdge(
                edge_id=f"binding-{pb.policy_id}-condition",
                type_id="requires",  # Preview 边
                source_id=pb.policy_id,
                target_id=pb.binds_to_fact_type,
                label=f"{pb.policy_name} condition",
                properties={
                    "source": "projection",
                    "edge_category": "preview",
                    "policy_name": pb.policy_name,
                },
            )

        return None


# ─── Convenience Function ───


def project_runtime_to_visual(
    runtime: RuntimePackage,
    surface: SemanticSurface | None = None,
) -> tuple[VisualGraph, ProjectionReport]:
    """便捷投影函数。

    Args:
        runtime: 运行时包
        surface: 语义 Surface

    Returns:
        (VisualGraph, ProjectionReport)
    """
    projector = Projector(
        surface=surface or get_semantic_surface(),
    )
    return projector.project(runtime)
