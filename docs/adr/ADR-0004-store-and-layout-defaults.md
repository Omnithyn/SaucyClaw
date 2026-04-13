# ADR-0004: 存储实现与目录布局默认值

> 日期：2026-04-13
> 状态：已接受

---

## 背景

Phase 0-1 实施蓝图中有 6 个实现细节在讨论中确定，
但未正式写入决策记录。本 ADR 统一收敛。

## 决策

### 1. MemoryStore 默认实现

选择 `FileMemoryStore` 为 Phase 0-1 的默认实现。
`InMemoryMemoryStore` 不在此阶段实现。

理由：记忆需要跨会话持久化，文件存储最简且够用。

### 2. Evidence 文件组织方式

按 `session_id` 分 JSONL 文件。每个 session 一个文件：

```
stores/file/evidence/<session_id>.jsonl
```

理由：按 session 组织天然隔离，JSONL 适合追加写入和流式读取。

### 3. OpenClawHostAdapter 首轮挂接点

Phase 0-1 只实现模拟接口（纯测试用），不实际 hook OpenClaw 生命周期。

理由：先验证治理闭环的正确性，再处理真实接入。

### 4. GateResult.suggestions 类型

使用 `list[str]`，不使用结构化对象。

理由：Phase 0-1 的 suggestion 只是简单提示文本，不需要结构化解析。

### 5. 旧 tools/ 处理

Phase 0-1 期间不对旧 `tools/saucyclaw/` 做任何处理（不标记 deprecated，不迁移，不删除）。

理由：避免分散注意力，专注新核心模块。

### 6. pyproject.toml 位置

放在仓库根目录，仅声明 `pyyaml` 和 `pytest` 两个依赖。
不碰旧 `tools/pyproject.toml`。

理由：根目录 pyproject.toml 是 Python 项目的标准位置，新 core 模块可以直接使用。

## 后果

- `stores/file/evidence/` 下按 session 组织 JSONL 文件
- `stores/file/memory/` 下持久化记忆记录
- 首轮测试通过模拟事件驱动治理闭环
- 旧 tools/ 与新 core/ 并存，后续再处理

## 暂不做

- InMemoryMemoryStore
- 结构化 suggestion 对象
- 旧 tools/ 的迁移或废弃
- src/ 布局
