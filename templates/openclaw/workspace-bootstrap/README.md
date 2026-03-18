# Workspace Bootstrap Template

OpenClaw 工作区快速启动模板。

## 快速启动

```bash
# 1. 初始化项目结构
./scripts/bootstrap/init_saucyclaw.sh my-project

# 2. 验证结构
./scripts/validate/check_structure.sh

# 3. 创建智能体
./scripts/bootstrap/create_agent_role.sh researcher

# 4. 启动 demo
./scripts/demo/up_demo.sh
```

## 下一步

1. 阅读 system/SYSTEM_SPEC.md 了解治理规范
2. 阅读 agents/general-manager/AGENTS.md 了解角色定义
3. 根据实际需求定制系统配置
4. 创建所需的 specialist 角色
