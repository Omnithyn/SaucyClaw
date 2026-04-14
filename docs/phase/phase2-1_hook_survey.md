# Phase 2.1 — 真实 OpenClaw Hook 勘测与接点确认

> 创建时间：2026-04-14
> 状态：勘测中

---

## 📋 勘测目标

确认真实 OpenClaw hook 接入点，明确：
- 接在哪里
- 以什么形态接
- 会不会破坏现有契约
- 最小侵入路径是什么

**本阶段不写大量代码，只做勘测与契约确认。**

---

## 🔍 当前仓库状态

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
adapter.write_back_log  # 存储 GateResult 列表
```

---

## 🎯 可能的 Hook 点

### Hook 点 A：`adapter.write_back()`（推荐 ⭐）

**位置**：`adapters/openclaw/adapter.py:77-79`

```python
def write_back(self, gate_result: GateResult) -> None:
    """记录 GateResult 到内部日志。"""
    self._write_back_log.append(gate_result)
```

**优势**：
- ✅ 当前最接近输出边界的点
- ✅ 只需在 append 前调用 `bridge.enhance_output()`
- ✅ 不改变方法签名
- ✅ 可选择性记录增强信息（如存到 `_write_back_enhanced_log`）

**风险**：
- ⚠️ 需要确认 OpenClaw 真实运行时是否也有 `write_back()` 方法
- ⚠️ 如果真实运行时没有，需要额外适配层

**最小侵入方案**：

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

### Hook 点 B：`adapter.intercept_output()`（备选）

**位置**：`adapters/openclaw/adapter.py:63-75`

```python
def intercept_output(self, result: dict) -> GateResult:
    """Phase 0-1: 占位实现。

    实际拦截逻辑由 GovernanceEngine.process_event 完成。
    此方法仅返回一个默认的 Allow 结果。
    """
    return GateResult(
        decision="Allow",
        reason="mock: 实际拦截由 GovernanceEngine 处理",
        matched_rules=[],
        evidence_ids=[],
        suggestions=[],
    )
```

**优势**：
- ✅ 方法名直接表明"拦截输出"的意图
- ✅ 可以直接返回增强后的结构

**风险**：
- ⚠️ 当前是占位实现，实际逻辑在 `engine.process_event`
- ⚠️ 改这里可能需要重构输出链路
- ⚠️ 不确定真实 OpenClaw 是否有此方法

**最小侵入方案**：

```python
def intercept_output(self, result: dict) -> GateResult:
    # 实际逻辑仍由 engine 处理
    gate_result = self._engine.process_event(result)

    # Phase 2.1+: Shadow Mode explain（可选）
    if self._explain_bridge and self._explain_bridge.enabled:
        enhanced = self._explain_bridge.enhance_output(gate_result)
        # 记录到增强日志或返回增强结构
        return enhanced  # 需要调整返回类型

    return gate_result
```

---

### Hook 点 C：Engine 返回后（外围包装）

**位置**：调用方代码中

```python
# 调用方代码
result = engine.process_event(raw_event)
enhanced = bridge.enhance_output(result)  # 外围包装

adapter.write_back(result)  # 仍保持原契约
```

**优势**：
- ✅ 完全不修改 adapter
- ✅ 最小侵入
- ✅ 适合调试/日志场景

**风险**：
- ⚠️ 不是真正的 hook，依赖调用方主动包装
- ⚠️ 无法保证所有调用点都包装

---

## 📊 接点对比

| 接点 | 侵入程度 | 稳定性 | 与 Phase 2.0 契约匹配度 | 推荐度 |
|------|---------|--------|----------------------|--------|
| Hook A: `write_back()` | 低 | 高 | 高 | ⭐⭐⭐⭐⭐ |
| Hook B: `intercept_output()` | 中 | 中 | 中 | ⭐⭐⭐ |
| Hook C: 外围包装 | 最低 | 低 | 高 | ⭐⭐ |

---

## ✅ 推荐方案

### 主推荐：Hook A（`write_back()`）

**理由**：
1. **最小侵入**：只需在 append 前增加可选的增强逻辑
2. **保持契约**：方法签名不变，仍接受 `GateResult`
3. **Shadow Mode 友好**：通过开关控制是否生成增强信息
4. **与 Phase 2.0 一致**：`ExplainBridge` 已设计为不改变 adapter 行为

**实现路径**：

```python
# Phase 2.1: 在 adapter 中增加 explain_bridge 引用
class OpenClawHostAdapter:
    def __init__(self, explain_bridge: ExplainBridge | None = None) -> None:
        self._explain_bridge = explain_bridge
        self._write_back_log: list[GateResult] = []
        self._write_back_enhanced_log: list[AdapterExplainOutput] = []

    def write_back(self, gate_result: GateResult) -> None:
        self._write_back_log.append(gate_result)

        # Shadow Mode: 可选记录增强信息
        if self._explain_bridge and self._explain_bridge.enabled:
            enhanced = self._explain_bridge.enhance_output(gate_result)
            self._write_back_enhanced_log.append(enhanced)
```

---

## 🔧 需要确认的问题

### 1. 真实 OpenClaw 运行时的 hook 点

**问题**：真实 OpenClaw 是否有 `write_back()` 或类似的输出回调方法？

**勘测方法**：
- [ ] 查阅 OpenClaw 官方文档
- [ ] 搜索 OpenClaw 源码仓库中的 hook 相关 API
- [ ] 确认输出拦截的标准位置

### 2. 输出契约的兼容性

**问题**：如果在 `write_back()` 中增加 Shadow Mode 逻辑，会不会影响现有调用方？

**验证方法**：
- [ ] 检查当前所有调用 `adapter.write_back()` 的位置
- [ ] 确认是否依赖 `_write_back_log` 的特定行为
- [ ] 验证新增 `_write_back_enhanced_log` 不会破坏现有逻辑

### 3. 最小侵入路径

**问题**：是否需要在 adapter 内部持有 `ExplainBridge`，还是外围包装更合适？

**决策依据**：
- 如果真实 OpenClaw 有标准的 hook 注入机制 → 在 adapter 内部集成
- 如果真实 OpenClaw 没有标准机制 → 外围包装，保持 adapter 纯净

---

## 📝 下一步行动

### Phase 2.1 产物

1. **勘测文档**：本文档（持续更新）
2. **Hook Contract 探针文件**（可选）：
   - `adapters/openclaw/hook_contract.py`
   - 定义预期的 hook 接口和数据流
3. **验证测试**（可选）：
   - 验证 `write_back()` 修改后的向后兼容性
   - 验证 Shadow Mode 开关的隔离性

### Phase 2.2 预期

基于本阶段勘测结果，实现真实 hook 接入。

---

## 📌 关键结论

**推荐接点**：`adapter.write_back()`（Hook A）

**原因**：
- 最接近输出边界
- 最小侵入
- 与 Phase 2.0 的 `ExplainBridge` 设计一致
- 可通过开关控制，保持向后兼容

**备选接点**：`adapter.intercept_output()`（Hook B）

**风险点**：
- 需要确认真实 OpenClaw 的 hook 机制
- 需要验证修改后不影响现有契约

---

## 🔄 待办事项

- [ ] 确认真实 OpenClaw 的输出 hook 点
- [ ] 验证 `write_back()` 修改的兼容性
- [ ] 决定是否在 adapter 内部持有 `ExplainBridge`
- [ ] 编写 Hook Contract 探针文件（可选）
- [ ] 准备 Phase 2.2 实现方案

---
