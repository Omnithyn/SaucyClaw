# Phase 2.1 — 真实 OpenClaw Hook 勘测与接点确认

> 创建时间：2026-04-14
> 状态：勘测完成
>
> **勘测目标**：确认真实 OpenClaw hook 接入点，明确接在哪里、以什么形态接、会不会破坏现有契约、最小侵入路径是什么
>
> **关键原则**：本阶段不写大量代码，只做勘测与契约确认。**不基于 mock adapter 的局部现实做出真实集成决策**。

---

## 一、当前仓库状态

### 已实现模块

| 模块 | 文件 | 状态 |
|------|------|------|
| Governance Engine | `core/engine/orchestrator.py` | ✅ 已完成 |
| Governance Matcher | `core/governance/matcher.py` | ✅ 已完成 |
| Rule Metadata | `core/governance/models.py` | ✅ 已完成 |
| Explanation Helper | `core/governance/explainer.py` | ✅ 已完成 |
| Explanation Bundle | `core/governance/explainer_bundle.py` | ✅ 已完成 |
| Adapter Bridge | `adapters/openclaw/explain_bridge.py` | ✅ 已完成 (Phase 2.0) |
| Mock Adapter | `adapters/openclaw/adapter.py` | ✅ 已完成 |

### 当前输出链路

```python
# 1. 引擎处理
result: GateResult = engine.process_event(raw_event)

# 2. Adapter 回写
adapter.write_back(result)  # 接受 GateResult，无返回值

# 3. 内部日志
adapter.write_back_log  # 存储 GateResult 列表（通过 @property 暴露只读副本）
```

### 当前 Mock Adapter 特性

- `write_back(result)` 只把 `GateResult` 记进 `_write_back_log`
- `write_back()` 没有返回值
- `write_back_log` 通过只读副本暴露
- `intercept_output()` 还是占位实现
- `get_capabilities()` 返回的 hook 列表是模拟数据

---

## 二、可能的 Hook 点分析

### Hook 点 A：`adapter.write_back()`（mock adapter 候选接点）

**位置**：`adapters/openclaw/adapter.py:77-79`

```python
def write_back(self, gate_result: GateResult) -> None:
    """记录 GateResult 到内部日志。"""
    self._write_back_log.append(gate_result)
```

**优势**：
- ✅ 在当前 mock adapter 中最接近输出边界的点
- ✅ 只需在 append 前调用 `bridge.enhance_output()`
- ✅ 不改变方法签名
- ✅ 可选择性记录增强信息

**限制**：
- ⚠️ **目前尚无证据证明真实 OpenClaw 也存在这一接点**
- ⚠️ 如果真实运行时没有，需要额外适配层
- ⚠️ 不能将其表述为真实集成主推荐

**最小侵入方案**（仅作为 mock 环境参考）：

```python
def write_back(self, gate_result: GateResult) -> None:
    """记录 GateResult 到内部日志。"""
    self._write_back_log.append(gate_result)

    # Phase 2.1+: Shadow Mode explain（可选）
    if self._explain_bridge and self._explain_bridge.enabled:
        enhanced = self._explain_bridge.enhance_output(gate_result)
        self._write_back_enhanced_log.append(enhanced)
```

---

### Hook 点 B：`adapter.intercept_output()`（不推荐）

**位置**：`adapters/openclaw/adapter.py:63-75`

**现状**：当前是占位实现，实际逻辑在 `engine.process_event`

**风险**：
- ⚠️ 改这里可能需要重构输出链路
- ⚠️ 不确定真实 OpenClaw 是否有此方法
- ⚠️ 当前占位实现，不建议作为首选

---

### Hook 点 C：Engine 返回后（外围包装）— 当前已验证可行路径

**位置**：调用方代码中

```python
# 调用方代码
result = engine.process_event(raw_event)
enhanced = bridge.enhance_output(result)  # 外围包装

adapter.write_back(result)  # 仍保持原契约
```

**优势**：
- ✅ **已被现有代码路径验证**
- ✅ **零侵入**（adapter 完全不修改）
- ✅ **不依赖真实 OpenClaw hook 机制**
- ✅ **与 Phase 2.0 Shadow Mode 契约完全一致**

**风险**：
- ⚠️ 不是真正的 hook，依赖调用方主动包装
- ⚠️ 无法保证所有调用点都包装

---

## 三、接点对比（修正后）

| 接点 | 当前可执行性 | 真实宿主适用性 | 备注 |
|------|------------|--------------|------|
| Hook C 外围包装 | 高 | 高 | **当前已验证路径** |
| Hook A write_back | 中 | 待确认 | **mock adapter 候选注入点** |
| Hook B intercept_output | 低 | 待确认 | 当前占位实现，不建议作为首选 |

**关键说明**：

- **当前可执行性**：基于当前 mock adapter 和已实现的 ExplainBridge 能否立即执行
- **真实宿主适用性**：是否适用于真实 OpenClaw 运行时（需后续确认）

---

## 四、勘测结论

### 当前阶段推荐方案

**Hook C：外围包装**

**理由**：

1. **已被现有代码路径验证**：`ExplainBridge` 作为独立桥接器已实现，不改变 adapter 契约
2. **零侵入**：adapter 完全不修改，调用方显式调用 `bridge.enhance_output()`
3. **最大灵活性**：在真实 OpenClaw hook 机制确认前，保持 adapter 纯净
4. **完全兼容**：`adapter.write_back(result)` 仍接受原始 `GateResult`，无任何变更

**实现示例**：

```python
# 外围包装（推荐）
result = engine.process_event(raw_event)
enhanced = bridge.enhance_output(result)  # 调用方显式增强

adapter.write_back(result)  # adapter 完全不变

# 记录增强信息到日志
_logger.info("增强输出: %s", enhanced.explanation_bundle.readable_summary)
```

---

### Mock Adapter 候选接点

**Hook A：`adapter.write_back()`**

**定位**：**mock adapter 上的候选注入点**，**未来真实宿主若存在等价边界，可参考**

**适用场景**：
- 真实 OpenClaw 有标准 hook 机制后
- 需要在 adapter 内部统一管理增强逻辑时

**限制**：
- **目前尚无证据证明真实 OpenClaw 也存在这一接点**
- **不能将其表述为真实集成主推荐**

---

## 五、关键验证结果

### 1. 仓库内 `write_back()` 使用情况（已验证）

**勘测结果**：
- ✅ 当前仓库内有 **2 处调用点**，全部在测试文件中：
  - `tests/integration/test_openclaw_adapter.py:81` — Block 场景
  - `tests/integration/test_openclaw_adapter.py:127` — Allow 场景

**调用模式**：
```python
adapter = OpenClawHostAdapter()
adapter.write_back(result)  # 直接传入 GateResult
assert len(adapter.write_back_log) == 1  # 只验证日志长度
assert adapter.write_back_log[0].decision == "Block"  # 只验证决策结果
```

**结论**：
- ✅ 调用方**不依赖** `_write_back_log` 的内部实现细节
- ✅ 调用方**只关心** `write_back_log` 属性（通过 `@property` 暴露的只读副本）
- ✅ 可以安全地在 `_write_back_log.append()` 后增加额外逻辑

---

### 2. 与真实 OpenClaw 的兼容性（待确认）

**问题**：真实 OpenClaw 是否有 `write_back()` 或类似的输出回调方法？

**当前状态**：
- ⚠️ `OpenClawHostAdapter` 是 Phase 0-1 的 mock，**尚未确认**真实 OpenClaw 的 hook 机制
- ⚠️ `get_capabilities()` 返回的 hook 列表 `["output_intercept", "task_assign", "review_request"]` 是模拟数据

**建议**：
- 后续需查阅真实 OpenClaw 文档，确认是否有标准的"输出回调"或"写回"方法
- 如果真实 OpenClaw 有标准 hook，优先对接标准接口
- 如果没有，当前 `write_back()` 设计可作为适配层

---

### 3. 最小侵入路径决策

**问题**：是否需要在 adapter 内部持有 `ExplainBridge`，还是外围包装更合适？

**推荐方案**：**外围包装（Hook C）优先，adapter 内部集成（Hook A）备选**

**理由**：
1. **真实 hook 尚未确认**：在确认真实 OpenClaw 的标准 hook 机制前，保持 adapter 纯净更稳妥
2. **外围包装完全不侵入**：调用方代码显式调用 `bridge.enhance_output()`，adapter 零修改
3. **adapter 内部集成需权衡**：如果真实 OpenClaw 有标准 hook，再考虑在 `write_back()` 内部集成

---

## 六、Phase 2.1 产物

### 1. 勘测文档（已完成）

- 本文档（已完成勘测与结论修正）

### 2. 验证测试（建议添加）

**目的**：验证 `write_back()` 的向后兼容性，为未来可能的内部集成做准备

**建议测试用例**：
```python
def test_adapter_write_back_backwards_compatible():
    """验证 write_back() 签名不变，调用方代码无需修改。"""
    adapter = OpenClawHostAdapter()
    result = GateResult(
        decision="Block",
        reason="test",
        matched_rules=[],
        evidence_ids=[],
        suggestions=[],
    )

    # 原始调用方式仍然有效
    adapter.write_back(result)
    assert len(adapter.write_back_log) == 1
    assert adapter.write_back_log[0] == result

    # 调用方不依赖内部实现细节
    assert isinstance(adapter.write_back_log, list)
    assert hasattr(adapter, 'write_back_log')  # 通过 @property 暴露
```

---

### 3. Hook Contract 探针文件（可选，建议创建）

**文件路径**：`adapters/openclaw/hook_contract.py`

**目的**：定义预期的 hook 接口和数据流，便于未来对接真实 OpenClaw

**内容框架**：
```python
"""OpenClaw Hook 接口契约定义（探针文件）。

用于未来对接真实 OpenClaw 运行时的标准 hook 机制。
当前为文档性质，不参与实际运行。
"""

from typing import Protocol
from stores.protocols import GateResult
from adapters.openclaw.explain_bridge import AdapterExplainOutput


class OpenClawOutputHook(Protocol):
    """OpenClaw 输出回调协议。"""

    def on_output(self, result: GateResult) -> None:
        """输出拦截回调。

        真实 OpenClaw 运行时的标准 hook 点。
        """
        ...

    def on_explain(self, enhanced: AdapterExplainOutput) -> None:
        """解释输出回调（可选）。

        Shadow Mode 的增强解释输出。
        """
        ...
```

---

## 七、Phase 2.2 前置条件

在进入 Phase 2.2（真实 hook 集成）之前，必须完成以下前置条件：

### 必须确认的事项

- [ ] **真实 OpenClaw hook 位置已确认**
  - 是否存在类似 `write_back()` 的边界点
  - 输出回写的真实生命周期在哪里
  - 宿主是否有标准 output transformer / callback / middleware 机制

- [ ] **真实输出链路已确认**
  - 从 engine 处理完成到最终输出的完整路径
  - 是否允许在 adapter 内部持有额外 bridge 状态

- [ ] **Shadow Mode 接入不会破坏宿主契约**
  - 验证增强逻辑不会影响现有输出行为
  - 验证开关控制的有效性

### 如果没有标准 hook

**继续采用外围包装模式**，而不是强塞进 adapter 内部。

**理由**：
- 保持治理能力与 runtime 的解耦
- 避免围绕 mock adapter 内卷
- 为未来对接其他 runtime 保留灵活性

---

## 八、关键结论

### 当前阶段正式推荐

**Hook C：外围包装**

**原因**：
- 已被现有代码路径验证
- 零侵入
- 不依赖真实 OpenClaw hook 机制
- 与 Phase 2.0 Shadow Mode 契约完全一致

### Mock Adapter 候选接点

**Hook A：`write_back()`**

**定位**：
- mock adapter 上的候选注入点
- 未来真实宿主若存在等价边界，可参考
- **当前不能上升为真实集成主推荐**

### 风险点

- 需要确认真实 OpenClaw 的 hook 机制
- 当前阶段过早耦合可能带来维护成本
- 不能把 mock adapter 的局部现实当作真实集成依据

---

## 九、待办事项

- [x] 仓库内 `write_back()` 使用情况验证
- [ ] 确认真实 OpenClaw 的输出 hook 点
- [ ] 决定是否创建 Hook Contract 探针文件
- [ ] 准备 Phase 2.2 实现方案（基于外围包装）
- [ ] 验证 `write_back()` 修改的兼容性（如需）

---

> **勘测人**：core-engineer
> **勘测日期**：2026-04-14
> **勘测分支**：feat/phase0-1-commit1
> **勘测原则**：不基于 mock adapter 的局部现实做出真实集成决策
