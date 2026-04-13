"""MemoryRecord 构造器测试。"""

from __future__ import annotations

from core.engine.memory_builder import build_memory_record
from core.governance.models import Condition, GovernanceRule


def _make_block_rule() -> GovernanceRule:
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
# Block 场景
# ---------------------------------------------------------------------------

class TestBuildMemoryRecordBlock:
    def test_violation_type(self):
        rule = _make_block_rule()
        record = build_memory_record(
            decision="Block",
            triggered=[rule],
            input_data={"task_type": "C", "assignee": "dev", "reviewer": "dev"},
            source="openclaw",
        )

        assert record.type == "violation"

    def test_summary_template(self):
        rule = _make_block_rule()
        record = build_memory_record(
            decision="Block",
            triggered=[rule],
            input_data={"task_type": "C"},
            source="openclaw",
        )

        assert "C 类任务触发阻断" in record.summary
        assert rule.description in record.summary

    def test_tags_include_task_and_decision(self):
        rule = _make_block_rule()
        record = build_memory_record(
            decision="Block",
            triggered=[rule],
            input_data={"task_type": "C"},
            source="openclaw",
        )

        assert "task:C" in record.tags
        assert "decision:Block" in record.tags
        assert "source:openclaw" in record.tags

    def test_tags_include_rule_id(self):
        rule = _make_block_rule()
        record = build_memory_record(
            decision="Block",
            triggered=[rule],
            input_data={"task_type": "C"},
            source="openclaw",
        )

        assert f"rule:{rule.id}" in record.tags

    def test_id_is_unique(self):
        rule = _make_block_rule()
        ids = {
            build_memory_record("Block", [rule], {"task_type": "C"}).id
            for _ in range(5)
        }
        assert len(ids) == 5


# ---------------------------------------------------------------------------
# Allow 场景
# ---------------------------------------------------------------------------

class TestBuildMemoryRecordAllow:
    def test_pass_type(self):
        record = build_memory_record(
            decision="Allow",
            triggered=[],
            input_data={"task_type": "C"},
            source="openclaw",
        )

        assert record.type == "pass"

    def test_summary_template(self):
        record = build_memory_record(
            decision="Allow",
            triggered=[],
            input_data={"task_type": "C"},
            source="openclaw",
        )

        assert "C 类任务通过治理检查" in record.summary
        assert "no rules triggered" in record.summary

    def test_tags_no_rule_id(self):
        record = build_memory_record(
            decision="Allow",
            triggered=[],
            input_data={"task_type": "C"},
            source="openclaw",
        )

        assert "task:C" in record.tags
        assert "decision:Allow" in record.tags
        assert "source:openclaw" in record.tags
        # 不应包含 rule: 前缀的 tag
        assert not any(t.startswith("rule:") for t in record.tags)

    def test_empty_source_evidences(self):
        record = build_memory_record(
            decision="Allow",
            triggered=[],
            input_data={"task_type": "C"},
        )

        assert record.source_evidences == []

    def test_default_trend(self):
        record = build_memory_record(
            decision="Allow",
            triggered=[],
            input_data={"task_type": "C"},
        )

        assert record.trend == "stable"


# ---------------------------------------------------------------------------
# Review Required 场景
# ---------------------------------------------------------------------------

class TestBuildMemoryRecordReview:
    def test_violation_type_for_review(self):
        rule = GovernanceRule(
            id="r-review",
            task_type="C",
            description="需要额外审查",
            conditions=[],
            severity="review",
            on_hit="Review Required",
        )
        record = build_memory_record(
            decision="Review Required",
            triggered=[rule],
            input_data={"task_type": "C"},
        )

        assert record.type == "violation"
        assert "task:C" in record.tags
        assert "decision:Review Required" in record.tags
