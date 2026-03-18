#!/bin/bash
# 手动运行 pre-commit 检查脚本

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")/../.."

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}===================================${NC}"
echo -e "${BLUE}🦞 手动运行 Pre-commit 检查${NC}"
echo -e "${BLUE}===================================${NC}"
echo ""

# 进入项目根目录
cd "$PROJECT_ROOT"

# 1. 检查行尾空格
echo -e "${YELLOW}[1/5] 检查行尾空格...${NC}"
if git diff --cached --check > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 无行尾空格${NC}"
else
    echo -e "${RED}❌ 发现行尾空格${NC}"
    git diff --cached --check 2>&1
    exit 1
fi

# 2. 检查是否有修改
echo -e "${YELLOW}[2/5] 检查是否有实际修改...${NC}"
if git diff-index --cached --quiet HEAD -- 2>/dev/null; then
    echo -e "${RED}❌ 警告：没有待提交的修改${NC}"
    exit 1
else
    echo -e "${GREEN}✅ 有实际修改${NC}"
fi

# 3. 检查大文件
echo -e "${YELLOW}[3/5] 检查大文件 (>100KB)...${NC}"
LARGE_FILES=""
if git diff --cached --name-only | grep -q .; then
    LARGE_FILES=$(git diff --cached --name-only | while read -r file; do
        if [ -f "$file" ]; then
            size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo 0)
            if [ "$size" -gt 102400 ]; then
                echo "$file ($size bytes)"
            fi
        fi
    done)
fi

if [ -n "$LARGE_FILES" ]; then
    echo -e "${RED}❌ 发现大文件:${NC}"
    echo "$LARGE_FILES"
    echo -e "${YELLOW}提示：大文件应使用 Git LFS 管理${NC}"
    exit 1
else
    echo -e "${GREEN}✅ 无大文件${NC}"
fi

# 4. 检查 Python 语法
echo -e "${YELLOW}[4/5] 检查 Python 语法...${NC}"
PYTHON_FILES=$(git diff --cached --name-only | grep '\.py$' || true)
if [ -n "$PYTHON_FILES" ]; then
    if python3 -m py_compile $PYTHON_FILES > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Python 语法正确${NC}"
    else
        echo -e "${RED}❌ Python 语法错误${NC}"
        python3 -m py_compile $PYTHON_FILES 2>&1 || true
        exit 1
    fi
else
    echo -e "${BLUE}ℹ️  无 Python 文件${NC}"
fi

# 5. 检查 Shell 语法
echo -e "${YELLOW}[5/5] 检查 Shell 语法...${NC}"
SHELL_FILES=$(git diff --cached --name-only | grep '\.sh$' || true)
if [ -n "$SHELL_FILES" ]; then
    ERROR=0
    for file in $SHELL_FILES; do
        if [ -f "$file" ]; then
            if ! bash -n "$file" > /dev/null 2>&1; then
                echo -e "${RED}❌ Shell 语法错误: $file${NC}"
                bash -n "$file" 2>&1 || true
                ERROR=1
            fi
        fi
    done
    if [ $ERROR -eq 0 ]; then
        echo -e "${GREEN}✅ Shell 语法正确${NC}"
    else
        exit 1
    fi
else
    echo -e "${BLUE}ℹ️  无 Shell 文件${NC}"
fi

echo ""
echo -e "${GREEN}===================================${NC}"
echo -e "${GREEN}✅ 所有检查通过！${NC}"
echo -e "${GREEN}===================================${NC}"
echo ""
echo -e "${BLUE}提示：${NC}你也可以直接使用 ${YELLOW}git commit${NC}，hooks 会自动运行这些检查"
echo ""
