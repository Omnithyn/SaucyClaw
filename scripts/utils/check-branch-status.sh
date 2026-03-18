#!/bin/bash
# 检查本地分支状态和待处理的 PR

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")/../.."

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

cd "$PROJECT_ROOT"

echo -e "${BLUE}===================================${NC}"
echo -e "${BLUE}🦞 分支状态检查${NC}"
echo -e "${BLUE}===================================${NC}"
echo ""

# 当前分支
CURRENT=$(git symbolic-ref --short HEAD)
echo -e "${BLUE}当前分支：${NC}$CURRENT"
echo ""

# 本地分支列表
echo -e "${BLUE}本地分支：${NC}"
git branch -v | while read line; do
    if echo "$line" | grep -q "^\*"; then
        echo -e "${GREEN}$line${NC}"
    else
        echo "$line"
    fi
done
echo ""

# 检查是否有未推送的提交
echo -e "${BLUE}检查未推送的提交：${NC}"
UNPUSHED=$(git log @{u}.. 2>/dev/null | head -20 || true)
if [ -n "$UNPUSHED" ]; then
    echo -e "${YELLOW}⚠️  有未推送的提交：${NC}"
    echo "$UNPUSHED"
else
    echo -e "${GREEN}✅ 所有提交已推送${NC}"
fi
echo ""

# 检查是否有未提交的修改
echo -e "${BLUE}检查未提交的修改：${NC}"
STATUS=$(git status --short)
if [ -n "$STATUS" ]; then
    echo -e "${YELLOW}⚠️  有未提交的修改：${NC}"
    echo "$STATUS" | head -10
    if [ "$(echo "$STATUS" | wc -l)" -gt 10 ]; then
        echo "  ...（还有更多）"
    fi
else
    echo -e "${GREEN}✅ 工作目录干净${NC}"
fi
echo ""

# 检查是否有远程已删除的本地分支
echo -e "${BLUE}检查远程已删除的本地分支：${NC}"
GONE=$(git branch -vv | grep ': gone]' | awk '{print $1}')
if [ -n "$GONE" ]; then
    echo -e "${YELLOW}⚠️  以下本地分支在远程已删除：${NC}"
    echo "$GONE" | while read branch; do
        echo "  - $branch"
    done
    echo ""
    echo "建议执行清理："
    echo "  ./scripts/utils/cleanup-merged-branch.sh"
else
    echo -e "${GREEN}✅ 无 gone 分支${NC}"
fi
echo ""

echo -e "${GREEN}===================================${NC}"
echo -e "${GREEN}✅ 检查完成！${NC}"
echo -e "${GREEN}===================================${NC}"
