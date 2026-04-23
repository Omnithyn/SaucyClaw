"""Ontology Studio Contract 单元测试。

N1.6 — Studio Contract Closure
N1.7 — Ontology Studio Semantic Surface Expansion

验证：
1. Studio manifest 可加载
2. Catalog / Palette / FormSchema 的 source of truth 一致
3. round-trip 对"正式支持"元素成立
4. 对"预览支持"元素有明确警告语义
5. N1.7 三层 Surface：supported / preview / reserved
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

# N1.7 新增导入
from ontology.semantic_surface import (
    is_preview_node_type,
    is_preview_edge_type,
)


class TestStudioManifestLoad:
    def test_load_studio_manifest(self):
        """Studio manifest 可加载（N1.7 版本 1.1）。"""
        result = load_studio_manifest()
        assert result.palette is not None
        assert result.preview_palette is not None  # N1.7 新增
        assert result.version == "1.1"  # N1.7 升级版本
        assert len(result.visual_node_types) > 0

    def test_palette_contains_supported_categories(self):
        """Palette 包含 supported categories（含 entity）。"""
        result = load_studio_manifest()
        categories = result.palette.categories
        assert len(categories) >= 4  # event, context, fact, entity（N1.7 新增）
        cat_ids = [c.id for c in categories]
        assert "event" in cat_ids
        assert "context" in cat_ids
        assert "fact" in cat_ids
        assert "entity" in cat_ids  # N1.7: entity 升级为 supported

    def test_palette_excludes_reserved_categories(self):
        """Palette 不包含 reserved categories（N1.7：reserved 为空）。"""
        result = load_studio_manifest()
        categories = result.palette.categories
        cat_ids = [c.id for c in categories]
        # N1.7: relation/policy 在 preview_palette 中，不在 palette 中
        assert "relation" not in cat_ids
        assert "policy" not in cat_ids

    def test_preview_palette_contains_preview_categories(self):
        """Preview Palette 包含 preview categories（N1.7 新增）。"""
        result = load_studio_manifest()
        preview_categories = result.preview_palette.categories
        cat_ids = [c.id for c in preview_categories]
        assert "relation" in cat_ids
        assert "policy" in cat_ids


class TestSupportedSurface:
    def test_get_supported_surface(self):
        """get_supported_surface 返回默认 surface（N1.7 兼容）。"""
        surface = get_supported_surface()
        assert "event" in surface.supported_node_prefixes
        assert "context" in surface.supported_node_prefixes
        assert "fact" in surface.supported_node_prefixes
        assert "entity" in surface.supported_node_prefixes  # N1.7: entity 升级

    def test_reserved_prefixes(self):
        """reserved prefixes 现在为空（N1.7 升级）。"""
        # N1.7: relation/policy 升级为 preview，reserved 为空
        surface = get_supported_surface()
        assert len(surface.reserved_node_prefixes) == 0

    def test_supported_edge_types(self):
        """supported edge types 正确。"""
        surface = get_supported_surface()
        assert "derives" in surface.supported_edge_types

    def test_reserved_edge_types(self):
        """reserved edge types 现在为空（N1.7 升级）。"""
        # N1.7: relates/triggers/requires 升级为 preview，reserved 为空
        surface = get_supported_surface()
        assert len(surface.reserved_edge_types) == 0


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

    def test_is_supported_entity_type(self):
        """entity 类型被识别为 supported（N1.7 升级）。"""
        assert is_supported_node_type("entity-agent") is True

    def test_is_reserved_entity_type(self):
        """entity 类型不再被识别为 reserved（N1.7 升级为 supported）。"""
        # N1.7: entity 已升级为 supported
        assert is_reserved_node_type("entity-agent") is False

    def test_is_reserved_relation_type(self):
        """relation 类型现在是 preview 而非 reserved（N1.7）。"""
        # N1.7: relation 升级为 preview
        # 使用 SemanticSurface 检测
        assert is_preview_node_type("relation-xyz") is True
        # 兼容层（SupportedSurface）中 relation 不在 reserved
        assert is_reserved_node_type("relation-xyz") is False

    def test_is_reserved_policy_type(self):
        """policy 类型现在是 preview 而非 reserved（N1.7）。"""
        # N1.7: policy 升级为 preview
        assert is_preview_node_type("policy-xyz") is True
        # 兼容层（SupportedSurface）中 policy 不在 reserved
        assert is_reserved_node_type("policy-xyz") is False

    def test_unknown_type_not_supported(self):
        """未知类型既不是 supported/preview/reserved。"""
        assert is_supported_node_type("unknown-type") is False
        assert is_reserved_node_type("unknown-type") is False


class TestEdgeTypeDetection:
    def test_is_supported_derives(self):
        """derives 边被识别为 supported。"""
        assert is_supported_edge_type("derives") is True

    def test_is_reserved_relates(self):
        """relates 边现在是 preview 而非 reserved（N1.7）。"""
        # N1.7: relates 升级为 preview
        assert is_preview_edge_type("relates") is True
        # 兼容层（SupportedSurface）中 relates 不在 reserved
        assert is_reserved_edge_type("relates") is False

    def test_is_reserved_triggers(self):
        """triggers 边现在是 preview 而非 reserved（N1.7）。"""
        # N1.7: triggers 升级为 preview
        assert is_preview_edge_type("triggers") is True
        # 兼容层（SupportedSurface）中 triggers 不在 reserved
        assert is_reserved_edge_type("triggers") is False

    def test_unknown_edge_not_supported(self):
        """未知边既不是 supported/preview/reserved。"""
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
    def test_preview_node_skipped(self):
        """preview node 类型被跳过（N1.7）。"""
        # N1.7: relation 是 preview 类型，不抛异常，只跳过
        graph = VisualGraph(
            graph_id="g1",
            name="Test",
            nodes=[
                VisualNode(
                    node_id="n1",
                    type_id="relation-agent-role",  # N1.7 preview 类型
                    label="Relation",
                )
            ],
        )
        # N1.7: preview 类型不抛异常
        schema = visual_graph_to_schema(graph, strict=True)
        # preview 类型跳过，不编译到 Schema
        assert len(schema.event_types) == 0
        assert len(schema.fact_types) == 0

    def test_unknown_node_raises_error_strict(self):
        """未知 node 类型在 strict 模式抛异常（N1.7）。"""
        graph = VisualGraph(
            graph_id="g1",
            name="Test",
            nodes=[
                VisualNode(
                    node_id="n1",
                    type_id="unknown-type",  # 未知类型
                    label="Unknown",
                )
            ],
        )
        import pytest
        with pytest.raises(RoundTripUnsupportedError) as exc_info:
            visual_graph_to_schema(graph, strict=True)
        assert "unknown-type" in str(exc_info.value)

    def test_reserved_node_skipped_non_strict(self):
        """preview node 类型在 non-strict 模式跳过（N1.7）。"""
        graph = VisualGraph(
            graph_id="g1",
            name="Test",
            nodes=[
                VisualNode(
                    node_id="n1",
                    type_id="relation-agent-role",  # N1.7 preview 类型
                    label="Relation",
                )
            ],
        )
        schema = visual_graph_to_schema(graph, strict=False)
        assert len(schema.event_types) == 0
        assert len(schema.fact_types) == 0

    def test_reserved_edge_raises_error_strict(self):
        """preview edge 类型在 strict 模式不抛异常（N1.7）。"""
        # N1.7: relates 是 preview 边，有编译目标，不抛异常
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
                    type_id="relates",  # N1.7 preview 边
                    source_id="n1",
                    target_id="n2",
                )
            ],
        )
        # N1.7: preview 边不抛异常，只是跳过
        schema = visual_graph_to_schema(graph, strict=True)
        # 边不影响 Schema 编译
        assert len(schema.event_types) == 1

    def test_verify_roundtrip_reports_unsupported(self):
        """verify_roundtrip_with_surface 报告 preview 元素（N1.7）。"""
        # N1.7: preview 类型不算 unsupported，算 preview_elements
        graph = VisualGraph(
            graph_id="g1",
            name="Test",
            nodes=[
                VisualNode(
                    node_id="n1",
                    type_id="relation-agent-role",  # preview 类型
                    label="Relation",
                )
            ],
        )
        report = verify_roundtrip_with_surface(graph)
        # N1.7: preview 类型在 preview_elements 中
        assert report.is_equivalent is True  # preview 不算 unsupported
        assert len(report.preview_elements) > 0
        assert any("preview node type" in e for e in report.preview_elements)


class TestValidationUnsupportedElements:
    def test_reserved_node_validation_warning(self):
        """preview node 在 validation 中发出 warning（N1.7）。"""
        graph = VisualGraph(
            graph_id="g1",
            name="Test",
            nodes=[
                VisualNode(
                    node_id="n1",
                    type_id="relation-agent-role",  # preview 类型
                    label="Relation",
                )
            ],
        )
        result = validate_visual_graph(graph)
        # N1.7: preview 类型发 warning，不发 error
        assert result.is_valid is True  # preview 不阻止验证
        assert any("Preview 类型" in w for w in result.warnings)

    def test_reserved_edge_validation_warning(self):
        """preview edge 在 validation 中发出 warning（N1.7）。"""
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
                    type_id="relates",  # preview 边
                    source_id="n1",
                    target_id="n2",
                )
            ],
        )
        result = validate_visual_graph(graph)
        # N1.7: preview 边发 warning
        assert result.is_valid is True
        assert any("Preview 类型" in w for w in result.warnings)

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
