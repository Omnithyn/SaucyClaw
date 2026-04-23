"""Ontology Package Compilation 单元测试。

N1.8 — Ontology Package Compilation & Projection Pipeline

验证：
1. PackageCompiler 类功能
2. validate_before_compile() 校验
3. compile() 编译流程
4. Projector 类功能
5. project() 投影流程
6. Round-trip 保证（Supported 元素完整往返）
7. Preview 元素信息丢失追踪
"""

import pytest

from ontology.authoring_package import (
    AuthoringPackage,
    CompilationReport,
    RuntimePackage,
)
from ontology.compiler import (
    CompilationValidationError,
    PackageCompiler,
    ValidationResult,
    compile_package,
    validate_package,
)
from ontology.projection import (
    ProjectionReport,
    Projector,
    project_runtime_to_visual,
)
from ontology.semantic_surface import (
    SemanticSurface,
    get_semantic_surface,
)
from ontology.schema import (
    EventType,
    ContextType,
    FactType,
    OntologySchema,
)
from ontology.visual_model import (
    VisualEdge,
    VisualGraph,
    VisualNode,
)

from core.meta_model.models import RelationType


class TestPackageCompilerValidation:
    """PackageCompiler 校验测试。"""

    def test_validate_empty_package(self):
        """空包校验通过。"""
        authoring = AuthoringPackage(
            package_id="empty-package",
            visual_graph=None,
        )
        compiler = PackageCompiler()
        result = compiler.validate_before_compile(authoring)

        assert result.is_valid is True
        assert len(result.reserved_elements) == 0
        assert len(result.unknown_elements) == 0

    def test_validate_supported_nodes(self):
        """Supported 节点校验通过。"""
        graph = VisualGraph(
            graph_id="g1",
            name="Test",
            nodes=[
                VisualNode(
                    node_id="n1",
                    type_id="event-tool-invocation",
                    label="Event",
                ),
                VisualNode(
                    node_id="n2",
                    type_id="fact-review",
                    label="Fact",
                ),
            ],
        )
        authoring = AuthoringPackage(
            package_id="supported-package",
            visual_graph=graph,
        )
        compiler = PackageCompiler()
        result = compiler.validate_before_compile(authoring)

        assert result.is_valid is True
        assert len(result.reserved_elements) == 0
        assert len(result.preview_elements) == 0

    def test_validate_preview_nodes_warning(self):
        """Preview 节点发出警告。"""
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
        authoring = AuthoringPackage(
            package_id="preview-package",
            visual_graph=graph,
        )
        compiler = PackageCompiler()
        result = compiler.validate_before_compile(authoring)

        # Preview 不阻止编译
        assert result.is_valid is True
        assert len(result.preview_elements) > 0
        assert any("preview" in e for e in result.preview_elements)

    def test_validate_unknown_nodes_invalid(self):
        """Unknown 节点阻止编译。"""
        graph = VisualGraph(
            graph_id="g1",
            name="Test",
            nodes=[
                VisualNode(
                    node_id="n1",
                    type_id="unknown-type",
                    label="Unknown",
                ),
            ],
        )
        authoring = AuthoringPackage(
            package_id="unknown-package",
            visual_graph=graph,
        )
        compiler = PackageCompiler()
        result = compiler.validate_before_compile(authoring)

        assert result.is_valid is False
        assert len(result.unknown_elements) > 0
        assert any("unknown" in e for e in result.unknown_elements)

    def test_validate_visual_only_edges_warning(self):
        """Visual-only 边发出警告。"""
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
                    type_id="derives",  # Visual-only
                    source_id="n1",
                    target_id="n2",
                ),
            ],
        )
        authoring = AuthoringPackage(
            package_id="visual-only-package",
            visual_graph=graph,
        )
        compiler = PackageCompiler()
        result = compiler.validate_before_compile(authoring)

        assert result.is_valid is True
        assert any("Visual-only" in w for w in result.warnings)


class TestPackageCompilerCompile:
    """PackageCompiler 编译测试。"""

    def test_compile_empty_package(self):
        """空包编译返回空 Runtime。"""
        authoring = AuthoringPackage(
            package_id="empty-package",
            visual_graph=None,
        )
        compiler = PackageCompiler()
        runtime = compiler.compile(authoring)

        assert runtime.package_id == "empty-package"
        assert len(runtime.ontology_schema.event_types) == 0
        assert len(runtime.relation_types) == 0
        assert runtime.compilation_report.is_complete is True

    def test_compile_supported_nodes_complete(self):
        """Supported 节点完整编译。"""
        graph = VisualGraph(
            graph_id="g1",
            name="Test",
            nodes=[
                VisualNode(
                    node_id="tool-invocation",
                    type_id="event-tool-invocation",
                    label="Tool Invocation",
                    properties={
                        "subject_type": "agent-role",
                    },
                ),
                VisualNode(
                    node_id="review-requirement",
                    type_id="fact-review-requirement",
                    label="Review Requirement",
                    properties={
                        "subject_type": "agent-role",
                        "establishment_condition": "tool_name == Write",
                    },
                ),
            ],
        )
        authoring = AuthoringPackage(
            package_id="supported-package",
            visual_graph=graph,
        )
        compiler = PackageCompiler()
        runtime = compiler.compile(authoring)

        assert runtime.package_id == "supported-package"
        assert len(runtime.ontology_schema.event_types) == 1
        assert len(runtime.ontology_schema.fact_types) == 1
        assert runtime.compilation_report.is_complete is True
        assert runtime.compilation_report.supported_types == 2
        assert runtime.compilation_report.preview_types == 0

    def test_compile_preview_nodes_partial(self):
        """Preview 节点部分编译（跳过）。"""
        graph = VisualGraph(
            graph_id="g1",
            name="Test",
            nodes=[
                VisualNode(
                    node_id="n1",
                    type_id="relation-agent-role",  # Preview
                    label="Relation",
                ),
            ],
        )
        authoring = AuthoringPackage(
            package_id="preview-package",
            visual_graph=graph,
        )
        compiler = PackageCompiler(strict=False)
        runtime = compiler.compile(authoring)

        # Preview 节点不编译到 Schema
        assert len(runtime.ontology_schema.event_types) == 0
        assert runtime.compilation_report.preview_types == 1
        assert not runtime.compilation_report.is_complete

    def test_compile_unknown_nodes_raises_strict(self):
        """Unknown 节点在 strict 模式抛异常。"""
        graph = VisualGraph(
            graph_id="g1",
            name="Test",
            nodes=[
                VisualNode(
                    node_id="n1",
                    type_id="unknown-type",
                    label="Unknown",
                ),
            ],
        )
        authoring = AuthoringPackage(
            package_id="unknown-package",
            visual_graph=graph,
        )
        compiler = PackageCompiler(strict=True)

        with pytest.raises(CompilationValidationError) as exc_info:
            compiler.compile(authoring)

        assert "unknown-package" in str(exc_info.value)

    def test_compile_preview_edges_to_relation_types(self):
        """Preview 边编译为 RelationType。"""
        graph = VisualGraph(
            graph_id="g1",
            name="Test",
            nodes=[
                VisualNode(
                    node_id="agent",
                    type_id="entity-agent",
                    label="Agent",
                    properties={"entity_type": "Agent"},
                ),
                VisualNode(
                    node_id="role",
                    type_id="entity-role",
                    label="Role",
                    properties={"entity_type": "Role"},
                ),
            ],
            edges=[
                VisualEdge(
                    edge_id="e1",
                    type_id="relates",  # Preview 边
                    source_id="agent",
                    target_id="role",
                    label="Agent-Role",
                    properties={"cardinality": "one-to-many"},
                ),
            ],
        )
        authoring = AuthoringPackage(
            package_id="edge-package",
            visual_graph=graph,
        )
        compiler = PackageCompiler()
        runtime = compiler.compile(authoring)

        # Preview 边编译为 RelationType
        assert len(runtime.relation_types) == 1
        assert runtime.relation_types[0].id == "e1"
        assert runtime.relation_types[0].source == "Agent"
        assert runtime.relation_types[0].target == "Role"

    def test_compile_visual_only_edges_skipped(self):
        """Visual-only 边跳过编译。"""
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
                    type_id="derives",  # Visual-only
                    source_id="n1",
                    target_id="n2",
                ),
            ],
        )
        authoring = AuthoringPackage(
            package_id="visual-only-package",
            visual_graph=graph,
        )
        compiler = PackageCompiler()
        runtime = compiler.compile(authoring)

        # Visual-only 边不编译
        assert len(runtime.relation_types) == 0
        assert runtime.compilation_report.visual_only_elements == 1

    def test_compile_package_convenience_function(self):
        """便捷编译函数。"""
        authoring = AuthoringPackage(
            package_id="test-package",
            visual_graph=None,
        )
        runtime = compile_package(authoring)

        assert runtime.package_id == "test-package"


class TestProjector:
    """Projector 投影测试。"""

    def test_project_empty_runtime(self):
        """空 Runtime 投影返回空 VisualGraph。"""
        runtime = RuntimePackage(
            package_id="empty-runtime",
            ontology_schema=OntologySchema(),
            relation_types=[],
            policy_bindings=[],
        )
        projector = Projector()
        graph, report = projector.project(runtime)

        assert graph.graph_id == "empty-runtime-projection"
        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0
        assert report.is_complete is True

    def test_project_schema_to_visual_nodes(self):
        """OntologySchema 投影为 VisualNodes。"""
        schema = OntologySchema(
            event_types=[
                EventType(
                    id="tool-invocation",
                    name="Tool Invocation",
                    description="工具调用事件",
                    subject_type="agent-role",
                ),
            ],
            context_types=[
                ContextType(
                    id="session",
                    name="Session Context",
                    description="会话上下文",
                    lifecycle="ephemeral",
                ),
            ],
            fact_types=[
                FactType(
                    id="review-requirement",
                    name="Review Requirement",
                    description="审查要求",
                    subject_type="agent-role",
                ),
            ],
        )
        runtime = RuntimePackage(
            package_id="schema-runtime",
            ontology_schema=schema,
            relation_types=[],
            policy_bindings=[],
        )
        projector = Projector()
        graph, report = projector.project(runtime)

        assert report.projected_nodes == 3
        assert len(graph.nodes) == 3

        # 检查节点类型
        event_node = [n for n in graph.nodes if n.type_id.startswith("event")]
        assert len(event_node) == 1

        context_node = [n for n in graph.nodes if n.type_id.startswith("context")]
        assert len(context_node) == 1

        fact_node = [n for n in graph.nodes if n.type_id.startswith("fact")]
        assert len(fact_node) == 1

    def test_project_relation_types_to_visual_edges(self):
        """RelationTypes 投影为 VisualEdges (relates)。"""
        schema = OntologySchema()
        runtime = RuntimePackage(
            package_id="relation-runtime",
            ontology_schema=schema,
            relation_types=[
                RelationType(
                    id="agent-role-rel",
                    name="Agent-Role Relation",
                    source="Agent",
                    target="Role",
                    cardinality="one-to-many",
                ),
            ],
            policy_bindings=[],
        )
        projector = Projector()
        graph, report = projector.project(runtime)

        assert len(graph.edges) == 1
        assert graph.edges[0].type_id == "relates"  # Preview 边
        assert graph.edges[0].source_id == "Agent"
        assert graph.edges[0].target_id == "Role"

    def test_project_preview_elements_lossy(self):
        """Preview 元素投影有信息丢失警告。"""
        schema = OntologySchema()
        compilation_report = CompilationReport(
            is_complete=False,
            supported_types=0,
            preview_types=1,
            visual_only_elements=0,
            information_loss_notes={"n1": "Preview 类型，字段丢失"},
            warnings=["Preview 元素不可逆"],
        )
        runtime = RuntimePackage(
            package_id="preview-runtime",
            ontology_schema=schema,
            relation_types=[],
            policy_bindings=[],
            compilation_report=compilation_report,
        )
        projector = Projector()
        graph, report = projector.project(runtime)

        assert not report.is_complete
        assert len(report.warnings) > 0
        assert any("Preview" in w for w in report.warnings)

    def test_project_runtime_to_visual_convenience_function(self):
        """便捷投影函数。"""
        runtime = RuntimePackage(
            package_id="test-runtime",
            ontology_schema=OntologySchema(),
            relation_types=[],
            policy_bindings=[],
        )
        graph, report = project_runtime_to_visual(runtime)

        assert graph.graph_id == "test-runtime-projection"


class TestRoundTripProjection:
    """Round-trip 投影测试。"""

    def test_supported_elements_roundtrip_complete(self):
        """Supported 元素完整往返。"""
        # 1. 创建 AuthoringPackage
        original_graph = VisualGraph(
            graph_id="original",
            name="Original",
            nodes=[
                VisualNode(
                    node_id="tool-invocation",
                    type_id="event-tool-invocation",
                    label="Tool Invocation",
                    properties={
                        "subject_type": "agent-role",
                        "timestamp_field": "timestamp",
                    },
                ),
            ],
        )
        authoring = AuthoringPackage(
            package_id="roundtrip-test",
            visual_graph=original_graph,
        )

        # 2. 编译为 RuntimePackage
        compiler = PackageCompiler()
        runtime = compiler.compile(authoring)

        # 3. 投影回 VisualGraph
        projector = Projector()
        projected_graph, report = projector.project(runtime)

        # 4. 验证往返完整性
        assert runtime.compilation_report.is_complete is True
        assert report.is_complete is True

        # 5. 验证节点存在
        assert len(projected_graph.nodes) == 1
        assert projected_graph.nodes[0].node_id == "tool-invocation"
        assert projected_graph.nodes[0].label == "Tool Invocation"

    def test_preview_elements_roundtrip_lossy(self):
        """Preview 元素往返有信息丢失。"""
        # 1. 创建包含 Preview 元素的 AuthoringPackage
        original_graph = VisualGraph(
            graph_id="original",
            name="Original",
            nodes=[
                VisualNode(
                    node_id="n1",
                    type_id="relation-agent-role",  # Preview
                    label="Relation",
                    properties={
                        "cardinality": "one-to-many",  # 不保证编译
                        "constraints": "required",  # 不保证编译
                    },
                ),
            ],
        )
        authoring = AuthoringPackage(
            package_id="preview-roundtrip-test",
            visual_graph=original_graph,
        )

        # 2. 编译为 RuntimePackage（Preview 节点跳过）
        compiler = PackageCompiler()
        runtime = compiler.compile(authoring)

        # 3. Preview 节点不编译到 Schema
        assert len(runtime.ontology_schema.event_types) == 0
        assert runtime.compilation_report.preview_types == 1

        # 4. 投影回 VisualGraph（空，因为 Preview 不编译）
        projector = Projector()
        projected_graph, report = projector.project(runtime)

        # 5. 信息丢失不可逆
        assert len(projected_graph.nodes) == 0
        assert not report.is_complete