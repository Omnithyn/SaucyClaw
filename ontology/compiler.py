"""Ontology Package Compiler — 正式编译器模块。

N1.8 — Ontology Package Compilation & Projection Pipeline

定义正式的 PackageCompiler 类：
- 单一入口：compile() 方法
- 编译前校验：validate_before_compile() 方法
- 编译报告：CompilationReport（信息丢失追踪）

Source of Truth：
- AuthoringPackage > RuntimePackage
- Supported 元素：完整编译
- Preview 元素：部分编译，记录信息丢失
- Visual-only 元素：跳过编译
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ontology.authoring_package import (
    AuthoringPackage,
    CompilationReport,
    RuntimePackage,
)
from ontology.edge_semantics import (
    EdgeCompilationResult,
    compile_edges_from_visual_graph,
)
from ontology.semantic_surface import (
    SemanticSurface,
    get_semantic_surface,
    get_node_surface_level,
    get_edge_surface_level,
    get_unsupported_fields_for_node_type,
    is_preview_node_type,
    is_reserved_node_type,
    is_visual_only_edge,
)
from ontology.roundtrip import (
    RoundTripUnsupportedError,
    visual_graph_to_schema,
)
from ontology.schema import OntologySchema
from ontology.visual_model import VisualGraph


# ─── Compilation Validation Error ───


class CompilationValidationError(Exception):
    """编译前校验失败。"""

    def __init__(
        self,
        package_id: str,
        issues: list[str],
    ) -> None:
        self.package_id = package_id
        self.issues = issues
        super().__init__(
            f"AuthoringPackage {package_id!r} 校验失败: {issues}"
        )


# ─── Validation Result ───


@dataclass(frozen=True)
class ValidationResult:
    """编译前校验结果。

    Attributes:
        is_valid: 是否可编译
        reserved_elements: Reserved 元素列表（阻止编译）
        unknown_elements: 未知元素列表（阻止编译）
        preview_elements: Preview 元素列表（允许编译，信息丢失）
        warnings: 校验警告
    """

    is_valid: bool
    reserved_elements: list[str] = field(default_factory=list)
    unknown_elements: list[str] = field(default_factory=list)
    preview_elements: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


# ─── Package Compiler ───


@dataclass(frozen=True)
class PackageCompiler:
    """Ontology Package 正式编译器。

    将 AuthoringPackage 编译为 RuntimePackage。

    编译规则：
    - Supported 节点：完整编译到 OntologySchema
    - Preview 节点：跳过，记录信息丢失
    - Reserved 节点：阻止编译（strict=True）或跳过（strict=False）
    - Supported 边：完整编译（当前无）
    - Preview 边：部分编译到 RelationType/PolicyBinding
    - Visual-only 边：跳过编译
    - Reserved 边：阻止编译（strict=True）或跳过（strict=False）

    Attributes:
        surface: 语义 Surface（默认 get_semantic_surface()）
        strict: 严格模式（遇到 Reserved 元素抛异常）
    """

    surface: SemanticSurface = field(default_factory=get_semantic_surface)
    strict: bool = True

    def validate_before_compile(
        self,
        authoring: AuthoringPackage,
    ) -> ValidationResult:
        """编译前校验 AuthoringPackage。

        检查：
        - Reserved 元素（阻止编译）
        - Unknown 元素（阻止编译）
        - Preview 元素（警告信息丢失）

        Args:
            authoring: 待编译的 AuthoringPackage

        Returns:
            ValidationResult
        """
        reserved: list[str] = []
        unknown: list[str] = []
        preview: list[str] = []
        warnings: list[str] = []

        if authoring.visual_graph is None:
            return ValidationResult(
                is_valid=True,
                warnings=["AuthoringPackage 不包含 VisualGraph"],
            )

        graph = authoring.visual_graph

        # 检查节点
        for node in graph.nodes:
            level = get_node_surface_level(node.type_id, self.surface)

            if level == "reserved":
                reserved.append(f"reserved node: {node.node_id} ({node.type_id})")
            elif level == "unknown":
                unknown.append(f"unknown node: {node.node_id} ({node.type_id})")
            elif level == "preview":
                preview.append(f"preview node: {node.node_id} ({node.type_id})")
                unsupported = get_unsupported_fields_for_node_type(
                    node.type_id, self.surface
                )
                if unsupported:
                    warnings.append(
                        f"节点 {node.node_id!r} ({node.type_id}) "
                        f"是 Preview 类型，以下字段不保证编译: {unsupported}"
                    )

        # 检查边
        for edge in graph.edges:
            level = get_edge_surface_level(edge.type_id, self.surface)

            if level == "reserved":
                reserved.append(f"reserved edge: {edge.edge_id} ({edge.type_id})")
            elif level == "unknown":
                unknown.append(f"unknown edge: {edge.edge_id} ({edge.type_id})")
            elif level == "preview":
                preview.append(f"preview edge: {edge.edge_id} ({edge.type_id})")
            elif is_visual_only_edge(edge.type_id, self.surface):
                warnings.append(
                    f"边 {edge.edge_id!r} ({edge.type_id}) "
                    f"是 Visual-only，不编译为 Runtime"
                )

        is_valid = len(reserved) == 0 and len(unknown) == 0

        return ValidationResult(
            is_valid=is_valid,
            reserved_elements=reserved,
            unknown_elements=unknown,
            preview_elements=preview,
            warnings=warnings,
        )

    def compile(
        self,
        authoring: AuthoringPackage,
    ) -> RuntimePackage:
        """将 AuthoringPackage 编译为 RuntimePackage。

        Args:
            authoring: 设计时包

        Returns:
            RuntimePackage: 运行时编译包

        Raises:
            CompilationValidationError: 当 strict=True 且存在 Reserved/Unknown 元素
        """
        # 1. 编译前校验
        validation = self.validate_before_compile(authoring)

        if self.strict and not validation.is_valid:
            issues = validation.reserved_elements + validation.unknown_elements
            raise CompilationValidationError(authoring.package_id, issues)

        # 2. 编译 VisualGraph
        if authoring.visual_graph is None:
            return self._compile_empty_package(authoring, validation)

        graph = authoring.visual_graph
        nodes_dict = {n.node_id: n for n in graph.nodes}

        # 3. 编译节点为 OntologySchema
        try:
            schema = visual_graph_to_schema(
                graph,
                strict=self.strict,
                surface=self.surface,
            )
        except RoundTripUnsupportedError as e:
            if self.strict:
                raise CompilationValidationError(
                    authoring.package_id,
                    [str(e)],
                )
            schema = OntologySchema()

        # 4. 编译边为 RelationType / PolicyBinding
        edge_result = compile_edges_from_visual_graph(
            graph.edges,
            nodes_dict,
            self.surface,
            strict=self.strict,
        )

        # 5. 生成编译报告
        report = self._build_compilation_report(
            graph,
            edge_result,
            validation,
        )

        return RuntimePackage(
            package_id=authoring.package_id,
            version=authoring.version,
            ontology_schema=schema,
            relation_types=edge_result.relation_types,
            policy_bindings=edge_result.policy_bindings,
            compilation_report=report,
            metadata=authoring.metadata,
        )

    def _compile_empty_package(
        self,
        authoring: AuthoringPackage,
        validation: ValidationResult,
    ) -> RuntimePackage:
        """编译空的 AuthoringPackage。"""
        return RuntimePackage(
            package_id=authoring.package_id,
            version=authoring.version,
            ontology_schema=OntologySchema(),
            relation_types=[],
            policy_bindings=[],
            compilation_report=CompilationReport(
                is_complete=True,
                supported_types=0,
                preview_types=0,
                visual_only_elements=0,
                information_loss_notes={},
                warnings=validation.warnings,
            ),
            metadata=authoring.metadata,
        )

    def _build_compilation_report(
        self,
        graph: VisualGraph,
        edge_result: EdgeCompilationResult,
        validation: ValidationResult,
    ) -> CompilationReport:
        """构建编译报告。"""
        supported_count = 0
        preview_count = 0
        info_loss: dict[str, str] = {}
        warnings: list[str] = []

        # 节点统计
        for node in graph.nodes:
            if is_preview_node_type(node.type_id, self.surface):
                preview_count += 1
                unsupported = get_unsupported_fields_for_node_type(
                    node.type_id, self.surface
                )
                if unsupported:
                    info_loss[node.node_id] = (
                        f"节点 {node.node_id!r} 是 Preview 类型"
                        f"，以下字段不保证编译: {unsupported}"
                    )
            elif not is_reserved_node_type(node.type_id, self.surface):
                supported_count += 1

        # 边信息丢失
        for edge_id, note in edge_result.partial_compilation_notes.items():
            info_loss[edge_id] = note

        # 警告合并
        warnings.extend(validation.warnings)
        warnings.extend(edge_result.compilation_warnings)

        return CompilationReport(
            is_complete=len(info_loss) == 0 and len(warnings) == 0,
            supported_types=supported_count,
            preview_types=preview_count,
            visual_only_elements=len(edge_result.visual_only_edges),
            information_loss_notes=info_loss,
            edge_compilation_result=edge_result,
            warnings=warnings,
        )


# ─── Convenience Function ───


def compile_package(
    authoring: AuthoringPackage,
    strict: bool = True,
    surface: SemanticSurface | None = None,
) -> RuntimePackage:
    """便捷编译函数。

    Args:
        authoring: 设计时包
        strict: 严格模式
        surface: 语义 Surface

    Returns:
        RuntimePackage
    """
    compiler = PackageCompiler(
        surface=surface or get_semantic_surface(),
        strict=strict,
    )
    return compiler.compile(authoring)


def validate_package(
    authoring: AuthoringPackage,
    surface: SemanticSurface | None = None,
) -> ValidationResult:
    """便捷校验函数。

    Args:
        authoring: 设计时包
        surface: 语义 Surface

    Returns:
        ValidationResult
    """
    compiler = PackageCompiler(
        surface=surface or get_semantic_surface(),
    )
    return compiler.validate_before_compile(authoring)
