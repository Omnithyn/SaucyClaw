# MESSAGE_ROUTING.md - 消息与交接路由

## 一、标准流向

CEO（人类角色） -> General Manager -> Specialist -> Reviewer -> General Manager -> CEO（人类角色）

## 二、默认规则

1. specialist 不直接根据用户原始需求对外输出
2. specialist 不默认直连 CEO
3. 同级 specialist 协作必须留痕
4. 正式流转优先通过 handoff 文件完成

## 三、升级路径

Specialist -> General Manager -> CEO（人类角色）

只有当：
- 方向冲突
- 输入不足
- 范围冲突
- 重大取舍需要决策
时才升级。

## 四、公共信息

以下内容适合进入 plaza：

- 阶段性发现
- 规则变化
- 公共风险
- 可复用经验
