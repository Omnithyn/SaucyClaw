# 首次试运行任务示例

## 示例任务
请输出一份《SaucyClaw 多智能体运行手册 v1》并附一张协作流程图。

## 推荐处理方式
- General Manager 先做任务处理判断
- 建议模式：D 类（多角色串行协作）

## 先输出任务处理判断（示例骨架）

```text
# 任务处理判断
## 用户真实目标
产出《SaucyClaw 多智能体运行手册 v1》并附协作流程图

## 处理模式
D 类（多角色串行协作）

## 选择该模式的原因
该任务包含文档编写、流程可视化与质量审查三个不同阶段，单角色难以稳定闭环。

## 当前启动的角色
writer（仅阶段 1）

## 当前等待的角色
designer, reviewer, general-manager

## 下一步
进入阶段 1，输出 stage contract 并开始执行
```

## 可能拆解
### 阶段 1
- owner：writer
- 目标：整理运行手册正文结构
- 交付物：手册初稿
- 验收标准：目录完整、关键流程描述清晰、标注待补图位置
- 交接对象：designer

### 阶段 2
- owner：designer
- 目标：绘制协作流程图
- 交付物：流程图草稿
- 验收标准：覆盖 GM / specialist / reviewer / evaluator / policy guardian 关系
- 交接对象：reviewer

### 阶段 3
- owner：reviewer
- 目标：审查手册与流程图
- 交付物：review 结果
- 验收标准：给出 pass / revise / reject 与依据
- 交接对象：general-manager

### 阶段 4
- owner：general-manager
- 目标：统一收口对外输出
- 交付物：最终版运行手册
- 验收标准：确认已完成 handoff + review，且不存在边界风险遗漏

## 必填模板建议（用于回放）

建议每个阶段至少产出以下模板化结果：

1. `templates/task-judgement-template.md`
2. `templates/stage-contract-template.md`
3. `templates/handoff-template.md`
4. `templates/closure-check-template.md`
