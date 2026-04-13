"""元模型加载与验证测试。"""

from __future__ import annotations

from pathlib import Path

import pytest

from core.meta_model.loader import (
    MetaModelLoadError,
    load_meta_model,
    validate_meta_model,
)
from core.meta_model.models import EntityType, MetaModel


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SCHEMAS_DIR = Path(__file__).parent.parent.parent / "schemas" / "meta"


# ---------------------------------------------------------------------------
# 加载测试
# ---------------------------------------------------------------------------

class TestLoadMetaModel:
    def test_load_from_schemas_dir(self):
        """从 schemas/meta/ 目录应能加载完整元模型。"""
        model = load_meta_model(SCHEMAS_DIR)

        assert len(model.entity_types) == 3
        assert len(model.relation_types) == 3
        assert len(model.action_types) == 2

    def test_entity_types_loaded(self):
        et = load_meta_model(SCHEMAS_DIR).get_entity_type("agent-role")
        assert et is not None
        assert et.name == "智能体角色"
        assert len(et.properties) == 2

    def test_property_required_field(self):
        et = load_meta_model(SCHEMAS_DIR).get_entity_type("governance-rule")
        assert et is not None
        severity_prop = next(p for p in et.properties if p.name == "severity")
        assert severity_prop.values == ["info", "warn", "review", "block"]
        assert severity_prop.required is True

    def test_relation_types_loaded(self):
        model = load_meta_model(SCHEMAS_DIR)
        rt = model.get_relation_type("rule-applies-to")
        assert rt is not None
        assert rt.source == "governance-rule"
        assert rt.target == "task-type"
        assert rt.cardinality == "many-to-one"

    def test_action_types_loaded(self):
        model = load_meta_model(SCHEMAS_DIR)
        at = model.get_action_type("assign-task")
        assert at is not None
        assert at.target_object == "task-type"
        assert "assignee has capability required by task" in at.preconditions

    def test_empty_directory_returns_empty_model(self, tmp_path: Path):
        """空目录应返回空元模型而非报错。"""
        model = load_meta_model(tmp_path)
        assert model == MetaModel()

    def test_get_missing_type_returns_none(self):
        model = load_meta_model(SCHEMAS_DIR)
        assert model.get_entity_type("nonexistent") is None
        assert model.get_relation_type("nonexistent") is None
        assert model.get_action_type("nonexistent") is None

    def test_invalid_property_type_raises(self, tmp_path: Path):
        bad = tmp_path / "object_types.yaml"
        bad.write_text(
            "entity_types:\n"
            "  - id: bad\n"
            "    name: Bad\n"
            "    description: ''\n"
            "    properties:\n"
            "      - name: x\n"
            "        type: invalid_type\n"
        )
        with pytest.raises(MetaModelLoadError, match="未知属性类型"):
            load_meta_model(tmp_path)


# ---------------------------------------------------------------------------
# 验证测试
# ---------------------------------------------------------------------------

class TestValidateMetaModel:
    def test_schemas_dir_valid(self):
        errors = validate_meta_model(load_meta_model(SCHEMAS_DIR))
        assert errors == []

    def test_missing_source_entity(self):
        model = MetaModel(
            relation_types=[
                __import__("core.meta_model.models", fromlist=["RelationType"]).RelationType(
                    id="r1", name="R1", source="ghost", target="agent-role"
                )
            ],
            entity_types=[
                EntityType(id="agent-role", name="角色", description="")
            ],
        )
        errors = validate_meta_model(model)
        assert len(errors) == 1
        assert "ghost" in errors[0]

    def test_missing_target_entity(self):
        from core.meta_model.models import RelationType

        model = MetaModel(
            entity_types=[EntityType(id="a", name="A", description="")],
            relation_types=[
                RelationType(id="r1", name="R1", source="a", target="b")
            ],
        )
        errors = validate_meta_model(model)
        assert len(errors) == 1
        assert "b" in errors[0]

    def test_duplicate_entity_id(self):
        model = MetaModel(
            entity_types=[
                EntityType(id="a", name="A1", description=""),
                EntityType(id="a", name="A2", description=""),
            ]
        )
        errors = validate_meta_model(model)
        assert any("重复" in e and "a" in e for e in errors)

    def test_invalid_cardinality(self):
        from core.meta_model.models import RelationType

        model = MetaModel(
            entity_types=[EntityType(id="a", name="A", description="")],
            relation_types=[
                RelationType(id="r1", name="R1", source="a", target="a", cardinality="bad")
            ],
        )
        errors = validate_meta_model(model)
        assert any("cardinality" in e for e in errors)
