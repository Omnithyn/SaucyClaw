"""Ontology Studio Loader — 设计时入口加载器。

N1.6 — Ontology Studio Contract Closure
N1.7 — Ontology Studio Semantic Surface Expansion

从 schemas/ontology/studio_manifest.yaml 加载 Studio 设计时配置：
- supported_categories → Palette / VisualNodeType
- preview_categories → Preview VisualNodeType（部分编译）
- supported_edge_types → VisualEdgeType
- preview_edge_types → Preview VisualEdgeType（有编译目标）

提供 get_semantic_surface() 函数，声明当前三层语义 Surface：
- Supported：正式支持，完整 round-trip 保证
- Preview：预览支持，部分语义可用
- Reserved：预留不支持

Source of Truth 优先级：
- AuthoringPackage > RuntimePackage > Studio Manifest
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from ontology.semantic_surface import (
    SemanticSurface,
    DEFAULT_SEMANTIC_SURFACE,
    get_semantic_surface,
    is_supported_node_type as _is_supported_node_type,
    is_preview_node_type as _is_preview_node_type,
    is_reserved_node_type as _is_reserved_node_type,
    is_supported_edge_type as _is_supported_edge_type,
    is_preview_edge_type as _is_preview_edge_type,
    is_reserved_edge_type as _is_reserved_edge_type,
)
from ontology.visual_model import (
    Category,
    Palette,
    VisualEdgeType,
    VisualNodeType,
)


# ─── Legacy SupportedSurface (N1.6 compatibility) ───
# 保留 N1.6 的 SupportedSurface 以兼容旧代码


@dataclass(frozen=True)
class SupportedSurface:
    """N1.6 SupportedSurface（兼容层）。

    N1.7 使用 SemanticSurface 替代，但保留此类型以兼容旧代码。
    """

    supported_node_prefixes: list[str] = field(default_factory=list)
    reserved_node_prefixes: list[str] = field(default_factory=list)
    supported_edge_types: list[str] = field(default_factory=list)
    reserved_edge_types: list[str] = field(default_factory=list)
    supported_node_fields: list[str] = field(default_factory=list)
    ignored_visual_fields: list[str] = field(default_factory=list)


DEFAULT_SUPPORTED_SURFACE = SupportedSurface(
    supported_node_prefixes=["event", "context", "fact", "entity"],
    reserved_node_prefixes=[],  # N1.7: relation/policy 升级为 preview
    supported_edge_types=["derives"],
    reserved_edge_types=[],  # N1.7: relates/triggers/requires 升级为 preview
    supported_node_fields=[
        "node_id",
        "label",
        "properties.subject_type",
        "properties.object_type",
        "properties.properties",
        "properties.establishment_condition",
        "properties.lifecycle",
    ],
    ignored_visual_fields=[
        "visual_hint",
        "color",
        "position",
        "min_instances",
        "max_instances",
        "metadata",
    ],
)


def get_supported_surface() -> SupportedSurface:
    """获取 N1.6 兼容的 SupportedSurface。

    N1.7 推荐：使用 get_semantic_surface() 替代。

    Returns:
        SupportedSurface: 包含 supported/reserved 前缀和字段清单
    """
    return DEFAULT_SUPPORTED_SURFACE


# ─── Studio Load Error ───


class StudioLoadError(Exception):
    """Studio Manifest 加载失败。"""


# ─── Studio Manifest Result ───


@dataclass(frozen=True)
class StudioManifestResult:
    """Studio Manifest 加载结果。

    Attributes:
        palette: 设计时 Palette（仅包含 supported categories）
        preview_palette: Preview Palette（包含 preview categories）
        visual_node_types: 支持的 VisualNodeType 列表
        preview_node_types: Preview VisualNodeType 列表
        visual_edge_types: 支持的 VisualEdgeType 列表
        preview_edge_types: Preview VisualEdgeType 列表
        semantic_surface: 语义 Surface（三层结构）
        version: Manifest 版本
    """

    palette: Palette
    preview_palette: Palette | None = None
    visual_node_types: list[VisualNodeType] = field(default_factory=list)
    preview_node_types: list[VisualNodeType] = field(default_factory=list)
    visual_edge_types: list[VisualEdgeType] = field(default_factory=list)
    preview_edge_types: list[VisualEdgeType] = field(default_factory=list)
    semantic_surface: SemanticSurface = field(
        default_factory=get_semantic_surface
    )
    version: str = "1.0"


# ─── Manifest Loader ───


SCHEMA_DIR = Path(__file__).parent.parent / "schemas" / "ontology"


def load_studio_manifest(
    manifest_path: str | Path | None = None,
) -> StudioManifestResult:
    """加载 Studio Manifest。

    Args:
        manifest_path: Manifest 文件路径（默认 schemas/ontology/studio_manifest.yaml）

    Returns:
        StudioManifestResult: 包含 Palette / PreviewPalette / VisualNodeTypes / VisualEdgeTypes

    Raises:
        StudioLoadError: 文件不存在或格式错误
    """
    path = (
        Path(manifest_path)
        if manifest_path
        else SCHEMA_DIR / "studio_manifest.yaml"
    )

    if not path.exists():
        raise StudioLoadError(f"Studio Manifest 不存在: {path}")

    with open(path) as f:
        data = yaml.safe_load(f) or {}

    studio_data = data.get("studio", {})

    # 构建 Supported Palette
    supported_categories: list[Category] = []
    supported_visual_node_types: list[VisualNodeType] = []

    for cat_data in studio_data.get("supported_categories", []):
        cat = Category(
            id=cat_data["id"],
            name=cat_data.get("name", cat_data["id"]),
            description=cat_data.get("description", ""),
            color=cat_data.get("color", "#808080"),
            node_types=cat_data.get("node_types", []),
        )
        supported_categories.append(cat)

        visual_hint = cat_data.get("visual_hint", cat.id)
        color = cat_data.get("color", "#808080")
        for nt_id in cat_data.get("node_types", []):
            supported_visual_node_types.append(
                VisualNodeType(
                    id=nt_id,
                    name=_format_node_type_name(nt_id, cat.id),
                    category=cat.id,
                    description=f"{cat.description} 类型",
                    visual_hint=visual_hint,
                    color=color,
                )
            )

    supported_palette = Palette(categories=supported_categories)

    # 构建 Preview Palette (N1.7)
    preview_categories: list[Category] = []
    preview_visual_node_types: list[VisualNodeType] = []

    for cat_data in studio_data.get("preview_categories", []):
        cat = Category(
            id=cat_data["id"],
            name=cat_data.get("name", cat_data["id"]),
            description=cat_data.get("description", ""),
            color=cat_data.get("color", "#808080"),
            node_types=cat_data.get("node_types", []),
        )
        preview_categories.append(cat)

        visual_hint = cat_data.get("visual_hint", cat.id)
        color = cat_data.get("color", "#808080")
        for nt_id in cat_data.get("node_types", []):
            preview_visual_node_types.append(
                VisualNodeType(
                    id=nt_id,
                    name=_format_node_type_name(nt_id, cat.id),
                    category=cat.id,
                    description=f"{cat.description} 类型（Preview）",
                    visual_hint=visual_hint,
                    color=color,
                )
            )

    preview_palette = Palette(categories=preview_categories)

    # 构建 Supported VisualEdgeTypes
    supported_visual_edge_types: list[VisualEdgeType] = []
    for edge_data in studio_data.get("supported_edge_types", []):
        supported_visual_edge_types.append(
            VisualEdgeType(
                id=edge_data["id"],
                name=edge_data.get("name", edge_data["id"]),
                source_type=edge_data.get("source_category"),
                target_type=edge_data.get("target_category"),
                label=edge_data.get("name", edge_data["id"]),
                directed=edge_data.get("directed", True),
            )
        )

    # 构建 Preview VisualEdgeTypes (N1.7)
    preview_visual_edge_types: list[VisualEdgeType] = []
    for edge_data in studio_data.get("preview_edge_types", []):
        preview_visual_edge_types.append(
            VisualEdgeType(
                id=edge_data["id"],
                name=edge_data.get("name", edge_data["id"]),
                source_type=edge_data.get("source_category"),
                target_type=edge_data.get("target_category"),
                label=edge_data.get("name", edge_data["id"]),
                directed=edge_data.get("directed", True),
            )
        )

    # 构建 SemanticSurface（从 manifest 或默认）
    surface_data = studio_data.get("semantic_surface", {})
    semantic_surface = SemanticSurface(
        supported_node_prefixes=surface_data.get(
            "supported_node_prefixes",
            DEFAULT_SEMANTIC_SURFACE.supported_node_prefixes,
        ),
        preview_node_prefixes=surface_data.get(
            "preview_node_prefixes",
            DEFAULT_SEMANTIC_SURFACE.preview_node_prefixes,
        ),
        reserved_node_prefixes=surface_data.get(
            "reserved_node_prefixes",
            DEFAULT_SEMANTIC_SURFACE.reserved_node_prefixes,
        ),
        supported_edge_types=surface_data.get(
            "supported_edge_types",
            DEFAULT_SEMANTIC_SURFACE.supported_edge_types,
        ),
        preview_edge_types=surface_data.get(
            "preview_edge_types",
            DEFAULT_SEMANTIC_SURFACE.preview_edge_types,
        ),
        reserved_edge_types=surface_data.get(
            "reserved_edge_types",
            DEFAULT_SEMANTIC_SURFACE.reserved_edge_types,
        ),
        supported_compilation_fields=(
            DEFAULT_SEMANTIC_SURFACE.supported_compilation_fields
        ),
        preview_partial_fields=(
            DEFAULT_SEMANTIC_SURFACE.preview_partial_fields
        ),
        edge_compilation_targets=(
            DEFAULT_SEMANTIC_SURFACE.edge_compilation_targets
        ),
        visual_only_edges=surface_data.get(
            "visual_only_edges",
            DEFAULT_SEMANTIC_SURFACE.visual_only_edges,
        ),
    )

    return StudioManifestResult(
        palette=supported_palette,
        preview_palette=preview_palette,
        visual_node_types=supported_visual_node_types,
        preview_node_types=preview_visual_node_types,
        visual_edge_types=supported_visual_edge_types,
        preview_edge_types=preview_visual_edge_types,
        semantic_surface=semantic_surface,
        version=studio_data.get("version", "1.0"),
    )


# ─── Surface Detection Functions ───
# 这些函数现在从 semantic_surface 模块导入，这里提供别名以兼容旧代码


def is_supported_node_type(
    type_id: str,
    surface: SupportedSurface | SemanticSurface | None = None,
) -> bool:
    """判断节点类型是否正式支持。

    Args:
        type_id: VisualNodeType.id
        surface: Surface（默认 get_semantic_surface()）

    Returns:
        True 如果是正式支持的类型前缀
    """
    if isinstance(surface, SupportedSurface):
        s = surface
        for prefix in s.supported_node_prefixes:
            if type_id.startswith(prefix):
                return True
        return False
    return _is_supported_node_type(type_id, surface)


def is_preview_node_type(
    type_id: str,
    surface: SemanticSurface | None = None,
) -> bool:
    """判断节点类型是否预览支持（N1.7 新增）。

    Args:
        type_id: VisualNodeType.id
        surface: SemanticSurface（默认 get_semantic_surface()）

    Returns:
        True 如果是预览支持的类型前缀
    """
    return _is_preview_node_type(type_id, surface)


def is_reserved_node_type(
    type_id: str,
    surface: SupportedSurface | SemanticSurface | None = None,
) -> bool:
    """判断节点类型是否预留（不支持）。

    Args:
        type_id: VisualNodeType.id
        surface: Surface（默认 get_semantic_surface()）

    Returns:
        True 如果是预留的类型前缀
    """
    if isinstance(surface, SupportedSurface):
        s = surface
        for prefix in s.reserved_node_prefixes:
            if type_id.startswith(prefix):
                return True
        return False
    return _is_reserved_node_type(type_id, surface)


def is_supported_edge_type(
    type_id: str,
    surface: SupportedSurface | SemanticSurface | None = None,
) -> bool:
    """判断边类型是否正式支持。

    Args:
        type_id: VisualEdgeType.id
        surface: Surface（默认 get_semantic_surface()）

    Returns:
        True 如果是正式支持的边类型
    """
    if isinstance(surface, SupportedSurface):
        s = surface
        return type_id in s.supported_edge_types
    return _is_supported_edge_type(type_id, surface)


def is_preview_edge_type(
    type_id: str,
    surface: SemanticSurface | None = None,
) -> bool:
    """判断边类型是否预览支持（N1.7 新增）。

    Args:
        type_id: VisualEdgeType.id
        surface: SemanticSurface（默认 get_semantic_surface()）

    Returns:
        True 如果是预览支持的边类型
    """
    return _is_preview_edge_type(type_id, surface)


def is_reserved_edge_type(
    type_id: str,
    surface: SupportedSurface | SemanticSurface | None = None,
) -> bool:
    """判断边类型是否预留（不支持）。

    Args:
        type_id: VisualEdgeType.id
        surface: Surface（默认 get_semantic_surface()）

    Returns:
        True 如果是预留的边类型
    """
    if isinstance(surface, SupportedSurface):
        s = surface
        return type_id in s.reserved_edge_types
    return _is_reserved_edge_type(type_id, surface)


# ─── Internal Helpers ───


def _format_node_type_name(nt_id: str, category_id: str) -> str:
    """格式化节点类型名称。

    Args:
        nt_id: 原始 node_type ID
        category_id: 所属 category ID

    Returns:
        格式化后的显示名称
    """
    base = nt_id.replace(f"{category_id}-", "")
    return base.replace("-", " ").title()
