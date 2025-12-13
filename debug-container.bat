@echo off
chcp 65001 >nul
echo 🔍 诊断容器问题

echo.
echo 📋 检查容器状态...
docker ps -a | findstr canteen-menu

echo.
echo 📝 查看容器日志...
docker logs canteen-menu

echo.
echo 🌐 测试API健康检查...
curl -f http://localhost:1214/api/health

echo.
echo 📁 检查容器内静态文件...
docker exec canteen-menu ls -la /app/static/

echo.
echo 🔧 检查Flask应用状态...
docker exec canteen-menu ps aux | grep python

pause