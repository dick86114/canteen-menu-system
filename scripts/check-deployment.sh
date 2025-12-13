#!/bin/bash

# 食堂菜单系统部署状态检查脚本

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🍽️  食堂菜单系统部署状态检查${NC}"
echo "=================================="

# 获取仓库信息
if [ -d ".git" ]; then
    repo_url=$(git config --get remote.origin.url)
    if [[ $repo_url == *"github.com"* ]]; then
        # 提取用户名和仓库名
        if [[ $repo_url == *".git" ]]; then
            repo_path=$(echo $repo_url | sed 's/.*github.com[:/]\([^.]*\).git/\1/')
        else
            repo_path=$(echo $repo_url | sed 's/.*github.com[:/]\([^/]*\/[^/]*\).*/\1/')
        fi
        username=$(echo $repo_path | cut -d'/' -f1)
        repo_name=$(echo $repo_path | cut -d'/' -f2)
        
        echo -e "${BLUE}📋 仓库信息:${NC}"
        echo "  用户名: $username"
        echo "  仓库名: $repo_name"
        echo "  完整路径: $repo_path"
        echo ""
    else
        echo -e "${RED}❌ 未检测到GitHub仓库${NC}"
        exit 1
    fi
else
    echo -e "${RED}❌ 当前目录不是Git仓库${NC}"
    exit 1
fi

# 检查GitHub Actions工作流文件
echo -e "${YELLOW}🔍 检查GitHub Actions配置...${NC}"

if [ -f ".github/workflows/docker-publish.yml" ]; then
    echo -e "${GREEN}✅ Docker构建工作流已配置${NC}"
else
    echo -e "${RED}❌ 缺少Docker构建工作流文件${NC}"
fi

if [ -f ".github/workflows/release.yml" ]; then
    echo -e "${GREEN}✅ 发布工作流已配置${NC}"
else
    echo -e "${RED}❌ 缺少发布工作流文件${NC}"
fi

# 检查Dockerfile
if [ -f "Dockerfile" ]; then
    echo -e "${GREEN}✅ Dockerfile已存在${NC}"
else
    echo -e "${RED}❌ 缺少Dockerfile${NC}"
fi

# 检查docker-compose.yml
if [ -f "docker-compose.yml" ]; then
    echo -e "${GREEN}✅ Docker Compose配置已存在${NC}"
else
    echo -e "${RED}❌ 缺少Docker Compose配置${NC}"
fi

echo ""
echo -e "${BLUE}🚀 部署链接:${NC}"
echo "  GitHub仓库: https://github.com/$repo_path"
echo "  Actions页面: https://github.com/$repo_path/actions"
echo "  Packages页面: https://github.com/$repo_path/pkgs/container/$repo_name"
echo "  Releases页面: https://github.com/$repo_path/releases"

echo ""
echo -e "${YELLOW}📝 下一步操作:${NC}"
echo "1. 推送代码到GitHub仓库"
echo "2. 检查Actions页面确认工作流运行"
echo "3. 创建Release发布新版本"
echo "4. 使用GHCR镜像部署应用"

echo ""
echo -e "${BLUE}🐳 镜像拉取命令:${NC}"
echo "docker pull ghcr.io/$username/$repo_name:latest"

echo ""
echo -e "${GREEN}✅ 检查完成！${NC}"