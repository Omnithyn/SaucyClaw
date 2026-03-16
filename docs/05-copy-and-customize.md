# 05 复制与定制指南

## 5.1 最小复制集

如果只想快速复用，至少复制：

1. `system/`
2. `agents/general-manager/`
3. `agents/reviewer/`
4. `agents/specialists/`
5. `templates/`
6. `examples/`

## 5.2 推荐定制顺序

### 第一步：改组织名称
把项目中的：
- SaucyClaw
- 虾酱
- CEO
替换成你的组织命名。

### 第二步：改角色数量
如果你的项目不需要 Designer 或 Researcher，可精简角色，不影响整体模型。

### 第三步：改风格偏好
在：
- PROJECT_CONTEXT.md
- STANDARDS.md
- 各角色 memory.md
中调整输出偏好。

### 第四步：改授权边界
如果你想让 General Manager 更保守或更激进，可以修改：
- agents/general-manager/PROMPT.md
- system/SYSTEM_SPEC.md
- system/ORCHESTRATION.md

## 5.3 不建议直接修改的核心原则

建议保留以下原则，不轻易删除：

1. 先分流，再决定是否调人
2. 多智能体不是默认动作
3. 未被点名不得启动
4. 单任务单 owner
5. handoff 必须留痕
6. review 是正式关卡
7. General Manager 统一收口

## 5.4 对外分享时建议的呈现方式

建议介绍顺序：

1. 为什么会做 SaucyClaw
2. 它解决了 OpenClaw 的什么问题
3. 它的组织模型是什么
4. 它怎么避免全员并发抢答
5. General Manager 如何做任务处理判断
6. 如何复制到自己的项目里
