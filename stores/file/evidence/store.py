"""基于 JSONL 文件的证据存储实现。"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from stores.protocols import Evidence


class FileEvidenceStore:
    """将证据以 JSONL 格式写入文件系统。

    存储布局: {base_dir}/{session_id}.jsonl
    每行一个证据的 JSON 序列化数据。
    """

    def __init__(self, base_dir: str | Path = "data/evidence") -> None:
        self._base = Path(base_dir)
        self._base.mkdir(parents=True, exist_ok=True)

    def _session_path(self, session_id: str) -> Path:
        return self._base / f"{session_id}.jsonl"

    def record(self, evidence: Evidence) -> str:
        """写入单条证据，返回 evidence_id。"""
        path = self._session_path(evidence.applicable_scope.get("session_id", "_default") if evidence.applicable_scope else "_default")
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(evidence), ensure_ascii=False) + "\n")
        return evidence.id

    def batch_record(self, evidences: list[Evidence]) -> list[str]:
        """批量写入证据。"""
        ids = []
        for ev in evidences:
            ids.append(self.record(ev))
        return ids

    def query(self, filters: dict) -> list[Evidence]:
        """按过滤条件查询证据。

        支持的过滤键：
        - session_id: 匹配文件名
        - type: 匹配 evidence.type
        - confidence_gte: confidence >= 该值
        """
        session_id = filters.get("session_id")
        if session_id:
            paths = [self._session_path(session_id)]
        else:
            paths = list(self._base.glob("*.jsonl"))

        results: list[Evidence] = []
        for path in paths:
            for line in path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                ev = Evidence(**json.loads(line))
                if _matches_filter(ev, filters):
                    results.append(ev)
        return results

    def get(self, evidence_id: str) -> Evidence | None:
        """按 ID 获取单条证据（线性扫描）。"""
        for path in self._base.glob("*.jsonl"):
            for line in path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                data = json.loads(line)
                if data.get("id") == evidence_id:
                    return Evidence(**data)
        return None


def _matches_filter(evidence: Evidence, filters: dict) -> bool:
    """检查证据是否匹配所有过滤条件。"""
    ev_type = filters.get("type")
    if ev_type and evidence.type != ev_type:
        return False

    confidence_gte = filters.get("confidence_gte")
    if confidence_gte is not None and evidence.confidence < confidence_gte:
        return False

    return True
