"""Package-driven Governance Loop 单元测试。

N2.1 — RuntimePackage-Driven Governance Realignment

验证：
1. RuntimePackage 成为治理闭环正式输入
2. Schema-driven 事件映射
3. Schema-driven 事实建立
4. CompilationReport 影响运行时判定
5. 现有最小场景继续可跑
"""

import pytest

from ontology.authoring_package import (
    AuthoringPackage,
    RuntimePackage,
    CompilationReport,
)
from ontology.compiler import PackageCompiler
from ontology.governance_loop import (
    OntologyGovernanceResult,
    OntologyGovernanceError,
    run_package_driven_governance,
    run_ontology_governance_loop,
)
from ontology.mapping import (
    EventMappingResult,
    EventMappingError,
    map_raw_event_with_package,
)
from ontology.establishment import (
    FactEstablishmentResult,
    establish_fact_with_package,
)
from ontology.runtime_readiness import (
    ExecuteReadiness,
    check_runtime_readiness,
    adapt_readiness_to_judgment_mode,
)
from ontology.schema import (
    EventType,
    ContextType,
    FactType,
    OntologySchema,
    PolicyBinding,
)
from ontology.visual_model import (
    VisualGraph,
    VisualNode,
    VisualEdge,
)


class TestRuntimeReadiness:
    """Runtime Readiness 测试。"""

    def test_full_readiness_complete_report(self):
        """完整编译 → full readiness。"""
        report = CompilationReport(
            is_complete=True,
            supported_types=2,
            preview_types=0,
            visual_only_elements=0,
            information_loss_notes={},
            warnings=[],
        )
        runtime = RuntimePackage(
            package_id="test",
            ontology_schema=OntologySchema(),
            relation_types=[],
            policy_bindings=[],
            compilation_report=report,
        )

        readiness = check_runtime_readiness(runtime)

        assert readiness.level == "full"
        assert readiness.can_execute is True
        assert readiness.requires_review is False

    def test_warning_readiness_preview_types(self):
        """Preview 类型 → warning readiness。"""
        report = CompilationReport(
            is_complete=False,
            supported_types=1,
            preview_types=1,
            visual_only_elements=0,
            information_loss_notes={"n1": "Preview 类型，字段丢失"},
            warnings=["Preview 元素"],
        )
        runtime = RuntimePackage(
            package_id="test",
            ontology_schema=OntologySchema(),
            relation_types=[],
            policy_bindings=[],
            compilation_report=report,
        )

        readiness = check_runtime_readiness(runtime)

        assert readiness.level == "warning"
        assert readiness.can_execute is True
        assert len(readiness.preview_warnings) > 0

    def test_review_readiness_critical_loss(self):
        """关键字段丢失 → review readiness。"""
        report = CompilationReport(
            is_complete=False,
            supported_types=1,
            preview_types=1,
            visual_only_elements=0,
            information_loss_notes={
                "n1": "subject_type 字段丢失",
            },
            warnings=[],
        )
        runtime = RuntimePackage(
            package_id="test",
            ontology_schema=OntologySchema(),
            relation_types=[],
            policy_bindings=[],
            compilation_report=report,
        )

        readiness = check_runtime_readiness(runtime)

        assert readiness.level == "review"
        assert readiness.can_execute is True
        assert readiness.requires_review is True

    def test_judgment_mode_adaptation(self):
        """Readiness → Judgment mode 映射。"""
        # full → auto
        full_readiness = ExecuteReadiness(
            level="full",
            can_execute=True,
        )
        assert adapt_readiness_to_judgment_mode(full_readiness) == "auto"

        # warning → auto
        warning_readiness = ExecuteReadiness(
            level="warning",
            can_execute=True,
        )
        assert adapt_readiness_to_judgment_mode(warning_readiness) == "auto"

        # review → review
        review_readiness = ExecuteReadiness(
            level="review",
            can_execute=True,
            requires_review=True,
        )
        assert adapt_readiness_to_judgment_mode(review_readiness) == "review"

        # blocked → block
        blocked_readiness = ExecuteReadiness(
            level="blocked",
            can_execute=False,
        )
        assert adapt_readiness_to_judgment_mode(blocked_readiness) == "block"


class TestSchemaDrivenMapping:
    """Schema-driven 映射测试。"""

    def test_map_event_with_schema_event_types(self):
        """Schema 包含 event_types 时匹配。"""
        schema = OntologySchema(
            event_types=[
                EventType(
                    id="tool-invocation",
                    name="Tool Invocation",
                    description="工具调用事件",
                    subject_type="agent-role",
                ),
            ],
        )
        runtime = RuntimePackage(
            package_id="test",
            ontology_schema=schema,
            relation_types=[],
            policy_bindings=[],
        )

        raw_event = {
            "event": "tool-invocation",
            "payload": {
                "tool_name": "Write",
                "agent": "test-agent",
            },
        }

        result = map_raw_event_with_package(raw_event, runtime)

        assert result.event_instance.event_type == "tool-invocation"
        assert result.event_instance.subject_instance_id is not None
        assert len(result.entity_instances) == 1

    def test_map_event_fallback_to_default(self):
        """Schema 无匹配时 fallback。"""
        schema = OntologySchema(
            event_types=[],  # 空 schema
        )
        runtime = RuntimePackage(
            package_id="test",
            ontology_schema=schema,
            relation_types=[],
            policy_bindings=[],
        )

        raw_event = {
            "event": "pre_tool_use",
            "payload": {
                "tool_name": "Read",
            },
        }

        result = map_raw_event_with_package(raw_event, runtime)

        # Fallback 到 tool-invocation
        assert result.event_instance.event_type == "tool-invocation"

    def test_schema_driven_entity_type(self):
        """Schema-driven entity_type 推导。"""
        schema = OntologySchema(
            event_types=[
                EventType(
                    id="task-assignment",
                    name="Task Assignment",
                    description="任务分配",
                    subject_type="agent-role",
                ),
            ],
        )
        runtime = RuntimePackage(
            package_id="test",
            ontology_schema=schema,
            relation_types=[],
            policy_bindings=[],
        )

        raw_event = {
            "event": "task-assignment",
            "payload": {
                "assignee": "developer-1",
            },
        }

        result = map_raw_event_with_package(raw_event, runtime)

        # entity_type 应为 event_type.subject_type
        assert result.entity_instances[0].entity_type == "agent-role"


class TestSchemaDrivenEstablishment:
    """Schema-driven 事实建立测试。"""

    def test_establish_fact_with_condition(self):
        """Schema 包含 establishment_condition 时推导。"""
        schema = OntologySchema(
            event_types=[
                EventType(
                    id="tool-invocation",
                    name="Tool Invocation",
                    description="",
                    subject_type="agent-role",
                ),
            ],
            fact_types=[
                FactType(
                    id="review-requirement",
                    name="Review Requirement",
                    description="",
                    subject_type="agent-role",
                    establishment_condition="tool_name == 'Write'",
                ),
            ],
        )
        runtime = RuntimePackage(
            package_id="test",
            ontology_schema=schema,
            relation_types=[],
            policy_bindings=[],
        )

        # 创建事件实例
        from ontology.instances import build_event_instance, build_entity_instance

        event_instance = build_event_instance(
            event_type="tool-invocation",
            subject_instance_id="agent-1",
            event_data={"tool_name": "Write"},
        )

        entity_instances = [
            build_entity_instance(
                entity_type="agent-role",
                name="developer",
                properties={},
                source="runtime",
            ),
        ]

        result = establish_fact_with_package(event_instance, entity_instances, runtime)

        assert result is not None
        assert result.fact_record.fact_type == "review-requirement"

    def test_establish_fact_condition_not_matched(self):
        """条件不匹配时返回 None。"""
        schema = OntologySchema(
            event_types=[
                EventType(
                    id="tool-invocation",
                    name="Tool Invocation",
                    description="",
                    subject_type="agent-role",
                ),
            ],
            fact_types=[
                FactType(
                    id="review-requirement",
                    name="Review Requirement",
                    description="",
                    subject_type="agent-role",
                    establishment_condition="tool_name == 'Write'",
                ),
            ],
        )
        runtime = RuntimePackage(
            package_id="test",
            ontology_schema=schema,
            relation_types=[],
            policy_bindings=[],
        )

        from ontology.instances import build_event_instance, build_entity_instance

        # tool_name != "Write"
        event_instance = build_event_instance(
            event_type="tool-invocation",
            subject_instance_id="agent-1",
            event_data={"tool_name": "Read"},
        )

        entity_instances = [
            build_entity_instance(
                entity_type="agent-role",
                name="developer",
                properties={},
                source="runtime",
            ),
        ]

        result = establish_fact_with_package(event_instance, entity_instances, runtime)

        # 条件不匹配，返回 None
        assert result is None


class TestPackageDrivenGovernance:
    """Package-driven 治理闭环测试。"""

    def test_run_package_driven_governance_complete(self):
        """完整 Package-driven 闭环。"""
        # 创建 AuthoringPackage
        graph = VisualGraph(
            graph_id="test",
            name="Test",
            nodes=[
                VisualNode(
                    node_id="tool-invocation",
                    type_id="event-tool-invocation",
                    label="Tool Invocation",
                    properties={"subject_type": "agent-role"},
                ),
                VisualNode(
                    node_id="review-requirement",
                    type_id="fact-review-requirement",
                    label="Review Requirement",
                    properties={
                        "subject_type": "agent-role",
                        "establishment_condition": "tool_name == 'Write'",
                    },
                ),
            ],
        )

        authoring = AuthoringPackage(
            package_id="test-package",
            visual_graph=graph,
        )

        # 编译为 RuntimePackage
        compiler = PackageCompiler()
        runtime = compiler.compile(authoring)

        # 运行 Package-driven 治理
        raw_event = {
            "event": "tool-invocation",
            "payload": {
                "tool_name": "Write",
                "agent": "developer",
            },
        }

        result = run_package_driven_governance(raw_event, runtime)

        assert result.governance_status in ("mapped", "established", "judged")
        assert result.execute_readiness is not None
        assert result.execute_readiness.can_execute is True

    def test_readiness_affects_judgment(self):
        """Readiness 影响 judgment。"""
        # 创建带 Preview 的 RuntimePackage
        report = CompilationReport(
            is_complete=False,
            supported_types=1,
            preview_types=1,
            visual_only_elements=0,
            information_loss_notes={"n1": "subject_type 字段丢失"},
            warnings=["关键字段丢失"],
        )

        schema = OntologySchema(
            event_types=[
                EventType(
                    id="tool-invocation",
                    name="Tool Invocation",
                    description="",
                    subject_type="agent-role",
                ),
            ],
        )

        runtime = RuntimePackage(
            package_id="test",
            ontology_schema=schema,
            relation_types=[],
            policy_bindings=[],
            compilation_report=report,
        )

        raw_event = {
            "event": "tool-invocation",
            "payload": {"tool_name": "Write"},
        }

        result = run_package_driven_governance(raw_event, runtime)

        # review mode
        assert result.execute_readiness.level == "review"
        assert result.execute_readiness.requires_review is True

    def test_legacy_loop_still_works(self):
        """现有 legacy 入口仍可工作。"""
        schema = OntologySchema(
            event_types=[
                EventType(
                    id="tool-invocation",
                    name="Tool Invocation",
                    description="",
                    subject_type="agent-role",
                ),
            ],
            fact_types=[
                FactType(
                    id="review-requirement",
                    name="Review Requirement",
                    description="",
                    subject_type="agent-role",
                    establishment_condition=None,
                ),
            ],
        )

        raw_event = {
            "event": "pre_tool_use",
            "payload": {
                "tool_name": "Write",
                "agent": "test-agent",
            },
        }

        result = run_ontology_governance_loop(raw_event, schema, [])

        assert result.governance_status in ("mapped", "established")


class TestAuthoringToRuntimeToGovernance:
    """完整闭环：Authoring → Runtime → Governance。"""

    def test_full_pipeline(self):
        """AuthoringPackage → RuntimePackage → Governance Loop。"""
        # 1. 创建 AuthoringPackage
        graph = VisualGraph(
            graph_id="full-test",
            name="Full Test",
            nodes=[
                VisualNode(
                    node_id="tool-invocation",
                    type_id="event-tool-invocation",
                    label="Tool Invocation",
                    properties={
                        "subject_type": "agent-role",
                        "properties": ["tool_name", "tool_args"],
                    },
                ),
            ],
        )

        authoring = AuthoringPackage(
            package_id="full-pipeline-test",
            version="1.0",
            visual_graph=graph,
        )

        # 2. 编译为 RuntimePackage
        compiler = PackageCompiler()
        runtime = compiler.compile(authoring)

        # 3. 检查编译结果
        assert len(runtime.ontology_schema.event_types) == 1
        assert runtime.compilation_report.is_complete is True

        # 4. 运行治理闭环
        raw_event = {
            "event": "tool-invocation",
            "payload": {
                "tool_name": "Read",
                "agent": "developer",
            },
        }

        result = run_package_driven_governance(raw_event, runtime)

        # 5. 验证闭环成功
        assert result.mapping_result is not None
        assert result.execute_readiness.level == "full"

    def test_preview_pipeline_warning(self):
        """Preview 元素产生 warning。"""
        graph = VisualGraph(
            graph_id="preview-test",
            name="Preview Test",
            nodes=[
                VisualNode(
                    node_id="n1",
                    type_id="relation-agent-role",  # Preview 类型
                    label="Relation",
                ),
            ],
        )

        authoring = AuthoringPackage(
            package_id="preview-test",
            visual_graph=graph,
        )

        compiler = PackageCompiler()
        runtime = compiler.compile(authoring)

        # Preview 类型不阻止编译
        assert runtime.compilation_report.preview_types == 1
        assert not runtime.compilation_report.is_complete

        # 运行治理
        raw_event = {"event": "unknown", "payload": {}}
        result = run_package_driven_governance(raw_event, runtime)

        # Warning mode
        assert result.execute_readiness.can_execute is True