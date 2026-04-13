"""治理引擎：事件 → 规则匹配 → 证据生成 → 存储 的编排器。"""

from __future__ import annotations

from stores.protocols import (
    Evidence,
    EvidenceStore,
    GateResult,
    MemoryStore,
    NormalizedEvent,
)
from core.engine.memory_builder import build_memory_record
from core.events.normalizer import EventNormalizer
from core.evidence.generator import EvidenceGenerator, summarize_governance_action
from core.governance.matcher import match_rules
from core.governance.models import GovernanceRule


class GovernanceEngine:
    """治理引擎核心。

    编排流程：
    1. 接收原始事件 → 标准化
    2. 从标准化事件提取输入数据
    3. 匹配治理规则
    4. 生成证据
    5. 存储证据和记忆
    6. 返回 GateResult
    """

    def __init__(
        self,
        rules: list[GovernanceRule],
        evidence_store: EvidenceStore,
        memory_store: MemoryStore,
    ) -> None:
        self._rules = rules
        self._evidence_store = evidence_store
        self._memory_store = memory_store
        self._normalizer = EventNormalizer()
        self._generator = EvidenceGenerator()

    def process_event(self, raw_event: dict) -> GateResult:
        """处理单次原始事件，返回治理放行结果。

        流程：
        1. 标准化事件
        2. 提取评估输入
        3. 匹配规则
        4. 生成并存储证据（仅违规时）
        5. 决策
        6. 构建并写入记忆记录
        7. 返回 GateResult
        """
        # 1. 标准化
        event = self._normalizer.normalize(raw_event)

        # 2. 提取输入数据（payload + 元信息）
        input_data = self._extract_input(raw_event, event)

        # 3. 匹配规则
        triggered = match_rules(self._rules, input_data)

        # 4. 生成并存储证据（仅违规时）
        evidences: list[Evidence] = []
        if triggered:
            evidences = self._generator.generate_batch(triggered, event, input_data)
            self._evidence_store.batch_record(evidences)

        # 5. 决策
        decision, reason, matched_ids = summarize_governance_action(triggered)

        # 6. 构建并写入记忆记录
        source = input_data.get("source", event.source)
        memory_record = build_memory_record(
            decision=decision,
            triggered=triggered,
            input_data=input_data,
            source=source,
            session_id=event.session_id,
        )
        self._memory_store.write(memory_record)

        # 7. 建议（Phase 0-1: 基于决策类型生成简单建议）
        suggestions = self._generate_suggestions(decision, triggered)

        return GateResult(
            decision=decision,
            reason=reason,
            matched_rules=matched_ids,
            evidence_ids=[e.id for e in evidences],
            suggestions=suggestions,
        )

    def _extract_input(self, raw_event: dict, event: NormalizedEvent) -> dict:
        """从原始事件和标准化事件中提取规则评估输入。"""
        # 合并 payload 和顶层关键字段
        input_data = dict(event.payload)
        # 顶层关键字可覆盖 payload
        for key in ("assignee", "reviewer", "task_type", "session_id"):
            if key in raw_event:
                input_data[key] = raw_event[key]
        return input_data

    def _generate_suggestions(
        self, decision: str, triggered: list[GovernanceRule]
    ) -> list[str]:
        """根据决策类型生成简单建议。"""
        suggestions: list[str] = []
        if decision == "Block":
            suggestions.append("输出被阻断，请检查治理规则配置")
            for rule in triggered:
                if rule.severity == "block":
                    suggestions.append(f"阻断原因: {rule.description}")
        elif decision == "Review Required":
            suggestions.append("输出需要人工审查后放行")
        elif decision == "Escalate":
            suggestions.append("事件已升级到更高层级")
        return suggestions
