"""Ontology Studio Loader — 设计时入口加载器。

N1.6 — Ontology Studio Contract Closure

从 schemas/ontology/studio_manifest.yaml 加载 Studio 设计时配置：
- supported_categories → Palette / VisualNodeType
- supported_edge_types → VisualEdgeType
- reserved_categories / reserved_edge_types → 预留（不加载到 Palette）

提供 get_supported_surface() 函数，声明当前承诺的 node/edge 类型清单。

Source of Truth 优先级：
- Runtime Schema > Studio Manifest
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from ontology.visual_model import (
    Category,
    Palette,
    VisualEdgeType,
    VisualNodeType,
)


# ─── Supported Surface ───


@dataclass(frozen=True)
class SupportedSurface:
    """当前正式支持的能力声明。

    Attributes:
        supported_node_prefixes: 正式支持的节点类型前缀
        reserved_node_prefixes: 预留的节点类型前缀（不支持）
        supported_edge_types: 正式支持的边类型 ID
        reserved_edge_types: 预留的边类型 ID（不支持）
        supported_node_fields: round-trip 保证覆盖的字段
        ignored_visual_fields: visual-only 字段（不进入 runtime）
    """

    supported_node_prefixes: list[str] = field(default_factory=list)
    reserved_node_prefixes: list[str] = field(default_factory=list)
    supported_edge_types: list[str] = field(default_factory=list)
    reserved_edge_types: list[str] = field(default_factory=list)
    supported_node_fields: list[str] = field(default_factory=list)
    ignored_visual_fields: list[str] = field(default_factory=list)


# ─── Studio Load Error ───


class StudioLoadError(Exception):
    """Studio Manifest 加载失败。"""


# ─── Studio Manifest Result ───


@dataclass(frozen=True)
class StudioManifestResult:
    """Studio Manifest 加载结果。

    Attributes:
        palette: 设计时 Palette（仅包含 supported categories）
        visual_node_types: 支持的 VisualNodeType 列表
        visual_edge_types: 支持的 VisualEdgeType 列表
        supported_surface: 正式支持的能力声明
        version: Manifest 版本
    """

    palette: Palette
    visual_node_types: list[VisualNodeType] = field(default_factory=list)
    visual_edge_types: list[VisualEdgeType] = field(default_factory=list)
    supported_surface: SupportedSurface = field(
        default_factory=SupportedSurface
    )
    version: str = "1.0"


# ─── Default Supported Surface ───
# 当前承诺（N1.6）

DEFAULT_SUPPORTED_SURFACE = SupportedSurface(
    supported_node_prefixes=["event", "context", "fact"],
    reserved_node_prefixes=["entity", "relation", "policy"],
    supported_edge_types=["derives"],
    reserved_edge_types=["relates", "triggers", "requires"],
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
    """获取当前正式支持的能力声明。

    Returns:
        SupportedSurface: 包含 supported/reserved 前缀和字段清单
    """
    return DEFAULT_SUPPORTED_SURFACE


# ─── Manifest Loader ───


SCHEMA_DIR = Path(__file__).parent.parent / "schemas" / "ontology"


def load_studio_manifest(
    manifest_path: str | Path | None = None,
) -> StudioManifestResult:
    """加载 Studio Manifest。

    Args:
        manifest_path: Manifest 文件路径（默认 schemas/ontology/studio_manifest.yaml）

    Returns:
        StudioManifestResult: 包含 Palette / VisualNodeTypes / VisualEdgeTypes

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

    # 构建 Palette（仅 supported categories）
    categories: list[Category] = []
    visual_node_types: list[VisualNodeType] = []

    for cat_data in studio_data.get("supported_categories", []):
        cat = Category(
            id=cat_data["id"],
            name=cat_data.get("name", cat_data["id"]),
            description=cat_data.get("description", ""),
            color=cat_data.get("color", "#808080"),
            node_types=cat_data.get("node_types", []),
        )
        categories.append(cat)

        # 为每个 node_type 构建 VisualNodeType
        visual_hint = cat_data.get("visual_hint", cat.id)
        color = cat_data.get("color", "#808080")
        for nt_id in cat_data.get("node_types", []):
            visual_node_types.append(
                VisualNodeType(
                    id=nt_id,
                    name=_format_node_type_name(nt_id, cat.id),
                    category=cat.id,
                    description=f"{cat.description} 类型",
                    visual_hint=visual_hint,
                    color=color,
                )
            )

    palette = Palette(categories=categories)

    # 构建 VisualEdgeTypes（仅 supported）
    visual_edge_types: list[VisualEdgeType] = []
    for edge_data in studio_data.get("supported_edge_types", []):
        visual_edge_types.append(
            VisualEdgeType(
                id=edge_data["id"],
                name=edge_data.get("name", edge_data["id"]),
                source_type=edge_data.get("source_category"),
                target_type=edge_data.get("target_category"),
                label=edge_data.get("name", edge_data["id"]),
                directed=edge_data.get("directed", True),
            )
        )

    # 构建 SupportedSurface（从 manifest 或默认）
    surface_data = studio_data.get("roundtrip_surface", {})
    supported_surface = SupportedSurface(
        supported_node_prefixes=(
            DEFAULT_SUPPORTED_SURFACE.supported_node_prefixes
        ),
        reserved_node_prefixes=(
            DEFAULT_SUPPORTED_SURFACE.reserved_node_prefixes
        ),
        supported_edge_types=(
            DEFAULT_SUPPORTED_SURFACE.supported_edge_types
        ),
        reserved_edge_types=(
            DEFAULT_SUPPORTED_SURFACE.reserved_edge_types
        ),
        supported_node_fields=surface_data.get(
            "supported_node_fields",
            DEFAULT_SUPPORTED_SURFACE.supported_node_fields,
        ),
        ignored_visual_fields=surface_data.get(
            "ignored_visual_fields",
            DEFAULT_SUPPORTED_SURFACE.ignored_visual_fields,
        ),
    )

    return StudioManifestResult(
        palette=palette,
        visual_node_types=visual_node_types,
        visual_edge_types=visual_edge_types,
        supported_surface=supported_surface,
        version=studio_data.get("version", "1.0"),
    )


def is_supported_node_type(
    type_id: str,
    surface: SupportedSurface | None = None,
) -> bool:
    """判断节点类型是否正式支持。

    Args:
        type_id: VisualNodeType.id
        surface: SupportedSurface（默认 get_supported_surface()）

    Returns:
        True 如果是正式支持的类型前缀
    """
    s = surface or get_supported_surface()
    for prefix in s.supported_node_prefixes:
        if type_id.startswith(prefix):
            return True
    return False


def is_reserved_node_type(
    type_id: str,
    surface: SupportedSurface | None = None,
) -> bool:
    """判断节点类型是否预留（不支持）。

    Args:
        type_id: VisualNodeType.id
        surface: SupportedSurface（默认 get_supported_surface()）

    Returns:
        True 如果是预留的类型前缀
    """
    s = surface or get_supported_surface()
    for prefix in s.reserved_node_prefixes:
        if type_id.startswith(prefix):
            return True
    return False


def is_supported_edge_type(
    type_id: str,
    surface: SupportedSurface | None = None,
) -> bool:
    """判断边类型是否正式支持。

    Args:
        type_id: VisualEdgeType.id
        surface: SupportedSurface（默认 get_supported_surface()）

    Returns:
        True 如果是正式支持的边类型
    """
    s = surface or get_supported_surface()
    return type_id in s.supported_edge_types


def is_reserved_edge_type(
    type_id: str,
    surface: SupportedSurface | None = None,
) -> bool:
    """判断边类型是否预留（不支持）。

    Args:
        type_id: VisualEdgeType.id
        surface: SupportedSurface（默认 get_supported_surface()）

    Returns:
        True 如果是预留的边类型
    """
    s = surface or get_supported_surface()
    return type_id in s.reserved_edge_types


# ─── Internal Helpers ───


def _format_node_type_name(nt_id: str, category_id: str) -> str:
    """格式化节点类型名称。

    Args:
        nt_id: 原始 node_type ID
        category_id: 所属 category ID

    Returns:
        格式化后的显示名称
    """
    # 移除 category 前缀，然后替换连字符为空格并首字母大写
    base = nt_id.replace(f"{category_id}-", "")
    return base.replace("-", " ").title()
