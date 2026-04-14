# 接入能力矩阵

> M2 — 真实宿主接入准备包
> 说明：每项能力按"当前状态 / 是否可复用 / 进入真实宿主前还差什么"逐项说明

---

## 能力矩阵总表

| 能力 | 文件 | 当前状态 | 与真实宿主无关 | 可直接复用 | 仍依赖 mock | 进入真实宿主前还差什么 |
|------|------|----------|:-------------:|:---------:|:----------:|----------------------|
| **GovernanceEngine** | `core/engine/orchestrator.py` | 可用 | 是 | 是 | 否 | 无。引擎与宿主无关 |
| **规则匹配器** | `core/governance/matcher.py` | 可用 | 是 | 是 | 否 | 无。匹配器与宿主无关 |
| **Schema Loader** | `core/governance/loader.py` | 可用 | 是 | 是 | 否 | 无。装载器与宿主无关 |
| **Evidence 生成** | `core/events/` + `stores/file/evidence/` | 可用 | 是 | 是 | 否 | 无。证据格式可独立使用 |
| **Memory 构建** | `core/engine/memory_builder.py` | 可用 | 是 | 是 | 否 | 无。记忆模板与宿主无关 |
| **解释构造器** | `core/governance/explainer.py` | 可用 | 是 | 是 | 否 | 无。纯函数，与宿主无关 |
| **解释打包器** | `core/governance/explainer_bundle.py` | 可用 | 是 | 是 | 否 | 无。纯函数，与宿主无关 |
| **ExplainBridge** | `adapters/openclaw/explain_bridge.py` | 可用 | 是 | 是 | 否 | 无。桥接逻辑与 adapter 解耦 |
| **ShadowRuntime** | `adapters/openclaw/shadow_runtime.py` | 可用 | 部分 | 是 | 否 | 需替换 adapter 实现，流程可复用 |
| **RuntimeTrace** | `adapters/openclaw/runtime_trace.py` | 可用 | 是 | 是 | 否 | 无。摘要构建与宿主无关 |
| **DebugRender** | `adapters/openclaw/debug_render.py` | 可用 | 是 | 是 | 否 | 无。调试输出与宿主无关 |
| **Hook Contract** | `adapters/openclaw/hook_contract.py` | 探针 | 部分 | 是 | 部分 | 需与真实宿主 API 对齐验证 |
| **Mock Adapter** | `adapters/openclaw/adapter.py` | **mock** | 否 | 否 | 是 | **需替换为真实宿主实现** |
| **Example** | `examples/openclaw_shadow_runtime_example.py` | 可用 | 部分 | 部分 | 部分 | 演示流程可复用，需换 adapter |
| **Smoke Test** | `tests/integration/test_openclaw_adapter.py` | 可用 | 部分 | 部分 | 部分 | adapter 替换后需更新 fixture |
| **Contract Test** | `tests/unit/test_hook_contract.py` | 可用 | 部分 | 是 | 部分 | Protocol 对齐后自动更新 |
| **Conformance Test** | `tests/unit/test_hook_contract_conformance.py` | 可用 | 部分 | 是 | 部分 | 真实 adapter 满足 Protocol 时自动通过 |

---

## 分类说明

### 与宿主无关（可直接复用）

以下能力完全与宿主类型无关，接入真实宿主时**不需要任何修改**：

- `GovernanceEngine` — 治理引擎核心
- `规则匹配器` — applies_when + conditions 匹配
- `Schema Loader` — YAML 装载
- `Evidence 生成` — 违规证据
- `Memory 构建` — 记忆模板
- `解释构造器` — 规则解释
- `解释打包器` — ExplanationBundle
- `ExplainBridge` — 解释桥接
- `RuntimeTrace` — 运行摘要
- `DebugRender` — 调试渲染

### 部分与宿主相关（流程可复用，需替换组件）

- `ShadowRuntime` — 流程模板可复用，但需替换 `adapter` 参数
- `Hook Contract` — Protocol 草图正确，但需与真实宿主 API 对齐验证
- `Example` — 演示流程可复用，但需替换 mock adapter
- `Smoke Test` — 测试结构可复用，但需更新 fixture

### 完全依赖 mock（必须替换）

- `Mock Adapter` — 整个文件需要替换为真实宿主实现
  - `connect()` — 当前从 dict 提取，需改为真实连接
  - `collect_event()` — 当前字段映射，需改为真实事件流
  - `intercept_output()` — 当前占位，需改为真实拦截
  - `write_back()` — 当前写内部列表，需改为真实回写

---

## 进入真实宿主前的差距清单

| 差距 | 优先级 | 说明 |
|------|--------|------|
| 替换 adapter 实现 | **P0** | 这是进入真实宿主的第一步 |
| 确认真实宿主 hook API | **P0** | 决定 adapter 如何对接 |
| 验证事件格式兼容性 | **P0** | raw_event dict 需与真实事件格式对齐 |
| 确认回写点存在 | **P1** | 决定 write_back 如何实现 |
| 验证 Protocol 兼容性 | **P1** | hook_contract.py 可能与真实宿主 API 有偏差 |
| 对接真实证据存储 | **P2** | 如果宿主要求特定证据格式 |
| 对接真实记忆系统 | **P2** | 如果宿主有自己的记忆 API |
| 平台管理面 | **P3** | 远期：规则热更新、版本管理等 |
