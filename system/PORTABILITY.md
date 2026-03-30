# PORTABILITY.md - 可迁移性说明

## 一、目的

SaucyClaw 不应只适用于单一 agent 工具。

本文件用于说明：

1. 哪些内容属于通用方法
2. 哪些内容属于某一具体工具的适配层
3. 如何在不同 agent 工作流之间迁移

## 二、可迁移的核心

以下内容应尽量保持工具无关：

- 角色边界
- 任务处理判断
- 单任务单 owner
- handoff 结构
- review 关卡
- evaluator 与 rubric

## 三、适配层内容

以下内容可以因工具不同而调整：

- 入口文件命名
- 命令行脚本
- 工作区目录约定
- 提示词注入方式
- 是否存在特定 runtime 配置

## 四、迁移建议

### 从 OpenClaw 迁移
保留：
- `AGENTS.md` 中的主角色规则
- `system/` 中的治理方法
- `templates/` 与 `evals/` 中的通用资产

### 到 Codex 或其他工作流
优先带走：
- 根入口文件
- 关键 system 文件
- task contract 模板
- rubric 与 scenarios

## 五、判定标准

如果 SaucyClaw 的核心方法必须依赖某一特定工具才能成立，则说明可迁移性不足。
