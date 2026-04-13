"""基于 JSON 文件的记忆存储实现。"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from stores.protocols import MemoryRecord


class FileMemoryStore:
    """将记忆记录以 JSON 格式写入文件系统。

    存储布局: {base_dir}/{record_id}.json
    Phase 0-1: 每条记忆一个文件，search 为全量扫描。
    """

    def __init__(self, base_dir: str | Path = "data/memory") -> None:
        self._base = Path(base_dir)
        self._base.mkdir(parents=True, exist_ok=True)

    def write(self, record: MemoryRecord) -> str:
        """写入记忆记录，返回 record_id。"""
        path = self._base / f"{record.id}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(asdict(record), f, ensure_ascii=False, indent=2)
        return record.id

    def search(self, query: dict, limit: int = 10) -> list[MemoryRecord]:
        """按标签/类型检索记忆。

        支持的查询键：
        - tags: 匹配任一标签
        - type: 匹配 record.type
        """
        target_tags = query.get("tags", [])
        target_type = query.get("type")

        results: list[MemoryRecord] = []
        for path in self._base.glob("*.json"):
            data = json.loads(path.read_text(encoding="utf-8"))
            record = MemoryRecord(**data)

            if target_type and record.type != target_type:
                continue
            if target_tags and not any(t in record.tags for t in target_tags):
                continue

            results.append(record)
            if len(results) >= limit:
                break

        return results

    def decay(self) -> None:
        """执行衰减策略。

        Phase 0-1: 空实现。后续可根据 created_at 和 trend
        实现记录老化。
        """
        pass
