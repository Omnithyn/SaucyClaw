"""Ontology Studio Contract 单元测试。

N1.6 — Studio Contract Closure

验证：
1. Studio manifest 可加载
2. Catalog / Palette / FormSchema 的 source of truth 一致
3. round-trip 对"正式支持"元素成立
4. 对"未正式支持"元素有明确报错或警告语义
"""

from ontology.roundtrip import (
    RoundTripUnsupportedError,
    verify_roundtrip_with_surface,
    verify_schema_roundtrip,
    visual_graph_to_schema,
)
from ontology.schema import (
    EventType,
    FactType,
    OntologySchema,
)
from ontology.studio_loader import (
    get_supported_surface,
    load_studio_manifest,
    is_reserved_edge_type,
    is_reserved_node_type,
    is_supported_edge_type,
    is_supported_node_type,
)
from ontology.validation import validate_visual_graph
from ontology.visual_model import (
    VisualEdge,
    VisualGraph,
    VisualNode,
)


class TestStudioManifestLoad:
    def test_load_studio_manifest(self):
        """Studio manifest 可加载。"""
        result = load_studio_manifest()
        assert result.palette is not None
        assert result.version == "1.0"
        assert len(result.visual_node_types) > 0

    def test_palette_contains_supported_categories(self):
        """Palette 包含 supported categories。"""
        result = load_studio_manifest()
        categories = result.palette.categories
        assert len(categories) >= 3  # event, context, fact
        cat_ids = [c.id for c in categories]
        assert "event" in cat_ids
        assert "context" in cat_ids
        assert "fact" in cat_ids

    def test_palette_excludes_reserved_categories(self):
        """Palette 不包含 reserved categories。"""
        result = load_studio_manifest()
        categories = result.palette.categories
        cat_ids = [c.id for c in categories]
        assert "entity" not in cat_ids
        assert "relation" not in cat_ids
        assert "policy" not in cat_ids


class TestSupportedSurface:
    def test_get_supported_surface(self):
        """get_supported_surface 返回默认 surface。"""
        surface = get_supported_surface()
        assert "event" in surface.supported_node_prefixes
        assert "context" in surface.supported_node_prefixes
        assert "fact" in surface.supported_node_prefixes

    def test_reserved_prefixes(self):
        """reserved prefixes 正确。"""
        surface = get_supported_surface()
        assert "entity" in surface.reserved_node_prefixes
        assert "relation" in surface.reserved_node_prefixes
        assert "policy" in surface.reserved_node_prefixes

    def test_supported_edge_types(self):
        """supported edge types 正确。"""
        surface = get_supported_surface()
        assert "derives" in surface.supported_edge_types

    def test_reserved_edge_types(self):
        """reserved edge types 正确。"""
        surface = get_supported_surface()
        assert "relates" in surface.reserved_edge_types
        assert "triggers" in surface.reserved_edge_types
        assert "requires" in surface.reserved_edge_types


class TestNodeTypeDetection:
    def test_is_supported_event_type(self):
        """event 类型被识别为 supported。"""
        assert is_supported_node_type("event-tool-invocation") is True
        assert is_supported_node_type("event-xyz") is True

    def test_is_supported_context_type(self):
        """context 类型被识别为 supported。"""
        assert is_supported_node_type("context-session") is True

    def test_is_supported_fact_type(self):
        """fact 类型被识别为 supported。"""
        assert is_supported_node_type("fact-review-requirement") is True

    def test_is_reserved_entity_type(self):
        """entity 类型被识别为 reserved。"""
        assert is_reserved_node_type("entity-agent") is True

    def test_is_reserved_relation_type(self):
        """relation 类型被识别为 reserved。"""
        assert is_reserved_node_type("relation-xyz") is True

    def test_is_reserved_policy_type(self):
        """policy 类型被识别为 reserved。"""
        assert is_reserved_node_type("policy-xyz") is True

    def test_unknown_type_not_supported(self):
        """未知类型既不是 supported 也不是 reserved。"""
        assert is_supported_node_type("unknown-type") is False
        assert is_reserved_node_type("unknown-type") is False


class TestEdgeTypeDetection:
    def test_is_supported_derives(self):
        """derives 边被识别为 supported。"""
        assert is_supported_edge_type("derives") is True

    def test_is_reserved_relates(self):
        """relates 边被识别为 reserved。"""
        assert is_reserved_edge_type("relates") is True

    def test_is_reserved_triggers(self):
        """triggers 边被识别为 reserved。"""
        assert is_reserved_edge_type("triggers") is True

    def test_unknown_edge_not_supported(self):
        """未知边既不是 supported 也不是 reserved。"""
        assert is_supported_edge_type("unknown-edge") is False
        assert is_reserved_edge_type("unknown-edge") is False


class TestRoundTripSupportedElements:
    def test_supported_event_roundtrip(self):
        """supported event 类型 round-trip 通过。"""
        schema = OntologySchema(
            event_types=[
                EventType(
                    id="tool-invocation",
                    name="工具调用",
                    description="",
                    subject_type="agent-role",
                )
            ]
        )
        report = verify_schema_roundtrip(schema)
        assert report.is_equivalent is True

    def test_supported_fact_roundtrip(self):
        """supported fact 类型 round-trip 通过。"""
        schema = OntologySchema(
            fact_types=[
                FactType(
                    id="review-requirement",
                    name="审查要求",
                    description="",
                    subject_type="agent-role",
                    establishment_condition="tool_name == Write",
                )
            ]
        )
        report = verify_schema_roundtrip(schema)
        assert report.is_equivalent is True

    def test_verify_roundtrip_with_surface_supported_only(self):
        """仅包含 supported 元素的 graph 通过验证。"""
        graph = VisualGraph(
            graph_id="g1",
            name="Test",
            nodes=[
                VisualNode(
                    node_id="n1",
                    type_id="event-tool-invocation",
                    label="Tool",
                )
            ],
        )
        report = verify_roundtrip_with_surface(graph)
        assert report.is_equivalent is True
        assert report.unsupported_elements == []


class TestRoundTripUnsupportedElements:
    def test_reserved_node_raises_error_strict(self):
        """reserved node 类型在 strict 模式抛出异常。"""
        graph = VisualGraph(
            graph_id="g1",
            name="Test",
            nodes=[
                VisualNode(
                    node_id="n1",
                    type_id="entity-agent",
                    label="Agent",
                )
            ],
        )
        import pytest
        with pytest.raises(RoundTripUnsupportedError) as exc_info:
            visual_graph_to_schema(graph, strict=True)
        assert "entity-agent" in str(exc_info.value)

    def test_reserved_node_skipped_non_strict(self):
        """reserved node 类型在 non-strict 模式跳过。"""
        graph = VisualGraph(
            graph_id="g1",
            name="Test",
            nodes=[
                VisualNode(
                    node_id="n1",
                    type_id="entity-agent",
                    label="Agent",
                )
            ],
        )
        schema = visual_graph_to_schema(graph, strict=False)
        assert len(schema.event_types) == 0
        assert len(schema.fact_types) == 0

    def test_reserved_edge_raises_error_strict(self):
        """reserved edge 类型在 strict 模式抛出异常。"""
        graph = VisualGraph(
            graph_id="g1",
            name="Test",
            nodes=[
                VisualNode(
                    node_id="n1",
                    type_id="event-tool-invocation",
                    label="E1",
                ),
                VisualNode(
                    node_id="n2",
                    type_id="fact-review",
                    label="F1",
                ),
            ],
            edges=[
                VisualEdge(
                    edge_id="e1",
                    type_id="relates",
                    source_id="n1",
                    target_id="n2",
                )
            ],
        )
        import pytest
        with pytest.raises(RoundTripUnsupportedError) as exc_info:
            visual_graph_to_schema(graph, strict=True)
        assert "relates" in str(exc_info.value)

    def test_verify_roundtrip_reports_unsupported(self):
        """verify_roundtrip_with_surface 报告 unsupported 元素。"""
        graph = VisualGraph(
            graph_id="g1",
            name="Test",
            nodes=[
                VisualNode(
                    node_id="n1",
                    type_id="entity-agent",
                    label="Agent",
                )
            ],
        )
        report = verify_roundtrip_with_surface(graph)
        assert report.is_equivalent is False
        assert len(report.unsupported_elements) > 0
        assert any("entity-agent" in e for e in report.unsupported_elements)


class TestValidationUnsupportedElements:
    def test_reserved_node_validation_error(self):
        """reserved node 在 validation 中发出 error。"""
        graph = VisualGraph(
            graph_id="g1",
            name="Test",
            nodes=[
                VisualNode(
                    node_id="n1",
                    type_id="entity-agent",
                    label="Agent",
                )
            ],
        )
        result = validate_visual_graph(graph)
        assert result.is_valid is False
        assert any("预留类型" in e for e in result.errors)

    def test_reserved_edge_validation_error(self):
        """reserved edge 在 validation 中发出 error。"""
        graph = VisualGraph(
            graph_id="g1",
            name="Test",
            nodes=[
                VisualNode(
                    node_id="n1",
                    type_id="event-tool",
                    label="E",
                ),
                VisualNode(
                    node_id="n2",
                    type_id="fact-review",
                    label="F",
                ),
            ],
            edges=[
                VisualEdge(
                    edge_id="e1",
                    type_id="relates",
                    source_id="n1",
                    target_id="n2",
                )
            ],
        )
        result = validate_visual_graph(graph)
        assert result.is_valid is False
        assert any("预留类型" in e for e in result.errors)

    def test_unknown_node_validation_error(self):
        """未知 node 类型在 validation 中发出 error。"""
        graph = VisualGraph(
            graph_id="g1",
            name="Test",
            nodes=[
                VisualNode(
                    node_id="n1",
                    type_id="unknown-type",
                    label="Unknown",
                )
            ],
        )
        result = validate_visual_graph(graph)
        assert result.is_valid is False
        assert any("未知类型" in e for e in result.errors)


class TestCatalogPaletteAlignment:
    def test_catalog_and_palette_from_manifest(self):
        """Catalog 和 Palette 从 manifest 构建时对齐。"""
        manifest = load_studio_manifest()
        palette = manifest.palette

        # Palette categories 应与 catalog type_count 的 event/context/fact 对齐
        cat_ids = [c.id for c in palette.categories]
        assert "event" in cat_ids
        assert "context" in cat_ids
        assert "fact" in cat_ids

    def test_manifest_node_types_count(self):
        """manifest 中 node_types 数量与 visual_node_types 一致。"""
        manifest = load_studio_manifest()
        palette = manifest.palette
        total_palette_nodes = sum(
            len(c.node_types) for c in palette.categories
        )
        assert total_palette_nodes == len(manifest.visual_node_types)
