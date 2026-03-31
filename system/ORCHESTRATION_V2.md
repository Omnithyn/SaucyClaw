# ORCHESTRATION_V2.md - 编排规程（V2 草案）

## 一、起点

所有任务仍以 General Manager 的任务处理判断为正式起点。

V2 相较于旧版的差异在于：

- 更强调启动范围控制
- 更强调阶段契约
- 更强调评测与回归可挂接

## 二、标准流程

### A 类：总控直接完成
1. General Manager 做任务处理判断
2. 明确为何可由总控闭环
3. 完成结果并统一收口

### B 类：单 specialist
1. General Manager 判断为 B 类
2. 明确 owner、交付物、验收标准
3. specialist 输出中间产物
4. General Manager 收口

### C 类：single specialist + review
1. General Manager 判断为 C 类
2. specialist 交付中间产物
3. reviewer 审查 pass / revise / reject
4. General Manager 收口

### D 类：多角色串行协作
1. General Manager 判断为 D 类
2. 先定义阶段边界
3. 只启动第一阶段 owner
4. 每阶段结束时形成 handoff
5. 如需要，插入 reviewer
6. General Manager 决定是否进入下一阶段
7. 最终统一收口

### E 类：暂不启动执行
1. General Manager 判断为 E 类
2. 指出缺口、风险或冲突
3. 不启动 specialist
4. 等待条件补足或建议升级决策

## 三、V2 新增关注点

### 1. 阶段契约
进入某一阶段前，建议先定义：
- owner
- 输入
- 交付物
- 验收标准
- 是否需要 review

### 2. 评测挂接点
在以下节点可插入评测：
- 初次 smoke task
- 新角色加入后
- 调度规则变化后
- 重大重构后

### 3. 约束挂接点
在以下节点应优先检查约束：
- 启动 specialist 前
- 跨阶段流转前
- 标记完成前

## 四、禁止事项

1. 不在未判断前派单
2. 不默认并发启动多个 owner
3. 不把中间产物直接当最终答案
4. 不跳过必要的 review 或 handoff
