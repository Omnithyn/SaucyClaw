"""治理规则匹配器测试。"""

from __future__ import annotations

import pytest

from core.governance.matcher import ConditionError, evaluate_rule, match_rules
from core.governance.models import Condition, GovernanceRule


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def reviewer_must_differ_rule() -> GovernanceRule:
    """审查者不能与执行者相同的规则。"""
    return GovernanceRule(
        id="rule-reviewer-must-differ",
        task_type="C",
        description="审查者不能与执行者相同",
        conditions=[
            Condition(field="assignee", op="!=", value_from="reviewer"),
        ],
        severity="block",
        on_hit="Block",
    )


# ---------------------------------------------------------------------------
# evaluate_rule 测试 — Phase 0-1 原有
# ---------------------------------------------------------------------------

class TestEvaluateRule:
    def test_block_scenario(self, reviewer_must_differ_rule):
        """assignee == reviewer → 条件不命中 → 规则被触发（有违规）。"""
        inp = {"assignee": "developer", "reviewer": "developer"}
        assert evaluate_rule(reviewer_must_differ_rule, inp) is False

    def test_allow_scenario(self, reviewer_must_differ_rule):
        """assignee != reviewer → 条件命中 → 规则不被触发（无违规）。"""
        inp = {"assignee": "developer", "reviewer": "reviewer"}
        assert evaluate_rule(reviewer_must_differ_rule, inp) is True

    def test_static_value_equals(self):
        rule = GovernanceRule(
            id="t1",
            task_type="C",
            description="",
            conditions=[Condition(field="status", op="==", value="active")],
            severity="info",
            on_hit="Allow",
        )
        assert evaluate_rule(rule, {"status": "active"}) is True
        assert evaluate_rule(rule, {"status": "inactive"}) is False

    def test_in_operator(self):
        rule = GovernanceRule(
            id="t2",
            task_type="C",
            description="",
            conditions=[Condition(field="role", op="in", value=["admin", "mod"])],
            severity="warn",
            on_hit="Review Required",
        )
        assert evaluate_rule(rule, {"role": "admin"}) is True
        assert evaluate_rule(rule, {"role": "user"}) is False

    def test_not_in_operator(self):
        rule = GovernanceRule(
            id="t3",
            task_type="C",
            description="",
            conditions=[Condition(field="role", op="not_in", value=["banned"])],
            severity="info",
            on_hit="Allow",
        )
        assert evaluate_rule(rule, {"role": "user"}) is True
        assert evaluate_rule(rule, {"role": "banned"}) is False

    def test_exists_operator_true(self):
        rule = GovernanceRule(
            id="t4",
            task_type="C",
            description="",
            conditions=[Condition(field="metadata", op="exists")],
            severity="info",
            on_hit="Allow",
        )
        assert evaluate_rule(rule, {"metadata": {"key": "val"}}) is True

    def test_exists_operator_false(self):
        rule = GovernanceRule(
            id="t4",
            task_type="C",
            description="",
            conditions=[Condition(field="metadata", op="exists")],
            severity="info",
            on_hit="Allow",
        )
        assert evaluate_rule(rule, {"other_field": 1}) is True

    def test_empty_conditions_always_true(self):
        rule = GovernanceRule(
            id="t5",
            task_type="C",
            description="",
            conditions=[],
            severity="info",
            on_hit="Allow",
        )
        assert evaluate_rule(rule, {"anything": True}) is True

    def test_value_from_field_missing_raises(self, reviewer_must_differ_rule):
        with pytest.raises(ConditionError, match="reviewer"):
            evaluate_rule(reviewer_must_differ_rule, {"assignee": "dev"})

    def test_in_operator_non_list_value_raises(self):
        rule = GovernanceRule(
            id="t6",
            task_type="C",
            description="",
            conditions=[Condition(field="x", op="in", value="not-a-list")],
            severity="info",
            on_hit="Allow",
        )
        with pytest.raises(ConditionError, match="'in'.*列表"):
            evaluate_rule(rule, {"x": "a"})

    def test_unknown_operator_raises(self):
        rule = GovernanceRule(
            id="t7",
            task_type="C",
            description="",
            conditions=[Condition(field="x", op="regex", value=".*")],
            severity="info",
            on_hit="Allow",
        )
        with pytest.raises(ConditionError, match="regex"):
            evaluate_rule(rule, {"x": "hello"})


# ---------------------------------------------------------------------------
# match_rules 测试 — Phase 0-1 原有
# ---------------------------------------------------------------------------

class TestMatchRules:
    def test_block_input_matches(self):
        rules = [
            GovernanceRule(
                id="r1",
                task_type="C",
                description="",
                conditions=[
                    Condition(field="assignee", op="!=", value_from="reviewer"),
                ],
                severity="block",
                on_hit="Block",
            )
        ]
        matched = match_rules(rules, {"assignee": "developer", "reviewer": "developer"})
        assert len(matched) == 1
        assert matched[0].id == "r1"

    def test_allow_input_no_match(self):
        rules = [
            GovernanceRule(
                id="r1",
                task_type="C",
                description="",
                conditions=[
                    Condition(field="assignee", op="!=", value_from="reviewer"),
                ],
                severity="block",
                on_hit="Block",
            )
        ]
        matched = match_rules(rules, {"assignee": "developer", "reviewer": "reviewer"})
        assert matched == []

    def test_multiple_rules_partial_match(self):
        rules = [
            GovernanceRule(
                id="r-hit",
                task_type="C",
                description="",
                conditions=[
                    Condition(field="flag", op="==", value=True),
                ],
                severity="warn",
                on_hit="Review Required",
            ),
            GovernanceRule(
                id="r-miss",
                task_type="C",
                description="",
                conditions=[
                    Condition(field="flag", op="==", value=False),
                ],
                severity="info",
                on_hit="Allow",
            ),
        ]
        matched = match_rules(rules, {"flag": True})
        assert len(matched) == 1
        assert matched[0].id == "r-miss"


# ---------------------------------------------------------------------------
# Phase 1.2 新增规则测试
# ---------------------------------------------------------------------------

class TestPhase12Rules:

    # --- rule-specialist-not-direct-output ---
    # 合规检查风格：direct_output 必须为 "false"（输出需经 review）
    # 条件通过 = 合规，条件不通过 = 违规

    def test_specialist_direct_output_blocked(self):
        """direct_output 为 true → 条件不通过 → 违规触发。"""
        rule = GovernanceRule(
            id="rule-specialist-not-direct-output",
            task_type="C",
            description="specialist 不得直接输出最终答案给 CEO",
            conditions=[
                Condition(field="direct_output", op="==", value="false"),
            ],
            severity="block",
            on_hit="Block",
        )
        inp = {"assignee": "specialist", "direct_output": "true"}
        # "true" == "false" → False → evaluate_rule=False → match_rules 返回该规则
        matched = match_rules([rule], inp)
        assert len(matched) == 1
        assert matched[0].on_hit == "Block"

    def test_specialist_via_reviewer_allowed(self):
        """direct_output 为 false → 条件通过 → 合规。"""
        rule = GovernanceRule(
            id="rule-specialist-not-direct-output",
            task_type="C",
            description="specialist 不得直接输出最终答案给 CEO",
            conditions=[
                Condition(field="direct_output", op="==", value="false"),
            ],
            severity="block",
            on_hit="Block",
        )
        inp = {"assignee": "specialist", "direct_output": "false", "reviewer": "reviewer"}
        # "false" == "false" → True → evaluate_rule=True → match_rules=[]
        matched = match_rules([rule], inp)
        assert matched == []

    def test_non_specialist_direct_output_blocked(self):
        """非 specialist 角色 direct_output 为 true → 同样触发规则。

        注意：单条件合规检查不区分角色。direct_output == "true" 即违规。
        角色限制由 routing 层保证。
        """
        rule = GovernanceRule(
            id="rule-specialist-not-direct-output",
            task_type="C",
            description="specialist 不得直接输出最终答案给 CEO",
            conditions=[
                Condition(field="direct_output", op="==", value="false"),
            ],
            severity="block",
            on_hit="Block",
        )
        inp = {"assignee": "manager", "direct_output": "true"}
        # "true" == "false" → False → evaluate_rule=False → 违规
        matched = match_rules([rule], inp)
        assert len(matched) == 1

    # --- rule-handoff-required ---
    # 合规检查风格：handoff 必须为 "true"

    def test_d_task_no_handoff_blocked(self):
        """handoff 为 false → 条件不通过 → 违规触发。"""
        rule = GovernanceRule(
            id="rule-handoff-required",
            task_type="D",
            description="多阶段任务进入 review 前必须有 handoff 记录",
            conditions=[
                Condition(field="handoff", op="==", value="true"),
            ],
            severity="block",
            on_hit="Block",
        )
        inp = {"task_type": "D", "handoff": "false", "reviewer": "reviewer"}
        # "false" == "true" → False → evaluate=False → 违规
        matched = match_rules([rule], inp)
        assert len(matched) == 1
        assert matched[0].on_hit == "Block"

    def test_d_task_with_handoff_allowed(self):
        """handoff 为 true → 条件通过 → 合规。"""
        rule = GovernanceRule(
            id="rule-handoff-required",
            task_type="D",
            description="多阶段任务进入 review 前必须有 handoff 记录",
            conditions=[
                Condition(field="handoff", op="==", value="true"),
            ],
            severity="block",
            on_hit="Block",
        )
        inp = {"task_type": "D", "handoff": "true", "reviewer": "reviewer"}
        # "true" == "true" → True → evaluate=True → match_rules=[]
        matched = match_rules([rule], inp)
        assert matched == []

    # --- rule-restricted-routing ---
    # 合规检查风格：assignee 必须在 [manager, orchestrator] 中

    def test_a_task_wrong_assignee_blocked(self):
        """assignee 为 developer → 不在允许列表中 → 违规。"""
        rule = GovernanceRule(
            id="rule-restricted-routing",
            task_type="A",
            description="A 类任务只能由 manager 或 orchestrator 处理",
            conditions=[
                Condition(field="assignee", op="in", value=["manager", "orchestrator"]),
            ],
            severity="block",
            on_hit="Block",
        )
        inp = {"task_type": "A", "assignee": "developer"}
        # "developer" in [manager,orchestrator] → False → 违规
        matched = match_rules([rule], inp)
        assert len(matched) == 1
        assert matched[0].on_hit == "Block"

    def test_a_task_manager_allowed(self):
        """assignee 为 manager → 条件通过 → 合规。"""
        rule = GovernanceRule(
            id="rule-restricted-routing",
            task_type="A",
            description="A 类任务只能由 manager 或 orchestrator 处理",
            conditions=[
                Condition(field="assignee", op="in", value=["manager", "orchestrator"]),
            ],
            severity="block",
            on_hit="Block",
        )
        inp = {"task_type": "A", "assignee": "manager"}
        # "manager" in [manager,orchestrator] → True → evaluate=True → match_rules=[]
        matched = match_rules([rule], inp)
        assert matched == []

    # --- rule-escalate-on-conflict ---
    # 合规检查风格：conflict 必须为 "false"（无冲突）

    def test_conflict_triggers_escalate(self):
        """存在冲突 → conflict 为 true → 条件不通过 → 触发升级。"""
        rule = GovernanceRule(
            id="rule-escalate-on-conflict",
            task_type="C",
            description="方向、范围或输入不足冲突时必须升级",
            conditions=[
                Condition(field="conflict", op="==", value="false"),
            ],
            severity="block",
            on_hit="Escalate",
        )
        inp = {"conflict": "true"}
        # "true" == "false" → False → evaluate=False → match_rules=[rule]
        matched = match_rules([rule], inp)
        assert len(matched) == 1
        assert matched[0].on_hit == "Escalate"

    def test_no_conflict_no_escalate(self):
        """无冲突 → conflict 为 false → 条件通过 → 不触发升级。"""
        rule = GovernanceRule(
            id="rule-escalate-on-conflict",
            task_type="C",
            description="方向、范围或输入不足冲突时必须升级",
            conditions=[
                Condition(field="conflict", op="==", value="false"),
            ],
            severity="block",
            on_hit="Escalate",
        )
        inp = {"conflict": "false"}
        # "false" == "false" → True → evaluate=True → match_rules=[]
        matched = match_rules([rule], inp)
        assert matched == []

    # --- 正向路由场景 ---

    def test_specialist_to_reviewer_with_handoff_allowed(self):
        """specialist 输出给 reviewer 且 direct_output=false → 所有规则合规。"""
        rules = [
            GovernanceRule(
                id="rule-specialist-not-direct-output",
                task_type="C",
                description="specialist 不得直接输出最终答案给 CEO",
                conditions=[
                    Condition(field="direct_output", op="==", value="false"),
                ],
                severity="block",
                on_hit="Block",
            ),
            GovernanceRule(
                id="rule-reviewer-must-differ",
                task_type="C",
                description="审查者不能与执行者相同",
                conditions=[
                    Condition(field="assignee", op="!=", value_from="reviewer"),
                ],
                severity="block",
                on_hit="Block",
            ),
        ]
        inp = {
            "assignee": "specialist",
            "reviewer": "reviewer",
            "direct_output": "false",
            "handoff": "true",
        }
        # specialist rule: "false"=="false" → True → pass
        # reviewer rule: "specialist" != "reviewer" → True → pass
        matched = match_rules(rules, inp)
        assert matched == []
