"""记忆记录构造器。

根据治理决策结果生成 MemoryRecord，接入引擎主流程。
Phase 1.1：模板化 summary，不引入智能摘要。
"""

from __future__ import annotations

import uuid

from stores.protocols import MemoryRecord
from core.governance.models import GovernanceRule


def build_memory_record(
    decision: str,
    triggered: list[GovernanceRule],
    input_data: dict,
    source: str = "unknown",
) -> MemoryRecord:
    """构造一条记忆记录。

    类型规则：
    - 有触发的规则 → type="violation"
    - 无触发的规则 → type="pass"

    Summary 模板（按 decision 区分）：
    - Block: "{task_type} 类任务触发阻断：{rule_descriptions}"
    - Review Required: "{task_type} 类任务需要审查：{rule_descriptions}"
    - Escalate: "{task_type} 类任务触发升级：{rule_descriptions}"
    - Allow: "{task_type} 类任务通过治理检查：no rules triggered"

    Tags 集合：
    - task:<task_type>
    - decision:<decision>
    - source:<source>
    - 违规时附加: rule:<rule_id>（每条规则一条 tag）
    """
    task_type = input_data.get("task_type", "unknown")
    rec_type = "violation" if triggered else "pass"

    summary = _build_summary(decision, task_type, triggered)

    tags = [
        f"task:{task_type}",
        f"decision:{decision}",
        f"source:{source}",
    ]
    for rule in triggered:
        tags.append(f"rule:{rule.id}")

    return MemoryRecord(
        id=str(uuid.uuid4()),
        type=rec_type,
        summary=summary,
        tags=tags,
        source_evidences=[],
        created_at=_now_iso(),
        trend="stable",
    )


def _build_summary(
    decision: str, task_type: str, triggered: list[GovernanceRule]
) -> str:
    """根据决策类型生成 summary 模板。"""
    templates = {
        "Block": "{task} 类任务触发阻断：{desc}",
        "Review Required": "{task} 类任务需要审查：{desc}",
        "Escalate": "{task} 类任务触发升级：{desc}",
        "Allow": "{task} 类任务通过治理检查：no rules triggered",
    }
    template = templates.get(decision, "{task} 类任务治理决策：{desc}")
    if triggered:
        descriptions = ", ".join(r.description for r in triggered)
        return template.format(task=task_type, desc=descriptions)
    return template.format(task=task_type, desc="")


def _now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()
