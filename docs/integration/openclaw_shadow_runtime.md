# OpenClaw Shadow Runtime 宿主接入说明

> M1 — 宿主接入可交付包
> 当前状态：基于 mock adapter 的最小闭环，尚未接入真实 OpenClaw hook

---

## 1. 适用范围

本文档描述如何使用 SaucyClaw 的 OpenClaw 外围接入包，在当前阶段（基于 mock adapter）构建完整的治理决策链路。

**适合场景：**
- 调试 SaucyClaw 治理内核
- 验证规则集和治理语义
- 演示治理能力
- 为后续接入真实 OpenClaw 或其他 runtime 准备模板

**不适合场景：**
- 生产环境真实宿主接入（需等待真实 hook 接入）
- 平台管理面操作
- 大规模并发治理

---

## 2. 当前能力边界

外围接入包包含以下模块（全部位于 `adapters/openclaw/`）：

| 模块 | 文件 | 职责 |
|------|------|------|
| **Adapter** | `adapter.py` | 宿主适配器 mock，模拟 connect / collect / write_back |
| **Explain Bridge** | `explain_bridge.py` | 解释桥接器，将 GateResult 增强为 AdapterExplainOutput |
| **Shadow Runtime** | `shadow_runtime.py` | 外围接入模板，封装 engine → bridge → adapter 的标准流程 |
| **Runtime Trace** | `runtime_trace.py` | 运行链路最小摘要，提取 decision / matched_rules / severity 等 |
| **Debug Render** | `debug_render.py` | 调试输出渲染器，将运行结果转为稳定可读文本 |
| **Hook Contract** | `hook_contract.py` | 外部接入契约 Protocol，为未来真实集成预留接口 |

### 数据流

```
raw_event
    ↓
ShadowRuntime.process_and_write()
    ├── GovernanceEngine.process_event() → GateResult
    ├── ExplainBridge.enhance_output()  → AdapterExplainOutput（可选）
    └── OpenClawHostAdapter.write_back()
    ↓
ShadowRunResult(gate_result, enhanced_output)
    ↓
build_runtime_trace() → RuntimeTrace
    ↓
render_shadow_run()   → 调试文本
```

---

## 3. 接入步骤

### 3.1 加载治理规则

```python
from core.governance.loader import load_governance

schemas_dir = "schemas/governance"  # 包含 roles.yaml, task_types.yaml, rules.yaml
schema = load_governance(schemas_dir)
```

### 3.2 创建存储

```python
from stores.file.evidence.store import FileEvidenceStore
from stores.file.memory.store import FileMemoryStore

evidence_store = FileEvidenceStore(base_dir="./evidence")
memory_store = FileMemoryStore(base_dir="./memory")
```

### 3.3 创建治理引擎

```python
from core.engine.orchestrator import GovernanceEngine

engine = GovernanceEngine(
    rules=schema.rules,
    evidence_store=evidence_store,
    memory_store=memory_store,
)
```

### 3.4 创建宿主适配器

```python
from adapters.openclaw.adapter import OpenClawHostAdapter

adapter = OpenClawHostAdapter()  # mock 实现
```

### 3.5 创建解释桥接器

```python
from adapters.openclaw.explain_bridge import ExplainBridge

lookup = {r.id: r for r in schema.rules}
bridge = ExplainBridge(lookup, enable=True)  # enable=True 开启解释输出
```

### 3.6 创建 Shadow Runtime

```python
from adapters.openclaw.shadow_runtime import ShadowRuntime

runtime = ShadowRuntime(
    engine=engine,
    adapter=adapter,
    explain_bridge=bridge,  # 可选，传 None 则无解释输出
)
```

### 3.7 执行治理

```python
raw_event = {
    "event_type": "task_assign",
    "assignee": "alice",
    "reviewer": "alice",  # 同一个人 → 触发 rule-reviewer-must-differ
    "task_type": "C",
    "conflict": False,
    "handoff": True,
}

result = runtime.process_and_write(raw_event)
```

### 3.8 构建运行摘要与调试输出

```python
from adapters.openclaw.runtime_trace import build_runtime_trace
from adapters.openclaw.debug_render import render_shadow_run

trace = build_runtime_trace(result, bridge=bridge)
print(render_shadow_run(result, trace))
```

---

## 4. 输出对象说明

### 4.1 ShadowRunResult

```python
@dataclass(frozen=True)
class ShadowRunResult:
    gate_result: GateResult              # 原始治理决策
    enhanced_output: AdapterExplainOutput | None  # 增强输出（bridge 开启时）
```

### 4.2 GateResult

| 字段 | 类型 | 说明 |
|------|------|------|
| `decision` | str | Block / Allow / Escalate / Review Required |
| `matched_rules` | list[str] | 触发规则 ID 列表 |
| `reason` | str | 决策原因 |
| `suggestions` | list[str] | 建议列表 |
| `evidence_ids` | list[str] | 证据 ID 列表 |

### 4.3 AdapterExplainOutput

```python
@dataclass(frozen=True)
class AdapterExplainOutput:
    decision: str
    matched_rules: list[str]
    explanation_bundle: ExplanationBundle | None
    raw_result: GateResult
```

### 4.4 RuntimeTrace

```python
@dataclass(frozen=True)
class RuntimeTrace:
    decision: str           # Block / Allow / Escalate
    matched_rules: list[str]
    shadow_mode: bool       # bridge 侧状态
    has_explanation: bool   # 结果侧是否真有 explanation
    severity: str | None    # 最高风险级别（high / medium / low / None）
    summary: str            # 一行可读摘要
```

> **注意：** `severity` 表达的是最高风险级别（从 `explanation_bundle.explanations[*].risk_level` 推导），
> 不是 `GovernanceRule.severity` 原始字段。

---

## 5. Shadow Mode 说明

### 开启方式

```python
bridge = ExplainBridge(lookup, enable=True)  # 构造时开启
# 或运行时切换
bridge.enable_shadow_mode()
bridge.disable_shadow_mode()
```

### 开启 vs 关闭

| 状态 | `shadow_mode` | `has_explanation` | 说明 |
|------|---------------|-------------------|------|
| bridge=None | False | False | 无桥接器 |
| bridge 关闭 | False | False | 有桥接器但未开启 |
| bridge 开启 | True | True（有规则时） | 有解释输出 |

- `shadow_mode`：bridge 侧状态，表示桥接器是否处于开启
- `has_explanation`：结果侧状态，表示本次运行是否真的生成了 explanation
- 两者不等价：bridge 开启但无规则触发时，`shadow_mode=True` 但 `has_explanation=False`

### 不改变核心契约

- `adapter.write_back()` 仍接受 `GateResult`，签名不变
- `GateResult` 结构不变
- Explain Bridge 只是额外生成一个解释输出包

---

## 6. Hook Contract 说明

`adapters/openclaw/hook_contract.py` 定义了 4 个 Protocol，为未来真实集成预留接口：

| Protocol | 对应实现 | 职责 |
|----------|----------|------|
| `HostOutputSink` | `OpenClawHostAdapter` | 宿主输出回写 |
| `ExplainPayload` | `ExplainBridge` | 解释输出增强 |
| `GovernanceProcessor` | `GovernanceEngine` | 治理事件处理 |
| `ShadowOutput` | `ShadowRuntime` | Shadow 运行入口 |

当前实现已通过这些 Protocol 的运行时一致性验证（见 `tests/unit/test_hook_contract_conformance.py`）。

---

## 7. 当前限制

### 仍未接入真实 OpenClaw hook

- `OpenClawHostAdapter` 是 mock 实现
- `write_back()` 仅记录到内部日志
- `intercept_output()` 为占位实现
- 真实 OpenClaw hook 接入需后续完成

### 不提供的能力

- 日志框架 / tracing / span 系统
- 平台管理面（规则管理、版本管理、用户管理）
- 规则语法扩展（当前仅支持 AND-only 条件匹配）
- UI / 管理台
- 多租户 / 并发控制

---

## 8. 快速验证

```bash
# 运行 example
python -m examples.openclaw_shadow_runtime_example

# 运行接入包相关测试
pytest tests/unit/test_shadow_runtime.py -v
pytest tests/unit/test_hook_contract.py -v
pytest tests/unit/test_hook_contract_conformance.py -v
pytest tests/unit/test_runtime_trace.py -v
pytest tests/unit/test_debug_render.py -v
pytest tests/integration/test_openclaw_adapter.py -v
```

---

## 9. 从包导入（便捷方式）

```python
from adapters.openclaw import (
    OpenClawHostAdapter,
    ExplainBridge,
    AdapterExplainOutput,
    ShadowRuntime,
    ShadowRunResult,
    RuntimeTrace,
    build_runtime_trace,
    render_shadow_run,
    HostOutputSink,
    ExplainPayload,
    GovernanceProcessor,
    ShadowOutput,
)
```
