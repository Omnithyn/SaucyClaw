"""事件标准化器。

将宿主平台原始事件转换为 NormalizedEvent。
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from stores.protocols import NormalizedEvent


class EventNormalizer:
    """将原始事件 dict 转为标准化事件。

    支持的原始事件格式：
    - 显式字段：raw_event 包含 event_type/source/session_id/payload 等键
    - 极简格式：只包含 type 和 payload，其他字段自动生成
    """

    def normalize(self, raw_event: dict) -> NormalizedEvent:
        """转换原始事件为标准化事件。

        Args:
            raw_event: 宿主平台的原始事件 dict。

        Returns:
            NormalizedEvent 实例。
        """
        event_type = raw_event.get("event_type") or raw_event.get("type", "unknown")
        source = raw_event.get("source", "unknown")
        session_id = raw_event.get("session_id", "")
        timestamp = raw_event.get("timestamp") or _now_iso()

        # payload 提取：去掉元字段后剩余部分作为 payload
        _meta_keys = {"event_type", "type", "source", "session_id", "timestamp"}
        payload = {k: v for k, v in raw_event.items() if k not in _meta_keys}
        # 如果 raw_event 已有 payload 嵌套，优先使用
        if "payload" in raw_event:
            payload = raw_event["payload"]

        return NormalizedEvent(
            id=str(uuid.uuid4()),
            event_type=str(event_type),
            source=str(source),
            session_id=str(session_id),
            timestamp=timestamp,
            payload=payload,
        )

    def normalize_batch(self, raw_events: list[dict]) -> list[NormalizedEvent]:
        """批量转换原始事件。"""
        return [self.normalize(e) for e in raw_events]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
