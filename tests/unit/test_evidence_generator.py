"""证据生成器测试。"""

from __future__ import annotations

import uuid

from core.evidence.generator import EvidenceGenerator, summarize_governance_action
from core.governance.models import Condition, GovernanceRule
from stores.protocols import NormalizedEvent


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_event(session_id: str = "sess-001") -> NormalizedEvent:
    return NormalizedEvent(
        id=str(uuid.uuid4()),
        event_type="output_intercept",
        source="openclaw",
        session_id=session_id,
        timestamp="2026-04-13T10:00:00Z",
        payload={"output": "test"},
    )


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


def _make_review_rule() -> GovernanceRule:
    return GovernanceRule(
        id="rule-review-needed",
        task_type="C",
        description="需要额外审查",
        conditions=[
            Condition(field="risk", op="==", value="high"),
        ],
        severity="review",
        on_hit="Review Required",
    )


def _make_allow_rule() -> GovernanceRule:
    return GovernanceRule(
        id="rule-allow",
        task_type="C",
        description="放行规则",
        conditions=[],
        severity="info",
        on_hit="Allow",
    )


# ---------------------------------------------------------------------------
# EvidenceGenerator 测试
# ---------------------------------------------------------------------------

class TestEvidenceGenerator:
    def test_block_evidence(self):
        rule = _make_block_rule()
        event = _make_event()
        generator = EvidenceGenerator()
        evidence = generator.generate(rule, event, {"assignee": "a", "reviewer": "a"})

        assert evidence.type == "block"
        assert evidence.confidence == 1.0
        assert evidence.source_ref == event.id
        assert rule.id in evidence.assertion
        assert evidence.applicable_scope == {"session_id": event.session_id}
        assert evidence.governance_version == "C"

    def test_review_evidence(self):
        rule = _make_review_rule()
        event = _make_event("sess-review")
        generator = EvidenceGenerator()
        evidence = generator.generate(rule, event, {"risk": "high"})

        assert evidence.type == "review"
        assert evidence.confidence == 0.5

    def test_allow_evidence(self):
        rule = _make_allow_rule()
        event = _make_event()
        generator = EvidenceGenerator()
        evidence = generator.generate(rule, event, {})

        assert evidence.type == "allowance"
        assert evidence.confidence == 1.0

    def test_unknown_on_hit_defaults(self):
        rule = GovernanceRule(
            id="unknown",
            task_type="C",
            description="",
            conditions=[],
            severity="info",
            on_hit="Unknown Action",
        )
        event = _make_event()
        generator = EvidenceGenerator()
        evidence = generator.generate(rule, event, {})

        assert evidence.type == "observation"
        assert evidence.confidence == 0.0

    def test_batch_generate(self):
        rules = [_make_block_rule(), _make_review_rule()]
        event = _make_event()
        generator = EvidenceGenerator()
        evidences = generator.generate_batch(rules, event, {})

        assert len(evidences) == 2
        assert evidences[0].type == "block"
        assert evidences[1].type == "review"

    def test_unique_ids_per_evidence(self):
        rule = _make_block_rule()
        event = _make_event()
        generator = EvidenceGenerator()
        ids = {generator.generate(rule, event, {}).id for _ in range(5)}
        assert len(ids) == 5


# ---------------------------------------------------------------------------
# summarize_governance_action 测试
# ---------------------------------------------------------------------------

class TestSummarizeGovernanceAction:
    def test_no_rules_returns_allow(self):
        decision, reason, matched = summarize_governance_action([])
        assert decision == "Allow"
        assert matched == []

    def test_single_block_rule(self):
        rules = [_make_block_rule()]
        decision, reason, matched = summarize_governance_action(rules)
        assert decision == "Block"
        assert len(matched) == 1

    def test_highest_severity_wins(self):
        """block 应优于 review 被选为决策。"""
        rules = [_make_review_rule(), _make_block_rule()]
        decision, reason, matched = summarize_governance_action(rules)
        assert decision == "Block"
        assert len(matched) == 2

    def test_multiple_rules_same_severity(self):
        rules = [_make_block_rule(), _make_block_rule()]
        decision, reason, matched = summarize_governance_action(rules)
        assert decision == "Block"
        assert len(matched) == 2

    def test_review_only(self):
        rules = [_make_review_rule()]
        decision, reason, matched = summarize_governance_action(rules)
        assert decision == "Review Required"
