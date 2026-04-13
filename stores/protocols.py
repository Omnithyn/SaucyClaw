"""SaucyClaw 协议抽象层。

定义三域交互的最小接口契约。
"""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class SessionContext:
    """标准化会话上下文。"""
    session_id: str
    source: str
    metadata: dict


@dataclass(frozen=True)
class NormalizedEvent:
    """标准化事件结构。"""
    id: str
    event_type: str
    source: str
    session_id: str
    timestamp: str
    payload: dict


@dataclass(frozen=True)
class Evidence:
    """结构化证据对象。"""
    id: str
    type: str
    assertion: str
    source_ref: str
    timestamp: str
    confidence: float  # 只允许 1.0, 0.5, 0.0
    freshness: str | None = None
    verification_status: str | None = None
    applicable_scope: dict | None = None
    contradicted_by: list[str] | None = None
    governance_version: str | None = None


@dataclass(frozen=True)
class MemoryRecord:
    """记忆记录对象。"""
    id: str
    type: str
    summary: str
    tags: list[str]
    source_evidences: list[str]
    created_at: str
    trend: str = "stable"


@dataclass(frozen=True)
class GateResult:
    """治理放行结果。"""
    decision: str  # Allow, Review Required, Block, Escalate
    reason: str
    matched_rules: list[str]
    evidence_ids: list[str]
    suggestions: list[str]


class HostAdapter(Protocol):
    """宿主接入接口。"""

    def connect(self, context: dict) -> SessionContext:
        """建立与宿主上下文的连接，返回标准化会话上下文。"""
        ...

    def collect_event(self, raw_event: dict) -> NormalizedEvent:
        """将宿主原始事件转换为平台标准事件。"""
        ...

    def intercept_output(self, result: dict) -> GateResult:
        """在宿主输出前执行拦截，返回放行结果。"""
        ...

    def write_back(self, gate_result: GateResult) -> None:
        """将放行结果或治理提示回写宿主。"""
        ...

    def get_capabilities(self) -> dict:
        """返回宿主暴露的能力集（hook 点、插件接口、上下文注入点等）。"""
        ...


class EvidenceStore(Protocol):
    """证据存储接口。"""

    def record(self, evidence: Evidence) -> str:
        """写入证据并返回 evidence_id。"""
        ...

    def batch_record(self, evidences: list[Evidence]) -> list[str]:
        """批量写入证据。"""
        ...

    def query(self, filters: dict) -> list[Evidence]:
        """按过滤条件查询证据。"""
        ...

    def get(self, evidence_id: str) -> Evidence | None:
        """按 ID 获取单条证据。"""
        ...


class MemoryStore(Protocol):
    """记忆存储接口。"""

    def write(self, record: MemoryRecord) -> str:
        """写入记忆记录。"""
        ...

    def search(self, query: dict, limit: int = 10) -> list[MemoryRecord]:
        """按标签/关键词/类型检索。"""
        ...

    def decay(self) -> None:
        """执行衰减策略，Phase 0-1 可为空实现。"""
        ...
