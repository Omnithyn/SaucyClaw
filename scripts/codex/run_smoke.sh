#!/bin/bash
# SaucyClaw Codex smoke test helper

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT_DIR"

echo "========================================"
echo "🧪 SaucyClaw Codex Smoke Test"
echo "========================================"
echo ""

echo "1) 建议先阅读以下文件："
echo "   - README.md"
echo "   - AGENTS.md"
echo "   - system/SYSTEM_SPEC.md"
echo "   - system/AGENTS.md"
echo "   - agents/general-manager/AGENTS.md"
echo "   - examples/codex/smoke-task.md"
echo ""

echo "2) 检查关键入口文件是否存在..."
REQUIRED_FILES=(
  "README.md"
  "AGENTS.md"
  "CLAUDE.md"
  "system/SYSTEM_SPEC.md"
  "system/AGENTS.md"
  "agents/general-manager/AGENTS.md"
  "examples/codex/smoke-task.md"
)

MISSING=0
for file in "${REQUIRED_FILES[@]}"; do
  if [ -f "$file" ]; then
    echo "✅ $file"
  else
    echo "❌ $file"
    MISSING=$((MISSING + 1))
  fi
done

echo ""
echo "3) 如存在结构校验脚本，则一并执行..."
if [ -x "scripts/validate/check_structure.sh" ]; then
  ./scripts/validate/check_structure.sh || true
else
  echo "ℹ️ 未找到 scripts/validate/check_structure.sh，可跳过。"
fi

echo ""
echo "4) 推荐交给 Codex 的第一条任务："
echo "   请阅读 examples/codex/smoke-task.md，并基于当前仓库给出一次最小可验证迭代方案。"
echo ""

if [ "$MISSING" -gt 0 ]; then
  echo "⚠️ Smoke test completed with $MISSING missing files."
  exit 1
fi

echo "✅ Smoke test passed."
