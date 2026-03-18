#!/bin/bash
# 启动 Docker demo 环境

set -euo pipefail

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "==================================="
echo "🦞 Start Docker Demo"
echo "==================================="
echo ""

# 检查 docker-compose 是否安装
if ! command -v docker-compose &> /dev/null && ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker 或 docker-compose 未安装${NC}"
    echo "请先安装 Docker: https://www.docker.com/get-started"
    exit 1
fi

# 检查 Docker 是否运行
if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker 服务未运行${NC}"
    echo "请启动 Docker 服务后重试"
    exit 1
fi

# 检查环境变量文件
ENV_FILE=".env.demo"
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${YELLOW}⚠️  $ENV_FILE 不存在，创建默认配置${NC}"
    cat > "$ENV_FILE" <<'EOF'
# SaucyClaw Demo Environment Variables
ANTHROPIC_API_KEY=your-api-key-here
ANTHROPIC_BASE_URL=https://api.anthropic.com
PROJECT_NAME=SaucyClaw-Demo
LOG_LEVEL=INFO
EOF
    echo -e "${GREEN}✅ 已创建 $ENV_FILE${NC}"
    echo -e "${YELLOW}⚠️  请编辑 $ENV_FILE 并设置 ANTHROPIC_API_KEY${NC}"
    echo ""
fi

# 加载环境变量
export $(grep -v '^#' $ENV_FILE | xargs)

echo -e "${BLUE}📦 构建 Docker 镜像...${NC}"
docker-compose -f templates/docker/docker-compose.yml build

echo ""
echo -e "${BLUE}🚀 启动容器...${NC}"
docker-compose -f templates/docker/docker-compose.yml up -d

echo ""
echo -e "${GREEN}===================================${NC}"
echo -e "${GREEN}✅ Docker Demo 启动成功!${NC}"
echo -e "${GREEN}===================================${NC}"
echo ""
echo "容器信息:"
docker-compose -f templates/docker/docker-compose.yml ps
echo ""
echo "访问方式:"
echo "  1. 进入容器: docker exec -it saucyclaw-agent bash"
echo "  2. 运行脚本: docker exec saucyclaw-agent ./scripts/validate/check_structure.sh"
echo "  3. 停止服务: ./scripts/demo/down_demo.sh"
echo ""
echo "数据持久化:"
echo "  - 工作目录: /workspace (项目根目录)"
echo "  - 数据目录: /workspace/.data"
echo "  - 公共信息: /workspace/plaza"
echo ""
