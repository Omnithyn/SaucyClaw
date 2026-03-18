#!/bin/bash
# 验证 SaucyClaw 项目结构

set -euo pipefail

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "==================================="
echo "🦞 Validate Project Structure"
echo "==================================="
echo ""

ERRORS=0
WARNINGS=0

# 检查必需目录
echo -e "${BLUE}📁 检查必需目录${NC}"
echo "-----------------------------------"
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
        echo -e "  ${GREEN}✅ $dir/${NC}"
    else
        echo -e "  ${RED}❌ $dir/ (缺失)${NC}"
        ERRORS=$((ERRORS + 1))
    fi
done
echo ""

# 检查系统文件
echo -e "${BLUE}📄 检查系统文件${NC}"
echo "-----------------------------------"
SYSTEM_FILES=(
    "SYSTEM_SPEC.md"
    "AGENTS.md"
    "HUMAN_ROLES.md"
    "ORCHESTRATION.md"
    "MESSAGE_ROUTING.md"
    "STANDARDS.md"
    "PROJECT_CONTEXT.md"
    "DECISIONS.md"
)

for file in "${SYSTEM_FILES[@]}"; do
    if [ -f "system/$file" ]; then
        SIZE=$(wc -c < "system/$file" 2>/dev/null || echo "0")
        if [ "$SIZE" -gt 10 ]; then
            echo -e "  ${GREEN}✅ system/$file ($SIZE bytes)${NC}"
        else
            echo -e "  ${YELLOW}⚠️  system/$file (内容过少)${NC}"
            WARNINGS=$((WARNINGS + 1))
        fi
    else
        echo -e "  ${YELLOW}⚠️  system/$file (不存在)${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
done
echo ""

# 检查智能体定义
echo -e "${BLUE}👥 检查智能体定义${NC}"
echo "-----------------------------------"

# 检查 general-manager
if [ -d "agents/general-manager" ]; then
    echo -e "  ${GREEN}✅ agents/general-manager/${NC}"
    if [ -f "agents/general-manager/AGENTS.md" ]; then
        echo -e "     ${GREEN}✅ AGENTS.md${NC}"
    else
        echo -e "     ${RED}❌ AGENTS.md (缺失)${NC}"
        ERRORS=$((ERRORS + 1))
    fi
    if [ -f "agents/general-manager/soul.md" ]; then
        echo -e "     ${GREEN}✅ soul.md${NC}"
    else
        echo -e "     ${YELLOW}⚠️  soul.md (建议添加)${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
    if [ -f "agents/general-manager/memory.md" ]; then
        echo -e "     ${GREEN}✅ memory.md${NC}"
    else
        echo -e "     ${YELLOW}⚠️  memory.md (建议添加)${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo -e "  ${RED}❌ agents/general-manager/ (缺失)${NC}"
    ERRORS=$((ERRORS + 1))
fi

# 检查 reviewer
if [ -d "agents/reviewer" ]; then
    echo -e "  ${GREEN}✅ agents/reviewer/${NC}"
    if [ -f "agents/reviewer/AGENTS.md" ]; then
        echo -e "     ${GREEN}✅ AGENTS.md${NC}"
    else
        echo -e "     ${RED}❌ AGENTS.md (缺失)${NC}"
        ERRORS=$((ERRORS + 1))
    fi
fi

# 检查 specialists
if [ -d "agents/specialists" ]; then
    echo -e "  ${GREEN}✅ agents/specialists/${NC}"
    # 统计 specialists 数量
    SPECIALIST_DIRS=$(find agents/specialists -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | xargs)
    if [ "$SPECIALIST_DIRS" -gt 0 ]; then
        echo -e "     找到 ${GREEN}$SPECIALIST_DIRS${NC} 个 specialist"
        # 检查每个 specialist 的文件
        find agents/specialists -mindepth 1 -maxdepth 1 -type d | while read specialist_dir; do
            specialist_name=$(basename "$specialist_dir")
            echo -e "     - ${BLUE}$specialist_name${NC}"
            if [ ! -f "$specialist_dir/AGENTS.md" ]; then
                echo -e "       ${RED}❌ 缺少 AGENTS.md${NC}"
                ERRORS=$((ERRORS + 1))
            fi
            if [ ! -f "$specialist_dir/soul.md" ]; then
                echo -e "       ${YELLOW}⚠️  缺少 soul.md${NC}"
                WARNINGS=$((WARNINGS + 1))
            fi
            if [ ! -f "$specialist_dir/memory.md" ]; then
                echo -e "       ${YELLOW}⚠️  缺少 memory.md${NC}"
                WARNINGS=$((WARNINGS + 1))
            fi
        done
    else
        echo -e "     ${YELLOW}⚠️  未找到任何 specialist${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
fi
echo ""

# 检查文档
echo -e "${BLUE}📚 检查文档${NC}"
echo "-----------------------------------"
if [ -f "README.md" ]; then
    SIZE=$(wc -c < "README.md" 2>/dev/null || echo "0")
    if [ "$SIZE" -gt 100 ]; then
        echo -e "  ${GREEN}✅ README.md ($SIZE bytes)${NC}"
    else
        echo -e "  ${YELLOW}⚠️  README.md (内容过少)${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo -e "  ${RED}❌ README.md (缺失)${NC}"
    ERRORS=$((ERRORS + 1))
fi

if [ -f "CLAUDE.md" ]; then
    echo -e "  ${GREEN}✅ CLAUDE.md${NC}"
else
    echo -e "  ${YELLOW}⚠️  CLAUDE.md (建议添加)${NC}"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

# 检查模板
echo -e "${BLUE}📋 检查模板${NC}"
echo "-----------------------------------"
if [ -d "templates" ]; then
    TEMPLATE_COUNT=$(find templates -name "*.md" 2>/dev/null | wc -l | xargs)
    echo -e "  ${GREEN}✅ templates/ ($TEMPLATE_COUNT 个模板)${NC}"
else
    echo -e "  ${YELLOW}⚠️  templates/ (建议添加)${NC}"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

# 检查脚本
echo -e "${BLUE}🔧 检查脚本${NC}"
echo "-----------------------------------"
if [ -d "scripts/bootstrap" ]; then
    BOOTSTRAP_COUNT=$(find scripts/bootstrap -name "*.sh" 2>/dev/null | wc -l | xargs)
    echo -e "  ${GREEN}✅ scripts/bootstrap/ ($BOOTSTRAP_COUNT 个脚本)${NC}"
else
    echo -e "  ${YELLOW}⚠️  scripts/bootstrap/ (建议添加)${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

if [ -d "scripts/validate" ]; then
    VALIDATE_COUNT=$(find scripts/validate -name "*.sh" 2>/dev/null | wc -l | xargs)
    echo -e "  ${GREEN}✅ scripts/validate/ ($VALIDATE_COUNT 个脚本)${NC}"
else
    echo -e "  ${YELLOW}⚠️  scripts/validate/ (建议添加)${NC}"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

# 输出总结
echo "==================================="
echo -e "${BLUE}📊 检查总结${NC}"
echo "==================================="
echo -e "✅ ${GREEN}通过: $((REQUIRED_DIRS + SYSTEM_FILES + 1))${NC}"
echo -e "⚠️  ${YELLOW}警告: $WARNINGS${NC}"
echo -e "❌ ${RED}错误: $ERRORS${NC}"
echo ""

if [ $ERRORS -gt 0 ]; then
    echo -e "${RED}❌ 项目结构: 不完整${NC}"
    echo "建议修复上述错误后再继续开发"
    exit 1
elif [ $WARNINGS -gt 5 ]; then
    echo -e "${YELLOW}⚠️  项目结构: 需要改进${NC}"
    echo "建议处理上述警告以提高项目质量"
    exit 0
else
    echo -e "${GREEN}✅ 项目结构: 良好${NC}"
    exit 0
fi
