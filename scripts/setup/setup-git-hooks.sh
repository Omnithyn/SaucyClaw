#!/bin/bash
# 安装 Git hooks 脚本

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")/.."
GIT_DIR="$PROJECT_ROOT/.git/hooks"

echo "==================================="
echo "🦞 SaucyClaw Git Hooks 安装"
echo "==================================="
echo ""

# 确认 .git 目录存在
if [ ! -d "$GIT_DIR" ]; then
    echo "❌ 错误: .git 目录不存在"
    exit 1
fi

# 定义 hooks 文件
HOOKS=(
    "pre-commit"
    "commit-msg"
    "pre-push"
)

echo "安装以下 hooks:"
for hook in "${HOOKS[@]}"; do
    source_file="$SCRIPT_DIR/git-hooks/$hook"
    target_file="$GIT_DIR/$hook"

    if [ -f "$source_file" ]; then
        # 创建符号链接
        ln -sf "$source_file" "$target_file"
        chmod +x "$source_file"

        echo "  ✅ $hook"
    else
        echo "  ⚠️  $hook (源文件不存在: $source_file)"
    fi
done

echo ""
echo "所有 hooks 已安装到 $GIT_DIR/"
echo ""
echo "hooks 说明:"
echo "  • pre-commit: 提交前检查代码格式、空格等"
echo "  • commit-msg: 验证提交信息格式是否符合规范"
echo "  • pre-push: 阻止直接推送到 main 分支，运行测试"
echo ""
echo "如需禁用 hooks (不推荐):"
echo "  git commit --no-verify"
echo "  git push --no-verify"
echo ""
