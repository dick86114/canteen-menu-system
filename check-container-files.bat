@echo off
chcp 65001 >nul
echo 🔍 检查容器内文件结构

echo.
echo 📁 检查工作目录...
docker exec canteen-menu pwd
docker exec canteen-menu ls -la

echo.
echo 📁 检查静态文件目录...
docker exec canteen-menu ls -la static/ || echo "静态文件目录不存在"

echo.
echo 📁 检查静态文件内容...
docker exec canteen-menu find static/ -type f || echo "静态文件目录为空"

echo.
echo 🐍 检查Python进程...
docker exec canteen-menu ps aux | grep python

echo.
echo 🌐 检查端口监听...
docker exec canteen-menu netstat -tlnp | grep 5000

echo.
echo 📝 检查应用日志...
docker logs --tail 20 canteen-menu

pause