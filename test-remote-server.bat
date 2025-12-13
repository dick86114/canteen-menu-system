@echo off
chcp 65001 >nul
echo 🌐 测试远程Debian服务器

echo 请将下面的IP地址替换为你的Debian服务器IP
echo.

set /p SERVER_IP=输入你的Debian服务器IP地址: 

echo.
echo 🧪 测试远程服务器 %SERVER_IP%:1214

echo.
echo 1. 测试API健康检查...
curl -v http://%SERVER_IP%:1214/api/health

echo.
echo 2. 测试根路径...
curl -v http://%SERVER_IP%:1214/

echo.
echo 3. 检查端口连通性...
telnet %SERVER_IP% 1214

pause