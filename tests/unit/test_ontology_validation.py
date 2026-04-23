"""Ontology Validation 单元测试。"""

from ontology.catalog import OntologyCatalog
from ontology.schema import (
    EventType,
    FactType,
    OntologySchema,
)
from ontology.validation import (
    validate_catalog_completeness,
    validate_full_ontology,
    validate_schema_references,
    validate_visual_graph,
)
from ontology.visual_model import VisualEdge, VisualGraph, VisualNode


class TestValidateSchemaReferences:
    def test_valid_schema(self):
        """有效 Schema 通过校验。"""
        schema = OntologySchema(
            event_types=[
                EventType(
                    id="tool-invocation",
                    name="工具调用",
                    description="",
                    subject_type="agent-role",
                )
            ],
            fact_types=[
                FactType(
                    id="review-requirement",
                    name="审查要求",
                    description="",
                    subject_type="agent-role",
                    establishment_condition="tool_name == Write",
                )
            ],
        )
        result = validate_schema_references(schema)
        assert result.is_valid is True
        assert result.errors == []

    def test_empty_establishment_condition(self):
        """空的 establishment_condition 报错。"""
        schema = OntologySchema(
            fact_types=[
                FactType(
                    id="bad-fact",
                    name="Bad",
                    description="",
                    subject_type="agent-role",
                    establishment_condition="  ",
                )
            ]
        )
        result = validate_schema_references(schema)
        assert result.is_valid is False
        assert any("establishment_condition" in e for e in result.errors)

    def test_missing_subject_type(self):
        """EventType 缺少 subject_type 报错。"""
        schema = OntologySchema(
            event_types=[
                EventType(
                    id="bad-event",
                    name="Bad",
                    description="",
                    subject_type="",
                )
            ]
        )
        result = validate_schema_references(schema)
        assert result.is_valid is False
        assert any("subject_type" in e for e in result.errors)


class TestValidateVisualGraph:
    def test_valid_graph(self):
        """有效图通过校验。"""
        graph = VisualGraph(
            graph_id="g1",
            name="Test",
            nodes=[
                VisualNode(node_id="n1", type_id="event-t", label="N1"),
                VisualNode(node_id="n2", type_id="fact-t", label="N2"),
            ],
            edges=[
                VisualEdge(
                    edge_id="e1",
                    type_id="derives",
                    source_id="n1",
                    target_id="n2",
                )
            ],
        )
        result = validate_visual_graph(graph)
        assert result.is_valid is True

    def test_dangling_edge(self):
        """悬空边报错。"""
        graph = VisualGraph(
            graph_id="g1",
            name="Test",
            nodes=[
                VisualNode(node_id="n1", type_id="event-t", label="N1"),
            ],
            edges=[
                VisualEdge(
                    edge_id="e1",
                    type_id="derives",
                    source_id="n1",
                    target_id="missing",
                )
            ],
        )
        result = validate_visual_graph(graph)
        assert result.is_valid is False
        assert any("悬空边" in e for e in result.errors)

    def test_duplicate_node_id(self):
        """重复节点 ID 报错。"""
        graph = VisualGraph(
            graph_id="g1",
            name="Test",
            nodes=[
                VisualNode(node_id="n1", type_id="event-t", label="N1"),
                VisualNode(node_id="n1", type_id="fact-t", label="N2"),
            ],
        )
        result = validate_visual_graph(graph)
        assert result.is_valid is False
        assert any("重复" in e for e in result.errors)

    def test_self_loop_warning(self):
        """自环发出警告。"""
        graph = VisualGraph(
            graph_id="g1",
            name="Test",
            nodes=[
                VisualNode(node_id="n1", type_id="event-t", label="N1"),
            ],
            edges=[
                VisualEdge(
                    edge_id="e1",
                    type_id="self",
                    source_id="n1",
                    target_id="n1",
                )
            ],
        )
        result = validate_visual_graph(graph)
        assert result.is_valid is True  # 只是警告
        assert any("自环" in w for w in result.warnings)


class TestValidateCatalogCompleteness:
    def test_empty_catalog(self):
        """空 Catalog 报错。"""
        catalog = OntologyCatalog()
        result = validate_catalog_completeness(catalog)
        assert result.is_valid is False
        assert any("Catalog 为空" in e for e in result.errors)

    def test_facts_without_events(self):
        """有 FactType 没有 EventType 发出警告。"""
        catalog = OntologyCatalog(
            fact_types=[
                FactType(
                    id="f1", name="F", description="", subject_type="t"
                )
            ]
        )
        result = validate_catalog_completeness(catalog)
        assert result.is_valid is True
        assert any(
            "FactType" in w and "EventType" in w for w in result.warnings
        )

    def test_complete_catalog(self):
        """完整的 Catalog 通过。"""
        catalog = OntologyCatalog(
            event_types=[
                EventType(
                    id="e1", name="E", description="", subject_type="t"
                )
            ],
            fact_types=[
                FactType(
                    id="f1", name="F", description="", subject_type="t"
                )
            ],
        )
        result = validate_catalog_completeness(catalog)
        assert result.is_valid is True
        assert result.warnings == []


class TestValidateFullOntology:
    def test_full_valid_ontology(self):
        """完整校验通过。"""
        schema = OntologySchema(
            event_types=[
                EventType(
                    id="tool-invocation",
                    name="工具调用",
                    description="",
                    subject_type="agent-role",
                )
            ],
            fact_types=[
                FactType(
                    id="review-requirement",
                    name="审查要求",
                    description="",
                    subject_type="agent-role",
                    establishment_condition="tool_name == Write",
                )
            ],
        )
        result = validate_full_ontology(schema)
        assert result.is_valid is True
        assert result.errors == []

    def test_duplicate_id_detected(self):
        """重复 ID 被检测。"""
        schema = OntologySchema(
            event_types=[
                EventType(
                    id="dup", name="A", description="", subject_type="t"
                ),
                EventType(
                    id="dup", name="B", description="", subject_type="t"
                ),
            ]
        )
        result = validate_full_ontology(schema)
        assert result.is_valid is False
        assert any("dup" in e and "重复" in e for e in result.errors)
