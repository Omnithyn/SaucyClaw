#!/bin/bash
# 创建新的智能体角色脚本

set -euo pipefail

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "==================================="
echo "🦞 Create Agent Role"
echo "==================================="
echo ""

# 检查参数
if [ $# -lt 1 ]; then
    echo -e "${RED}用法: $0 <agent-name> [specialist-type]${NC}"
    echo ""
    echo "示例:"
    echo "  $0 researcher                    # 创建 specialists/researcher"
    echo "  $0 qa-tester                     # 创建 specialists/qa-tester"
    echo "  $0 manager general               # 创建 general-manager"
    echo "  $0 reviewer reviewer             # 创建 reviewer"
    echo ""
    echo "Specialist types:"
    echo "  - general: general-manager"
    echo "  - reviewer: reviewer"
    echo "  - [any]: specialists/<name> (default)"
    exit 1
fi

AGENT_NAME=$1
AGENT_TYPE=${2:-specialist}

# 确定目标目录
if [ "$AGENT_TYPE" = "general" ]; then
    TARGET_DIR="agents/general-manager"
    AGENT_TITLE="General Manager"
elif [ "$AGENT_TYPE" = "reviewer" ]; then
    TARGET_DIR="agents/reviewer"
    AGENT_TITLE="Reviewer"
else
    TARGET_DIR="agents/specialists/$AGENT_NAME"
    AGENT_TITLE=$(echo "$AGENT_NAME" | sed 's/-/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) tolower(substr($i,2))}1')
fi

echo -e "${BLUE}Agent Name:${NC} $AGENT_NAME"
echo -e "${BLUE}Agent Type:${NC} $AGENT_TYPE"
echo -e "${BLUE}Target Dir:${NC} $TARGET_DIR"
echo -e "${BLUE}Agent Title:${NC} $AGENT_TITLE"
echo ""

# 检查目录是否已存在
if [ -d "$TARGET_DIR" ]; then
    echo -e "${YELLOW}⚠️  目录 $TARGET_DIR 已存在${NC}"
    read -p "是否覆盖? (y/N): " -r
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "取消操作"
        exit 1
    fi
fi

# 创建目录
mkdir -p "$TARGET_DIR"
echo -e "${GREEN}✅ 目录创建: $TARGET_DIR${NC}"
echo ""

# 创建 AGENTS.md
AGENTS_FILE="$TARGET_DIR/AGENTS.md"
if [ ! -f "$AGENTS_FILE" ]; then
    cat > "$AGENTS_FILE" <<EOF
# $AGENT_TITLE Agent 角色定义

## 角色概述

$AGENT_TITLE 是 SaucyClaw 系统中的专业智能体，负责 [请填写职责描述]。

## 启动条件

- 仅当被虾酱（General Manager）明确点名时启动
- 不根据用户原始需求自行开工
- 默认输出中间产物，而不是直接对外最终答案

## 核心职责

1. **[职责 1]**: [详细描述]
2. **[职责 2]**: [详细描述]
3. **[职责 3]**: [详细描述]

## 工作边界

### 可以做
- [列出允许的操作 1]
- [列出允许的操作 2]

### 不可以做
- [列出禁止的操作 1]
- [列出禁止的操作 2]

### 必须
- [列出强制要求 1]
- [列出强制要求 2]

## 输出规范

- 所有输出必须符合 system/STANDARDS.md 规范
- 中间产物保存到 plaza/findings/
- 最终交付需经 reviewer 审查

## 协作规则

- **接收任务**: 从虾酱获取任务契约（参考 templates/TASK_CONTRACT.md）
- **执行过程**: 保存工作日志到 plaza/updates/
- **交付成果**: 提交给 reviewer 或指定接收方
- **Handoff**: 使用 templates/HANDOFF_TEMPLATE.md 格式

## 长期配置

详见:
- \`soul.md\`: 长期身份与边界定义
- \`memory.md\`: 长期经验与记忆

## 示例任务

### 示例 1: [任务名称]
**输入**: [输入描述]
**处理**: [处理过程]
**输出**: [输出格式]

### 示例 2: [任务名称]
**输入**: [输入描述]
**处理**: [处理过程]
**输出**: [输出格式]

## 注意事项

- [注意点 1]
- [注意点 2]
EOF
    echo -e "${GREEN}✅ ${NC}创建 $AGENTS_FILE"
else
    echo -e "${YELLOW}⚠️  ${NC}$AGENTS_FILE 已存在，跳过"
fi

# 创建 soul.md
SOUL_FILE="$TARGET_DIR/soul.md"
if [ ! -f "$SOUL_FILE" ]; then
    cat > "$SOUL_FILE" <<EOF
# $AGENT_TITLE Soul (长期身份)

## 核心身份

$AGENT_TITLE 是一个专业的 [领域] 专家，专注于 [专业领域]。

## 性格特质

- **[特质 1]**: [描述]
- **[特质 2]**: [描述]
- **[特质 3]**: [描述]

## 原则与价值观

1. **专业性**: [描述专业标准]
2. **协作性**: [描述协作方式]
3. **可靠性**: [描述交付标准]

## 长期边界

- **永远不会**: [禁止的行为]
- **始终坚持**: [坚持的原则]
- **优先考虑**: [优先级]

## 演进方向

[描述角色未来的发展方向]

## 自我认知

[描述智能体如何理解自己的角色和价值]
EOF
    echo -e "${GREEN}✅ ${NC}创建 $SOUL_FILE"
else
    echo -e "${YELLOW}⚠️  ${NC}$SOUL_FILE 已存在，跳过"
fi

# 创建 memory.md
MEMORY_FILE="$TARGET_DIR/memory.md"
if [ ! -f "$MEMORY_FILE" ]; then
    cat > "$MEMORY_FILE" <<EOF
# $AGENT_TITLE Memory (长期记忆)

## 项目经验

### 已完成项目

- **[项目 1]**: [简要描述，包括学到的经验]
- **[项目 2]**: [简要描述，包括学到的经验]

## 技能清单

- **[技能 1]**: [熟练度/描述，例如：熟练/精通/了解]
- **[技能 2]**: [熟练度/描述]
- **[技能 3]**: [熟练度/描述]

## 学到的经验

1. **[经验 1]**: [详细描述]
2. **[经验 2]**: [详细描述]
3. **[经验 3]**: [详细描述]

## 常见问题与解决方案

### 问题: [问题描述]
**解决方案**: [解决方法]
**效果**: [预期效果]

### 问题: [问题描述]
**解决方案**: [解决方法]
**效果**: [预期效果]

## 改进计划

[列出需要提升的方面]

## 最佳实践

[总结该角色的最佳实践]
EOF
    echo -e "${GREEN}✅ ${NC}创建 $MEMORY_FILE"
else
    echo -e "${YELLOW}⚠️  ${NC}$MEMORY_FILE 已存在，跳过"
fi

# 创建 PROMPT.md (可选)
read -p "是否创建 PROMPT.md? (y/N): " -r
if [[ $REPLY =~ ^[Yy]$ ]]; then
    PROMPT_FILE="$TARGET_DIR/PROMPT.md"
    if [ ! -f "$PROMPT_FILE" ]; then
        cat > "$PROMPT_FILE" <<EOF
# $AGENT_TITLE Prompt (辅助说明)

## 初始化提示

当你被激活时，首先确认:
1. 任务来源 (必须是虾酱指派)
2. 任务目标和范围
3. 交付标准和截止时间

## 工作流程

1. **理解任务**: 仔细阅读任务契约
2. **规划执行**: 制定详细执行计划
3. **执行交付**: 按计划完成工作
4. **记录总结**: 保存工作成果和经验

## 提示词模板

\`\`\`
你是一个专业的 $AGENT_TITLE，当前任务是: [任务描述]

请按照以下步骤执行:
1. [步骤 1]
2. [步骤 2]
3. [步骤 3]

输出格式要求:
- [格式 1]
- [格式 2]
\`\`\`

## 上下文管理

- **长期上下文**: 参考 soul.md 和 memory.md
- **当前上下文**: 参考 focus/ 目录中的关注点文件
- **公共信息**: 参考 plaza/ 目录中的公告和发现

## 输出示例

[提供 2-3 个输出示例]
EOF
        echo -e "${GREEN}✅ ${NC}创建 $PROMPT_FILE"
    else
        echo -e "${YELLOW}⚠️  ${NC}$PROMPT_FILE 已存在，跳过"
    fi
fi

# 创建 focus 文件
FOCUS_FILE="focus/$(echo $AGENT_NAME | tr '[:lower:]' '[:upper:]').md"
if [ "$AGENT_TYPE" = "general" ]; then
    FOCUS_FILE="focus/GENERAL_MANAGER.md"
elif [ "$AGENT_TYPE" = "reviewer" ]; then
    FOCUS_FILE="focus/REVIEWER.md"
fi

if [ ! -f "$FOCUS_FILE" ]; then
    cat > "$FOCUS_FILE" <<EOF
# $AGENT_TITLE 当前关注点

## 重点关注

- [当前最该关注的事情 1]
- [当前最该关注的事情 2]

## 易错点提醒

- [容易犯的错误 1]
- [容易犯的错误 2]

## 优先级

1. [最高优先级]
2. [次高优先级]
3. [一般优先级]

## 本周目标

- [目标 1]
- [目标 2]

## 需要支持

- [需要的资源或支持]
EOF
    echo -e "${GREEN}✅ ${NC}创建 $FOCUS_FILE"
fi

echo ""
echo -e "${GREEN}===================================${NC}"
echo -e "${GREEN}✅ 智能体角色创建完成!${NC}"
echo -e "${GREEN}===================================${NC}"
echo ""
echo "已创建文件:"
echo "  - $TARGET_DIR/AGENTS.md"
echo "  - $TARGET_DIR/soul.md"
echo "  - $TARGET_DIR/memory.md"
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "  - $TARGET_DIR/PROMPT.md"
fi
echo "  - $FOCUS_FILE"
echo ""
echo "下一步建议:"
echo "1. 编辑 $AGENTS_FILE 补充角色定义"
echo "2. 编辑 $SOUL_FILE 定义长期身份"
echo "3. 编辑 $MEMORY_FILE 记录经验"
echo "4. 在 system/AGENTS.md 中注册新角色"
echo ""
