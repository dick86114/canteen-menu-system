@echo off
chcp 65001 >nul
echo 🌐 本地测试远程服务器

set /p SERVER_IP=请输入远程服务器IP地址: 

echo.
echo 🧪 测试远程服务器连接...

echo.
echo 1. 测试API健康检查...
curl -v http://%SERVER_IP%:1214/api/health

echo.
echo 2. 测试根路径...
curl -v http://%SERVER_IP%:1214/

echo.
echo 3. 测试菜单API...
curl -v http://%SERVER_IP%:1214/api/dates

echo.
echo 4. 检查HTTP响应头...
curl -I http://%SERVER_IP%:1214/

pause