# 08 Tooling 与 Bootstrap 说明

## 目标

SaucyClaw 未来不仅提供治理样例，也提供帮助用户快速铺设和校验 OpenClaw 工作区的工具。

## 工具分层

### scripts/
适合 shell 脚本，处理：
- 初始化目录
- 注入 SaucyClaw 配置
- 校验结构
- 启停 demo
- 备份与导出

### tools/
适合 Python 工具，处理：
- 目录生成
- 模板渲染
- 配置解析
- 合规校验
- bundle 打包

## 当前策略

先保留清晰目录与 README/占位文件，后续逐步填充实现。
