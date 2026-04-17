"""治理域数据模型。

定义角色、任务类型、治理规则、放行结果等核心数据结构。
Phase 0-1 只做 dataclass，不包含匹配逻辑。
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Condition:
    """单层简单条件表达式。

    仅支持 op: ==, !=, in, not_in, exists
    不支持 and/or 嵌套、嵌套对象路径、自定义表达式。
    """
    field: str
    op: str
    value: str | list[str] | None = None
    value_from: str | None = None


@dataclass(frozen=True)
class RoleDefinition:
    """智能体角色定义。"""
    id: str
    name: str
    description: str = ""
    capabilities: list[str] = field(default_factory=list)
    permissions: dict = field(default_factory=dict)
    handoff_to: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class TaskType:
    """任务类型定义。"""
    id: str
    name: str
    description: str
    required_roles: list[str] = field(default_factory=list)
    review_required: bool = False
    allowed_roles: list[str] = field(default_factory=list)
    blocking_rules: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class GovernanceRule:
    """治理规则定义。

    conditions 仅支持单层简单结构，不支持 and/or 嵌套。
    severity 只允许: info, warn, review, block
    on_hit 只允许: Allow, Review Required, Block, Escalate
    applies_when: 规则适用前提，Phase 1.3 与 conditions 一样，均为单层 AND-only 条件列表。
    """
    id: str
    task_type: str
    description: str
    conditions: list[Condition]
    severity: str
    on_hit: str
    applies_when: list[Condition] = field(default_factory=list)
    # Phase 1.7: 规则元数据
    category: str = ""  # separation_of_duties / routing / handoff / escalation
    source: str = ""    # 规则来源文档
    rationale: str = ""  # 规则理由
    risk_level: str = ""  # low / medium / high


@dataclass(frozen=True)
class ReviewPolicy:
    """审查策略定义。"""
    id: str
    task_types: list[str]
    reviewer_must_differ_from: list[str] = field(default_factory=list)
    min_reviewers: int = 1


@dataclass(frozen=True)
class EscalationPolicy:
    """升级策略定义。"""
    id: str
    trigger_conditions: list[str]
    escalate_to: str
    requires_evidence: bool = True
