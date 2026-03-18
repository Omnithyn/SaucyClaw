# OpenClaw Project Skeleton Template

This is a template for creating a new OpenClaw multi-agent project.

## 目录结构

```
project-name/
├── agents/
│   ├── general-manager/
│   │   ├── AGENTS.md
│   │   ├── soul.md
│   │   ├── memory.md
│   │   └── PROMPT.md
│   ├── reviewer/
│   └── specialists/
├── system/
│   ├── SYSTEM_SPEC.md
│   ├── AGENTS.md
│   ├── ORCHESTRATION.md
│   └── STANDARDS.md
├── templates/
├── examples/
├── focus/
├── plaza/
├── README.md
└── CLAUDE.md
```

## 使用说明

1. 复制此目录结构到新项目
2. 根据实际需求定制 system/ 下的治理规则
3. 创建或修改 agents/ 下的角色定义
4. 运行验证脚本确保结构正确

## 核心文件说明

### system/SYSTEM_SPEC.md
定义项目的整体治理规范和运行规则。

### system/AGENTS.md
定义系统级别的角色边界和协作规则。

### agents/general-manager/AGENTS.md
总经理角色的详细定义，包括职责、边界、输出规范。

### CLAUDE.md
项目级别的 Claude 指令文件，定义开发原则。
