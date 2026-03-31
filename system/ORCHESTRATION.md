# ORCHESTRATION.md - 运行编排

## 一、起点

所有任务以 General Manager 的“任务处理判断”作为正式起点。

若未完成“任务处理判断”，不得启动任何 specialist。

## 二、编排目标

SaucyClaw 的编排目标不是让更多角色同时行动，而是：

1. 控制启动范围
2. 保持单任务单 owner
3. 让阶段边界清晰
4. 让 handoff、review、evaluation 能自然挂接

## 三、标准流程

### A 类
1. General Manager 判断为 A 类
2. General Manager 说明为何可直接闭环
3. General Manager 完成结果并统一收口

### B 类
1. General Manager 判断为 B 类
2. 点名一个 specialist
3. 明确 owner、输入、交付物、验收标准
4. specialist 交付中间产物
5. General Manager 收口并对外输出

### C 类
1. General Manager 判断为 C 类
2. 点名一个 specialist
3. specialist 交付中间产物
4. reviewer 审查
5. General Manager 收口并对外输出

### D 类
1. General Manager 判断为 D 类
2. General Manager 拆解阶段
3. 只启动第一阶段 owner
4. owner 交付阶段产物
5. 写 handoff
6. reviewer（如需要）审查
7. evaluator（如需要）记录评测结论
8. General Manager 决定是否进入下一阶段
9. 全部阶段完成后统一收口

### E 类
1. General Manager 判断为 E 类
2. 不启动 specialist
3. 先整理缺口、风险或冲突
4. 视情况等待条件补足或升级决策

## 四、阶段契约

进入某一阶段前，建议至少明确：

- owner
- 输入
- 交付物
- 验收标准
- 完成后交给谁
- 是否需要 review

## 五、默认等待机制

任何 specialist 若未被明确点名，则默认待命，禁止自行启动。

## 六、关键挂接点

### 1. review 挂接点
适用于：
- 正式交付前
- 高风险结果前
- 需要质量把关的阶段末尾

### 2. evaluation 挂接点
适用于：
- 新角色加入后
- 新流程上线后
- 重大改动后
- 需要做 smoke 或 replay 的任务

### 3. policy check 挂接点
适用于：
- 启动 specialist 前
- 跨阶段流转前
- 标记完成前

## 七、禁止事项

1. 不在未判断前派单
2. 不默认并发启动多个 owner
3. 不把中间产物直接当最终答案
4. 不跳过必要的 review 或 handoff
5. 不因用户催促而绕开编排纪律
