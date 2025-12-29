@echo off
REM Docker部署修复脚本

echo === 食堂菜单系统 Docker 部署修复 ===
echo.

echo 1. 停止现有容器...
docker stop canteen-menu 2>nul
docker rm canteen-menu 2>nul
echo.

echo 2. 重新构建镜像...
docker build -t ghcr.io/dick86114/canteen-menu-system:latest .
if %errorlevel% neq 0 (
    echo 构建失败！
    pause
    exit /b 1
)
echo.

echo 3. 启动新容器...
docker-compose up -d
if %errorlevel% neq 0 (
    echo 启动失败！
    pause
    exit /b 1
)
echo.

echo 4. 等待容器启动...
timeout /t 10 /nobreak >nul
echo.

echo 5. 检查容器状态...
docker ps | findstr canteen-menu
echo.

echo 6. 查看启动日志...
docker logs canteen-menu --tail 20
echo.

echo 7. 测试API连接...
timeout /t 5 /nobreak >nul
curl -s http://localhost:1214/api/health || echo API连接失败
echo.

echo 8. 手动触发菜单扫描...
curl -s -X POST http://localhost:1214/api/scanner/scan
echo.

echo === 修复完成 ===
echo 请访问 http://localhost:1214 查看应用
echo 如果仍有问题，请运行 debug-docker.bat 进行诊断
pause