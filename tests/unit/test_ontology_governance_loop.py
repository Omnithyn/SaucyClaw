"""测试本体 Governance Loop。

N2 — Ontology Governance Loop
验证 run_ontology_governance_loop 的完整流程。
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ontology.governance_loop import (  # noqa: E402
    run_ontology_governance_loop,
    run_minimal_ontology_governance,
    OntologyGovernanceResult,
)
from ontology.schema import PolicyBinding  # noqa: E402
from ontology.loader import load_default_ontology_schema  # noqa: E402


class TestRunOntologyGovernanceLoop:
    """测试 run_ontology_governance_loop。"""

    def test_governance_loop_mapping_only(self):
        """治理循环：仅映射阶段。"""
        ontology_schema = load_default_ontology_schema()

        raw_event = {
            "event": "pre_tool_use",
            "payload": {
                "tool_name": "Read",  # 不是 Write，不会建立事实
                "assignee": "CEO",
            },
        }

        result = run_ontology_governance_loop(raw_event, ontology_schema, [])

        assert isinstance(result, OntologyGovernanceResult)
        assert result.governance_status == "mapped"
        assert result.establishment_result is None
        assert result.judgment is None

    def test_governance_loop_with_fact_establishment(self):
        """治理循环：映射 + 建立事实。"""
        ontology_schema = load_default_ontology_schema()

        raw_event = {
            "event": "pre_tool_use",
            "payload": {
                "tool_name": "Write",  # Write → 建立 review-requirement
                "assignee": "CEO",
            },
        }

        result = run_ontology_governance_loop(raw_event, ontology_schema, [])

        assert result.governance_status == "established"
        assert result.establishment_result is not None
        assert result.establishment_result.fact_record.fact_type == "review-requirement"

    def test_governance_loop_with_policy_judgment(self):
        """治理循环：映射 + 建立事实 + 策略判断。"""
        ontology_schema = load_default_ontology_schema()

        # 创建 policy binding
        policy_binding = PolicyBinding(
            policy_id="policy-review-required",
            policy_name="Write 需要审查",
            binds_to_fact_type="review-requirement",
            ontology_condition="required == True",
            judgment_mode="ontology",
        )

        raw_event = {
            "event": "pre_tool_use",
            "payload": {
                "tool_name": "Write",
                "assignee": "CEO",
            },
        }

        result = run_ontology_governance_loop(
            raw_event, ontology_schema, [policy_binding]
        )

        assert result.governance_status == "judged"
        assert result.judgment is not None
        assert result.judgment.judgment_result in ["review", "pass"]

    def test_governance_loop_summary(self):
        """治理循环：验证 summary 输出。"""
        ontology_schema = load_default_ontology_schema()

        raw_event = {
            "event": "pre_tool_use",
            "payload": {
                "tool_name": "Write",
                "assignee": "CEO",
            },
        }

        result = run_ontology_governance_loop(raw_event, ontology_schema, [])

        assert "事件已映射" in result.summary
        assert "事实已建立" in result.summary


class TestRunMinimalOntologyGovernance:
    """测试 run_minimal_ontology_governance。"""

    def test_minimal_governance_with_write_event(self):
        """最小治理：Write 事件。"""
        raw_event = {
            "event": "pre_tool_use",
            "payload": {
                "tool_name": "Write",
                "assignee": "CEO",
            },
        }

        result = run_minimal_ontology_governance(raw_event)

        assert result.governance_status in ["mapped", "established"]
        assert result.mapping_result.event_instance.event_type == "tool-invocation"

    def test_minimal_governance_with_read_event(self):
        """最小治理：Read 事件（不建立事实）。"""
        raw_event = {
            "event": "pre_tool_use",
            "payload": {
                "tool_name": "Read",
                "assignee": "Reviewer",
            },
        }

        result = run_minimal_ontology_governance(raw_event)

        assert result.governance_status == "mapped"
        assert result.establishment_result is None

    def test_minimal_governance_with_policy_bindings(self):
        """最小治理：带策略绑定。"""
        policy_binding = PolicyBinding(
            policy_id="policy-001",
            policy_name="测试策略",
            binds_to_fact_type="review-requirement",
            ontology_condition="required == True",
        )

        raw_event = {
            "event": "pre_tool_use",
            "payload": {
                "tool_name": "Write",
                "assignee": "CEO",
            },
        }

        result = run_minimal_ontology_governance(raw_event, [policy_binding])

        assert result.judgment is not None
