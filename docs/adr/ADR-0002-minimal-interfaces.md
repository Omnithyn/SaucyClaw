# ADR-0002: 最小接口定义

> 日期：2026-04-12
> 状态：已接受

---

## 背景

Phase 0-1 需要打通三域（宿主执行域 → 治理域 → 证据域），
但不应在首轮就定义完整的 Provider 抽象森林。

## 决策

Phase 0-1 只定义三个最小抽象接口：

### HostAdapter

```python
class HostAdapter(Protocol):
    def connect(self, context: dict) -> "SessionContext": ...
    def collect_event(self, raw_event: dict) -> "NormalizedEvent": ...
    def intercept_output(self, result: dict) -> "GateResult": ...
    def write_back(self, gate_result: "GateResult") -> None: ...
    def get_capabilities(self) -> dict: ...
```

### EvidenceStore

```python
class EvidenceStore(Protocol):
    def record(self, evidence: "Evidence") -> str: ...
    def batch_record(self, evidences: list["Evidence"]) -> list[str]: ...
    def query(self, filters: dict) -> list["Evidence"]: ...
    def get(self, evidence_id: str) -> "Evidence | None": ...
```

### MemoryStore

```python
class MemoryStore(Protocol):
    def write(self, record: "MemoryRecord") -> str: ...
    def search(self, query: dict, limit: int = 10) -> list["MemoryRecord"]: ...
    def decay(self) -> None: ...
```

Phase 0-1 仅实现每个接口的单一默认实现：
- `OpenClawHostAdapter`
- `FileEvidenceStore`
- `FileMemoryStore`

## 取舍

### 选择 Protocol 的理由

1. Python 的 Protocol 提供结构化子类型检查，无需显式继承
2. 后续替换实现时接口签名不变
3. mypy 等工具可以静态检查接口合规性

### 只定义三个接口的理由

1. 三域之间的交互只需要这三个接口
2. 更多接口（GraphProvider、VectorProvider 等）是 Phase 2+ 的事
3. 避免"为抽象而抽象"的空接口森林

## 后果

- Protocol 定义放在 `stores/protocols.py` 中，不分散到各模块
- 接口签名已确定，后续实现不得增减方法
- 后续阶段新增 Provider 接口时，遵循同一模式

## 暂不做

- GraphProvider、VectorProvider、PolicyEngineProvider 等扩展接口
- Provider 注册表或工厂模式
- 接口版本化
