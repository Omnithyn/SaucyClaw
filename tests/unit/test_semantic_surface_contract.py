"""Ontology Semantic Surface Contract 单元测试。

N1.7 — Ontology Studio Semantic Surface Expansion

验证：
1. SemanticSurface 三层结构正确
2. Supported / Preview / Reserved 节点类型检测
3. Edge semantics 编译规则
4. AuthoringPackage → RuntimePackage 编译
5. Preview 类型信息丢失报告
"""

from ontology import (
    AuthoringPackage,
    compile_authoring_to_runtime,
    compile_edges_from_visual_graph,
    compile_edge_to_relation_type,
    get_edge_compilation_target,
    get_edge_semantics_description,
    get_guaranteed_fields_for_node_type,
    get_node_surface_level,
    get_semantic_surface,
    get_unsupported_fields_for_node_type,
    is_preview_edge_type,
    is_preview_node_type,
    is_supported_edge_type,
    is_supported_node_type,
    is_reserved_edge_type,
    is_reserved_node_type,
    is_visual_only_edge,
    load_studio_manifest,
    verify_roundtrip_with_surface,
    VisualGraph,
    VisualNode,
    VisualEdge,
)


class TestSemanticSurfaceStructure:
    """测试 SemanticSurface 三层结构。"""

    def test_supported_node_prefixes(self):
        """supported node prefixes 包含 event/context/fact/entity。"""
        surface = get_semantic_surface()
        assert "event" in surface.supported_node_prefixes
        assert "context" in surface.supported_node_prefixes
        assert "fact" in surface.supported_node_prefixes
        assert "entity" in surface.supported_node_prefixes

    def test_preview_node_prefixes(self):
        """preview node prefixes 包含 relation/policy。"""
        surface = get_semantic_surface()
        assert "relation" in surface.preview_node_prefixes
        assert "policy" in surface.preview_node_prefixes

    def test_reserved_node_prefixes_empty(self):
        """reserved node prefixes 为空（N1.7）。"""
        surface = get_semantic_surface()
        assert len(surface.reserved_node_prefixes) == 0

    def test_supported_edge_types(self):
        """supported edge types 包含 derives。"""
        surface = get_semantic_surface()
        assert "derives" in surface.supported_edge_types

    def test_preview_edge_types(self):
        """preview edge types 包含 relates/triggers/requires/contains。"""
        surface = get_semantic_surface()
        assert "relates" in surface.preview_edge_types
        assert "triggers" in surface.preview_edge_types
        assert "requires" in surface.preview_edge_types
        assert "contains" in surface.preview_edge_types

    def test_visual_only_edges(self):
        """visual-only edges 包含 derives/contains。"""
        surface = get_semantic_surface()
        assert "derives" in surface.visual_only_edges
        assert "contains" in surface.visual_only_edges


class TestNodeTypeDetection:
    """测试节点类型 Surface 检测。"""

    def test_is_supported_event_type(self):
        """event 类型被识别为 supported。"""
        assert is_supported_node_type("event-tool-invocation") is True
        assert is_supported_node_type("event-xyz") is True

    def test_is_supported_entity_type(self):
        """entity 类型被识别为 supported（N1.7）。"""
        assert is_supported_node_type("entity-agent") is True
        assert is_supported_node_type("entity-role") is True

    def test_is_preview_relation_type(self):
        """relation 类型被识别为 preview（N1.7）。"""
        assert is_preview_node_type("relation-agent-role") is True

    def test_is_preview_policy_type(self):
        """policy 类型被识别为 preview（N1.7）。"""
        assert is_preview_node_type("policy-review-rule") is True

    def test_is_reserved_node_type_false(self):
        """N1.7 没有 reserved node 类型。"""
        assert is_reserved_node_type("entity-agent") is False
        assert is_reserved_node_type("relation-xyz") is False

    def test_unknown_type_not_supported(self):
        """未知类型既不是 supported/preview/reserved。"""
        assert is_supported_node_type("unknown-type") is False
        assert is_preview_node_type("unknown-type") is False
        assert is_reserved_node_type("unknown-type") is False

    def test_get_node_surface_level(self):
        """get_node_surface_level 返回正确层级。"""
        assert get_node_surface_level("event-tool") == "supported"
        assert get_node_surface_level("entity-agent") == "supported"
        assert get_node_surface_level("relation-xyz") == "preview"
        assert get_node_surface_level("policy-xyz") == "preview"
        assert get_node_surface_level("unknown-type") == "unknown"


class TestEdgeTypeDetection:
    """测试边类型 Surface 检测。"""

    def test_is_supported_derives(self):
        """derives 边被识别为 supported。"""
        assert is_supported_edge_type("derives") is True

    def test_is_preview_relates(self):
        """relates 边被识别为 preview（N1.7）。"""
        assert is_preview_edge_type("relates") is True

    def test_is_preview_triggers(self):
        """triggers 边被识别为 preview（N1.7）。"""
        assert is_preview_edge_type("triggers") is True

    def test_is_preview_requires(self):
        """requires 边被识别为 preview（N1.7）。"""
        assert is_preview_edge_type("requires") is True

    def test_is_visual_only_derives(self):
        """derives 边是 visual-only。"""
        assert is_visual_only_edge("derives") is True

    def test_is_visual_only_contains(self):
        """contains 边是 visual-only。"""
        assert is_visual_only_edge("contains") is True

    def test_unknown_edge_not_supported(self):
        """未知边既不是 supported/preview/reserved。"""
        assert is_supported_edge_type("unknown-edge") is False
        assert is_preview_edge_type("unknown-edge") is False
        assert is_reserved_edge_type("unknown-edge") is False


class TestEdgeSemantics:
    """测试 Edge Semantics 编译规则。"""

    def test_get_edge_compilation_target_derives(self):
        """derives 边编译目标为 visual_only。"""
        target = get_edge_compilation_target("derives")
        assert target is not None
        assert target.target_type == "visual_only"
        assert target.is_visual_only is True

    def test_get_edge_compilation_target_relates(self):
        """relates 边编译目标为 relation_type。"""
        target = get_edge_compilation_target("relates")
        assert target is not None
        assert target.target_type == "relation_type"
        assert target.target_field == "source_type/target_type"

    def test_get_edge_compilation_target_triggers(self):
        """triggers 边编译目标为 policy_binding.trigger。"""
        target = get_edge_compilation_target("triggers")
        assert target is not None
        assert target.target_type == "policy_binding"
        assert target.target_field == "trigger"

    def test_get_edge_compilation_target_requires(self):
        """requires 边编译目标为 policy_binding.condition。"""
        target = get_edge_compilation_target("requires")
        assert target is not None
        assert target.target_type == "policy_binding"
        assert target.target_field == "condition"

    def test_get_edge_semantics_description(self):
        """get_edge_semantics_description 返回语义描述。"""
        desc = get_edge_semantics_description("derives")
        assert "Visual-only" in desc

        desc = get_edge_semantics_description("relates")
        assert "relation_type" in desc

    def test_compile_edge_to_relation_type(self):
        """relates 边编译为 RelationType。"""
        edge = VisualEdge(
            edge_id="e1",
            type_id="relates",
            source_id="n1",
            target_id="n2",
            label="Agent-Role",
            properties={"cardinality": "one-to-many"},
        )
        nodes = {
            "n1": VisualNode(
                node_id="n1",
                type_id="entity-agent",
                label="Agent",
                properties={"entity_type": "agent"},
            ),
            "n2": VisualNode(
                node_id="n2",
                type_id="entity-role",
                label="Role",
                properties={"entity_type": "role"},
            ),
        }

        rt = compile_edge_to_relation_type(edge, nodes)
        assert rt is not None
        assert rt.id == "e1"
        assert rt.name == "Agent-Role"
        assert rt.source == "agent"  # RelationType 使用 source/target
        assert rt.target == "role"   # RelationType 使用 source/target

    def test_compile_edge_to_relation_type_non_entity_fail(self):
        """relates 边源/目标非 entity 则编译失败。"""
        edge = VisualEdge(
            edge_id="e1",
            type_id="relates",
            source_id="n1",
            target_id="n2",
        )
        nodes = {
            "n1": VisualNode(node_id="n1", type_id="event-tool", label="E"),
            "n2": VisualNode(node_id="n2", type_id="entity-role", label="R"),
        }

        rt = compile_edge_to_relation_type(edge, nodes)
        assert rt is None


class TestCompilationFields:
    """测试编译字段保证。"""

    def test_get_guaranteed_fields_for_supported(self):
        """supported 类型返回完整保证字段。"""
        fields = get_guaranteed_fields_for_node_type("event-tool")
        assert "node_id" in fields
        assert "label" in fields
        assert "subject_type" in fields

    def test_get_guaranteed_fields_for_preview(self):
        """preview 类型返回部分保证字段。"""
        fields = get_guaranteed_fields_for_node_type("relation-xyz")
        assert "node_id" in fields
        assert "label" in fields
        # cardinality 不在保证字段中
        assert "cardinality" not in fields

    def test_get_unsupported_fields_for_preview(self):
        """preview 类型返回不保证字段。"""
        unsupported = get_unsupported_fields_for_node_type("relation-xyz")
        assert "cardinality" in unsupported
        assert "constraints" in unsupported

    def test_get_unsupported_fields_for_policy(self):
        """policy 类型返回不保证字段。"""
        unsupported = get_unsupported_fields_for_node_type("policy-rule")
        assert "conditions" in unsupported
        assert "judgments" in unsupported


class TestAuthoringPackage:
    """测试 AuthoringPackage 和 RuntimePackage。"""

    def test_authoring_package_creation(self):
        """AuthoringPackage 创建成功。"""
        graph = VisualGraph(
            graph_id="g1",
            name="Test Graph",
            nodes=[
                VisualNode(
                    node_id="n1",
                    type_id="event-tool",
                    label="Tool",
                ),
            ],
        )

        pkg = AuthoringPackage(
            package_id="pkg-1",
            visual_graph=graph,
        )

        assert pkg.package_id == "pkg-1"
        assert pkg.visual_graph is not None
        assert len(pkg.visual_graph.nodes) == 1

    def test_compile_authoring_to_runtime_empty(self):
        """空 AuthoringPackage 编译为空 RuntimePackage。"""
        pkg = AuthoringPackage(package_id="pkg-1")
        runtime = compile_authoring_to_runtime(pkg)

        assert runtime.package_id == "pkg-1"
        assert len(runtime.ontology_schema.event_types) == 0
        assert runtime.compilation_report is not None

    def test_compile_authoring_to_runtime_with_supported(self):
        """supported 类型完整编译。"""
        graph = VisualGraph(
            graph_id="g1",
            name="Test",
            nodes=[
                VisualNode(
                    node_id="tool-invocation",
                    type_id="event-tool-invocation",
                    label="Tool Invocation",
                    properties={"subject_type": "agent"},
                ),
            ],
        )

        pkg = AuthoringPackage(package_id="pkg-1", visual_graph=graph)
        runtime = compile_authoring_to_runtime(pkg)

        assert len(runtime.ontology_schema.event_types) == 1
        assert runtime.compilation_report.is_complete is True
        assert runtime.compilation_report.supported_types == 1
        assert runtime.compilation_report.preview_types == 0

    def test_compile_authoring_to_runtime_with_preview(self):
        """preview 类型部分编译，记录信息丢失。"""
        graph = VisualGraph(
            graph_id="g1",
            name="Test",
            nodes=[
                VisualNode(
                    node_id="agent-role",
                    type_id="relation-agent-role",
                    label="Agent-Role",
                    properties={"cardinality": "one-to-many"},
                ),
            ],
        )

        pkg = AuthoringPackage(package_id="pkg-1", visual_graph=graph)
        runtime = compile_authoring_to_runtime(pkg)

        # preview 类型跳过，不编译到 schema
        assert len(runtime.ontology_schema.event_types) == 0
        assert runtime.compilation_report.preview_types == 1
        assert len(runtime.compilation_report.information_loss_notes) > 0

    def test_compile_authoring_to_runtime_with_preview_edges(self):
        """preview edges 编译为 RelationType/PolicyBinding。"""
        graph = VisualGraph(
            graph_id="g1",
            name="Test",
            nodes=[
                VisualNode(
                    node_id="n1",
                    type_id="entity-agent",
                    label="Agent",
                    properties={"entity_type": "agent"},
                ),
                VisualNode(
                    node_id="n2",
                    type_id="entity-role",
                    label="Role",
                    properties={"entity_type": "role"},
                ),
            ],
            edges=[
                VisualEdge(
                    edge_id="e1",
                    type_id="relates",
                    source_id="n1",
                    target_id="n2",
                    label="Agent-Role",
                ),
            ],
        )

        pkg = AuthoringPackage(package_id="pkg-1", visual_graph=graph)
        runtime = compile_authoring_to_runtime(pkg)

        # relates 边编译为 RelationType
        assert len(runtime.relation_types) == 1
        assert runtime.relation_types[0].id == "e1"


class TestRoundTripWithSurface:
    """测试 verify_roundtrip_with_surface 三层报告。"""

    def test_verify_roundtrip_supported_only(self):
        """仅 supported 元素通过验证。"""
        graph = VisualGraph(
            graph_id="g1",
            name="Test",
            nodes=[
                VisualNode(
                    node_id="n1",
                    type_id="event-tool",
                    label="Tool",
                ),
            ],
        )

        report = verify_roundtrip_with_surface(graph)
        assert report.is_equivalent is True
        assert len(report.unsupported_elements) == 0
        assert len(report.preview_elements) == 0

    def test_verify_roundtrip_with_preview(self):
        """包含 preview 元素，报告 preview_elements。"""
        graph = VisualGraph(
            graph_id="g1",
            name="Test",
            nodes=[
                VisualNode(
                    node_id="n1",
                    type_id="relation-agent-role",
                    label="Relation",
                ),
            ],
        )

        report = verify_roundtrip_with_surface(graph)
        # preview 类型不算 unsupported
        assert report.is_equivalent is True
        assert len(report.preview_elements) == 1
        assert "preview node type" in report.preview_elements[0]

    def test_verify_roundtrip_with_preview_edges(self):
        """包含 preview edges，报告 preview_elements。"""
        graph = VisualGraph(
            graph_id="g1",
            name="Test",
            nodes=[
                VisualNode(node_id="n1", type_id="entity-agent", label="A"),
                VisualNode(node_id="n2", type_id="entity-role", label="R"),
            ],
            edges=[
                VisualEdge(
                    edge_id="e1",
                    type_id="relates",
                    source_id="n1",
                    target_id="n2",
                ),
            ],
        )

        report = verify_roundtrip_with_surface(graph)
        assert len(report.preview_elements) == 1
        assert "preview edge type" in report.preview_elements[0]


class TestStudioManifestLoad:
    """测试 Studio Manifest 加载（N1.7）。"""

    def test_load_studio_manifest(self):
        """Studio manifest 可加载。"""
        result = load_studio_manifest()
        assert result.palette is not None
        assert result.preview_palette is not None
        assert result.semantic_surface is not None
        assert result.version == "1.1"

    def test_palette_contains_supported_categories(self):
        """Palette 包含 supported categories（含 entity）。"""
        result = load_studio_manifest()
        categories = result.palette.categories
        cat_ids = [c.id for c in categories]
        assert "event" in cat_ids
        assert "context" in cat_ids
        assert "fact" in cat_ids
        assert "entity" in cat_ids  # N1.7 新增

    def test_preview_palette_contains_preview_categories(self):
        """Preview Palette 包含 preview categories（N1.7）。"""
        result = load_studio_manifest()
        preview_categories = result.preview_palette.categories
        cat_ids = [c.id for c in preview_categories]
        assert "relation" in cat_ids
        assert "policy" in cat_ids

    def test_visual_edge_types_include_preview(self):
        """visual_edge_types 包含 preview 边（N1.7）。"""
        result = load_studio_manifest()
        preview_edge_ids = [e.id for e in result.preview_edge_types]
        assert "relates" in preview_edge_ids
        assert "triggers" in preview_edge_ids
        assert "requires" in preview_edge_ids


class TestEdgeCompilation:
    """测试 Edge 编译结果。"""

    def test_compile_edges_from_visual_graph_visual_only(self):
        """visual-only edges 不编译。"""
        graph = VisualGraph(
            graph_id="g1",
            name="Test",
            nodes=[
                VisualNode(node_id="n1", type_id="event-tool", label="E"),
                VisualNode(node_id="n2", type_id="fact-review", label="F"),
            ],
            edges=[
                VisualEdge(
                    edge_id="e1",
                    type_id="derives",
                    source_id="n1",
                    target_id="n2",
                ),
            ],
        )

        nodes_dict = {n.node_id: n for n in graph.nodes}
        result = compile_edges_from_visual_graph(graph.edges, nodes_dict)

        assert len(result.relation_types) == 0
        assert len(result.policy_bindings) == 0
        assert len(result.visual_only_edges) == 1
        assert "e1" in result.visual_only_edges

    def test_compile_edges_from_visual_graph_relates(self):
        """relates edges 编译为 RelationType。"""
        graph = VisualGraph(
            graph_id="g1",
            name="Test",
            nodes=[
                VisualNode(
                    node_id="n1",
                    type_id="entity-agent",
                    label="Agent",
                    properties={"entity_type": "agent"},
                ),
                VisualNode(
                    node_id="n2",
                    type_id="entity-role",
                    label="Role",
                    properties={"entity_type": "role"},
                ),
            ],
            edges=[
                VisualEdge(
                    edge_id="e1",
                    type_id="relates",
                    source_id="n1",
                    target_id="n2",
                    label="Agent-Role",
                ),
            ],
        )

        nodes_dict = {n.node_id: n for n in graph.nodes}
        result = compile_edges_from_visual_graph(graph.edges, nodes_dict)

        assert len(result.relation_types) == 1
        assert result.relation_types[0].id == "e1"
        assert len(result.compilation_warnings) >= 1  # preview edge warning


class TestSurfaceUpgradePath:
    """测试 Surface 升级路径（为什么 N1.7 合理）。"""

    def test_entity_is_now_supported(self):
        """entity 从 N1.6 的 reserved 升级为 N1.7 的 supported。"""
        # N1.7: entity 是 supported
        assert is_supported_node_type("entity-agent") is True
        assert is_preview_node_type("entity-agent") is False
        assert is_reserved_node_type("entity-agent") is False

    def test_relation_policy_are_preview(self):
        """relation/policy 是 preview（介于 supported 和 reserved 之间）。"""
        # N1.7: relation/policy 是 preview
        assert is_preview_node_type("relation-xyz") is True
        assert is_preview_node_type("policy-xyz") is True
        # 不是 supported，也不是 reserved
        assert is_supported_node_type("relation-xyz") is False
        assert is_reserved_node_type("relation-xyz") is False

    def test_all_edges_have_semantics(self):
        """所有边都有语义定义（不再有 reserved edges）。"""
        surface = get_semantic_surface()
        # N1.7: 没有 reserved edges
        assert len(surface.reserved_edge_types) == 0
        # derives 是 supported
        assert "derives" in surface.supported_edge_types
        # relates/triggers/requires/contains 是 preview
        assert len(surface.preview_edge_types) == 4
