#!/bin/bash
# 创建开发分支脚本

set -euo pipefail

if [ $# -lt 2 ]; then
    cat <<EOF
用法: $0 <type> <description>

类型 (type):
  feat      - 新功能
  fix       - Bug 修复
  docs      - 文档更新
  style     - 格式调整
  refactor  - 代码重构
  test      - 测试相关
  chore     - 构建、依赖等

描述 (description): 简短的描述（使用小写字母和连字符）

示例:
  $0 feat add-github-workflow
  $0 fix lint-error
  $0 docs update-readme

EOF
    exit 1
fi

TYPE=$1
DESCRIPTION=$2

# 验证类型
VALID_TYPES="feat fix docs style refactor test chore perf"
if ! echo "$VALID_TYPES" | grep -w "$TYPE" > /dev/null; then
    echo "❌ 错误：类型 '$TYPE' 不在有效列表中"
    echo "有效类型: $VALID_TYPES"
    exit 1
fi

# 标准化描述
DESCRIPTION=$(echo "$DESCRIPTION" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')

BRANCH_NAME="${TYPE}/${DESCRIPTION}"

# 确保在最新 main 上创建
git fetch origin
git checkout -b "$BRANCH_NAME" origin/main

echo "✅ 已创建开发分支: $BRANCH_NAME"
echo ""
echo "下一步:"
echo "  1. 进行开发工作"
echo "  2. 提交更改: git commit -m \"${TYPE}(${DESCRIPTION}): 描述\""
echo "  3. 推送到远程: git push origin $BRANCH_NAME"
echo "  4. 创建 Pull Request"
