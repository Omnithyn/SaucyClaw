#!/bin/bash
# 回退最后一次提交（保留修改）

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")/../.."

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}===================================${NC}"
echo -e "${BLUE}🦞 回退最后一次提交${NC}"
echo -e "${BLUE}===================================${NC}"
echo ""

cd "$PROJECT_ROOT"

# 显示最近的提交
echo -e "${YELLOW}最近的提交：${NC}"
git log -1 --oneline
echo ""

read -p "是否回退最后一次提交（保留修改）？(y/N): " -r
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}取消操作${NC}"
    exit 1
fi

# 执行回退
git reset --soft HEAD~1

echo ""
echo -e "${GREEN}✅ 已回退最后一次提交${NC}"
echo ""
echo "现在你可以："
echo "  - 修改代码后重新提交"
echo "  - git commit -m \"新的提交信息\""
echo "  - git push --force-with-lease (如果已推送)"
echo ""
