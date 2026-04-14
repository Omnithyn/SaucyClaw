# Smoke 验证清单

> M2 — 真实宿主接入准备包
> 用途：快速验证当前接入包是否可用

---

## 一键验证

```bash
# 运行完整 example（Block + Allow 场景）
python -m examples.openclaw_shadow_runtime_example
```

### 成功标志

- 输出末尾出现 `演示完成`
- Block 场景输出包含 `决策: Block` + `风险: high`
- Allow 场景输出包含 `决策: Allow` + `未触发治理规则`

---

## 区分 bridge 开启 / 关闭

### Bridge 开启（有解释输出）

```python
bridge = ExplainBridge(lookup, enable=True)
runtime = ShadowRuntime(engine=engine, adapter=adapter, explain_bridge=bridge)
```

**验证方法：** 运行 example 后，输出中应包含：
- `Shadow Mode: ON`
- `解释: 有`
- `── Explanation ──` 区块（Block 场景下有规则解释项）

### Bridge 关闭（无解释输出）

```python
bridge = ExplainBridge(lookup, enable=False)
# 或
runtime = ShadowRuntime(engine=engine, adapter=adapter, explain_bridge=None)
```

**验证方法：** 输出中应包含：
- `Shadow Mode: OFF`
- `解释: 无`
- `── Explanation ──` 区块显示 `explanation-unavailable`

---

## 验证 Block / Allow 两条路径

### Block 路径

```bash
python -c "
import yaml, tempfile
from pathlib import Path
from core.governance.loader import load_governance
from core.engine.orchestrator import GovernanceEngine
from adapters.openclaw.adapter import OpenClawHostAdapter
from adapters.openclaw.explain_bridge import ExplainBridge
from adapters.openclaw.shadow_runtime import ShadowRuntime
from adapters.openclaw.runtime_trace import build_runtime_trace
from stores.file.evidence.store import FileEvidenceStore
from stores.file.memory.store import FileMemoryStore

schema = load_governance('schemas/governance')
lookup = {r.id: r for r in schema.rules}
bridge = ExplainBridge(lookup, enable=True)

with tempfile.TemporaryDirectory() as tmp:
    engine = GovernanceEngine(
        rules=schema.rules,
        evidence_store=FileEvidenceStore(base_dir=f'{tmp}/e'),
        memory_store=FileMemoryStore(base_dir=f'{tmp}/m'),
    )
    runtime = ShadowRuntime(engine=engine, adapter=OpenClawHostAdapter(), explain_bridge=bridge)

    with open('tests/fixtures/block_input.yaml') as f:
        event = yaml.safe_load(f)
    result = runtime.process_and_write(event)
    trace = build_runtime_trace(result, bridge=bridge)

    assert trace.decision == 'Block', f'Expected Block, got {trace.decision}'
    assert len(trace.matched_rules) > 0, 'Expected matched rules'
    assert trace.severity == 'high', f'Expected high severity, got {trace.severity}'
    assert trace.shadow_mode is True
    assert trace.has_explanation is True
    print('Block path: OK')
"
```

### Allow 路径

```bash
python -c "
import yaml, tempfile
from pathlib import Path
from core.governance.loader import load_governance
from core.engine.orchestrator import GovernanceEngine
from adapters.openclaw.adapter import OpenClawHostAdapter
from adapters.openclaw.explain_bridge import ExplainBridge
from adapters.openclaw.shadow_runtime import ShadowRuntime
from adapters.openclaw.runtime_trace import build_runtime_trace
from stores.file.evidence.store import FileEvidenceStore
from stores.file.memory.store import FileMemoryStore

schema = load_governance('schemas/governance')
lookup = {r.id: r for r in schema.rules}
bridge = ExplainBridge(lookup, enable=True)

with tempfile.TemporaryDirectory() as tmp:
    engine = GovernanceEngine(
        rules=schema.rules,
        evidence_store=FileEvidenceStore(base_dir=f'{tmp}/e'),
        memory_store=FileMemoryStore(base_dir=f'{tmp}/m'),
    )
    runtime = ShadowRuntime(engine=engine, adapter=OpenClawHostAdapter(), explain_bridge=bridge)

    with open('tests/fixtures/allow_input.yaml') as f:
        event = yaml.safe_load(f)
    result = runtime.process_and_write(event)
    trace = build_runtime_trace(result, bridge=bridge)

    assert trace.decision == 'Allow', f'Expected Allow, got {trace.decision}'
    assert trace.matched_rules == [], f'Expected no matched rules, got {trace.matched_rules}'
    assert trace.severity is None, f'Expected None severity, got {trace.severity}'
    assert trace.shadow_mode is True
    assert trace.has_explanation is True
    print('Allow path: OK')
"
```

---

## 测试验证

```bash
# 接入包核心测试（57 个）
pytest tests/unit/test_shadow_runtime.py \
       tests/unit/test_hook_contract.py \
       tests/unit/test_hook_contract_conformance.py \
       tests/unit/test_runtime_trace.py \
       tests/unit/test_debug_render.py \
       tests/unit/test_explain_bridge.py \
       tests/integration/test_openclaw_adapter.py -v

# 全部测试（201 个）
pytest tests/ -v
```

---

## 快速检查表

| 检查项 | 命令 | 预期结果 |
|--------|------|----------|
| Example 可运行 | `python -m examples.openclaw_shadow_runtime_example` | 输出演示完成 |
| Block 路径 | 见上方 python 脚本 | `Block path: OK` |
| Allow 路径 | 见上方 python 脚本 | `Allow path: OK` |
| Bridge 开启 | Example 输出 | `Shadow Mode: ON` |
| Bridge 关闭 | 改 enable=False 运行 | `Shadow Mode: OFF` |
| 核心测试 | `pytest ... -v` | 57 passed |
| 全部测试 | `pytest tests/ -v` | 201 passed |
