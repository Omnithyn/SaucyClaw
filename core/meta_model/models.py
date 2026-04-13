"""元模型 dataclass 定义。"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Property:
    """实体类型的属性定义。"""

    name: str
    type: str
    required: bool = False
    values: list[str] | None = None  # enum 类型的可选值


@dataclass(frozen=True)
class EntityType:
    """元模型中的对象类型。"""

    id: str
    name: str
    description: str
    properties: list[Property] = field(default_factory=list)


@dataclass(frozen=True)
class RelationType:
    """元模型中的关系类型。"""

    id: str
    name: str
    source: str
    target: str
    cardinality: str = "many-to-many"


@dataclass(frozen=True)
class ActionType:
    """元模型中的动作类型。"""

    id: str
    name: str
    description: str
    target_object: str
    preconditions: list[str] = field(default_factory=list)
    side_effects: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class MetaModel:
    """完整的元模型，包含所有类型定义。"""

    entity_types: list[EntityType] = field(default_factory=list)
    relation_types: list[RelationType] = field(default_factory=list)
    action_types: list[ActionType] = field(default_factory=list)

    def get_entity_type(self, type_id: str) -> EntityType | None:
        for et in self.entity_types:
            if et.id == type_id:
                return et
        return None

    def get_relation_type(self, type_id: str) -> RelationType | None:
        for rt in self.relation_types:
            if rt.id == type_id:
                return rt
        return None

    def get_action_type(self, type_id: str) -> ActionType | None:
        for at in self.action_types:
            if at.id == type_id:
                return at
        return None
