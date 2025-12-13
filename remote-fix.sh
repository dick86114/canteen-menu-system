#!/bin/bash

# 远程服务器容器修复脚本

echo "🔧 远程容器修复脚本"
echo "=================================="

# 停止现有容器
echo "⏹️ 停止现有容器..."
docker-compose -f compose.yaml down 2>/dev/null || echo "容器已停止或不存在"

# 清理旧镜像
echo "🧹 清理旧镜像..."
docker rmi ghcr.io/dick86114/canteen-menu-system:latest 2>/dev/null || echo "旧镜像已清理"

# 拉取最新镜像
echo "📥 拉取最新镜像..."
docker pull ghcr.io/dick86114/canteen-menu-system:latest

# 创建必要目录
echo "📁 创建菜单目录..."
mkdir -p ./menu

# 启动容器
echo "🚀 启动容器..."
docker-compose -f compose.yaml up -d

# 等待启动
echo "⏳ 等待容器启动..."
sleep 10

# 检查状态
echo "📋 检查容器状态..."
docker ps | grep canteen-menu

# 测试API
echo "🧪 测试API..."
sleep 5
curl -s http://localhost:1214/api/health && echo "✅ API正常" || echo "❌ API异常"

echo ""
echo "🎉 修复完成！请访问 http://你的服务器IP:1214"