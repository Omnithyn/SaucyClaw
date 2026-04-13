"""元模型 YAML 加载与验证。"""

from __future__ import annotations

from pathlib import Path

import yaml

from core.meta_model.models import (
    ActionType,
    EntityType,
    MetaModel,
    Property,
    RelationType,
)

# 合法属性类型
_VALID_TYPES = {"string", "boolean", "integer", "number", "array", "object", "enum"}

# 合法关系基数
_VALID_CARDINALITIES = {
    "one-to-one",
    "one-to-many",
    "many-to-one",
    "many-to-many",
}


class MetaModelLoadError(Exception):
    """元模型加载失败。"""


class MetaModelValidationError(Exception):
    """元模型验证失败。"""


def _load_properties(raw_list: list[dict]) -> list[Property]:
    """将 YAML 属性列表转为 Property 列表。"""
    props = []
    for item in raw_list:
        ptype = item.get("type", "string")
        if ptype not in _VALID_TYPES:
            raise MetaModelLoadError(
                f"未知属性类型: {ptype!r}，有效值: {sorted(_VALID_TYPES)}"
            )
        props.append(
            Property(
                name=item["name"],
                type=ptype,
                required=item.get("required", False),
                values=item.get("values"),
            )
        )
    return props


def load_meta_model(schema_dir: str | Path) -> MetaModel:
    """从 schemas/meta/ 目录加载元模型。

    读取 object_types.yaml, relation_types.yaml, action_types.yaml。
    缺少文件不会报错（空文件 = 空列表），但文件格式错误会抛出异常。
    """
    base = Path(schema_dir)

    entities: list[EntityType] = []
    obj_path = base / "object_types.yaml"
    if obj_path.exists():
        with open(obj_path) as f:
            data = yaml.safe_load(f) or {}
        for item in data.get("entity_types", []):
            entities.append(
                EntityType(
                    id=item["id"],
                    name=item["name"],
                    description=item.get("description", ""),
                    properties=_load_properties(item.get("properties", [])),
                )
            )

    relations: list[RelationType] = []
    rel_path = base / "relation_types.yaml"
    if rel_path.exists():
        with open(rel_path) as f:
            data = yaml.safe_load(f) or {}
        for item in data.get("relation_types", []):
            relations.append(
                RelationType(
                    id=item["id"],
                    name=item["name"],
                    source=item["source"],
                    target=item["target"],
                    cardinality=item.get("cardinality", "many-to-many"),
                )
            )

    actions: list[ActionType] = []
    act_path = base / "action_types.yaml"
    if act_path.exists():
        with open(act_path) as f:
            data = yaml.safe_load(f) or {}
        for item in data.get("action_types", []):
            actions.append(
                ActionType(
                    id=item["id"],
                    name=item["name"],
                    description=item.get("description", ""),
                    target_object=item.get("target_object", ""),
                    preconditions=item.get("preconditions", []),
                    side_effects=item.get("side_effects", []),
                )
            )

    return MetaModel(
        entity_types=entities,
        relation_types=relations,
        action_types=actions,
    )


def validate_meta_model(model: MetaModel) -> list[str]:
    """验证元模型一致性，返回错误列表（空列表 = 通过）。

    检查项：
    1. 关系类型的 source/target 必须引用已定义的 entity_type
    2. 动作类型的 target_object 必须引用已定义的 entity_type
    3. 同一类别内 ID 不能重复
    """
    errors: list[str] = []
    entity_ids = {et.id for et in model.entity_types}

    # 检查关系类型的 source/target
    for rt in model.relation_types:
        if rt.source not in entity_ids:
            errors.append(
                f"关系类型 {rt.id!r} 的 source {rt.source!r} 未定义"
            )
        if rt.target not in entity_ids:
            errors.append(
                f"关系类型 {rt.id!r} 的 target {rt.target!r} 未定义"
            )
        if rt.cardinality not in _VALID_CARDINALITIES:
            errors.append(
                f"关系类型 {rt.id!r} 的 cardinality {rt.cardinality!r} 无效"
            )

    # 检查动作类型的 target_object
    for at in model.action_types:
        if at.target_object not in entity_ids:
            errors.append(
                f"动作类型 {at.id!r} 的 target_object {at.target_object!r} 未定义"
            )

    # 检查 ID 重复
    entity_id_list = [et.id for et in model.entity_types]
    seen: set[str] = set()
    for eid in entity_id_list:
        if eid in seen:
            errors.append(f"entity_type ID {eid!r} 重复")
        seen.add(eid)

    relation_id_list = [rt.id for rt in model.relation_types]
    seen = set()
    for rid in relation_id_list:
        if rid in seen:
            errors.append(f"relation_type ID {rid!r} 重复")
        seen.add(rid)

    action_id_list = [at.id for at in model.action_types]
    seen = set()
    for aid in action_id_list:
        if aid in seen:
            errors.append(f"action_type ID {aid!r} 重复")
        seen.add(aid)

    return errors
