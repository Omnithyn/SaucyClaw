"""Schema 与运行模型对齐测试。

验证 schemas/governance/*.yaml 中的字段能完整进入对应的 dataclass。
这是契约一致性测试，不是功能测试。
"""

from __future__ import annotations

from pathlib import Path

import yaml

from core.governance.loader import load_governance
from core.governance.models import GovernanceRule, RoleDefinition, TaskType

SCHEMAS_DIR = Path(__file__).parent.parent.parent / "schemas" / "governance"


# ---------------------------------------------------------------------------
# YAML 字段 → dataclass 字段映射
# ---------------------------------------------------------------------------

class TestTaskTypeFieldAlignment:
    def test_all_yaml_fields_in_model(self):
        """task_types.yaml 中的每个字段都应进入 TaskType。"""
        with open(SCHEMAS_DIR / "task_types.yaml") as f:
            data = yaml.safe_load(f)

        yaml_keys = set()
        for item in data.get("task_types", []):
            yaml_keys.update(item.keys())

        model_keys = set(TaskType.__dataclass_fields__.keys())

        missing = yaml_keys - model_keys
        assert not missing, f"task_types.yaml 有字段 {missing} 但 TaskType model 中没有"

    def test_load_governance_task_types_complete(self):
        """批量加载的 TaskType 应包含 allowed_roles。"""
        schema = load_governance(SCHEMAS_DIR)
        for tt in schema.task_types:
            assert hasattr(tt, "allowed_roles")
            assert hasattr(tt, "required_roles")
            assert hasattr(tt, "blocking_rules")
            assert hasattr(tt, "review_required")

    def test_yaml_allowed_roles_roundtrip(self):
        """task_types.yaml 中 C 类的 allowed_roles 应能被加载。"""
        schema = load_governance(SCHEMAS_DIR)
        c_type = [t for t in schema.task_types if t.id == "C"]
        assert len(c_type) == 1
        assert "manager" in c_type[0].allowed_roles
        assert "specialist" in c_type[0].allowed_roles
        assert "reviewer" in c_type[0].allowed_roles


class TestRoleFieldAlignment:
    def test_all_yaml_fields_in_model(self):
        """roles.yaml 中的每个字段都应进入 RoleDefinition。"""
        with open(SCHEMAS_DIR / "roles.yaml") as f:
            data = yaml.safe_load(f)

        yaml_keys = set()
        for item in data.get("roles", []):
            yaml_keys.update(item.keys())

        model_keys = set(RoleDefinition.__dataclass_fields__.keys())

        missing = yaml_keys - model_keys
        assert not missing, f"roles.yaml 有字段 {missing} 但 RoleDefinition model 中没有"

    def test_load_governance_roles_complete(self):
        """批量加载的 Role 应包含全部字段。"""
        schema = load_governance(SCHEMAS_DIR)
        for role in schema.roles:
            assert hasattr(role, "capabilities")
            assert hasattr(role, "permissions")
            assert hasattr(role, "handoff_to")

    def test_specialist_can_output_to_ceo(self):
        """specialist 的 can_output_to_ceo 权限应为 False。"""
        schema = load_governance(SCHEMAS_DIR)
        specialist = [r for r in schema.roles if r.id == "specialist"]
        assert len(specialist) == 1
        assert specialist[0].permissions.get("can_output_to_ceo") is False

    def test_role_description_roundtrip(self):
        """roles.yaml 中的 description 应能完整进入 RoleDefinition。"""
        schema = load_governance(SCHEMAS_DIR)
        specialist = [r for r in schema.roles if r.id == "specialist"]
        assert len(specialist) == 1
        assert specialist[0].description == "通用 specialist，不直接对外输出"


class TestRuleFieldAlignment:
    def test_all_yaml_fields_in_model(self):
        """rules.yaml 中的每个字段都应进入 GovernanceRule。"""
        with open(SCHEMAS_DIR / "rules.yaml") as f:
            data = yaml.safe_load(f)

        yaml_keys = set()
        for item in data.get("rules", []):
            yaml_keys.update(item.keys())

        model_keys = set(GovernanceRule.__dataclass_fields__.keys())

        missing = yaml_keys - model_keys
        assert not missing, f"rules.yaml 有字段 {missing} 但 GovernanceRule model 中没有"

    def test_rules_with_applies_when(self):
        """使用 applies_when 的规则应能完整加载。"""
        schema = load_governance(SCHEMAS_DIR)
        spec_rule = [r for r in schema.rules if r.id == "rule-specialist-not-direct-output"]
        assert len(spec_rule) == 1
        assert len(spec_rule[0].applies_when) > 0
        assert len(spec_rule[0].conditions) > 0

    def test_rules_without_applies_when(self):
        """不使用 applies_when 的规则应返回空列表。"""
        schema = load_governance(SCHEMAS_DIR)
        base_rule = [r for r in schema.rules if r.id == "rule-reviewer-must-differ"]
        assert len(base_rule) == 1
        assert base_rule[0].applies_when == []


# ---------------------------------------------------------------------------
# 端到端：load_governance 作为集成入口
# ---------------------------------------------------------------------------

class TestLoadGovernanceEndToEnd:
    def test_full_schema_load(self):
        """load_governance() 应返回完整的 roles / task_types / rules。"""
        schema = load_governance(SCHEMAS_DIR)
        assert len(schema.roles) >= 5
        assert len(schema.task_types) == 5  # A, B, C, D, E
        assert len(schema.rules) >= 5

    def test_integration_uses_load_governance(self):
        """集成测试应能直接用 load_governance() 获取 rules。"""
        schema = load_governance(SCHEMAS_DIR)
        rule_ids = {r.id for r in schema.rules}
        assert "rule-reviewer-must-differ" in rule_ids
        assert "rule-specialist-not-direct-output" in rule_ids
        assert "rule-handoff-required" in rule_ids

    def test_blocking_rules_reference_exist(self):
        """task_types 中 blocking_rules 引用的规则 ID 应实际存在。"""
        schema = load_governance(SCHEMAS_DIR)
        rule_ids = {r.id for r in schema.rules}
        for tt in schema.task_types:
            for rule_id in tt.blocking_rules:
                assert rule_id in rule_ids, (
                    f"task_type {tt.id} 引用了不存在的规则: {rule_id}"
                )


class TestRuleMetadataRoundtrip:
    """Phase 1.7: 规则元数据 round-trip 验证。"""

    def test_category_roundtrip(self):
        """验证 category 字段能正确从 YAML 加载。"""
        schema = load_governance(SCHEMAS_DIR)
        rule = [r for r in schema.rules if r.id == "rule-reviewer-must-differ"]
        assert len(rule) == 1
        assert rule[0].category == "separation_of_duties"
        assert rule[0].risk_level == "high"

    def test_rationale_roundtrip(self):
        """验证 rationale 字段能正确从 YAML 加载。"""
        schema = load_governance(SCHEMAS_DIR)
        rule = [r for r in schema.rules if r.id == "rule-specialist-not-direct-output"]
        assert len(rule) == 1
        assert rule[0].rationale != ""
        assert "specialist" in rule[0].rationale
