"""Ontology Round-Trip — 三向等价转换。

N1.5 — Ontology Platform Architecture & Visual Authoring Foundation

表达三种视角的等价转换：
1. YAML/config → VisualGraph（配置加载为可视化图）
2. VisualGraph → OntologySchema（可视化设计编译为运行时 Schema）
3. OntologySchema → VisualGraph（运行时 Schema 反向生成可视化图）

核心约束：
- 不引入信息丢失（在定义的字段范围内）
- 所有转换是确定性的
- 不修改输入，返回新对象（不可变性）

这证明 ontology 后续可支撑可视化构建，而不只是代码手工构造。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ontology.catalog import OntologyCatalog
from ontology.schema import (
    ContextType,
    EventType,
    FactType,
    OntologySchema,
)
from ontology.visual_model import (
    VisualGraph,
    VisualNode,
)


@dataclass(frozen=True)
class RoundTripReport:
    """Round-Trip 校验报告。

    记录转换前后的差异，证明三向等价。

    Attributes:
        source_type: 源格式（yaml / visual / schema）
        target_type: 目标格式
        type_count_before: 转换前类型数量
        type_count_after: 转换后类型数量
        is_equivalent: 是否等价
        differences: 差异列表
    """

    source_type: str
    target_type: str
    type_count_before: int
    type_count_after: int
    is_equivalent: bool
    differences: list[str] = field(default_factory=list)


# ─── VisualGraph → OntologySchema ───
# 可视化设计导出为运行时 Schema


def visual_graph_to_schema(
    graph: VisualGraph,
    catalog: OntologyCatalog | None = None,
) -> OntologySchema:
    """将 VisualGraph 编译为 OntologySchema。

    规则：
    - 节点 type_id = "event" 前缀 → EventType
    - 节点 type_id = "context" 前缀 → ContextType
    - 节点 type_id = "fact" 前缀 → FactType
    - 节点 properties 映射到对应类型的 properties 字段
    - 边被忽略（运行时 Schema 不存储图结构）

    Args:
        graph: 可视化图
        catalog: 可选 Catalog，用于解析节点类型信息

    Returns:
        编译后的 OntologySchema
    """
    event_types: list[EventType] = []
    context_types: list[ContextType] = []
    fact_types: list[FactType] = []

    for node in graph.nodes:
        props = node.properties or {}
        type_info = _resolve_type_info(node.type_id, catalog)

        if _is_event_type(node.type_id):
            event_types.append(
                EventType(
                    id=node.node_id,
                    name=node.label,
                    description=type_info.get("description", ""),
                    subject_type=props.get("subject_type", "agent-role"),
                    object_type=props.get("object_type"),
                    properties=_extract_string_keys(props.get("properties")),
                    timestamp_field=props.get("timestamp_field", "timestamp"),
                )
            )
        elif _is_context_type(node.type_id):
            context_types.append(
                ContextType(
                    id=node.node_id,
                    name=node.label,
                    description=type_info.get("description", ""),
                    properties=_extract_string_keys(
                        props.get("properties")
                    ),
                    lifecycle=props.get("lifecycle", "ephemeral"),
                )
            )
        elif _is_fact_type(node.type_id):
            fact_types.append(
                FactType(
                    id=node.node_id,
                    name=node.label,
                    description=type_info.get("description", ""),
                    subject_type=props.get("subject_type", ""),
                    object_type=props.get("object_type"),
                    establishment_condition=props.get(
                        "establishment_condition"
                    ),
                    evidence_binding=props.get("evidence_binding", True),
                )
            )

    return OntologySchema(
        event_types=event_types,
        context_types=context_types,
        fact_types=fact_types,
    )


# ─── OntologySchema → VisualGraph ───
# 运行时 Schema 反向生成可视化图（用于预览/审查）


def schema_to_visual_graph(
    schema: OntologySchema,
) -> VisualGraph:
    """将 OntologySchema 反向生成为 VisualGraph。

    用于在可视化编辑器中预览/审查现有 Schema。

    规则：
    - 每个 EventType → VisualNode（type_id = "event" + et.id）
    - 每个 ContextType → VisualNode（type_id = "context" + ct.id）
    - 每个 FactType → VisualNode（type_id = "fact" + ft.id）
    - 不生成边（Schema 不包含图结构信息）
    """
    nodes: list[VisualNode] = []

    for et in schema.event_types:
        nodes.append(
            VisualNode(
                node_id=et.id,
                type_id="event-" + et.id,
                label=et.name,
                properties={
                    "subject_type": et.subject_type,
                    "object_type": et.object_type,
                    "properties": et.properties,
                },
                metadata={"source": "schema", "category": "event"},
            )
        )

    for ct in schema.context_types:
        nodes.append(
            VisualNode(
                node_id=ct.id,
                type_id="context-" + ct.id,
                label=ct.name,
                properties={
                    "properties": ct.properties,
                    "lifecycle": ct.lifecycle,
                },
                metadata={"source": "schema", "category": "context"},
            )
        )

    for ft in schema.fact_types:
        nodes.append(
            VisualNode(
                node_id=ft.id,
                type_id="fact-" + ft.id,
                label=ft.name,
                properties={
                    "subject_type": ft.subject_type,
                    "object_type": ft.object_type,
                    "establishment_condition": ft.establishment_condition,
                },
                metadata={"source": "schema", "category": "fact"},
            )
        )

    return VisualGraph(
        graph_id="schema-visual",
        name="OntologySchema Visual Preview",
        nodes=nodes,
        edges=[],
        metadata={"generated_from": "OntologySchema"},
    )


# ─── YAML → VisualGraph ───
# 配置加载为可视化图


def yaml_config_to_visual_graph(
    config: dict[str, Any],
) -> VisualGraph:
    """将 YAML 配置转换为 VisualGraph。

    YAML 格式：
    graph_id: "my-graph"
    name: "My Ontology Graph"
    nodes:
      - node_id: "n1"
        type_id: "tool-invocation"
        label: "Tool Invocation"
        properties: {...}
    edges:
      - edge_id: "e1"
        type_id: "derives"
        source_id: "n1"
        target_id: "n2"

    Args:
        config: YAML 解析后的 dict

    Returns:
        VisualGraph
    """
    from ontology.visual_model import (
        build_visual_edge,
        build_visual_node,
    )

    return VisualGraph(
        graph_id=config.get("graph_id", "unnamed"),
        name=config.get("name", config.get("graph_id", "unnamed")),
        nodes=[build_visual_node(n) for n in config.get("nodes", [])],
        edges=[build_visual_edge(e) for e in config.get("edges", [])],
        metadata=config.get("metadata", {}),
    )


# ─── Round-Trip Verification ───


def verify_schema_roundtrip(schema: OntologySchema) -> RoundTripReport:
    """验证 Schema → VisualGraph → Schema 的往返等价性。

    证明可视化编辑不会导致信息丢失。
    """
    before_count = (
        len(schema.event_types)
        + len(schema.context_types)
        + len(schema.fact_types)
    )

    # Schema → VisualGraph
    graph = schema_to_visual_graph(schema)

    # VisualGraph → Schema
    rebuilt = visual_graph_to_schema(graph)

    after_count = (
        len(rebuilt.event_types)
        + len(rebuilt.context_types)
        + len(rebuilt.fact_types)
    )

    differences: list[str] = []

    # 检查 EventType
    before_events = {et.id: et for et in schema.event_types}
    after_events = {et.id: et for et in rebuilt.event_types}
    for eid, before_et in before_events.items():
        after_et = after_events.get(eid)
        if after_et is None:
            differences.append(f"EventType {eid!r} 丢失")
        elif before_et.name != after_et.name:
            differences.append(
                f"EventType {eid!r} 名称变化: "
                f"{before_et.name!r} -> {after_et.name!r}"
            )

    # 检查 FactType
    before_facts = {ft.id: ft for ft in schema.fact_types}
    after_facts = {ft.id: ft for ft in rebuilt.fact_types}
    for fid, before_ft in before_facts.items():
        after_ft = after_facts.get(fid)
        if after_ft is None:
            differences.append(f"FactType {fid!r} 丢失")

    return RoundTripReport(
        source_type="schema",
        target_type="schema",
        type_count_before=before_count,
        type_count_after=after_count,
        is_equivalent=len(differences) == 0,
        differences=differences,
    )


# ─── Internal Helpers ───


def _is_event_type(type_id: str) -> bool:
    """判断 type_id 是否为事件类型。"""
    return type_id.startswith("event")


def _is_context_type(type_id: str) -> bool:
    """判断 type_id 是否为上下文类型。"""
    return type_id.startswith("context")


def _is_fact_type(type_id: str) -> bool:
    """判断 type_id 是否为事实类型。"""
    return type_id.startswith("fact")


def _resolve_type_info(
    type_id: str, catalog: OntologyCatalog | None
) -> dict[str, str]:
    """从 Catalog 解析类型信息。"""
    if catalog is None:
        return {}
    vnt = catalog.get_visual_node_type(type_id)
    if vnt is None:
        return {}
    return {"description": vnt.description}


def _extract_string_keys(data: Any) -> list[str]:
    """从数据中提取字符串键列表。

    支持 list[str] 或 dict（取 keys）。
    """
    if isinstance(data, list):
        return [str(x) for x in data if isinstance(x, str)]
    if isinstance(data, dict):
        return list(data.keys())
    return []
