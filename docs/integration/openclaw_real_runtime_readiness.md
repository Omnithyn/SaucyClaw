# 真实宿主接入准备文档

> M2 — 真实宿主接入准备包
> 当前状态：基于 mock adapter 的最小闭环已完成，尚未接入真实 OpenClaw hook

---

## 1. 文档目的

回答一个问题：

**"如果下周开始接真实 OpenClaw，当前仓库哪些东西已经能直接用，哪些不能，先做什么后做什么？"**

本文档不是 phase 过程记录，而是面向真实宿主接入的**准备清单**。

---

## 2. 当前 M1 已具备什么

以下能力已完成、可复用、与宿主类型无关（不限于 mock adapter）：

| 能力 | 文件 | 状态 | 说明 |
|------|------|------|------|
| 治理 schema | `schemas/governance/` | 可用 | roles / task_types / rules 定义 |
| schema loader | `core/governance/loader.py` | 可用 | 从 YAML 装载治理规则 |
| 规则匹配器 | `core/governance/matcher.py` | 可用 | applies_when + conditions AND-only |
| 治理引擎 | `core/engine/orchestrator.py` | 可用 | process_event → GateResult |
| evidence 生成 | `core/evidence/` | 可用 | 违规时生成证据 |
| memory 构建 | `core/engine/memory_builder.py` | 可用 | 决策后写入记忆 |
| 解释构造器 | `core/governance/explainer.py` | 可用 | 规则 → 结构化解释 |
| 解释打包器 | `core/governance/explainer_bundle.py` | 可用 | ExplanationBundle |
| 文件存储 | `stores/file/` | 可用 | EvidenceStore + MemoryStore |
| 协议定义 | `stores/protocols.py` | 可用 | GateResult / NormalizedEvent 等 |

以下能力属于外围接入包，**与真实宿主无关或可复用**：

| 能力 | 文件 | 状态 | 说明 |
|------|------|------|------|
| 解释桥接器 | `adapters/openclaw/explain_bridge.py` | 可复用 | Bridge 逻辑与 adapter 无关 |
| Shadow Runtime | `adapters/openclaw/shadow_runtime.py` | 可复用 | 流程模板，换 adapter 即可 |
| 运行摘要 | `adapters/openclaw/runtime_trace.py` | 可复用 | 从 ShadowRunResult 构建 |
| 调试渲染 | `adapters/openclaw/debug_render.py` | 可复用 | 稳定文本输出 |
| Hook Contract | `adapters/openclaw/hook_contract.py` | 探针 | Protocol 草图，需真实验证 |

---

## 3. 当前仍依赖 mock adapter 的部分

| 模块 | 文件 | 当前状态 | 说明 |
|------|------|----------|------|
| 宿主适配器 | `adapters/openclaw/adapter.py` | **mock** | 仅模拟行为，不接入真实宿主 |
| 拦截输出 | `adapter.intercept_output()` | **占位** | 返回默认 Allow，不真实拦截 |
| 回写日志 | `adapter.write_back()` | **mock** | 仅写入内部列表 |
| 会话连接 | `adapter.connect()` | **mock** | 从 dict 提取字段，无真实连接 |
| 事件收集 | `adapter.collect_event()` | **mock** | 简单字段映射 |

---

## 4. 真实 OpenClaw 接入前必须确认的事项

### 4.1 接口契约确认

| 确认项 | 检查点 | 验证方式 |
|--------|--------|----------|
| 真实宿主是否提供类似 `connect()` 的连接点 | 对照 OpenClaw hook API | 阅读 OpenClaw 文档 |
| 真实宿主的事件格式是否与 `raw_event` dict 兼容 | 字段映射检查 | 用真实事件跑 collect_event |
| 真实宿主是否有类似 `write_back()` 的回写点 | hook 出口确认 | 确认 output_intercept hook |
| 真实宿主的 GateResult 消费方式 | 数据结构兼容性 | 确认是否需要 JSON 序列化 |

### 4.2 协议对齐

| 协议 | 当前实现 | 需要确认 |
|------|----------|----------|
| `HostOutputSink` | mock adapter | 真实宿主是否接受类似结构 |
| `ExplainPayload` | ExplainBridge | 真实宿主是否需要 JSON 格式 |
| `GovernanceProcessor` | GovernanceEngine | 接口已稳定，一般无需改 |
| `ShadowOutput` | ShadowRuntime | 流程模板可复用 |

### 4.3 数据格式确认

- GateResult 是否需要序列化为宿主原生格式
- Evidence 的存储路径是否需要适配宿主的存储策略
- MemoryRecord 是否需要与宿主的记忆系统对接

---

## 5. 推荐真实接入顺序

### 第一阶段：最小替换

1. **替换 adapter 实现**：保留 `OpenClawHostAdapter` 类名，替换内部实现
   - `connect()` → 调用真实宿主连接 API
   - `collect_event()` → 从真实事件流提取字段
   - `write_back()` → 写入真实宿主回写点
   - `intercept_output()` → 从占位改为真实拦截

2. **保持其他模块不变**：engine / bridge / runtime / trace / render 全部可复用

### 第二阶段：验证

3. **跑现有 smoke test**：验证最小链路仍然可用
4. **跑 conformance test**：验证 Protocol 仍然满足
5. **用真实事件跑 Block / Allow 场景**：验证治理逻辑正确

### 第三阶段：增强

6. **对接真实证据存储**：如果宿主要求特定证据格式
7. **对接真实记忆系统**：如果宿主有自己的记忆 API
8. **接入平台管理面**：规则热更新、版本管理等（远期）

---

## 6. 风险点

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 真实宿主事件格式与 mock 差异大 | collect_event 需要重写 | 保留 collect_event 接口，适配映射 |
| 真实宿主无等价 write_back 点 | 需要新输出路径 | 降级为日志输出 + 文件写入 |
| 真实宿主 hook 调用方式不同 | ShadowRuntime 流程可能需要调整 | 流程是模板，可适配 |
| Protocol 与实际不兼容 | hook_contract.py 需修正 | 以真实宿主为准，修正 Protocol |

---

## 7. 回退策略

如果真实宿主接入后出现问题：

1. **切回 mock adapter**：现有测试仍可用，可快速验证治理内核是否正确
2. **关闭 Shadow Mode**：bridge.enable=False 即可关闭解释输出
3. **关闭 Bridge**：ShadowRuntime 传 explain_bridge=None 即可绕过
4. **保留所有测试**：201 个测试是回归验证的基线

---

## 8. 快速验证当前接入包

```bash
# 1. 运行 example，确认最小链路可用
python -m examples.openclaw_shadow_runtime_example

# 2. 运行接入包测试（57 个测试）
pytest tests/unit/test_shadow_runtime.py \
       tests/unit/test_hook_contract.py \
       tests/unit/test_hook_contract_conformance.py \
       tests/unit/test_runtime_trace.py \
       tests/unit/test_debug_render.py \
       tests/unit/test_explain_bridge.py \
       tests/integration/test_openclaw_adapter.py -v

# 3. 运行全部测试（201 个）
pytest tests/ -v
```

看到 `201 passed` 说明接入包完整可用。
