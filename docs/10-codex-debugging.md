# SaucyClaw 在 Codex 中的调试建议

## 一、定位
SaucyClaw 当前最适合在 Codex 中承担的角色，不是完整运行时，而是：

- 治理基线仓库
- 多智能体边界样板
- 角色组织与调度规则样例
- 便于回放与迭代的调试入口

因此，第一次把仓库交给 Codex 时，目标不应设为“跑通完整 OpenClaw 运行时”，而应设为：

1. 能否快速识别核心治理文件
2. 能否理解 General Manager 的判断机制
3. 能否给出最小、可验证的改动方案
4. 能否按 smoke task 输出稳定结果

## 二、推荐进入顺序
建议让 Codex 或其他代理按以下顺序阅读：

1. `README.md`
2. `AGENTS.md`
3. `CLAUDE.md`
4. `system/SYSTEM_SPEC.md`
5. `system/AGENTS.md`
6. `agents/general-manager/AGENTS.md`
7. `examples/codex/smoke-task.md`

## 三、第一轮任务建议
推荐先使用以下任务，而不是直接要求大规模重构：

### 任务 A：入口清晰度验证
检查一个首次进入仓库的 AI 代理，能否在短时间内回答：
- 谁是外部角色
- 谁是内部总控
- 多智能体是否默认启动
- review 是否允许代写

### 任务 B：最小改动方案
要求 Codex 给出一轮最小迭代建议，且必须包含：
- 受影响文件
- 变更原因
- 验证方法

### 任务 C：回放 smoke task
直接使用 `examples/codex/smoke-task.md`，观察其是否：
- 一进来就误重构
- 忽略系统级文件
- 跳过验证

## 四、不建议一开始就做的事

1. 不要一开始就把 SaucyClaw 改造成 orchestrator
2. 不要一开始就强行接完整 OpenClaw runtime
3. 不要直接围绕单一 specialist 深改，而忽略系统级结构
4. 不要让 Codex 在无验证脚手架时大范围改目录

## 五、建议的后续增强
当第一轮 smoke test 稳定后，可以继续补：

1. 更多回放样例
2. 评分 rubric
3. 输出模板
4. 合规校验脚本
5. 与 OpenClaw workspace 对接的桥接脚本

## 六、推荐命令
如需快速检查当前仓库是否已具备最小入口，可执行：

```bash
bash scripts/codex/run_smoke.sh
```

如需验证整体目录结构，可执行：

```bash
bash scripts/validate/check_structure.sh
```
