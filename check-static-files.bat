@echo off
chcp 65001 >nul
echo 🔍 检查静态文件问题

echo.
echo 1. 检查静态文件目录是否存在...
docker exec canteen-menu ls -la /app/static/

echo.
echo 2. 检查静态文件内容...
docker exec canteen-menu find /app/static/ -type f

echo.
echo 3. 检查index.html是否存在...
docker exec canteen-menu cat /app/static/index.html

echo.
echo 4. 测试根路径...
curl -v http://localhost:1214/

pause