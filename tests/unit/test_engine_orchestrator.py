"""GovernanceEngine 集成测试。"""

from __future__ import annotations

from pathlib import Path

from core.engine.orchestrator import GovernanceEngine
from core.governance.models import Condition, GovernanceRule
from stores.file.evidence.store import FileEvidenceStore
from stores.file.memory.store import FileMemoryStore
from stores.protocols import GateResult


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

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


def _make_engine(tmp_path: Path, rules: list[GovernanceRule] | None = None) -> GovernanceEngine:
    if rules is None:
        rules = [_make_block_rule()]
    return GovernanceEngine(
        rules=rules,
        evidence_store=FileEvidenceStore(tmp_path / "evidence"),
        memory_store=FileMemoryStore(tmp_path / "memory"),
    )


# ---------------------------------------------------------------------------
# Block 场景
# ---------------------------------------------------------------------------

class TestEngineBlockScenario:
    def test_block_decision(self, tmp_path):
        """assignee == reviewer → 阻断。"""
        engine = _make_engine(tmp_path)
        result = engine.process_event({
            "type": "output_intercept",
            "session_id": "sess-block",
            "assignee": "developer",
            "reviewer": "developer",
            "payload": {"output": "generated code"},
        })

        assert result.decision == "Block"
        assert len(result.matched_rules) == 1
        assert result.matched_rules[0] == "rule-reviewer-must-differ"
        assert len(result.evidence_ids) > 0

    def test_block_generates_evidence(self, tmp_path):
        engine = _make_engine(tmp_path)
        result = engine.process_event({
            "type": "output_intercept",
            "session_id": "sess-block-ev",
            "assignee": "alice",
            "reviewer": "alice",
            "payload": {},
        })

        store = FileEvidenceStore(tmp_path / "evidence")
        ev = store.get(result.evidence_ids[0])
        assert ev is not None
        assert ev.type == "block"
        assert ev.confidence == 1.0

    def test_block_has_suggestions(self, tmp_path):
        engine = _make_engine(tmp_path)
        result = engine.process_event({
            "type": "output_intercept",
            "session_id": "sess-block-sug",
            "assignee": "bob",
            "reviewer": "bob",
            "payload": {},
        })

        assert len(result.suggestions) > 0
        assert "阻断" in result.suggestions[0]


# ---------------------------------------------------------------------------
# Allow 场景
# ---------------------------------------------------------------------------

class TestEngineAllowScenario:
    def test_allow_decision(self, tmp_path):
        """assignee != reviewer → 放行。"""
        engine = _make_engine(tmp_path)
        result = engine.process_event({
            "type": "output_intercept",
            "session_id": "sess-allow",
            "assignee": "developer",
            "reviewer": "reviewer",
            "payload": {"output": "safe code"},
        })

        assert result.decision == "Allow"
        assert result.matched_rules == []
        assert result.evidence_ids == []

    def test_allow_has_no_suggestions(self, tmp_path):
        engine = _make_engine(tmp_path)
        result = engine.process_event({
            "type": "output_intercept",
            "session_id": "sess-allow-sug",
            "assignee": "dev",
            "reviewer": "rev",
            "payload": {},
        })

        assert result.suggestions == []


# ---------------------------------------------------------------------------
# 无规则场景
# ---------------------------------------------------------------------------

class TestEngineNoRules:
    def test_empty_rules_always_allow(self, tmp_path):
        engine = _make_engine(tmp_path, rules=[])
        result = engine.process_event({
            "type": "any_event",
            "session_id": "sess-empty",
            "payload": {},
        })

        assert result.decision == "Allow"
        assert result.matched_rules == []


# ---------------------------------------------------------------------------
# 多规则场景
# ---------------------------------------------------------------------------

class TestEngineMultipleRules:
    def test_highest_severity_wins(self, tmp_path):
        rules = [
            GovernanceRule(
                id="r-review",
                task_type="C",
                description="需要审查",
                conditions=[Condition(field="risk", op="==", value="high")],
                severity="review",
                on_hit="Review Required",
            ),
            GovernanceRule(
                id="r-block",
                task_type="C",
                description="阻断规则",
                conditions=[Condition(field="risk", op="==", value="high")],
                severity="block",
                on_hit="Block",
            ),
        ]
        engine = _make_engine(tmp_path, rules=rules)
        result = engine.process_event({
            "type": "output_intercept",
            "session_id": "sess-multi",
            "risk": "high",
            "payload": {},
        })

        # block severity > review → decision should be Block
        assert result.decision == "Block"
        assert len(result.matched_rules) == 2
