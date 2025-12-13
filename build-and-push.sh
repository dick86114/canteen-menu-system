#!/bin/bash

# 食堂菜单系统 Docker 镜像构建和发布脚本

set -e

# 配置变量
DOCKER_USERNAME="your-dockerhub-username"
IMAGE_NAME="canteen-menu-system"
VERSION="latest"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🍽️  食堂菜单系统 Docker 构建脚本${NC}"
echo "=================================="

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker 未安装，请先安装 Docker${NC}"
    exit 1
fi

# 检查是否登录Docker Hub
echo -e "${YELLOW}📋 检查 Docker Hub 登录状态...${NC}"
if ! docker info | grep -q "Username"; then
    echo -e "${YELLOW}🔐 请登录 Docker Hub:${NC}"
    docker login
fi

# 构建前端
echo -e "${YELLOW}🔨 构建前端应用...${NC}"
cd frontend
npm ci
npm run build
cd ..

# 构建Docker镜像
echo -e "${YELLOW}🐳 构建 Docker 镜像...${NC}"
docker build -t ${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION} .

# 添加额外标签
docker tag ${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION} ${DOCKER_USERNAME}/${IMAGE_NAME}:$(date +%Y%m%d)

# 推送到Docker Hub
echo -e "${YELLOW}📤 推送镜像到 Docker Hub...${NC}"
docker push ${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION}
docker push ${DOCKER_USERNAME}/${IMAGE_NAME}:$(date +%Y%m%d)

echo -e "${GREEN}✅ 构建和推送完成！${NC}"
echo -e "${GREEN}📦 镜像地址: ${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION}${NC}"
echo ""
echo -e "${YELLOW}🚀 使用方法:${NC}"
echo "docker run -d --name canteen-menu -p 5000:5000 -v \$(pwd)/menu:/app/menu ${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION}"
echo ""
echo -e "${YELLOW}📖 更多信息请查看 README.md${NC}"