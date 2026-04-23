"""Ontology Round-Trip 单元测试。"""

from ontology.roundtrip import (
    schema_to_visual_graph,
    verify_schema_roundtrip,
    visual_graph_to_schema,
    yaml_config_to_visual_graph,
)
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


def _make_schema():
    """创建测试用 Schema。"""
    return OntologySchema(
        event_types=[
            EventType(
                id="tool-invocation",
                name="工具调用",
                description="Agent 调用工具的事件",
                subject_type="agent-role",
                object_type="task-type",
                properties=["tool_name", "tool_args"],
            ),
        ],
        context_types=[
            ContextType(
                id="session-context",
                name="会话上下文",
                description="会话环境",
                properties=["session_id"],
            ),
        ],
        fact_types=[
            FactType(
                id="review-requirement",
                name="审查要求",
                description="Write 工具需要审查",
                subject_type="agent-role",
                establishment_condition="tool_name == Write",
            ),
        ],
    )


class TestSchemaToVisualGraph:
    def test_schema_to_graph(self):
        """Schema 转为 VisualGraph。"""
        schema = _make_schema()
        graph = schema_to_visual_graph(schema)
        assert graph.graph_id == "schema-visual"
        assert len(graph.nodes) == 3  # 1 event + 1 context + 1 fact

    def test_event_node_structure(self):
        """事件节点结构正确。"""
        schema = _make_schema()
        graph = schema_to_visual_graph(schema)
        event_nodes = [
            n for n in graph.nodes if n.metadata.get("category") == "event"
        ]
        assert len(event_nodes) == 1
        node = event_nodes[0]
        assert node.node_id == "tool-invocation"
        assert node.label == "工具调用"
        assert node.properties["subject_type"] == "agent-role"

    def test_context_node_structure(self):
        """上下文节点结构正确。"""
        schema = _make_schema()
        graph = schema_to_visual_graph(schema)
        ctx_nodes = [
            n for n in graph.nodes if n.metadata.get("category") == "context"
        ]
        assert len(ctx_nodes) == 1
        assert ctx_nodes[0].node_id == "session-context"
        assert ctx_nodes[0].properties["lifecycle"] == "ephemeral"

    def test_fact_node_structure(self):
        """事实节点结构正确。"""
        schema = _make_schema()
        graph = schema_to_visual_graph(schema)
        fact_nodes = [
            n for n in graph.nodes if n.metadata.get("category") == "fact"
        ]
        assert len(fact_nodes) == 1
        node = fact_nodes[0]
        assert node.node_id == "review-requirement"
        assert node.properties.get(
            "establishment_condition"
        ) == "tool_name == Write"


class TestVisualGraphToSchema:
    def test_graph_to_schema(self):
        """VisualGraph 转为 OntologySchema。"""
        graph = VisualGraph(
            graph_id="g1",
            name="Test",
            nodes=[
                VisualNode(
                    node_id="evt-1",
                    type_id="event-tool-invocation",
                    label="Tool Call",
                    properties={
                        "subject_type": "agent-role",
                        "object_type": "task-type",
                        "properties": ["tool_name"],
                    },
                )
            ],
        )
        schema = visual_graph_to_schema(graph)
        assert len(schema.event_types) == 1
        assert schema.event_types[0].id == "evt-1"
        assert schema.event_types[0].name == "Tool Call"


class TestYamlConfigToVisualGraph:
    def test_yaml_to_graph(self):
        """YAML 配置转为 VisualGraph。"""
        config = {
            "graph_id": "test-graph",
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
        graph = yaml_config_to_visual_graph(config)
        assert graph.graph_id == "test-graph"
        assert len(graph.nodes) == 1
        assert graph.nodes[0].node_id == "n1"


class TestRoundTripVerification:
    def test_schema_roundtrip_equivalent(self):
        """Schema 往返等价。"""
        schema = _make_schema()
        report = verify_schema_roundtrip(schema)
        assert report.is_equivalent is True
        assert report.differences == []

    def test_roundtrip_preserves_type_count(self):
        """Round-Trip 保留类型数量。"""
        schema = _make_schema()
        before = (
            len(schema.event_types)
            + len(schema.context_types)
            + len(schema.fact_types)
        )
        report = verify_schema_roundtrip(schema)
        assert report.type_count_before == before
        assert report.type_count_after == before

    def test_empty_schema_roundtrip(self):
        """空 Schema 往返。"""
        schema = OntologySchema()
        report = verify_schema_roundtrip(schema)
        assert report.is_equivalent is True
        assert report.type_count_before == 0
        assert report.type_count_after == 0
