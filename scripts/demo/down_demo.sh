#!/bin/bash
# 停止 Docker demo 环境

set -euo pipefail

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "==================================="
echo "🦞 Stop Docker Demo"
echo "==================================="
echo ""

# 检查 docker-compose 是否安装
if ! command -v docker-compose &> /dev/null && ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker 或 docker-compose 未安装${NC}"
    exit 1
fi

echo -e "${BLUE}🛑 停止容器...${NC}"
docker-compose -f templates/docker/docker-compose.yml down

echo ""
echo -e "${GREEN}✅ Docker Demo 已停止${NC}"
echo ""
echo "清理选项:"
echo "  1. 清理卷数据: docker-compose -f templates/docker/docker-compose.yml down -v"
echo "  2. 重新构建: ./scripts/demo/up_demo.sh"
echo ""
