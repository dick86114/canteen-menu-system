#!/bin/bash

# 食堂菜单系统发布脚本

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🍽️  食堂菜单系统发布脚本${NC}"
echo "=================================="

# 检查是否在main分支
current_branch=$(git branch --show-current)
if [ "$current_branch" != "main" ]; then
    echo -e "${RED}❌ 请在main分支上执行发布${NC}"
    exit 1
fi

# 检查工作目录是否干净
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${RED}❌ 工作目录不干净，请先提交所有更改${NC}"
    exit 1
fi

# 获取版本号
if [ -z "$1" ]; then
    echo -e "${YELLOW}请输入版本号 (例如: 1.0.0):${NC}"
    read -r version
else
    version=$1
fi

# 验证版本号格式
if ! [[ $version =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo -e "${RED}❌ 版本号格式不正确，请使用 x.y.z 格式${NC}"
    exit 1
fi

tag="v$version"

# 检查标签是否已存在
if git tag -l | grep -q "^$tag$"; then
    echo -e "${RED}❌ 标签 $tag 已存在${NC}"
    exit 1
fi

echo -e "${BLUE}📋 发布信息:${NC}"
echo "  版本: $version"
echo "  标签: $tag"
echo "  分支: $current_branch"
echo ""

# 确认发布
read -p "确认发布? (y/N): " confirm
if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo -e "${YELLOW}❌ 发布已取消${NC}"
    exit 0
fi

# 运行测试
echo -e "${YELLOW}🧪 运行测试...${NC}"
cd frontend && npm test -- --watchAll=false && cd ..
cd backend && python -m pytest tests/ -v && cd ..

# 构建前端
echo -e "${YELLOW}🔨 构建前端...${NC}"
cd frontend && npm run build && cd ..

# 创建标签
echo -e "${YELLOW}🏷️  创建标签...${NC}"
git tag -a "$tag" -m "Release $version"

# 推送标签
echo -e "${YELLOW}📤 推送标签到GitHub...${NC}"
git push origin "$tag"

# 推送到main分支
git push origin main

echo -e "${GREEN}✅ 发布完成！${NC}"
echo ""
echo -e "${BLUE}📦 GitHub Actions将自动构建Docker镜像${NC}"
echo -e "${BLUE}🔗 查看构建状态: https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\([^.]*\).*/\1/')/actions${NC}"
echo ""
echo -e "${YELLOW}📝 下一步:${NC}"
echo "1. 访问GitHub创建Release说明"
echo "2. 等待Docker镜像构建完成"
echo "3. 测试新版本镜像"