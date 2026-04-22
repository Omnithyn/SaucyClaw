"""本体 YAML 加载器。

N2 — Ontology Governance Loop

从 schemas/ontology/ 加载 OntologySchema：
- event_types.yaml → EventType list
- context_types.yaml → ContextType list
- fact_types.yaml → FactType list

参考 core/meta_model/loader.py 模式。
"""

from __future__ import annotations

from pathlib import Path

import yaml

from ontology.schema import (
    ContextType,
    EventType,
    FactType,
    OntologySchema,
    build_event_type_from_dict,
    build_context_type_from_dict,
    build_fact_type_from_dict,
)


class OntologyLoadError(Exception):
    """本体加载失败。"""


def load_ontology_schema(schema_dir: str | Path) -> OntologySchema:
    """从 schemas/ontology/ 目录加载本体 Schema。

    读取 event_types.yaml, context_types.yaml, fact_types.yaml。
    缺少文件不会报错（空文件 = 空列表），但文件格式错误会抛出异常。
    """
    base = Path(schema_dir)

    event_types: list[EventType] = []
    event_path = base / "event_types.yaml"
    if event_path.exists():
        with open(event_path) as f:
            data = yaml.safe_load(f) or {}
        for item in data.get("event_types", []):
            event_types.append(build_event_type_from_dict(item))

    context_types: list[ContextType] = []
    context_path = base / "context_types.yaml"
    if context_path.exists():
        with open(context_path) as f:
            data = yaml.safe_load(f) or {}
        for item in data.get("context_types", []):
            context_types.append(build_context_type_from_dict(item))

    fact_types: list[FactType] = []
    fact_path = base / "fact_types.yaml"
    if fact_path.exists():
        with open(fact_path) as f:
            data = yaml.safe_load(f) or {}
        for item in data.get("fact_types", []):
            fact_types.append(build_fact_type_from_dict(item))

    return OntologySchema(
        event_types=event_types,
        context_types=context_types,
        fact_types=fact_types,
    )


def validate_ontology_schema(schema: OntologySchema) -> list[str]:
    """验证本体 Schema 一致性，返回错误列表（空列表 = 通过）。

    检查项：
    1. 同一类别内 ID 不能重复
    """
    errors: list[str] = []

    # 检查 EventType ID 重复
    event_ids = [et.id for et in schema.event_types]
    seen: set[str] = set()
    for eid in event_ids:
        if eid in seen:
            errors.append(f"EventType ID {eid!r} 重复")
        seen.add(eid)

    # 检查 ContextType ID 重复
    context_ids = [ct.id for ct in schema.context_types]
    seen = set()
    for cid in context_ids:
        if cid in seen:
            errors.append(f"ContextType ID {cid!r} 重复")
        seen.add(cid)

    # 检查 FactType ID 重复
    fact_ids = [ft.id for ft in schema.fact_types]
    seen = set()
    for fid in fact_ids:
        if fid in seen:
            errors.append(f"FactType ID {fid!r} 重复")
        seen.add(fid)

    return errors


# ─── Convenience Loader ───


SCHEMA_DIR = Path(__file__).parent.parent / "schemas" / "ontology"


def load_default_ontology_schema() -> OntologySchema:
    """加载默认本体 Schema（从 schemas/ontology/）。"""
    return load_ontology_schema(SCHEMA_DIR)
