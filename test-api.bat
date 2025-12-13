@echo off
chcp 65001 >nul
echo 🧪 测试API端点

echo.
echo 测试健康检查端点...
curl -v http://localhost:1214/api/health

echo.
echo 测试根路径...
curl -v http://localhost:1214/

echo.
echo 测试菜单API...
curl -v http://localhost:1214/api/dates

pause