#!/bin/bash
# Docker部署修复脚本 (Linux/Mac版本)

echo "=== 食堂菜单系统 Docker 部署修复 ==="
echo

echo "1. 停止现有容器..."
docker stop canteen-menu 2>/dev/null
docker rm canteen-menu 2>/dev/null
echo

echo "2. 重新构建镜像..."
docker build -t ghcr.io/dick86114/canteen-menu-system:latest .
if [ $? -ne 0 ]; then
    echo "构建失败！"
    exit 1
fi
echo

echo "3. 启动新容器..."
docker-compose up -d
if [ $? -ne 0 ]; then
    echo "启动失败！"
    exit 1
fi
echo

echo "4. 等待容器启动..."
sleep 10
echo

echo "5. 检查容器状态..."
docker ps | grep canteen-menu
echo

echo "6. 查看启动日志..."
docker logs canteen-menu --tail 20
echo

echo "7. 测试API连接..."
sleep 5
curl -s http://localhost:1214/api/health | python -m json.tool 2>/dev/null || echo "API连接失败"
echo

echo "8. 手动触发菜单扫描..."
curl -s -X POST http://localhost:1214/api/scanner/scan | python -m json.tool 2>/dev/null
echo

echo "=== 修复完成 ==="
echo "请访问 http://localhost:1214 查看应用"
echo "如果仍有问题，请运行 ./debug-docker.sh 进行诊断"