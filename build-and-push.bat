@echo off
REM 食堂菜单系统 Docker 镜像构建和发布脚本 (Windows)

setlocal enabledelayedexpansion

REM 配置变量
set DOCKER_USERNAME=dick86114
set IMAGE_NAME=canteen-menu-system
set VERSION=latest

echo 🍽️  食堂菜单系统 Docker 构建脚本
echo ==================================

REM 检查Docker是否安装
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker 未安装，请先安装 Docker
    pause
    exit /b 1
)

REM 检查是否登录Docker Hub
echo 📋 检查 Docker Hub 登录状态...
docker info | findstr "Username" >nul
if errorlevel 1 (
    echo 🔐 请登录 Docker Hub:
    docker login
)

REM 构建前端
echo 🔨 构建前端应用...
cd frontend
call npm ci
call npm run build
cd ..

REM 构建Docker镜像
echo 🐳 构建 Docker 镜像...
docker build -t %DOCKER_USERNAME%/%IMAGE_NAME%:%VERSION% .

REM 添加额外标签
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YMD=%dt:~0,8%"
docker tag %DOCKER_USERNAME%/%IMAGE_NAME%:%VERSION% %DOCKER_USERNAME%/%IMAGE_NAME%:%YMD%

REM 推送到Docker Hub
echo 📤 推送镜像到 Docker Hub...
docker push %DOCKER_USERNAME%/%IMAGE_NAME%:%VERSION%
docker push %DOCKER_USERNAME%/%IMAGE_NAME%:%YMD%

echo ✅ 构建和推送完成！
echo 📦 镜像地址: %DOCKER_USERNAME%/%IMAGE_NAME%:%VERSION%
echo.
echo 🚀 使用方法:
echo docker run -d --name canteen-menu -p 5000:5000 -v "%cd%\menu:/app/menu" %DOCKER_USERNAME%/%IMAGE_NAME%:%VERSION%
echo.
echo 📖 更多信息请查看 README.md
pause