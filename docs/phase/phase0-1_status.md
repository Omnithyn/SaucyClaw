# Phase 0-1 状态文档

> 创建时间：2026-04-12
> 最后更新：2026-04-12
> 状态：规划中

---

## 1. 当前阶段目标

在**不引入重型基础设施**的前提下，完成以下闭环：

```
YAML 元模型 / 治理规则 → 宿主事件标准化 → 证据记录 → 放行判断 → 记忆写入 → 可测试验证
```

详细迁移路径见：[phase0-1_repo_baseline.md](./phase0-1_repo_baseline.md)

---

## 2. 已冻结的边界

### 2.1 最小模块边界（7 模块，冻结）

| 模块 | 职责 | 备注 |
|------|------|------|
| `core/meta_model` | 定义如何定义治理对象与规则 | YAML Schema 即 DSL |
| `core/governance` | 角色、任务类型、规则、放行判断 | 治理域核心 |
| `core/events` | 宿主事件标准化 + 写入证据前处理 | **纯转换层，不持有状态** |
| `core/evidence` | 证据模型、证据生成、证据查询 | 证据域核心 |
| `core/engine` | 串联规则判断、证据记录、放行输出 | 最小运行支撑 |
| `adapters/openclaw` | 接入 OpenClaw 宿主生命周期 | 首个宿主适配 |
| `stores/file` | evidence / memory / schema 的本地存储实现 | 默认实现 |

模块边界约束：
- `meta_model` 不得直接依赖宿主
- `governance` 不得直接读写宿主上下文原始结构
- `events` 只做标准化，不做业务决策
- `evidence` 只处理结构化证据，不做复杂评分模型
- `engine` 负责编排，不承担 schema 定义职责
- `adapters/openclaw` 只做接入，不嵌入治理规则本身

### 2.2 三个最小抽象（冻结）

#### HostAdapter

```python
class HostAdapter(Protocol):
    def connect(self, context: dict) -> "SessionContext": ...
    def collect_event(self, raw_event: dict) -> "NormalizedEvent": ...
    def intercept_output(self, result: dict) -> "GateResult": ...
    def write_back(self, gate_result: "GateResult") -> None: ...
    def get_capabilities(self) -> dict: ...
```

Phase 0-1 仅实现 `OpenClawHostAdapter`。

#### EvidenceStore

```python
class EvidenceStore(Protocol):
    def record(self, evidence: "Evidence") -> str: ...
    def batch_record(self, evidences: list["Evidence"]) -> list[str]: ...
    def query(self, filters: dict) -> list["Evidence"]: ...
    def get(self, evidence_id: str) -> "Evidence | None": ...
```

Phase 0-1 仅实现 `FileEvidenceStore`。

#### MemoryStore

```python
class MemoryStore(Protocol):
    def write(self, record: "MemoryRecord") -> str: ...
    def search(self, query: dict, limit: int = 10) -> list["MemoryRecord"]: ...
    def decay(self) -> None: ...
```

Phase 0-1 仅实现 `FileMemoryStore`。

### 2.3 数据模型（冻结）

#### GovernanceRule

必填字段：`id`, `task_type`, `description`, `conditions`, `severity`, `on_hit`

Conditions 仅支持单层简单结构：
```yaml
conditions:
  - field: "assignee"
    op: "!="
    value_from: "reviewer"
```

允许的 op：`==`, `!=`, `in`, `not_in`, `exists`
不允许：`and/or` 嵌套、嵌套对象路径、自定义表达式

允许的 on_hit 值：`Allow`, `Review Required`, `Block`, `Escalate`
允许的 severity 值：`info`, `warn`, `review`, `block`

#### Evidence

最小必填：`id`, `type`, `assertion`, `source_ref`, `timestamp`, `confidence`
扩展可选：`freshness`, `verification_status`, `applicable_scope`, `contradicted_by`, `governance_version`

confidence 只允许三档离散值：`1.0`, `0.5`, `0.0`

#### GateResult

```yaml
decision: "Block" | "Allow" | "Review Required" | "Escalate"
reason: str
matched_rules: list[str]
evidence_ids: list[str]
suggestions: list[str]
```

#### NormalizedEvent

```yaml
id: str
event_type: str
source: str
session_id: str
timestamp: str
payload: dict
```

#### MemoryRecord

```yaml
id: str
type: str
summary: str
tags: list[str]
source_evidences: list[str]
created_at: str
trend: str
```

---

## 3. 明确不做的内容

Phase 0-1 明确不做：

- Web 管理台
- 图数据库
- 独立 sidecar 进程
- 复杂 DSL / 解析器
- 多宿主并行适配
- 自研复杂评估算法
- L3/L4 进化
- 实时流式事件总线
- 长周期 memory product 化

---

## 4. 当前态 → 实施态 → 目标态

| 维度 | 当前态 | Phase 0-1 实施态 | 目标态 |
|------|--------|-----------------|--------|
| 本体 | 无统一元模型 | YAML 元模型 + 治理本体 | 可配置本体平台 |
| 治理 | 模板式、分散（system/ 目录 Markdown） | 结构化规则库（schemas/governance/） | 可审核/可发布治理体系 |
| 证据 | 零散上下文 | JSON/YAML 证据记录 | 证据图与查询服务 |
| 记忆 | 宿主自带/文件（agents/*/memory.md） | File/Memory Store + 简单检索 | 外部 Memory Provider |
| 接入 | 手工嵌入（shell 脚本） | OpenClaw Adapter（Python） | 多宿主适配 |
| 评估 | 人工判断 | 放行等级 + 趋势标记 | 完整评估闭环 |
| 进化 | 无明确分层 | L1-L2（观察式 + 建议式） | L1-L4 |

---

## 5. 首轮测试场景

### Block 场景

输入：
- task_type = `C`
- assignee = `developer`
- reviewer = `developer`（与 assignee 相同）

预期：
- 命中 `rule-reviewer-must-differ`
- 生成一条 `rule_hit` 证据（confidence = 1.0）
- `GateResult.decision = Block`
- 写入一条 memory record

### Allow 场景

输入：
- task_type = `C`
- assignee = `developer`
- reviewer = `reviewer`（与 assignee 不同）

预期：
- 不命中阻断规则
- 生成一条 `rule_pass` 证据（confidence = 1.0）
- `GateResult.decision = Allow`
- 写入一条 memory record

---

## 6. 未决问题

见 [open_questions.md](./open_questions.md)

---

## 7. 评估机制（Phase 0-1）

- 规则命中次数统计
- 每种决策类型次数统计
- 每种任务类型下的放行分布
- 趋势标记只允许：`improving`, `stable`, `degrading`

明确不做：加权综合评分、置信度预测模型、规则自动调参、自动策略学习

---

## 8. 文档分层

| 文档 | 路径 | 职责 |
|------|------|------|
| 目标态架构总规 | `docs/superpowers/specs/2026-04-12-saucyclaw-repositioning-design.md` | 长期方向 |
| 目标态详细设计 | `docs/superpowers/specs/SaucyClaw_详细设计说明书_vNext.md` | 目标态规格 |
| Phase 0-1 状态 | `docs/phase/phase0-1_status.md` | 当前共识（本文件） |
| Phase 0-1 实施蓝图 | `docs/phase/phase0-1_implementation_plan.md` | 指导编码 |
| Phase 0-1 仓库基线 | `docs/phase/phase0-1_repo_baseline.md` | 迁移路径 |
| Phase 0-1 进度 | `docs/phase/phase0-1_progress.md` | 提交记录 |
| 未决问题 | `docs/phase/open_questions.md` | 待决议项 |
| ADR | `docs/adr/ADR-NNNN-*.md` | 架构决策 |
