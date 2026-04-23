"""Ontology Catalog — 类型注册与索引。

N1.5 — Ontology Platform Architecture & Visual Authoring Foundation

Catalog 是本体类型的集中注册表，提供：
- 按 ID 查找（EventType / ContextType / FactType）
- 按分类索引
- 类型存在性检查
- 与 OntologySchema 的双向构建

Catalog 不加载 YAML（那是 loader 的职责），
它接收已构建的类型集合，建立索引并提供查询接口。
"""

from __future__ import annotations

from dataclasses import dataclass

from ontology.schema import (
    ContextType,
    EventType,
    FactType,
    OntologySchema,
)
from ontology.visual_model import (
    VisualEdgeType,
    VisualGraph,
    VisualNodeType,
)


@dataclass(frozen=True)
class CatalogIndex:
    """单条索引条目。

    Attributes:
        type_id: 类型 ID
        type_name: 类型名称
        category: 所属分类
        description: 类型描述
        is_active: 是否活跃
    """

    type_id: str
    type_name: str
    category: str
    description: str
    is_active: bool = True


class OntologyCatalog:
    """本体类型目录。

    职责：
    - 索引所有已注册的本体类型
    - 支持按 ID、分类查询
    - 支持存在性检查
    - 支持从 OntologySchema 构建
    - 支持从 VisualGraph 构建（可视化设计导出）
    """

    def __init__(
        self,
        event_types: list[EventType] | None = None,
        context_types: list[ContextType] | None = None,
        fact_types: list[FactType] | None = None,
        visual_node_types: list[VisualNodeType] | None = None,
        visual_edge_types: list[VisualEdgeType] | None = None,
    ) -> None:
        """初始化 Catalog。

        Args:
            event_types: 事件类型列表
            context_types: 上下文类型列表
            fact_types: 事实类型列表
            visual_node_types: 可视化节点类型列表
            visual_edge_types: 可视化边类型列表
        """
        self._event_types: dict[str, EventType] = {}
        self._context_types: dict[str, ContextType] = {}
        self._fact_types: dict[str, FactType] = {}
        self._visual_node_types: dict[str, VisualNodeType] = {}
        self._visual_edge_types: dict[str, VisualEdgeType] = {}

        for et in event_types or []:
            self._event_types[et.id] = et
        for ct in context_types or []:
            self._context_types[ct.id] = ct
        for ft in fact_types or []:
            self._fact_types[ft.id] = ft
        for vnt in visual_node_types or []:
            self._visual_node_types[vnt.id] = vnt
        for vet in visual_edge_types or []:
            self._visual_edge_types[vet.id] = vet

    @classmethod
    def from_schema(cls, schema: OntologySchema) -> OntologyCatalog:
        """从 OntologySchema 构建 Catalog。"""
        return cls(
            event_types=schema.event_types,
            context_types=schema.context_types,
            fact_types=schema.fact_types,
        )

    @classmethod
    def from_visual_graph(
        cls,
        graph: VisualGraph,
        node_types: list[VisualNodeType] | None = None,
        edge_types: list[VisualEdgeType] | None = None,
    ) -> OntologyCatalog:
        """从 VisualGraph 构建 Catalog（可视化设计导出）。"""
        return cls(
            visual_node_types=node_types or [],
            visual_edge_types=edge_types or [],
        )

    # ─── Lookup ───

    def get_event_type(self, type_id: str) -> EventType | None:
        """获取事件类型。"""
        return self._event_types.get(type_id)

    def get_context_type(self, type_id: str) -> ContextType | None:
        """获取上下文类型。"""
        return self._context_types.get(type_id)

    def get_fact_type(self, type_id: str) -> FactType | None:
        """获取事实类型。"""
        return self._fact_types.get(type_id)

    def get_visual_node_type(self, type_id: str) -> VisualNodeType | None:
        """获取可视化节点类型。"""
        return self._visual_node_types.get(type_id)

    def get_visual_edge_type(self, type_id: str) -> VisualEdgeType | None:
        """获取可视化边类型。"""
        return self._visual_edge_types.get(type_id)

    # ─── Existence Checks ───

    def has_event_type(self, type_id: str) -> bool:
        """检查事件类型是否存在。"""
        return type_id in self._event_types

    def has_context_type(self, type_id: str) -> bool:
        """检查上下文类型是否存在。"""
        return type_id in self._context_types

    def has_fact_type(self, type_id: str) -> bool:
        """检查事实类型是否存在。"""
        return type_id in self._fact_types

    def has_visual_node_type(self, type_id: str) -> bool:
        """检查可视化节点类型是否存在。"""
        return type_id in self._visual_node_types

    # ─── Index ───

    def index_by_category(self) -> dict[str, list[CatalogIndex]]:
        """按分类生成索引。

        Returns:
            {category: [CatalogIndex, ...]}
        """
        result: dict[str, list[CatalogIndex]] = {}

        for et in self._event_types.values():
            result.setdefault("event", []).append(
                CatalogIndex(
                    type_id=et.id,
                    type_name=et.name,
                    category="event",
                    description=et.description,
                )
            )

        for ct in self._context_types.values():
            result.setdefault("context", []).append(
                CatalogIndex(
                    type_id=ct.id,
                    type_name=ct.name,
                    category="context",
                    description=ct.description,
                )
            )

        for ft in self._fact_types.values():
            result.setdefault("fact", []).append(
                CatalogIndex(
                    type_id=ft.id,
                    type_name=ft.name,
                    category="fact",
                    description=ft.description,
                )
            )

        return result

    def all_type_ids(self) -> dict[str, list[str]]:
        """获取所有已注册的类型 ID。

        Returns:
            {"event": [...], "context": [...], "fact": [...], ...}
        """
        return {
            "event": list(self._event_types.keys()),
            "context": list(self._context_types.keys()),
            "fact": list(self._fact_types.keys()),
            "visual_node": list(self._visual_node_types.keys()),
            "visual_edge": list(self._visual_edge_types.keys()),
        }

    def type_count(self) -> dict[str, int]:
        """获取各分类的类型数量。"""
        return {
            "event": len(self._event_types),
            "context": len(self._context_types),
            "fact": len(self._fact_types),
            "visual_node": len(self._visual_node_types),
            "visual_edge": len(self._visual_edge_types),
        }
