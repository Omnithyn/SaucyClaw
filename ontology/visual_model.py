"""Ontology Visual Authoring — 可视化构建规范模型。

N1.5 — Ontology Platform Architecture & Visual Authoring Foundation

定义可视化编辑器背后的规范模型（不做 UI）。

层级：
- VisualNodeType / VisualEdgeType：节点/边的类型定义
- VisualNode / VisualEdge：运行时实例
- PropertySchema / FormSchema：属性/表单 schema
- Palette / Category：设计时元数据（分类、图标、颜色）

核心约束：
- 所有类型 frozen，不可变
- 与 OntologySchema 存在 1:1 投影关系
- Visual Model 不进入运行时判断链路
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ─── Type Definitions ───


@dataclass(frozen=True)
class VisualNodeType:
    """可视化节点类型定义。

    对应本体中的概念类型（EntityType、EventType、FactType 等）。
    决定节点在画布上的呈现方式。

    Attributes:
        id: 类型唯一标识
        name: 显示名称
        category: 所属分类（entity / event / fact / context / relation / policy）
        description: 类型描述
        visual_hint: 视觉提示（icon 名或 emoji）
        color: 节点颜色（十六进制）
        min_instances: 最小实例数（0 = 可选，1 = 必填）
        max_instances: 最大实例数（None = 无限制）
    """

    id: str
    name: str
    category: str
    description: str
    visual_hint: str = "circle"
    color: str = "#808080"
    min_instances: int = 0
    max_instances: int | None = None


@dataclass(frozen=True)
class VisualEdgeType:
    """可视化边类型定义。

    对应本体中的关系（RelationType、事件推导关系等）。

    Attributes:
        id: 类型唯一标识
        name: 显示名称
        source_type: 允许的源节点类型 ID（None = 任意）
        target_type: 允许的目标节点类型 ID（None = 任意）
        label: 边上显示的文本
        directed: 是否有向
        cardinality: 基数（one-to-one / one-to-many / many-to-many）
        required: 是否必填
    """

    id: str
    name: str
    source_type: str | None = None
    target_type: str | None = None
    label: str = ""
    directed: bool = True
    cardinality: str = "many-to-many"
    required: bool = False


@dataclass(frozen=True)
class PropertySchema:
    """属性 Schema。

    定义节点/表单中单个属性的类型和约束。

    Attributes:
        name: 属性名
        prop_type: 类型（string / integer / boolean / enum / array）
        required: 是否必填
        default: 默认值
        enum_values: enum 类型的可选值
        description: 属性描述
    """

    name: str
    prop_type: str
    required: bool = False
    default: Any = None
    enum_values: list[str] | None = None
    description: str = ""


@dataclass(frozen=True)
class FormSchema:
    """表单 Schema。

    决定可视化编辑器中节点属性编辑面板的结构。

    Attributes:
        type_id: 关联的 VisualNodeType ID
        title: 表单标题
        sections: 分区列表，每个分区包含一组属性
        validation_rules: 校验规则（如 {"min_length": 3}）
    """

    type_id: str
    title: str
    sections: list[dict[str, Any]] = field(default_factory=list)
    validation_rules: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Category:
    """调色板分类。

    用于在可视化编辑器中对节点类型进行分组展示。

    Attributes:
        id: 分类唯一标识
        name: 显示名称
        description: 分类描述
        color: 分类主题色
        node_types: 该分类下的节点类型 ID 列表
    """

    id: str
    name: str
    description: str
    color: str = "#808080"
    node_types: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Palette:
    """调色板。

    聚合所有可用分类和节点类型，作为可视化编辑器的左侧面板数据源。
    """

    categories: list[Category] = field(default_factory=list)

    def get_category(self, category_id: str) -> Category | None:
        """获取分类。"""
        for cat in self.categories:
            if cat.id == category_id:
                return cat
        return None

    def all_node_type_ids(self) -> set[str]:
        """获取所有注册的节点类型 ID。"""
        ids: set[str] = set()
        for cat in self.categories:
            ids.update(cat.node_types)
        return ids


# ─── Instance Definitions ───


@dataclass(frozen=True)
class VisualNode:
    """可视化节点实例。

    画布上的一个具体节点。

    Attributes:
        node_id: 实例唯一标识
        type_id: 引用的 VisualNodeType ID
        label: 显示标签
        position: 画布位置 {"x": float, "y": float}
        properties: 属性键值对
        metadata: 附加元数据
    """

    node_id: str
    type_id: str
    label: str
    position: dict[str, float] = field(default_factory=dict)
    properties: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class VisualEdge:
    """可视化边实例。

    画布上连接两个节点的连线。

    Attributes:
        edge_id: 实例唯一标识
        type_id: 引用的 VisualEdgeType ID
        source_id: 源节点 ID
        target_id: 目标节点 ID
        label: 边上显示的文本
        properties: 属性键值对
    """

    edge_id: str
    type_id: str
    source_id: str
    target_id: str
    label: str = ""
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class VisualGraph:
    """可视化图。

    完整的画布状态，包含所有节点和边。

    Attributes:
        graph_id: 图唯一标识
        name: 图名称
        nodes: 节点列表
        edges: 边列表
        metadata: 附加元数据
    """

    graph_id: str
    name: str
    nodes: list[VisualNode] = field(default_factory=list)
    edges: list[VisualEdge] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


# ─── Builder Functions ───


def build_visual_node_type(data: dict[str, Any]) -> VisualNodeType:
    """从 dict 构建 VisualNodeType。"""
    return VisualNodeType(
        id=data["id"],
        name=data["name"],
        category=data["category"],
        description=data.get("description", ""),
        visual_hint=data.get("visual_hint", "circle"),
        color=data.get("color", "#808080"),
        min_instances=data.get("min_instances", 0),
        max_instances=data.get("max_instances"),
    )


def build_visual_edge_type(data: dict[str, Any]) -> VisualEdgeType:
    """从 dict 构建 VisualEdgeType。"""
    return VisualEdgeType(
        id=data["id"],
        name=data["name"],
        source_type=data.get("source_type"),
        target_type=data.get("target_type"),
        label=data.get("label", ""),
        directed=data.get("directed", True),
        cardinality=data.get("cardinality", "many-to-many"),
        required=data.get("required", False),
    )


def build_property_schema(data: dict[str, Any]) -> PropertySchema:
    """从 dict 构建 PropertySchema。"""
    return PropertySchema(
        name=data["name"],
        prop_type=data["prop_type"],
        required=data.get("required", False),
        default=data.get("default"),
        enum_values=data.get("enum_values"),
        description=data.get("description", ""),
    )


def build_form_schema(data: dict[str, Any]) -> FormSchema:
    """从 dict 构建 FormSchema。"""
    return FormSchema(
        type_id=data["type_id"],
        title=data.get("title", data["type_id"]),
        sections=data.get("sections", []),
        validation_rules=data.get("validation_rules", {}),
    )


def build_visual_node(data: dict[str, Any]) -> VisualNode:
    """从 dict 构建 VisualNode。"""
    return VisualNode(
        node_id=data["node_id"],
        type_id=data["type_id"],
        label=data.get("label", data["node_id"]),
        position=data.get("position", {}),
        properties=data.get("properties", {}),
        metadata=data.get("metadata", {}),
    )


def build_visual_edge(data: dict[str, Any]) -> VisualEdge:
    """从 dict 构建 VisualEdge。"""
    return VisualEdge(
        edge_id=data["edge_id"],
        type_id=data["type_id"],
        source_id=data["source_id"],
        target_id=data["target_id"],
        label=data.get("label", ""),
        properties=data.get("properties", {}),
    )


def build_visual_graph(data: dict[str, Any]) -> VisualGraph:
    """从 dict 构建 VisualGraph。"""
    return VisualGraph(
        graph_id=data["graph_id"],
        name=data.get("name", data["graph_id"]),
        nodes=[build_visual_node(n) for n in data.get("nodes", [])],
        edges=[build_visual_edge(e) for e in data.get("edges", [])],
        metadata=data.get("metadata", {}),
    )


def build_palette(data: dict[str, Any]) -> Palette:
    """从 dict 构建 Palette。"""
    return Palette(
        categories=[
            Category(
                id=cat["id"],
                name=cat["name"],
                description=cat.get("description", ""),
                color=cat.get("color", "#808080"),
                node_types=cat.get("node_types", []),
            )
            for cat in data.get("categories", [])
        ]
    )
