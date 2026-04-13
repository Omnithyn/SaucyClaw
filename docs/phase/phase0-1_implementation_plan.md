# Phase 0-1 实施蓝图

> 创建时间：2026-04-12
> 用途：直接指导首轮编码，不是设计讨论

---

## 1. 目标态目录结构

```text
saucyclaw/
├─ core/
│  ├─ meta_model/          # 元模型定义与校验
│  ├─ governance/          # 治理规则与决策逻辑
│  ├─ events/              # 事件标准化（纯转换层）
│  ├─ evidence/            # 证据对象、聚合、冲突处理
│  └─ engine/              # 串联规则判断、证据记录、放行输出
├─ adapters/
│  └─ openclaw/            # OpenClaw 宿主适配
├─ stores/
│  ├─ file/                # evidence / memory / schema 的本地文件存储
│  │  ├─ evidence/         #   JSON 证据文件
│  │  ├─ memory/           #   JSON 记忆文件
│  │  └─ cache/            #   可选的内存索引持久化
│  └─ memory/              # 内存存储实现（可选）
├─ schemas/
│  ├─ meta/                # 元模型 YAML Schema
│  └─ governance/          # 治理本体 YAML Schema
├─ tests/
│  ├─ fixtures/            # 测试固定数据
│  ├─ unit/                # 单元测试
│  └─ integration/         # 集成测试
├─ docs/
│  ├─ architecture/        # 架构文档
│  ├─ phase/               # 阶段文档
│  ├─ review/              # 评审记录
│  └─ process/             # 协作流程
└─ README.md
```

### 预留但当前不实现

```text
providers/
apps/
runtime/sidecar/
```

---

## 2. 文件清单（按提交分片）

### Commit 0 — 过程资料与仓库基线

| 文件 | 说明 |
|------|------|
| `docs/phase/phase0-1_status.md` | 阶段状态基线 |
| `docs/phase/phase0-1_repo_baseline.md` | 仓库基线报告 |
| `docs/phase/phase0-1_implementation_plan.md` | 本文件 |
| `docs/phase/open_questions.md` | 未决问题清单 |
| `docs/phase/phase0-1_progress.md` | 实施进度记录 |
| `docs/adr/ADR-0001-phase0-1-scope.md` | ADR: 范围冻结 |
| `docs/adr/ADR-0002-minimal-interfaces.md` | ADR: 最小接口 |
| `docs/adr/ADR-0003-evidence-model.md` | ADR: 证据模型 |

完成标准：所有文档存在、内容完整、无占位符

---

### Commit 1 — 项目骨架与 Schema 样例

| 文件 | 说明 |
|------|------|
| `core/__init__.py` | core 包初始化 |
| `core/meta_model/__init__.py` | meta_model 包初始化 |
| `core/governance/__init__.py` | governance 包初始化 |
| `core/events/__init__.py` | events 包初始化 |
| `core/evidence/__init__.py` | evidence 包初始化 |
| `core/engine/__init__.py` | engine 包初始化 |
| `adapters/__init__.py` | adapters 包初始化 |
| `adapters/openclaw/__init__.py` | openclaw 包初始化 |
| `stores/__init__.py` | stores 包初始化 |
| `stores/file/__init__.py` | file 包初始化 |
| `stores/file/evidence/__init__.py` | evidence 存储目录初始化 |
| `stores/file/memory/__init__.py` | memory 存储目录初始化 |
| `stores/file/cache/__init__.py` | cache 存储目录初始化 |
| `stores/memory/__init__.py` | memory 包初始化 |
| `schemas/__init__.py` | schemas 包初始化 |
| `schemas/meta/object_types.yaml` | 对象类型定义样例 |
| `schemas/meta/relation_types.yaml` | 关系类型定义样例 |
| `schemas/meta/action_types.yaml` | 动作类型定义样例 |
| `schemas/governance/roles.yaml` | 角色定义样例 |
| `schemas/governance/task_types.yaml` | 任务类型定义样例 |
| `schemas/governance/rules.yaml` | 治理规则定义样例 |
| `tests/__init__.py` | tests 包初始化 |
| `tests/fixtures/roles.yaml` | 测试用角色 fixture |
| `tests/fixtures/rules.yaml` | 测试用规则 fixture |
| `tests/fixtures/events.yaml` | 测试用事件 fixture |

完成标准：
- 所有目录可 import
- 所有 YAML schema 文件可加载（无语法错误）
- fixture 数据覆盖 Block 和 Allow 两种场景

---

### Commit 2 — meta_model + governance 最小闭环

| 文件 | 说明 |
|------|------|
| `core/meta_model/models.py` | 元模型 dataclass（EntityType, RelationType, ActionType, ConstraintType, EvidenceType） |
| `core/meta_model/loader.py` | YAML schema 加载器 |
| `core/meta_model/validator.py` | Schema 校验器（必填字段、枚举值、引用关系） |
| `core/meta_model/test_test.py` | meta_model 单元测试 |
| `core/governance/models.py` | 治理模型 dataclass（RoleDefinition, TaskType, GovernanceRule, GateResult） |
| `core/governance/matcher.py` | 规则匹配引擎（单层 condition 匹配） |
| `core/governance/test_test.py` | governance 单元测试 |

完成标准：
- YAML schema 可加载为 Python dataclass
- `governance.matcher` 能对给定事件返回匹配的规则列表
- Block 和 Allow 场景的规则匹配结果正确
- 单元测试覆盖所有 dataclass 和 matcher

---

### Commit 3 — events + evidence

| 文件 | 说明 |
|------|------|
| `core/events/models.py` | NormalizedEvent dataclass |
| `core/events/normalizer.py` | 宿主事件 → NormalizedEvent 转换 |
| `core/events/test_test.py` | events 单元测试 |
| `core/evidence/models.py` | Evidence dataclass |
| `core/evidence/generator.py` | NormalizedEvent + GovernanceRule → Evidence 生成 |
| `core/evidence/test_test.py` | evidence 单元测试 |

完成标准：
- 标准化事件生成正确
- 证据生成包含正确 assertion 和 confidence
- Block 场景生成 `rule_hit` 证据，Allow 场景生成 `rule_pass` 证据

---

### Commit 4 — file stores + engine

| 文件 | 说明 |
|------|------|
| `stores/protocols.py` | 三个 Protocol 抽象（HostAdapter, EvidenceStore, MemoryStore） |
| `stores/file/evidence_store.py` | FileEvidenceStore 实现 |
| `stores/file/memory_store.py` | FileMemoryStore 实现 |
| `stores/file/test_test.py` | stores 单元测试 |
| `core/engine/engine.py` | Engine 编排（事件→证据→规则匹配→GateResult→记忆写入） |
| `core/engine/test_test.py` | engine 单元测试 |

完成标准：
- Evidence 可写入文件并可查询
- Memory 可写入并可简单检索
- Engine 主流程串联成功：输入宿主事件 → 输出 GateResult
- Block 和 Allow 两种场景都能走通

---

### Commit 5 — openclaw adapter + integration test

| 文件 | 说明 |
|------|------|
| `adapters/openclaw/adapter.py` | OpenClawHostAdapter 实现 |
| `adapters/openclaw/test_test.py` | adapter 单元测试 |
| `tests/integration/test_full_flow.py` | 集成测试（Block + Allow 两种场景） |
| `tests/conftest.py` | pytest 共享 fixture |

完成标准：
- OpenClawHostAdapter 能收集模拟事件并返回 GateResult
- 集成测试通过 Block 和 Allow 两个场景
- 所有测试运行通过 `pytest tests/`

---

## 3. 每个提交的完成标准

| 提交 | 完成标准 |
|------|---------|
| Commit 0 | 5 个 phase 文档 + 3 个 ADR 存在且内容完整 |
| Commit 1 | 所有目录可 import，YAML 可加载，fixture 覆盖两种场景 |
| Commit 2 | meta_model 和 governance 单元测试通过，规则匹配正确 |
| Commit 3 | events 和 evidence 单元测试通过，证据生成正确 |
| Commit 4 | file_store 单元测试通过，engine 主流程走通 |
| Commit 5 | adapter 单元测试通过，集成测试两种场景都通过 |

---

## 4. 测试计划

### 单元测试

| 模块 | 测试内容 |
|------|---------|
| meta_model | YAML 加载成功、校验器拒绝无效 schema |
| governance | 规则匹配正确（== / != / in / not_in / exists） |
| events | 标准化事件生成正确 |
| evidence | 证据生成包含正确的 assertion 和 confidence |
| stores | 证据读写一致、记忆读写一致 |
| engine | 主流程输出正确的 GateResult |

### 集成测试

| 场景 | 输入 | 预期输出 |
|------|------|---------|
| Block | task_type=C, assignee=developer, reviewer=developer | decision=Block, 命中 rule-reviewer-must-differ |
| Allow | task_type=C, assignee=developer, reviewer=reviewer | decision=Allow, 无阻断规则命中 |

### 运行方式

```bash
cd /Users/yaochunyang/tools/AIGC/agent/SaucyClaw
pytest tests/ -v
```

---

## 5. 依赖

Phase 0-1 仅依赖 Python 标准库 + 以下第三方包：

```
pyyaml>=6.0
pytest>=7.0
```

不引入任何数据库、Web 框架、图数据库等重依赖。
