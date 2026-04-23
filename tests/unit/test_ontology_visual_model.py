"""Ontology Visual Model 单元测试。"""

from ontology.visual_model import (
    Palette,
    VisualNodeType,
    build_form_schema,
    build_palette,
    build_property_schema,
    build_visual_edge,
    build_visual_edge_type,
    build_visual_graph,
    build_visual_node,
    build_visual_node_type,
)


class TestVisualNodeType:
    def test_type_is_frozen(self):
        """VisualNodeType 不可变。"""
        t = VisualNodeType(
            id="event-test", name="Test", category="event", description=""
        )
        import dataclasses

        assert dataclasses.is_dataclass(t)
        assert t.__dataclass_fields__["id"].type in (str, "str")

    def test_build_from_dict(self):
        """从 dict 构建。"""
        data = {
            "id": "event-tool-invocation",
            "name": "工具调用",
            "category": "event",
            "description": "Agent 调用工具",
            "visual_hint": "tool",
            "color": "#4A90D9",
        }
        t = build_visual_node_type(data)
        assert t.id == "event-tool-invocation"
        assert t.name == "工具调用"
        assert t.category == "event"
        assert t.visual_hint == "tool"
        assert t.color == "#4A90D9"

    def test_defaults(self):
        """默认值正确。"""
        data = {"id": "e1", "name": "E", "category": "event"}
        t = build_visual_node_type(data)
        assert t.visual_hint == "circle"
        assert t.color == "#808080"
        assert t.min_instances == 0
        assert t.max_instances is None


class TestVisualEdgeType:
    def test_build_from_dict(self):
        """从 dict 构建 VisualEdgeType。"""
        data = {
            "id": "derives",
            "name": "推导出",
            "source_type": "event-tool-invocation",
            "target_type": "fact-review-requirement",
            "label": "derives",
        }
        t = build_visual_edge_type(data)
        assert t.id == "derives"
        assert t.source_type == "event-tool-invocation"
        assert t.target_type == "fact-review-requirement"
        assert t.directed is True


class TestPropertySchema:
    def test_build_from_dict(self):
        """从 dict 构建 PropertySchema。"""
        data = {
            "name": "tool_name",
            "prop_type": "string",
            "required": True,
            "description": "工具名称",
        }
        ps = build_property_schema(data)
        assert ps.name == "tool_name"
        assert ps.prop_type == "string"
        assert ps.required is True

    def test_enum_values(self):
        """enum 类型支持。"""
        data = {
            "name": "severity",
            "prop_type": "enum",
            "enum_values": ["low", "medium", "high"],
        }
        ps = build_property_schema(data)
        assert ps.enum_values == ["low", "medium", "high"]


class TestFormSchema:
    def test_build_from_dict(self):
        """从 dict 构建 FormSchema。"""
        data = {
            "type_id": "event-tool-invocation",
            "title": "工具调用配置",
            "sections": [
                {"title": "基本信息", "fields": ["name", "description"]}
            ],
        }
        fs = build_form_schema(data)
        assert fs.type_id == "event-tool-invocation"
        assert fs.title == "工具调用配置"
        assert len(fs.sections) == 1


class TestVisualNode:
    def test_build_from_dict(self):
        """从 dict 构建 VisualNode。"""
        data = {
            "node_id": "n1",
            "type_id": "event-tool-invocation",
            "label": "工具调用",
            "position": {"x": 100, "y": 200},
            "properties": {"tool_name": "Write"},
        }
        node = build_visual_node(data)
        assert node.node_id == "n1"
        assert node.type_id == "event-tool-invocation"
        assert node.position == {"x": 100, "y": 200}
        assert node.properties["tool_name"] == "Write"


class TestVisualEdge:
    def test_build_from_dict(self):
        """从 dict 构建 VisualEdge。"""
        data = {
            "edge_id": "e1",
            "type_id": "derives",
            "source_id": "n1",
            "target_id": "n2",
            "label": "derives",
        }
        edge = build_visual_edge(data)
        assert edge.source_id == "n1"
        assert edge.target_id == "n2"


class TestVisualGraph:
    def test_build_from_dict(self):
        """从 dict 构建 VisualGraph。"""
        data = {
            "graph_id": "g1",
            "name": "Test Graph",
            "nodes": [
                {
                    "node_id": "n1",
                    "type_id": "event-tool-invocation",
                    "label": "Tool",
                }
            ],
            "edges": [],
        }
        graph = build_visual_graph(data)
        assert graph.graph_id == "g1"
        assert len(graph.nodes) == 1
        assert len(graph.edges) == 0


class TestPalette:
    def test_palette_categories(self):
        """Palette 分类管理。"""
        p = build_palette({
            "categories": [
                {
                    "id": "events",
                    "name": "事件",
                    "description": "事件类型",
                    "color": "#4A90D9",
                    "node_types": ["event-tool-invocation"],
                }
            ]
        })
        cat = p.get_category("events")
        assert cat is not None
        assert cat.name == "事件"
        assert "event-tool-invocation" in cat.node_types

    def test_all_node_type_ids(self):
        """获取所有节点类型 ID。"""
        p = build_palette({
            "categories": [
                {
                    "id": "events",
                    "name": "E",
                    "description": "",
                    "node_types": ["e1", "e2"],
                },
                {
                    "id": "facts",
                    "name": "F",
                    "description": "",
                    "node_types": ["f1"],
                },
            ]
        })
        assert p.all_node_type_ids() == {"e1", "e2", "f1"}

    def test_get_missing_category(self):
        """获取不存在的分类返回 None。"""
        p = Palette()
        assert p.get_category("missing") is None
