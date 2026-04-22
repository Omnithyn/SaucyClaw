"""测试本体 Loader。

N2 — Ontology Governance Loop
验证 load_ontology_schema、validate_ontology_schema 的功能。
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ontology.loader import (  # noqa: E402
    load_ontology_schema,
    validate_ontology_schema,
    load_default_ontology_schema,
)


SCHEMA_DIR = PROJECT_ROOT / "schemas" / "ontology"


class TestLoadOntologySchema:
    """测试 load_ontology_schema。"""

    def test_load_from_existing_directory(self):
        """从现有目录加载 Schema。"""
        schema = load_ontology_schema(SCHEMA_DIR)

        assert len(schema.event_types) >= 1
        assert len(schema.context_types) >= 1
        assert len(schema.fact_types) >= 1

    def test_load_event_types(self):
        """加载 EventType。"""
        schema = load_ontology_schema(SCHEMA_DIR)

        tool_invocation = schema.get_event_type("tool-invocation")
        assert tool_invocation is not None
        assert tool_invocation.subject_type == "agent-role"

    def test_load_context_types(self):
        """加载 ContextType。"""
        schema = load_ontology_schema(SCHEMA_DIR)

        session_context = schema.get_context_type("session-context")
        assert session_context is not None
        assert session_context.lifecycle == "ephemeral"

    def test_load_fact_types(self):
        """加载 FactType。"""
        schema = load_ontology_schema(SCHEMA_DIR)

        review_requirement = schema.get_fact_type("review-requirement")
        assert review_requirement is not None
        assert review_requirement.evidence_binding is True

    def test_load_empty_directory(self):
        """从空目录加载 Schema（返回空 Schema）。"""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            schema = load_ontology_schema(tmpdir)

            assert schema.event_types == []
            assert schema.context_types == []
            assert schema.fact_types == []

    def test_load_default_ontology_schema(self):
        """加载默认 Schema。"""
        schema = load_default_ontology_schema()

        assert len(schema.event_types) >= 1
        assert len(schema.fact_types) >= 1


class TestValidateOntologySchema:
    """测试 validate_ontology_schema。"""

    def test_validate_valid_schema(self):
        """验证有效 Schema。"""
        schema = load_ontology_schema(SCHEMA_DIR)
        errors = validate_ontology_schema(schema)

        assert errors == []

    def test_validate_schema_with_duplicate_ids(self):
        """验证有重复 ID 的 Schema。"""
        from ontology.schema import EventType, OntologySchema

        # 创建有重复 ID 的 Schema
        event_type1 = EventType(
            id="duplicate-id",
            name="重复事件",
            description="测试重复",
            subject_type="agent-role",
        )
        event_type2 = EventType(
            id="duplicate-id",
            name="重复事件",
            description="测试重复",
            subject_type="agent-role",
        )

        schema = OntologySchema(event_types=[event_type1, event_type2])
        errors = validate_ontology_schema(schema)

        assert len(errors) >= 1
        assert "重复" in errors[0]
