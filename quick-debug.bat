@echo off
chcp 65001 >nul
echo 🔍 快速诊断404问题

echo.
echo 1. 检查容器是否运行...
docker ps | findstr canteen-menu

echo.
echo 2. 测试API健康检查...
curl http://localhost:1214/api/health

echo.
echo 3. 查看容器日志（最后10行）...
docker logs --tail 10 canteen-menu

echo.
echo 4. 检查容器内静态文件...
docker exec canteen-menu ls -la /app/static/

echo.
echo 5. 检查Flask应用是否启动...
docker exec canteen-menu ps aux | findstr python

pause