@echo off
chcp 65001 >nul
echo 🔍 简单检查（不使用docker命令）

echo.
echo 1. 测试API健康检查...
curl -v http://localhost:1214/api/health

echo.
echo 2. 测试根路径...
curl -v http://localhost:1214/

echo.
echo 3. 测试其他端口（检查是否端口冲突）...
netstat -an | findstr :1214

pause