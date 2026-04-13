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
    session_id: str = "",
) -> MemoryRecord:
    """构造一条记忆记录。

    类型规则：
    - 有触发的规则 → type="violation"
    - 无触发的规则 → type="pass"

    Summary 模板：
    - 违规: "{task_type} 类任务触发阻断：{rule_descriptions}"
    - 放行: "{task_type} 类任务通过治理检查：no rules triggered"

    Tags 集合：
    - task:<task_type>
    - decision:<decision>
    - source:<source>
    - 违规时附加: rule:<rule_id>（每条规则一条 tag）
    """
    task_type = input_data.get("task_type", "unknown")
    rec_type = "violation" if triggered else "pass"

    if triggered:
        descriptions = ", ".join(r.description for r in triggered)
        summary = f"{task_type} 类任务触发阻断：{descriptions}"
    else:
        summary = f"{task_type} 类任务通过治理检查：no rules triggered"

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


def _now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()
