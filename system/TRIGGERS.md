# TRIGGERS.md - 轻量触发规则

## 一、Task Created
当 General Manager 新建任务处理判断或任务契约时，视为任务触发。

## 二、Owner Assigned
当某角色被明确点名并分配交付物与验收标准时，视为启动条件满足。

## 三、Handoff Created
当 handoff 文件生成时，视为交接触发。

## 四、Review Submitted
当 review 文件生成时，视为评审触发。

## 五、Decision Updated
当系统级关键决策更新时，General Manager 检查是否影响现有任务。

## 六、禁止事项

1. 不允许没有 owner 就触发执行
2. 不允许通过口头暗示代替正式点名
3. 不允许 reviewer 触发后直接下场代工
