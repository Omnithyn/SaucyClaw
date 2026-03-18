#!/bin/bash
# 合并后清理本地和远程分支

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")/../.."

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}===================================${NC}"
echo -e "${BLUE}🦞 清理已合并的分支${NC}"
echo -e "${BLUE}===================================${NC}"
echo ""

cd "$PROJECT_ROOT"

# 获取当前分支
CURRENT_BRANCH=$(git symbolic-ref --short HEAD)

# 检查是否在 main
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo -e "${YELLOW}⚠️  警告：当前不在 main 分支${NC}"
    read -p "是否切换到 main 并继续？(y/N): " -r
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git checkout main
        git pull
    else
        echo -e "${RED}取消操作${NC}"
        exit 1
    fi
fi

# 获取远程已删除的本地分支
echo -e "${YELLOW}查找已合并的远程分支...${NC}"
DELETED_BRANCHES=$(git branch -r --merged | grep -v "origin/main$\|origin/HEAD" | sed 's/origin\///' | while read branch; do
    if ! git ls-remote --heads origin "$branch" > /dev/null 2>&1; then
        echo "$branch"
    fi
done)

if [ -n "$DELETED_BRANCHES" ]; then
    echo -e "${GREEN}找到以下已删除的远程分支：${NC}"
    echo "$DELETED_BRANCHES" | while read branch; do
        echo "  - $branch"
    done
    echo ""
    read -p "是否删除这些本地分支？(y/N): " -r
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "$DELETED_BRANCHES" | while read branch; do
            git branch -d "$branch" 2>/dev/null || git branch -D "$branch"
            echo -e "${GREEN}✅ 已删除本地分支: $branch${NC}"
        done
    fi
else
    echo -e "${GREEN}✅ 无已删除的远程分支${NC}"
fi

echo ""
echo -e "${GREEN}===================================${NC}"
echo -e "${GREEN}✅ 清理完成！${NC}"
echo -e "${GREEN}===================================${NC}"
echo ""
echo "提示：如需删除当前已合并的分支，请手动执行："
echo "  git branch -d <branch-name>"
echo "  git push origin --delete <branch-name>"
echo ""
