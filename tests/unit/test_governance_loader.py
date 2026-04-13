"""治理 schema 加载器测试。"""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from core.governance.loader import (
    SchemaError,
    GovernanceSchema,
    load_governance,
    load_roles,
    load_rules,
    load_task_types,
)

SCHEMAS_DIR = Path(__file__).parent.parent.parent / "schemas" / "governance"


# ---------------------------------------------------------------------------
# 从真实 YAML 加载
# ---------------------------------------------------------------------------

class TestLoadFromRealSchemas:
    def test_load_rules(self):
        rules = load_rules(SCHEMAS_DIR / "rules.yaml")
        assert len(rules) >= 3  # Phase 1.2 至少 5 条
        ids = {r.id for r in rules}
        assert "rule-reviewer-must-differ" in ids

    def test_load_rules_applies_when(self):
        """验证 applies_when 被正确解析。"""
        rules = load_rules(SCHEMAS_DIR / "rules.yaml")
        spec_rule = [r for r in rules if r.id == "rule-specialist-not-direct-output"]
        assert len(spec_rule) == 1
        assert len(spec_rule[0].applies_when) > 0

    def test_load_roles(self):
        roles = load_roles(SCHEMAS_DIR / "roles.yaml")
        ids = {r.id for r in roles}
        assert "developer" in ids
        assert "specialist" in ids
        assert "reviewer" in ids
        assert len(roles) >= 5

    def test_load_task_types(self):
        task_types = load_task_types(SCHEMAS_DIR / "task_types.yaml")
        ids = {t.id for t in task_types}
        assert "A" in ids
        assert "B" in ids
        assert "C" in ids
        assert "D" in ids
        assert "E" in ids

    def test_load_governance_batch(self):
        schema = load_governance(SCHEMAS_DIR)
        assert isinstance(schema, GovernanceSchema)
        assert len(schema.rules) > 0
        assert len(schema.roles) > 0
        assert len(schema.task_types) > 0

    def test_load_governance_missing_dir_returns_empty(self):
        schema = load_governance("/nonexistent/path")
        assert schema == GovernanceSchema()


# ---------------------------------------------------------------------------
# 错误处理
# ---------------------------------------------------------------------------

class TestLoadErrors:
    def test_missing_file_raises_schema_error(self, tmp_path):
        with pytest.raises(SchemaError, match="文件不存在"):
            load_rules(tmp_path / "no_such.yaml")

    def test_missing_required_keys_raises_schema_error(self, tmp_path):
        path = tmp_path / "rules.yaml"
        path.write_text(dedent("""\
            rules:
              - id: "r1"
        """))
        with pytest.raises(SchemaError, match="缺少必填字段"):
            load_rules(path)

    def test_non_list_rules_raises(self, tmp_path):
        path = tmp_path / "rules.yaml"
        path.write_text("rules: not_a_list")
        with pytest.raises(SchemaError, match="必须是列表"):
            load_rules(path)

    def test_non_dict_root_raises(self, tmp_path):
        path = tmp_path / "rules.yaml"
        path.write_text("- just\n- a\n- list")
        with pytest.raises(SchemaError, match="映射"):
            load_rules(path)

    def test_applies_when_must_be_list(self, tmp_path):
        path = tmp_path / "rules.yaml"
        path.write_text(dedent("""\
            rules:
              - id: "r1"
                task_type: "C"
                conditions: []
                severity: "block"
                on_hit: "Block"
                applies_when: "not_a_list"
        """))
        with pytest.raises(SchemaError, match="applies_when.*列表"):
            load_rules(path)

    def test_missing_role_keys_raises(self, tmp_path):
        path = tmp_path / "roles.yaml"
        path.write_text(dedent("""\
            roles:
              - id: "r1"
        """))
        with pytest.raises(SchemaError, match="缺少必填字段.*name"):
            load_roles(path)

    def test_missing_task_type_keys_raises(self, tmp_path):
        path = tmp_path / "task_types.yaml"
        path.write_text(dedent("""\
            task_types:
              - id: "X"
        """))
        with pytest.raises(SchemaError, match="缺少必填字段.*name"):
            load_task_types(path)


# ---------------------------------------------------------------------------
# 解析完整性
# ---------------------------------------------------------------------------

class TestParseCompleteness:
    def test_rules_conditions_parsed(self, tmp_path):
        path = tmp_path / "rules.yaml"
        path.write_text(dedent("""\
            rules:
              - id: "r1"
                task_type: "C"
                description: "test rule"
                conditions:
                  - field: "assignee"
                    op: "!="
                    value_from: "reviewer"
                severity: "block"
                on_hit: "Block"
                applies_when:
                  - field: "role"
                    op: "in"
                    value: ["specialist"]
        """))
        rules = load_rules(path)
        assert len(rules) == 1
        rule = rules[0]
        assert rule.description == "test rule"
        assert len(rule.conditions) == 1
        assert rule.conditions[0].value_from == "reviewer"
        assert len(rule.applies_when) == 1
        assert rule.applies_when[0].value == ["specialist"]

    def test_role_permissions_parsed(self, tmp_path):
        path = tmp_path / "roles.yaml"
        path.write_text(dedent("""\
            roles:
              - id: "specialist"
                name: "专家"
                capabilities: ["analysis"]
                permissions:
                  can_output_to_ceo: false
                handoff_to: ["reviewer"]
        """))
        roles = load_roles(path)
        assert roles[0].permissions["can_output_to_ceo"] is False
        assert roles[0].handoff_to == ["reviewer"]
