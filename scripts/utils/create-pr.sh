#!/bin/bash
# 快速创建 Pull Request 脚本（使用 GitHub CLI）

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")/../.."

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}===================================${NC}"
echo -e "${BLUE}🦞 创建 Pull Request${NC}"
echo -e "${BLUE}===================================${NC}"
echo ""

# 检查是否安装 gh
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ 错误：未找到 GitHub CLI (gh)${NC}"
    echo ""
    echo "请先安装 gh："
    echo "  macOS: brew install gh"
    echo "  Linux: curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg"
    exit 1
fi

# 获取当前分支名
CURRENT_BRANCH=$(git symbolic-ref --short HEAD 2>/dev/null)

# 检查是否在 main 或 develop
if [ "$CURRENT_BRANCH" = "main" ] || [ "$CURRENT_BRANCH" = "develop" ]; then
    echo -e "${RED}❌ 错误：不能在 $CURRENT_BRANCH 分支创建 PR${NC}"
    echo -e "${YELLOW}提示：请切换到开发分支${NC}"
    exit 1
fi

# 检查是否有远程分支
REMOTE_BRANCH=$(git rev-parse --symbolic-full-name --abbrev-ref @{u} 2>/dev/null || echo "")

if [ -z "$REMOTE_BRANCH" ]; then
    echo -e "${YELLOW}⚠️  警告：当前分支尚未推送到远程${NC}"
    echo ""
    read -p "是否现在推送？(y/N): " -r
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git push -u origin "$CURRENT_BRANCH"
    else
        echo -e "${RED}取消操作${NC}"
        exit 1
    fi
fi

# 检查远程仓库信息
REMOTE_URL=$(git remote get-url origin)
OWNER_REPO=$(echo "$REMOTE_URL" | sed -E 's/.*github.com[:\/]([^\/]+\/[^.]+).*/\1/')

echo -e "${GREEN}✅ 准备创建 Pull Request${NC}"
echo ""
echo -e "${BLUE}当前分支：${NC}$CURRENT_BRANCH"
echo -e "${BLUE}远程仓库：${NC}$OWNER_REPO"
echo ""

# 询问是否使用默认模板创建
read -p "是否使用默认模板创建 PR？(y/N): " -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # 使用 gh 命令创建 PR
    gh pr create --fill
    echo ""
    echo -e "${GREEN}===================================${NC}"
    echo -e "${GREEN}✅ PR 创建成功！${NC}"
    echo -e "${GREEN}===================================${NC}"
else
    # 生成 PR 链接
    echo -e "${YELLOW}===================================${NC}"
    echo -e "${YELLOW}📋 手动创建 PR 指引：${NC}"
    echo -e "${YELLOW}===================================${NC}"
    echo ""
    PR_URL="https://github.com/$OWNER_REPO/compare/main...$CURRENT_BRANCH?expand=1"
    echo -e "${GREEN}访问：${NC}$PR_URL"
    echo ""
    echo "或执行："
    echo "  gh pr create"
    echo ""

    # 提示填写 PR 模板内容
    echo -e "${BLUE}PR 模板内容（复制到 PR 描述中）：${NC}"
    cat <<EOF

## 📝 变更说明
<!-- 简要描述此 PR 的目的 -->

## 🔗 关联 Issue
<!-- 例如：Fixes #123 -->

## 🧪 测试计划
<!-- 说明如何测试这些更改 -->

## ✅ 检查清单
- [ ] 代码已通过自查
- [ ] 已添加/更新测试
- [ ] 文档已同步更新
- [ ] 变更日志已更新

## 📸 截图（如适用）
<!-- 上传前后对比截图 -->

EOF
fi
