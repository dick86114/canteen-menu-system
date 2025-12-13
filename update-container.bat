@echo off
chcp 65001 >nul
echo 🔄 更新容器到最新版本

echo.
echo 1. 停止当前容器...
docker-compose -f compose.yaml down

echo.
echo 2. 拉取最新镜像...
docker pull ghcr.io/dick86114/canteen-menu-system:latest

echo.
echo 3. 重新启动容器...
docker-compose -f compose.yaml up -d

echo.
echo 4. 等待容器启动...
timeout /t 10

echo.
echo 5. 检查容器状态...
docker ps | findstr canteen-menu

echo.
echo 6. 测试API...
curl http://localhost:1214/api/health

pause