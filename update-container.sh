#!/bin/bash

echo "🔄 更新容器到最新版本..."
echo "================================"

echo "📥 拉取最新镜像..."
docker-compose -f compose.yaml pull

echo "🛑 停止当前容器..."
docker-compose -f compose.yaml down

echo "🚀 启动新容器..."
docker-compose -f compose.yaml up -d

echo "⏳ 等待容器启动..."
sleep 15

echo "🧪 测试健康状态..."
curl -s http://localhost:1214/api/health | jq . 2>/dev/null || curl -s http://localhost:1214/api/health

echo ""
echo "🔍 检查扫描状态..."
curl -s http://localhost:1214/api/scanner/status | jq . 2>/dev/null || curl -s http://localhost:1214/api/scanner/status

echo ""
echo "✅ 容器更新完成！"
echo "现在可以访问 http://192.168.31.60:1214 测试刷新功能。"