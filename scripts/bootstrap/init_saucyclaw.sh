#!/bin/bash
# SaucyClaw 项目初始化脚本
# 用于快速创建符合规范的 SaucyClaw 项目结构

set -euo pipefail

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "==================================="
echo "🦞 SaucyClaw Project Initializer"
echo "==================================="
echo ""

# 检查目标目录参数
if [ $# -lt 1 ]; then
    echo -e "${RED}用法: $0 <project-name>${NC}"
    echo ""
    echo "示例:"
    echo "  $0 my-agent-project"
    echo "  $0 /path/to/project"
    exit 1
fi

PROJECT_NAME=$1
TARGET_DIR=$PROJECT_NAME

# 检查目录是否已存在
if [ -d "$TARGET_DIR" ]; then
    echo -e "${YELLOW}⚠️  目录 $TARGET_DIR 已存在，将跳过已存在的文件${NC}"
    echo ""
else
    echo -e "${GREEN}📁 创建项目目录: $TARGET_DIR${NC}"
    mkdir -p "$TARGET_DIR"
fi

cd "$TARGET_DIR"

# 定义必需目录
REQUIRED_DIRS=(
    "system"
    "agents/general-manager"
    "agents/reviewer"
    "agents/specialists/researcher"
    "agents/specialists/architect"
    "agents/specialists/developer"
    "agents/specialists/writer"
    "agents/specialists/designer"
    "docs"
    "templates"
    "templates/docker"
    "templates/openclaw/project-skeleton"
    "templates/openclaw/agent-role-template"
    "templates/openclaw/workspace-bootstrap"
    "examples"
    "scripts/bootstrap"
    "scripts/validate"
    "scripts/demo"
    "scripts/utils"
    "tools/saucyclaw"
    "tools/saucyclaw/scaffold"
    "tools/saucyclaw/validators"
    "tools/saucyclaw/packagers"
    "tools/saucyclaw/utils"
    "tools/tests"
    "demo"
    "focus"
    "plaza/findings"
    "plaza/updates"
)

# 创建目录
echo -e "${GREEN}📋 创建项目目录结构...${NC}"
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        echo "  ✅ $dir/"
    fi
done
echo ""

# 创建系统层文件
echo -e "${GREEN}📄 创建系统层文件...${NC}"
SYSTEM_FILES=(
    "SYSTEM_SPEC.md"
    "AGENTS.md"
    "HUMAN_ROLES.md"
    "ORCHESTRATION.md"
    "MESSAGE_ROUTING.md"
    "TRIGGERS.md"
    "STANDARDS.md"
    "PROJECT_CONTEXT.md"
    "DECISIONS.md"
    "TASK_BOARD.yaml"
    "agenda.yaml"
)

for file in "${SYSTEM_FILES[@]}"; do
    if [ ! -f "system/$file" ]; then
        touch "system/$file"
        echo "  ✅ system/$file"
    fi
done
echo ""

# 创建 README.md
if [ ! -f "README.md" ]; then
    cat > README.md <<'EOF'
# My SaucyClaw Project

This is a SaucyClaw multi-agent governance project.

## Quick Start

```bash
# Validate project structure
./scripts/validate/check_structure.sh

# Create new agent role
./scripts/bootstrap/create_agent_role.sh my-agent

# Initialize demo environment
./scripts/demo/up_demo.sh
```

## Project Structure

See [CLAUDE.md](CLAUDE.md) for project guidelines.
EOF
    echo -e "  ✅ ${GREEN}README.md${NC}"
fi

# 创建 CLAUDE.md
if [ ! -f "CLAUDE.md" ]; then
    cat > CLAUDE.md <<'EOF'
# Project Guidelines

This project follows SaucyClaw governance principles.

## Core Principles

1. **OpenClaw Compatible** - Use AGENTS.md as the primary role definition
2. **Governance First** - Define rules before implementation
3. **AGENTS.md Centered** - Long-term behavior must be written to files
4. **Tool-Assisted** - Use scripts and tools for repetitive tasks

## Directory Structure

See the main SaucyClaw repository for detailed documentation.
EOF
    echo -e "  ✅ ${GREEN}CLAUDE.md${NC}"
fi

# 创建 .gitignore
if [ ! -f ".gitignore" ]; then
    cat > .gitignore <<'EOF'
# Python
__pycache__/
*.pyc
.venv/
venv/
*.egg-info/

# Environment
.env

# IDE
.DS_Store
.vscode/
.idea/

# Runtime data
.data/
.opencode/
.openspec/
EOF
    echo -e "  ✅ ${GREEN}.gitignore${NC}"
fi

# 创建验证脚本
if [ ! -f "scripts/validate/check_structure.sh" ]; then
    cat > scripts/validate/check_structure.sh <<'EOF'
#!/bin/bash
set -euo pipefail

echo "=== Validating SaucyClaw Project Structure ==="
echo ""

ERRORS=0

# Check required directories
echo "Checking required directories..."
REQUIRED_DIRS=(
    "system"
    "agents/general-manager"
    "agents/reviewer"
    "agents/specialists"
    "docs"
    "templates"
    "examples"
    "scripts"
    "tools"
    "demo"
    "focus"
    "plaza"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "✅ $dir/"
    else
        echo "❌ $dir/ (missing)"
        ERRORS=$((ERRORS + 1))
    fi
done

echo ""
echo "Validation complete: $ERRORS errors found"
exit $ERRORS
EOF
    chmod +x scripts/validate/check_structure.sh
    echo -e "  ✅ ${GREEN}scripts/validate/check_structure.sh${NC}"
fi

echo ""
echo -e "${GREEN}===================================${NC}"
echo -e "${GREEN}✅ Project initialization complete!${NC}"
echo -e "${GREEN}===================================${NC}"
echo ""
echo "Next steps:"
echo "1. Edit system/SYSTEM_SPEC.md to define your governance rules"
echo "2. Customize agents/ roles for your use case"
echo "3. Run ./scripts/validate/check_structure.sh to verify structure"
echo ""
