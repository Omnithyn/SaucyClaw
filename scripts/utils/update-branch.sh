#!/bin/bash
# 更新当前分支到最新 main

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")/../.."

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}===================================${NC}"
echo -e "${BLUE}🦞 更新分支到最新 main${NC}"
echo -e "${BLUE}===================================${NC}"
echo ""

cd "$PROJECT_ROOT"

# 获取当前分支
CURRENT_BRANCH=$(git symbolic-ref --short HEAD)

# 检查是否在 main
if [ "$CURRENT_BRANCH" = "main" ]; then
    echo -e "${YELLOW}当前在 main 分支，直接拉取最新代码${NC}"
    git pull
    echo -e "${GREEN}✅ main 分支已更新${NC}"
    exit 0
fi

echo -e "${YELLOW}当前分支：${NC}$CURRENT_BRANCH"
echo ""

# 确认操作
read -p "是否将 $CURRENT_BRANCH 变基到最新 main？(y/N): " -r
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}取消操作${NC}"
    exit 1
fi

# 拉取最新 main
echo ""
echo -e "${YELLOW}拉取最新 main...${NC}"
git fetch origin

# 变基
echo -e "${YELLOW}执行变基...${NC}"
if git rebase origin/main; then
    echo ""
    echo -e "${GREEN}===================================${NC}"
    echo -e "${GREEN}✅ 变基成功！${NC}"
    echo -e "${GREEN}===================================${NC}"
    echo ""
    echo "提示：如果远程分支已有推送，需要强制推送："
    echo "  git push --force-with-lease origin $CURRENT_BRANCH"
else
    echo ""
    echo -e "${RED}❌ 变基失败，存在冲突${NC}"
    echo ""
    echo "请手动解决冲突："
    echo "  1. git status          # 查看冲突文件"
    echo "  2. 编辑冲突文件"
    echo "  3. git add <文件>      # 标记为已解决"
    echo "  4. git rebase --continue"
    echo ""
    exit 1
fi
